from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI(title="Transcription Service MVP")

class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "Transcription Service"
    version: str = "MVP"
    timestamp: datetime = datetime.now()
    port: int = int(os.environ.get('PORT', 8080))

@app.get("/")
async def root():
    return HealthResponse()

@app.get("/health")
async def health():
    return HealthResponse()

@app.get("/api/status")
async def status():
    return {
        "status": "operational",
        "features": "minimal",
        "deployment": "Railway MVP"
    }