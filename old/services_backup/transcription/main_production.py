from fastapi import FastAPI, HTTPException, UploadFile, File, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
from typing import Optional

app = FastAPI(
    title="AIBOA Transcription Service",
    description="Video/Audio to Text Transcription Service",
    version="1.0.0-PRODUCTION"
)

# Simple in-memory storage for MVP
transcription_jobs = {}

class TranscriptionRequest(BaseModel):
    youtube_url: str
    language: str = "ko"

class TranscriptionJob(BaseModel):
    id: str
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    error: Optional[str] = None

def verify_api_key(x_api_key: str = Header(None)):
    """Simple API key verification"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # For MVP, accept any non-empty key
    return True

@app.get("/")
async def root():
    return {
        "service": "AIBOA Transcription Service",
        "status": "running",
        "version": "1.0.0-PRODUCTION",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/health",
            "/api/transcribe/upload",
            "/api/transcribe/youtube",
            "/api/transcribe/{job_id}"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/transcribe/upload")
async def transcribe_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = "ko",
    x_api_key: str = Header(None)
):
    """Upload file for transcription"""
    verify_api_key(x_api_key)
    
    job_id = str(uuid.uuid4())
    job = TranscriptionJob(
        id=job_id,
        status="processing",
        created_at=datetime.now()
    )
    transcription_jobs[job_id] = job
    
    # Simulate processing (in production, would use Whisper API)
    background_tasks.add_task(process_transcription, job_id, file.filename, language)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"File {file.filename} queued for transcription"
    }

@app.post("/api/transcribe/youtube")
async def transcribe_youtube(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    """Process YouTube URL for transcription"""
    verify_api_key(x_api_key)
    
    job_id = str(uuid.uuid4())
    job = TranscriptionJob(
        id=job_id,
        status="processing",
        created_at=datetime.now()
    )
    transcription_jobs[job_id] = job
    
    # Simulate processing
    background_tasks.add_task(process_youtube, job_id, request.youtube_url, request.language)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"YouTube URL queued for transcription"
    }

@app.get("/api/transcribe/{job_id}")
async def get_job_status(job_id: str, x_api_key: str = Header(None)):
    """Check transcription job status"""
    verify_api_key(x_api_key)
    
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = transcription_jobs[job_id]
    return {
        "job_id": job.id,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "result": job.result,
        "error": job.error
    }

async def process_transcription(job_id: str, filename: str, language: str):
    """Simulate transcription processing"""
    import asyncio
    await asyncio.sleep(2)  # Simulate processing time
    
    job = transcription_jobs[job_id]
    job.status = "completed"
    job.completed_at = datetime.now()
    job.result = {
        "text": f"[샘플 전사] 이것은 {filename} 파일의 전사 결과입니다.",
        "language": language,
        "duration": "00:05:00",
        "segments": [
            {"start": 0.0, "end": 5.0, "text": "안녕하세요, 오늘 수업을 시작하겠습니다."},
            {"start": 5.0, "end": 10.0, "text": "오늘 배울 내용은 매우 중요합니다."}
        ]
    }

async def process_youtube(job_id: str, url: str, language: str):
    """Simulate YouTube processing"""
    import asyncio
    await asyncio.sleep(3)  # Simulate processing time
    
    job = transcription_jobs[job_id]
    job.status = "completed"
    job.completed_at = datetime.now()
    job.result = {
        "text": f"[샘플 YouTube 전사] URL: {url}",
        "language": language,
        "duration": "00:10:00",
        "segments": [
            {"start": 0.0, "end": 5.0, "text": "YouTube 비디오 전사 시작"},
            {"start": 5.0, "end": 10.0, "text": "내용이 여기에 표시됩니다."}
        ]
    }