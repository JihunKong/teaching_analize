from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
import aiofiles
from typing import Optional

from ..models import (
    TranscriptionRequest, 
    YouTubeTranscriptionRequest,
    TranscriptionJob,
    JobStatus,
    TranscriptionMethod,
    OutputFormat,
    TranscriptionExport
)
from ..services.storage import StorageService
from ..services.whisper import WhisperService
from ..services.youtube import YouTubeService
from ..tasks import process_transcription_task
from ..database import get_db

router = APIRouter()
storage_service = StorageService()
whisper_service = WhisperService()
youtube_service = YouTubeService()

ALLOWED_EXTENSIONS = {'.mp3', '.mp4', '.wav', '.m4a', '.webm', '.mpeg', '.mpga'}
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

@router.post("/upload", response_model=TranscriptionJob)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = "ko",
    include_timestamps: bool = True,
    speaker_diarization: bool = False,
    db: Session = Depends(get_db)
):
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save file to storage
    try:
        file_path = await storage_service.save_upload(file, job_id)
        file_size = os.path.getsize(file_path)
        
        if file_size > MAX_FILE_SIZE:
            await storage_service.delete_file(file_path)
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 2GB")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create job record
    job = TranscriptionJob(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
        file_name=file.filename,
        file_size=file_size,
        language=language,
        method=TranscriptionMethod.WHISPER
    )
    
    # Save to database
    db_job = save_job_to_db(db, job)
    
    # Queue background task
    background_tasks.add_task(
        process_transcription_task,
        job_id=job_id,
        file_path=file_path,
        language=language,
        include_timestamps=include_timestamps,
        speaker_diarization=speaker_diarization
    )
    
    return job

@router.post("/youtube", response_model=TranscriptionJob)
async def transcribe_youtube(
    request: YouTubeTranscriptionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Validate YouTube URL
    if not youtube_service.validate_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    job_id = str(uuid.uuid4())
    
    # Try to get captions first if preferred
    if request.prefer_captions:
        try:
            captions = await youtube_service.get_captions(request.url, request.language)
            if captions:
                # Create completed job immediately
                job = TranscriptionJob(
                    job_id=job_id,
                    status=JobStatus.COMPLETED,
                    created_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    language=request.language,
                    method=TranscriptionMethod.YOUTUBE_CAPTIONS
                )
                
                # Save transcript
                await storage_service.save_transcript(job_id, captions)
                
                return job
        except Exception as e:
            print(f"Failed to get YouTube captions: {e}")
    
    # Fall back to downloading audio and using Whisper
    job = TranscriptionJob(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
        language=request.language,
        method=TranscriptionMethod.WHISPER
    )
    
    # Save to database
    db_job = save_job_to_db(db, job)
    
    # Queue background task
    background_tasks.add_task(
        process_youtube_transcription,
        job_id=job_id,
        url=request.url,
        language=request.language
    )
    
    return job

@router.get("/{job_id}/export", response_model=TranscriptionExport)
async def export_transcript(
    job_id: str,
    format: OutputFormat = OutputFormat.JSON,
    db: Session = Depends(get_db)
):
    # Get job from database
    job = get_job_from_db(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed. Current status: {job.status}"
        )
    
    # Load transcript
    transcript = await storage_service.load_transcript(job_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    # Convert to requested format
    if format == OutputFormat.JSON:
        content = json.dumps(transcript, ensure_ascii=False, indent=2)
    elif format == OutputFormat.SRT:
        content = convert_to_srt(transcript)
    elif format == OutputFormat.TXT:
        content = transcript.get("text", "")
    elif format == OutputFormat.VTT:
        content = convert_to_vtt(transcript)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    return TranscriptionExport(
        job_id=job_id,
        format=format,
        content=content,
        metadata={
            "language": job.language,
            "duration": job.duration,
            "created_at": job.created_at.isoformat()
        }
    )

# Helper functions
import json
from datetime import datetime

async def process_youtube_transcription(job_id: str, url: str, language: str):
    try:
        # Download audio from YouTube
        audio_path = await youtube_service.download_audio(url, job_id)
        
        # Process with Whisper
        await process_transcription_task(
            job_id=job_id,
            file_path=audio_path,
            language=language,
            include_timestamps=True,
            speaker_diarization=False
        )
    except Exception as e:
        # Update job status to failed
        print(f"YouTube transcription failed: {e}")
        # Update database with error

def save_job_to_db(db: Session, job: TranscriptionJob):
    # Implementation for saving job to database
    pass

def get_job_from_db(db: Session, job_id: str):
    # Implementation for getting job from database
    pass

def convert_to_srt(transcript: dict) -> str:
    # Convert transcript segments to SRT format
    srt_content = []
    for i, segment in enumerate(transcript.get("segments", []), 1):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"].strip()
        srt_content.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_content)

def convert_to_vtt(transcript: dict) -> str:
    # Convert transcript segments to WebVTT format
    vtt_content = ["WEBVTT\n"]
    for segment in transcript.get("segments", []):
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"].strip()
        vtt_content.append(f"{start} --> {end}\n{text}\n")
    return "\n".join(vtt_content)

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}".replace(".", ",")