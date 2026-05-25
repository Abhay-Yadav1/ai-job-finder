# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="AI Job Finder API")

# HINT: CORS configuration is crucial for local development.
# Without this, your React browser app will block the requests to the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite's default React port
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"], # Allow all headers
)

# Mount the routes we just created in routes.py
app.include_router(router, prefix="/api")

# A simple health check to verify the server is running
@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Job Finder Backend is running!"}