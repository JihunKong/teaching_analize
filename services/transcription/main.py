from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
import os
import uuid
import logging
import shutil
import tempfile
from datetime import datetime
from typing import Optional

# Local imports
from config import settings
from database import get_db, init_db, TranscriptionJob, JobStatus as DBJobStatus, TranscriptionType, SessionLocal
from schemas import (
    TranscriptionRequest,
    YouTubeTranscriptionRequest,
    TranscriptionJobResponse,
    TranscriptionStatusResponse,
    TranscriptionResultResponse,
    TranscriptionExportResponse,
    HealthResponse,
    ErrorResponse,
    JobStatus,
    ExportFormat
)
from auth import verify_api_key, get_optional_api_key
from whisper_client import WhisperClient
from youtube_handler import YouTubeHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION,
    description="AI-powered transcription service for converting audio/video to text",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize services
whisper_client = None
if settings.OPENAI_API_KEY:
    whisper_client = WhisperClient(settings.OPENAI_API_KEY)
    logger.info("Whisper client initialized")
else:
    logger.warning("OPENAI_API_KEY not set, Whisper transcription will not work")

youtube_handler = YouTubeHandler(settings.get_storage_path("youtube"))

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info(f"{settings.SERVICE_NAME} started on port {settings.PORT}")
    logger.info(f"Storage path: {settings.RAILWAY_VOLUME_PATH}")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION
    )

@app.post("/api/transcribe/upload", response_model=TranscriptionJobResponse)
async def upload_transcription(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = "ko",
    prompt: Optional[str] = None,
    temperature: float = 0.0,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Upload audio/video file for transcription
    
    - **file**: Audio or video file (mp3, wav, mp4, etc.)
    - **language**: Language code (ko for Korean, en for English, etc.)
    - **prompt**: Optional prompt to guide transcription
    - **temperature**: Sampling temperature (0-1)
    """
    if not whisper_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transcription service not configured"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    upload_dir = settings.get_storage_path("uploads")
    file_path = os.path.join(upload_dir, f"{job_id}_{file.filename}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file"
        )
    
    # Create job record
    job = TranscriptionJob(
        id=job_id,
        status=DBJobStatus.PENDING,
        type=TranscriptionType.FILE,
        file_path=file_path,
        original_filename=file.filename,
        file_size=file.size,
        language=language,
        api_key=api_key
    )
    db.add(job)
    db.commit()
    
    # Process in background
    background_tasks.add_task(
        process_transcription,
        job_id=job_id,
        file_path=file_path,
        language=language,
        prompt=prompt,
        temperature=temperature
    )
    
    return TranscriptionJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="File uploaded successfully, transcription started",
        created_at=job.created_at
    )

@app.post("/api/transcribe/youtube", response_model=TranscriptionJobResponse)
async def youtube_transcription(
    request: YouTubeTranscriptionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Transcribe YouTube video
    
    - **url**: YouTube video URL
    - **language**: Language code for transcription
    - **use_captions**: Try to use YouTube captions if available
    """
    if not whisper_client and not request.use_captions:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transcription service not configured"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    job = TranscriptionJob(
        id=job_id,
        status=DBJobStatus.PENDING,
        type=TranscriptionType.YOUTUBE,
        youtube_url=str(request.url),
        language=request.language,
        api_key=api_key
    )
    db.add(job)
    db.commit()
    
    # Process in background
    background_tasks.add_task(
        process_youtube_transcription,
        job_id=job_id,
        url=str(request.url),
        language=request.language,
        use_captions=request.use_captions
    )
    
    return TranscriptionJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="YouTube transcription started",
        created_at=job.created_at
    )

@app.get("/api/transcribe/{job_id}", response_model=TranscriptionStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get transcription job status
    """
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check API key matches
    if job.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return TranscriptionStatusResponse(
        job_id=job.id,
        status=JobStatus(job.status.value),
        created_at=job.created_at,
        updated_at=job.updated_at,
        error_message=job.error_message
    )

@app.get("/api/transcripts/{job_id}", response_model=TranscriptionResultResponse)
async def get_transcription_result(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get completed transcription result
    """
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check API key matches
    if job.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if job.status != DBJobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed. Current status: {job.status.value}"
        )
    
    return TranscriptionResultResponse(
        job_id=job.id,
        status=JobStatus.COMPLETED,
        text=job.transcript_text or "",
        language=job.language,
        duration=job.duration,
        word_count=job.word_count or 0,
        processing_time=job.processing_time or 0,
        segments=job.transcript_json.get("segments") if job.transcript_json else None
    )

@app.get("/api/transcripts/{job_id}/export")
async def export_transcription(
    job_id: str,
    format: ExportFormat = ExportFormat.TXT,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Export transcription in different formats
    
    - **format**: Export format (txt, srt, json)
    """
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check API key matches
    if job.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if job.status != DBJobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed. Current status: {job.status.value}"
        )
    
    # Generate export content
    if format == ExportFormat.TXT:
        content = job.transcript_text or ""
        media_type = "text/plain"
        extension = "txt"
    elif format == ExportFormat.SRT:
        content = job.transcript_srt or generate_srt(job.transcript_json)
        media_type = "text/plain"
        extension = "srt"
    elif format == ExportFormat.JSON:
        import json
        content = json.dumps(job.transcript_json or {}, ensure_ascii=False, indent=2)
        media_type = "application/json"
        extension = "json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}"
        )
    
    filename = f"transcript_{job_id}.{extension}"
    
    return PlainTextResponse(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# Background tasks
async def process_transcription(
    job_id: str,
    file_path: str,
    language: str,
    prompt: Optional[str],
    temperature: float
):
    """Process transcription job in background"""
    db = SessionLocal()
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
    
    if not job:
        logger.error(f"Job {job_id} not found")
        return
    
    try:
        # Update status to processing
        job.status = DBJobStatus.PROCESSING
        db.commit()
        
        start_time = datetime.now()
        
        # Check if video file needs conversion
        if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
            logger.info(f"Converting video to audio: {file_path}")
            audio_path = whisper_client.convert_to_audio(file_path)
        else:
            audio_path = file_path
        
        # Transcribe with Whisper
        logger.info(f"Starting transcription for job {job_id}")
        result = whisper_client.transcribe(
            file_path=audio_path,
            language=language,
            prompt=prompt,
            response_format="verbose_json",
            temperature=temperature
        )
        
        # Update job with results
        job.status = DBJobStatus.COMPLETED
        job.transcript_text = result["text"]
        job.transcript_json = result
        job.transcript_srt = generate_srt(result)
        job.word_count = len(result["text"].split())
        job.duration = result.get("duration")
        job.processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Transcription completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Transcription failed for job {job_id}: {str(e)}")
        job.status = DBJobStatus.FAILED
        job.error_message = str(e)
    
    finally:
        db.commit()
        db.close()
        
        # Clean up temporary audio file if created
        if 'audio_path' in locals() and audio_path != file_path:
            try:
                os.remove(audio_path)
            except:
                pass

async def process_youtube_transcription(
    job_id: str,
    url: str,
    language: str,
    use_captions: bool
):
    """Process YouTube transcription job in background"""
    db = SessionLocal()
    job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
    
    if not job:
        logger.error(f"Job {job_id} not found")
        return
    
    audio_path = None
    
    try:
        # Update status to processing
        job.status = DBJobStatus.PROCESSING
        db.commit()
        
        start_time = datetime.now()
        
        # Try to get captions first if requested
        if use_captions:
            logger.info(f"Trying to get YouTube captions for job {job_id}")
            caption_text = youtube_handler.get_captions(url, language)
            
            if caption_text:
                logger.info(f"Using YouTube captions for job {job_id}")
                job.status = DBJobStatus.COMPLETED
                job.transcript_text = caption_text
                job.transcript_json = {"text": caption_text, "source": "youtube_captions"}
                job.word_count = len(caption_text.split())
                job.processing_time = (datetime.now() - start_time).total_seconds()
                db.commit()
                return
        
        # Download audio from YouTube
        logger.info(f"Downloading YouTube audio for job {job_id}")
        audio_path, metadata = youtube_handler.download_audio(url)
        
        # Store metadata
        job.duration = metadata.get("duration")
        job.original_filename = metadata.get("title", "youtube_video")
        
        # Transcribe with Whisper
        logger.info(f"Transcribing YouTube audio for job {job_id}")
        result = whisper_client.transcribe(
            file_path=audio_path,
            language=language,
            response_format="verbose_json"
        )
        
        # Update job with results
        job.status = DBJobStatus.COMPLETED
        job.transcript_text = result["text"]
        job.transcript_json = {**result, "metadata": metadata}
        job.transcript_srt = generate_srt(result)
        job.word_count = len(result["text"].split())
        job.processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"YouTube transcription completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"YouTube transcription failed for job {job_id}: {str(e)}")
        job.status = DBJobStatus.FAILED
        job.error_message = str(e)
    
    finally:
        db.commit()
        db.close()
        
        # Clean up downloaded audio
        if audio_path:
            youtube_handler.cleanup(audio_path)

def generate_srt(transcript_data: dict) -> str:
    """Generate SRT format from transcript data"""
    if not transcript_data or "segments" not in transcript_data:
        return ""
    
    srt_lines = []
    for i, segment in enumerate(transcript_data["segments"], 1):
        start = format_timestamp(segment.get("start", 0))
        end = format_timestamp(segment.get("end", 0))
        text = segment.get("text", "").strip()
        
        srt_lines.append(f"{i}")
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)

def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.RAILWAY_ENVIRONMENT == "development" else None,
            "status_code": 500
        }
    )