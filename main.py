from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.routers import words

# Initialize FastAPI application
app = FastAPI(
    title="Gujarati API",
    description="API for Gujarati language words",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(words.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Gujarati API",
        "documentation": "/docs",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)