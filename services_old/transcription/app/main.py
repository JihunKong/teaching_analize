from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from .routers import transcribe, jobs
from .services.storage import StorageService
from .models import HealthCheck, TranscriptionJob
from .database import init_db, get_db

API_KEY = os.getenv("API_KEY", "development-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    # Cleanup code here if needed

app = FastAPI(
    title="AIBOA Transcription Service",
    description="Audio/Video transcription service for classroom analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/", tags=["root"])
async def root():
    return {
        "service": "AIBOA Transcription Service",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    return HealthCheck(
        status="healthy",
        service="transcription",
        timestamp=datetime.utcnow().isoformat()
    )

app.include_router(
    transcribe.router,
    prefix="/api/transcribe",
    tags=["transcription"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    jobs.router,
    prefix="/api/jobs",
    tags=["jobs"],
    dependencies=[Depends(verify_api_key)]
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "true" else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)