# backend/app/api/routes.py
import json
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any

from ..utils.parsers import extract_text_from_file
from ..agent.graph import agent_app

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Extracts text from uploaded PDF/DOCX and returns it to be cached by the frontend."""
    try:
        file_bytes = await file.read()
        extracted_text = extract_text_from_file(file_bytes, file.filename)
        return {"status": "success", "text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search-jobs")
async def search_jobs(payload: Dict[str, Any]):
    """
    Expects JSON payload: {"raw_resume_text": "...", "filters": {...}}
    Streams agent progress step-by-step.
    """
    
    # HINT: This is an async generator function. It yields data chunks one by one.
    async def event_generator():
        initial_state = {
            "raw_resume_text": payload.get("raw_resume_text"),
            "user_query": payload.get("user_query"),
            "filters": payload.get("filters", {}),
        }

        # LangGraph's .astream() yields the output of each node as it finishes!
        try:
            # TODO: Write a loop to iterate through the asynchronous stream:
            async for event in agent_app.astream(initial_state):
                if isinstance(event, dict):
                    for node_name, state_update in event.items():
                        chunk = {"node": node_name, "message": f"Finished {node_name}..."}
                        if node_name == "parse_results":
                            chunk["final_jobs"] = state_update.get("final_jobs", [])
                        yield f"data: {json.dumps(chunk)}\n\n"
                        await asyncio.sleep(0.1)  # tiny delay to keep the stream flowing smoothly
            
        except Exception as e:
            # If something breaks, stream the error back to the UI
            error_chunk = {"node": "error", "message": f"Agent crashed: {str(e)}"}
            yield f"data: {json.dumps(error_chunk)}\n\n"

    # Return the streaming response instead of standard JSON
    return StreamingResponse(event_generator(), media_type="text/event-stream")