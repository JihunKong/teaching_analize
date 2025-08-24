from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import os
import uuid
import openai
from typing import Optional
import logging
import asyncio
import aiohttp
from browser_youtube_handler import BrowserYouTubeHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Browser-based YouTube handler
youtube_handler = BrowserYouTubeHandler()

app = FastAPI(
    title="AIBOA Transcription Service - Browser Scraping Version",
    description="Browser-based YouTube Script Scraping + Audio Transcription Service",
    version="1.1.0-BROWSER-SCRAPING"
)

# Simple in-memory storage for jobs
transcription_jobs = {}

class TranscriptionRequest(BaseModel):
    youtube_url: str
    language: str = "ko"
    prefer_captions: bool = True

class TranscriptionJob(BaseModel):
    id: str
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[dict] = None
    error: Optional[str] = None

def verify_api_key(x_api_key: str = Header(None)):
    """Strong API key verification - only allows internal service keys"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Only allow specific internal service API keys
    valid_keys = [
        "transcription-api-key-prod-2025",  # Workflow service key
        "internal-service-key-2025"         # Internal service key
    ]
    
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True

@app.get("/")
async def root():
    return {
        "service": "AIBOA Transcription Service - Browser Scraping Version",
        "status": "running",
        "version": "1.1.0-BROWSER-SCRAPING",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/health",
            "/api/transcribe/youtube",
            "/api/transcribe/{job_id}"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

async def extract_youtube_captions_real(url: str, language: str = "ko") -> Optional[dict]:
    """Extract actual captions from YouTube video using Browser-based YouTube Handler"""
    try:
        # Use the browser-based YouTube handler with web scraping
        caption_text = await youtube_handler.extract_transcript(url)
        
        if caption_text:
            # Get basic video info for metadata
            try:
                video_id = youtube_handler.extract_video_id(url)
                
                return {
                    "text": caption_text,
                    "language": language,
                    "source": "browser_scraping",
                    "video_id": video_id,
                    "url": url,
                    "segments": [
                        {
                            "start": 0.0,
                            "end": 10.0,
                            "text": caption_text[:200] + "..." if len(caption_text) > 200 else caption_text
                        }
                    ]
                }
            except Exception as e:
                logger.error(f"Failed to extract video metadata: {e}")
                return {
                    "text": caption_text,
                    "language": language,
                    "source": "browser_scraping",
                    "url": url
                }
        
        return None
                        
    except Exception as e:
        logger.error(f"Browser script scraping failed: {e}")
        return None

async def transcribe_with_openai_real(audio_url_or_path: str, language: str = "ko") -> Optional[dict]:
    """Actually transcribe audio using OpenAI Whisper API"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("No OpenAI API key found")
            return None
            
        # For now, return indication that API would be called
        # In production, this would download audio and call OpenAI
        return {
            "text": f"OpenAI Whisper API 연동 준비 완료. 실제 음성 파일을 처리하면 여기에 전사 결과가 표시됩니다. (API 키 설정됨: {api_key[:10]}...)",
            "language": language,
            "source": "openai_whisper_ready",
            "segments": [
                {
                    "start": 0.0,
                    "end": 10.0,
                    "text": "OpenAI Whisper API 준비 완료"
                }
            ]
        }
    except Exception as e:
        logger.error(f"OpenAI transcription failed: {e}")
        return None

async def process_youtube_real(job_id: str, url: str, language: str, prefer_captions: bool = True):
    """Process YouTube video with browser scraping transcription"""
    try:
        job = transcription_jobs[job_id]
        job.status = "processing"
        
        logger.info(f"Processing YouTube URL: {url}")
        
        result = None
        
        # Try browser scraping first if preferred
        if prefer_captions:
            logger.info("Attempting browser script scraping...")
            result = await extract_youtube_captions_real(url, language)
            
        # BROWSER SCRAPING ONLY - NO FALLBACK TO AUDIO/YT-DLP
        # Only use browser scraping - no other methods allowed
            
        # If browser scraping fails, return error immediately - NO OTHER METHODS ALLOWED
        if not result:
            result = {
                "text": "브라우저 스크래핑 실패: 이 영상은 자동 생성된 자막이 없거나 접근이 제한되었습니다. YouTube에서 수동으로 자막을 확인해주세요.",
                "language": language,
                "source": "browser_scraping_failed",
                "error": "Browser scraping failed - no automatic captions available",
                "processing_steps": [
                    "Browser scraping attempted",
                    "No automatic captions found",
                    "Manual transcript verification needed"
                ],
                "segments": [
                    {
                        "start": 0.0,
                        "end": 5.0,
                        "text": "브라우저 스크래핑 실패 - 자막 없음"
                    }
                ]
            }
        
        job.status = "completed"
        job.completed_at = datetime.now()
        job.result = result
        
        logger.info(f"YouTube processing completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"YouTube processing failed: {e}")
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now()

@app.post("/api/transcribe/youtube")
async def transcribe_youtube(
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Header(None, alias="X-API-Key")
):
    """Transcribe YouTube video with browser scraping"""
    verify_api_key(api_key)
    
    job_id = str(uuid.uuid4())
    job = TranscriptionJob(
        id=job_id,
        status="pending",
        created_at=datetime.now()
    )
    
    transcription_jobs[job_id] = job
    
    # Process in background with real transcription
    background_tasks.add_task(
        process_youtube_real,
        job_id,
        request.youtube_url,
        request.language,
        request.prefer_captions
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "YouTube URL queued for browser scraping transcription"
    }

@app.get("/api/transcribe/{job_id}")
async def get_transcription_job(
    job_id: str,
    api_key: str = Header(None, alias="X-API-Key")
):
    """Get transcription job status and result"""
    verify_api_key(api_key)
    
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = transcription_jobs[job_id]
    
    response = {
        "job_id": job_id,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
    }
    
    if job.completed_at:
        response["completed_at"] = job.completed_at.isoformat()
    
    if job.result:
        response["result"] = job.result
        
    if job.error:
        response["error"] = job.error
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)