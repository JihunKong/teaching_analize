from celery import Celery, Task
from celery.result import AsyncResult
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .services.whisper import WhisperService
from .services.storage import StorageService
from .database import update_job_status, update_job_progress

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
app = Celery(
    'transcription',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    task_soft_time_limit=1500,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Initialize services
whisper_service = WhisperService()
storage_service = StorageService()

class CallbackTask(Task):
    """Task with callbacks for status updates"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Success callback"""
        job_id = kwargs.get('job_id')
        if job_id:
            logger.info(f"Task completed successfully for job {job_id}")
            update_job_status(job_id, "completed")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback"""
        job_id = kwargs.get('job_id')
        if job_id:
            logger.error(f"Task failed for job {job_id}: {str(exc)}")
            update_job_status(job_id, "failed", error_message=str(exc))
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Retry callback"""
        job_id = kwargs.get('job_id')
        if job_id:
            logger.warning(f"Task retrying for job {job_id}: {str(exc)}")

@app.task(base=CallbackTask, bind=True, max_retries=3)
def process_transcription_task(
    self,
    job_id: str,
    file_path: str,
    language: str = "ko",
    include_timestamps: bool = True,
    speaker_diarization: bool = False
) -> Dict[str, Any]:
    """
    Process audio/video file transcription
    
    Args:
        job_id: Unique job identifier
        file_path: Path to the audio/video file
        language: Language code for transcription
        include_timestamps: Whether to include timestamps
        speaker_diarization: Whether to perform speaker diarization
        
    Returns:
        Transcription result dictionary
    """
    try:
        logger.info(f"Starting transcription for job {job_id}")
        
        # Update job status to processing
        update_job_status(job_id, "processing")
        update_job_progress(job_id, 10)
        
        # Validate audio file
        validation = whisper_service.validate_audio_file(file_path)
        if not validation.get("valid"):
            raise ValueError(f"Invalid audio file: {validation.get('error')}")
        
        duration = validation.get("duration", 0)
        update_job_progress(job_id, 20)
        
        # Perform transcription
        logger.info(f"Transcribing file: {file_path}")
        
        # Build prompt for better Korean transcription
        prompt = None
        if language == "ko":
            prompt = "이것은 한국어 수업 녹음입니다. 교사와 학생들의 대화를 정확하게 전사해주세요."
        
        transcript = whisper_service.transcribe(
            file_path=file_path,
            language=language,
            include_timestamps=include_timestamps,
            prompt=prompt
        )
        
        update_job_progress(job_id, 70)
        
        # Perform speaker diarization if requested
        if speaker_diarization:
            logger.info("Performing speaker diarization...")
            transcript = perform_speaker_diarization(transcript, file_path)
            update_job_progress(job_id, 85)
        
        # Save transcript
        logger.info(f"Saving transcript for job {job_id}")
        storage_service.save_transcript(job_id, transcript)
        update_job_progress(job_id, 95)
        
        # Clean up uploaded file
        try:
            storage_service.delete_file(file_path)
        except Exception as e:
            logger.warning(f"Failed to delete uploaded file: {e}")
        
        # Update job completion
        update_job_status(
            job_id, 
            "completed",
            duration=duration,
            completed_at=datetime.utcnow()
        )
        update_job_progress(job_id, 100)
        
        logger.info(f"Transcription completed for job {job_id}")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "duration": duration,
            "language": language,
            "segments_count": len(transcript.get("segments", [])),
            "text_length": len(transcript.get("text", ""))
        }
        
    except Exception as e:
        logger.error(f"Transcription failed for job {job_id}: {str(e)}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_in = 2 ** self.request.retries * 60  # Exponential backoff
            logger.info(f"Retrying job {job_id} in {retry_in} seconds...")
            raise self.retry(exc=e, countdown=retry_in)
        
        # Final failure
        update_job_status(job_id, "failed", error_message=str(e))
        raise

@app.task(bind=True, max_retries=2)
def process_youtube_transcription(
    self,
    job_id: str,
    url: str,
    language: str = "ko"
) -> Dict[str, Any]:
    """
    Process YouTube video transcription
    
    Args:
        job_id: Unique job identifier
        url: YouTube video URL
        language: Language code for transcription
        
    Returns:
        Transcription result dictionary
    """
    try:
        from .services.youtube import YouTubeService
        youtube_service = YouTubeService()
        
        logger.info(f"Starting YouTube transcription for job {job_id}")
        
        # Update job status
        update_job_status(job_id, "processing")
        update_job_progress(job_id, 10)
        
        # Get video info
        video_info = youtube_service.get_video_info(url)
        duration = video_info.get("duration", 0)
        update_job_progress(job_id, 20)
        
        # Try to get captions first
        captions = youtube_service.get_captions(url, language)
        
        if captions:
            logger.info(f"Using YouTube captions for job {job_id}")
            transcript = captions
            update_job_progress(job_id, 80)
        else:
            # Download audio and transcribe
            logger.info(f"Downloading audio from YouTube for job {job_id}")
            audio_path = youtube_service.download_audio(url, job_id=job_id)
            update_job_progress(job_id, 50)
            
            # Transcribe with Whisper
            logger.info(f"Transcribing with Whisper for job {job_id}")
            transcript = whisper_service.transcribe(
                file_path=audio_path,
                language=language,
                include_timestamps=True
            )
            update_job_progress(job_id, 80)
            
            # Clean up audio file
            try:
                storage_service.delete_file(audio_path)
            except Exception as e:
                logger.warning(f"Failed to delete audio file: {e}")
        
        # Save transcript
        storage_service.save_transcript(job_id, transcript)
        update_job_progress(job_id, 95)
        
        # Update job completion
        update_job_status(
            job_id,
            "completed",
            duration=duration,
            completed_at=datetime.utcnow()
        )
        update_job_progress(job_id, 100)
        
        logger.info(f"YouTube transcription completed for job {job_id}")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "duration": duration,
            "language": language,
            "source": transcript.get("source", "whisper"),
            "segments_count": len(transcript.get("segments", [])),
            "text_length": len(transcript.get("text", ""))
        }
        
    except Exception as e:
        logger.error(f"YouTube transcription failed for job {job_id}: {str(e)}")
        
        if self.request.retries < self.max_retries:
            retry_in = 2 ** self.request.retries * 60
            logger.info(f"Retrying YouTube job {job_id} in {retry_in} seconds...")
            raise self.retry(exc=e, countdown=retry_in)
        
        update_job_status(job_id, "failed", error_message=str(e))
        raise

@app.task
def cleanup_old_files_task():
    """Periodic task to clean up old files"""
    try:
        logger.info("Starting cleanup of old files...")
        deleted_count = storage_service.cleanup_old_files()
        logger.info(f"Cleanup completed. Deleted {deleted_count} items.")
        return {"deleted_count": deleted_count}
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise

def perform_speaker_diarization(
    transcript: Dict[str, Any],
    audio_path: str
) -> Dict[str, Any]:
    """
    Perform speaker diarization on transcript
    
    This is a placeholder for actual speaker diarization implementation.
    You could use libraries like pyannote.audio or speechbrain for this.
    
    Args:
        transcript: Original transcript
        audio_path: Path to audio file
        
    Returns:
        Transcript with speaker labels
    """
    # TODO: Implement actual speaker diarization
    # For now, just return the original transcript
    logger.info("Speaker diarization not yet implemented")
    return transcript

# Periodic tasks configuration
from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'app.tasks.cleanup_old_files_task',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}

# Task monitoring
@app.task
def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get status of a Celery task"""
    result = AsyncResult(task_id, app=app)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.successful() else None,
        "error": str(result.info) if result.failed() else None,
        "ready": result.ready()
    }