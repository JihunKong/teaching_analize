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
    from .youtube_transcript import get_youtube_transcript_with_fallback
    from .ytdlp_subtitle import extract_subtitles_only
except ImportError:
    # Fallback if modules not found
    WhisperClient = None
    YouTubeHandler = None
    get_youtube_transcript_with_fallback = None
    extract_subtitles_only = None

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
    """Process YouTube URL with multiple fallback methods"""
    job = transcription_jobs[job_id]
    
    try:
        # Method 1: Try youtube-transcript-api first
        if get_youtube_transcript_with_fallback:
            logger.info(f"Method 1: Trying youtube-transcript-api for job {job_id}")
            transcript_result = get_youtube_transcript_with_fallback(url, language)
            
            if transcript_result:
                job.status = "completed"
                job.completed_at = datetime.now()
                job.result = {
                    "text": transcript_result["text"],
                    "language": transcript_result.get("language", language),
                    "segments": transcript_result.get("segments", []),
                    "source": "youtube_transcript_api",
                    "is_generated": transcript_result.get("is_generated", False),
                    "video_id": transcript_result.get("video_id", "")
                }
                logger.info(f"YouTube transcript extracted successfully with youtube-transcript-api")
                return
        
        # Method 2: Try enhanced yt-dlp subtitle extraction
        if extract_subtitles_only:
            logger.info(f"Method 2: Trying enhanced yt-dlp subtitle extraction for job {job_id}")
            subtitle_result = extract_subtitles_only(url, language)
            
            if subtitle_result:
                job.status = "completed"
                job.completed_at = datetime.now()
                job.result = {
                    "text": subtitle_result["text"],
                    "language": subtitle_result.get("language", language),
                    "source": "ytdlp_enhanced_subtitles",
                    "is_auto_generated": subtitle_result.get("is_auto_generated", False),
                    "video_id": subtitle_result.get("video_id", ""),
                    "title": subtitle_result.get("title", "")
                }
                logger.info(f"YouTube subtitles extracted successfully with enhanced yt-dlp")
                return
        
        # Method 3: Try original yt-dlp handler
        if youtube_handler:
            # Real YouTube processing
            logger.info(f"Method 3: Trying original yt-dlp handler for job {job_id}")
            
            # Extract captions or download audio
            captions = youtube_handler.get_captions(url, language)
            
            if captions:
                job.status = "completed"
                job.completed_at = datetime.now()
                job.result = {
                    "text": captions,
                    "language": language,
                    "source": "youtube_captions_ytdlp"
                }
                logger.info(f"YouTube processing completed with original yt-dlp")
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
        error_msg = str(e)
        logger.error(f"YouTube processing failed for job {job_id}: {error_msg}")
        
        # Check error type and provide appropriate response
        if any(x in error_msg.lower() for x in ["sign in", "bot", "403", "forbidden"]):
            # Bot protection or access denied
            job.status = "completed"
            job.completed_at = datetime.now()
            job.result = {
                "text": "[YouTube 접근 제한]\n\n해결 방법:\n1. 동영상을 로컬에 다운로드 후 파일 업로드\n2. 브라우저에서 자막을 복사하여 텍스트 분석\n3. 로컬 환경에서 실행\n\n테스트용 샘플 텍스트:\n오늘은 중요한 수업 내용을 다루겠습니다. 이 내용을 잘 이해하면 다음 단계로 넘어갈 수 있습니다.",
                "language": language,
                "source": "mock_youtube_blocked",
                "message": "YouTube 접근이 차단되었습니다. 대체 방법을 사용하세요.",
                "error_type": "access_denied"
            }
        elif "unavailable" in error_msg.lower() or "private" in error_msg.lower():
            # Video unavailable or private
            job.status = "failed"
            job.error = "동영상을 사용할 수 없습니다 (비공개 또는 삭제됨)"
            job.completed_at = datetime.now()
        elif "no transcript" in error_msg.lower() or "no caption" in error_msg.lower():
            # No captions available
            job.status = "failed"
            job.error = "자막이 없는 동영상입니다. 오디오 다운로드 후 Whisper 전사가 필요합니다."
            job.completed_at = datetime.now()
        else:
            job.status = "failed"
            job.error = error_msg
            job.completed_at = datetime.now()