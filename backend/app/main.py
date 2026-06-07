from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="AI Job Finder API")

# 1. The Standard CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.options("/{rest_of_path:path}")
async def preflight_fallback(rest_of_path: str, response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return {"message": "CORS preflight successful"}

# Mount your actual routes
app.include_router(router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Job Finder Backend is running!"}