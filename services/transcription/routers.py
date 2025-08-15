from fastapi import APIRouter, HTTPException, UploadFile, File, Header, BackgroundTasks, Form
from pydantic import BaseModel
from datetime import datetime
import uuid
import os
import sys
import logging
from typing import Optional
import asyncio
import aiofiles
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import settings

# Import real implementation modules
try:
    from .whisper_client import WhisperClient
    from .youtube_handler import YouTubeHandler
except ImportError:
    # Fallback if modules not found
    WhisperClient = None
    YouTubeHandler = None

router = APIRouter(prefix="/api/transcribe", tags=["transcription"])
logger = logging.getLogger(__name__)

# Initialize clients (will be None if API keys not configured)
whisper_client = None
youtube_handler = None

if settings.OPENAI_API_KEY and WhisperClient:
    whisper_client = WhisperClient(settings.OPENAI_API_KEY)
    logger.info("WhisperClient initialized with OpenAI API")
else:
    logger.warning("WhisperClient not initialized - using mock mode")

if YouTubeHandler:
    youtube_handler = YouTubeHandler()
    logger.info("YouTubeHandler initialized")

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
    file_path: Optional[str] = None

def verify_api_key(x_api_key: str = Header(None)):
    """Simple API key verification"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    return True

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file to storage"""
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(upload_file.filename).suffix
        file_path = settings.UPLOAD_DIR / f"{file_id}{file_ext}"
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await upload_file.read()
            await f.write(content)
        
        logger.info(f"Saved upload file to {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Failed to save upload file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save file")

@router.post("/upload")
async def transcribe_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form("ko"),
    x_api_key: str = Header(None)
):
    """Upload file for transcription"""
    verify_api_key(x_api_key)
    
    # Check file type
    if not settings.is_media_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Save file
    try:
        file_path = await save_upload_file(file)
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Create job
    job_id = str(uuid.uuid4())
    job = TranscriptionJob(
        id=job_id,
        status="processing",
        created_at=datetime.now(),
        file_path=file_path
    )
    transcription_jobs[job_id] = job
    
    # Process in background
    background_tasks.add_task(process_transcription, job_id, file_path, language)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"File {file.filename} queued for transcription"
    }

@router.post("/youtube")
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
    
    # Process in background
    background_tasks.add_task(process_youtube, job_id, request.youtube_url, request.language)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": f"YouTube URL queued for transcription"
    }

@router.get("/{job_id}")
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

async def process_transcription(job_id: str, file_path: str, language: str):
    """Process transcription with real Whisper API or mock"""
    job = transcription_jobs[job_id]
    
    try:
        if whisper_client:
            # Real Whisper transcription
            logger.info(f"Starting real Whisper transcription for job {job_id}")
            
            # Convert video to audio if needed
            if settings.is_video_file(file_path):
                logger.info(f"Converting video to audio: {file_path}")
                audio_path = whisper_client.convert_to_audio(file_path)
            else:
                audio_path = file_path
            
            # Transcribe
            result = whisper_client.transcribe(
                audio_path,
                language=language,
                response_format="verbose_json"
            )
            
            # Clean up temporary audio file
            if audio_path != file_path and os.path.exists(audio_path):
                os.remove(audio_path)
            
            job.status = "completed"
            job.completed_at = datetime.now()
            job.result = result
            logger.info(f"Whisper transcription completed for job {job_id}")
            
        else:
            # Mock transcription
            logger.info(f"Using mock transcription for job {job_id}")
            await asyncio.sleep(2)  # Simulate processing
            
            job.status = "completed"
            job.completed_at = datetime.now()
            job.result = {
                "text": f"[모의 전사] 이것은 테스트 전사입니다. 실제 API 키를 설정하면 실제 전사가 수행됩니다.",
                "language": language,
                "duration": "00:05:00",
                "segments": [
                    {"start": 0.0, "end": 5.0, "text": "안녕하세요, 오늘 수업을 시작하겠습니다."},
                    {"start": 5.0, "end": 10.0, "text": "오늘 배울 내용은 매우 중요합니다."},
                    {"start": 10.0, "end": 15.0, "text": "OPENAI_API_KEY를 Railway에 설정하면 실제 전사가 가능합니다."}
                ]
            }
            
    except Exception as e:
        logger.error(f"Transcription failed for job {job_id}: {str(e)}")
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now()
    
    finally:
        # Clean up uploaded file after processing
        try:
            if job.file_path and os.path.exists(job.file_path):
                os.remove(job.file_path)
                logger.info(f"Cleaned up file: {job.file_path}")
        except Exception as e:
            logger.error(f"Failed to clean up file: {str(e)}")

async def process_youtube(job_id: str, url: str, language: str):
    """Process YouTube URL with real handler or mock"""
    job = transcription_jobs[job_id]
    
    try:
        if youtube_handler:
            # Real YouTube processing
            logger.info(f"Starting real YouTube processing for job {job_id}")
            
            # Extract captions or download audio
            captions = youtube_handler.get_captions(url, language)
            
            if captions:
                job.status = "completed"
                job.completed_at = datetime.now()
                job.result = {
                    "text": captions,
                    "language": language,
                    "source": "youtube_captions"
                }
                logger.info(f"YouTube processing completed for job {job_id}")
            else:
                # Fallback to downloading and transcribing
                if whisper_client:
                    audio_path, info = youtube_handler.download_audio(url)
                    result = whisper_client.transcribe(audio_path, language=language)
                    
                    # Clean up
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                    
                    job.status = "completed"
                    job.completed_at = datetime.now()
                    job.result = result
                else:
                    raise Exception("No captions available and Whisper not configured")
                    
        else:
            # Mock YouTube processing
            logger.info(f"Using mock YouTube processing for job {job_id}")
            await asyncio.sleep(3)  # Simulate processing
            
            job.status = "completed"
            job.completed_at = datetime.now()
            job.result = {
                "text": f"[모의 YouTube 전사] URL: {url}\n실제 처리를 위해서는 API 키를 설정하세요.",
                "language": language,
                "duration": "00:10:00",
                "segments": [
                    {"start": 0.0, "end": 5.0, "text": "YouTube 비디오 전사 시작"},
                    {"start": 5.0, "end": 10.0, "text": "내용이 여기에 표시됩니다."},
                    {"start": 10.0, "end": 15.0, "text": "API 키 설정 후 실제 자막 추출이 가능합니다."}
                ]
            }
            
    except Exception as e:
        logger.error(f"YouTube processing failed for job {job_id}: {str(e)}")
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now()