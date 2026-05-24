# backend/test_agent.py
import json
from app.agent.nodes import (
    parse_resume_node,
    build_query_node,
    web_search_node,
    parse_results_node
)
from app.agent.state import AgentState

def run_test():
    print("--- STARTING AI NODE TEST ---\n")

    # 1. Initialize our mock AgentState
    # We pretend the user uploaded this resume and wants a remote job.
    mock_resume = """
    Abhay Sharma
    Software Engineering Student
    Experience: 
    - 6 months intern at TechCorp. Built React frontends and Python FastAPIs.
    Skills: Python, JavaScript, React, Node.js, AWS, SQL.
    Looking for Junior Software Engineer or Full Stack Developer roles.
    """
    
    state = AgentState(
        raw_resume_text=mock_resume,
        user_query=None,
        filters={"job_type": "Remote", "freshness": "Last 7 days"},
        parsed_profile=None,
        search_query="",
        raw_search_results=[],
        final_jobs=[]
    )

    try:
        # STEP 1: Test Resume Parsing (Groq API)
        print(">> Testing parse_resume_node...")
        result = parse_resume_node(state)
        state.update(result)
        print(f"Profile Extracted: {json.dumps(state['parsed_profile'], indent=2)}\n")

        # STEP 2: Test Query Building (Groq API)
        print(">> Testing build_query_node...")
        result = build_query_node(state)
        state.update(result)
        print(f"Search Query Built: '{state['search_query']}'\n")

        # STEP 3: Test Web Search (Tavily API)
        print(">> Testing web_search_node... (Fetching real jobs!)")
        result = web_search_node(state)
        state.update(result)
        print(f"Raw Jobs Found: {len(state['raw_search_results'])}\n")

        # STEP 4: Test Result Parsing (Groq API + Pydantic Strict JSON)
        print(">> Testing parse_results_node...")
        result = parse_results_node(state)
        state.update(result)
        print("Final Cleaned Job Cards:")
        print(json.dumps(state['final_jobs'], indent=2))
        
        print("\n--- TEST COMPLETE: ALL NODES FUNCTIONAL ---")

    except Exception as e:
        print(f"\n❌ ERROR OCCURRED: {str(e)}")
        print("Check your API keys and error message above.")

if __name__ == "__main__":
    run_test()