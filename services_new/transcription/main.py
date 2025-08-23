#!/usr/bin/env python3
"""
AIBOA Transcription Service
Robust implementation using the proven multi-method approach from TRANSCRIPT_METHOD.md

Implements 3-layer fallback strategy:
1. YouTube Transcript API (primary)
2. OpenAI Whisper API (secondary fallback) 
3. Browser Automation (final fallback)
"""

import os
import uuid
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis
import json

from urllib.parse import urlparse, parse_qs

# Import DOM scraping transcriber
from browser_transcriber import BrowserTranscriber

# Disable Celery for now to avoid import issues
CELERY_AVAILABLE = False
# Skip problematic celery_tasks import completely

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIBOA Transcription Service",
    description="YouTube transcription service for educational analysis",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for job management
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

class TranscriptionRequest(BaseModel):
    youtube_url: str
    language: str = "ko"
    export_format: str = "json"

class JobStatus(BaseModel):
    job_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from various YouTube URL formats"""
    parsed_url = urlparse(youtube_url)
    
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        elif parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    
    raise ValueError(f"Invalid YouTube URL: {youtube_url}")

async def get_transcript_with_browser_scraping(video_id: str, language: str = "ko", youtube_url: str = None) -> Dict[str, Any]:
    """
    DOM scraping transcription method - extracts transcript segments directly from YouTube page
    This is the only method used, no fallbacks needed
    """
    if not youtube_url:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    logger.info(f"Starting DOM scraping transcription for video: {video_id}")
    
    try:
        logger.info("Attempting Browser DOM scraping...")
        
        async with BrowserTranscriber() as browser_transcriber:
            result = await browser_transcriber.transcribe_youtube_video(youtube_url, language)
        
        if result["success"]:
            logger.info(f"SUCCESS: Browser DOM scraping transcribed {result['character_count']} characters")
            return result
        else:
            logger.error(f"FAILED: {result['error']}")
            return result
    
    except Exception as e:
        logger.error(f"Browser DOM scraping failed: {str(e)}")
        return {
            "success": False,
            "error": f"Browser DOM scraping failed: {str(e)}",
            "video_id": video_id
        }

async def process_transcription_job(job_id: str, youtube_url: str, language: str, export_format: str):
    """Background task for processing transcription using DOM scraping approach"""
    try:
        # Update job status to started
        job_data = {
            "job_id": job_id,
            "status": "started",
            "message": "DOM scraping in progress...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": 10
        }
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Update to processing
        job_data.update({
            "status": "progress",
            "message": "Extracting transcript from YouTube page...",
            "updated_at": datetime.now().isoformat(),
            "progress": 50
        })
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Extract video ID and process with DOM scraping
        video_id = extract_video_id(youtube_url)
        result = await get_transcript_with_browser_scraping(video_id, language, youtube_url)
        
        if result["success"]:
            # Success
            job_data.update({
                "status": "success",
                "message": f"Transcription completed using DOM scraping",
                "result": result,
                "updated_at": datetime.now().isoformat(),
                "progress": 100
            })
        else:
            # Failure
            error_msg = result.get("error", "DOM scraping failed")
            
            job_data.update({
                "status": "failed",
                "message": error_msg,
                "updated_at": datetime.now().isoformat(),
                "progress": 0,
                "error_details": result.get("error", "Unknown error")
            })
        
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
    except Exception as e:
        logger.error(f"Job {job_id} failed with exception: {str(e)}")
        job_data = {
            "job_id": job_id,
            "status": "failed",
            "message": f"Job failed with exception: {str(e)}",
            "updated_at": datetime.now().isoformat(),
            "progress": 0
        }
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "transcription", "timestamp": datetime.now().isoformat()}

# Add the new proven API endpoint structure
@app.post("/api/jobs/submit")
async def submit_transcription_job(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """
    Submit YouTube URL for transcription using DOM scraping method
    This endpoint uses browser automation to extract transcript segments directly from YouTube page
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initial job status (matches proven method)
        job_data = {
            "job_id": job_id,
            "status": "PENDING",
            "message": "Job submitted successfully",
            "submitted_at": datetime.now().isoformat(),
            "estimated_completion": str(time.time() + 120)  # Estimated 2 minutes
        }
        
        # Store in Redis
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Use Celery for proven async processing, fallback to FastAPI background tasks
        if CELERY_AVAILABLE:
            # Use Celery worker (proven method from TRANSCRIPT_METHOD.md)
            process_transcription_task.delay(
                job_id,
                request.youtube_url,
                request.language,
                request.export_format
            )
        else:
            # Fallback to FastAPI background tasks
            asyncio.create_task(
                process_transcription_job(
                    job_id,
                    request.youtube_url,
                    request.language,
                    request.export_format
                )
            )
        
        return job_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Keep the old endpoint for backward compatibility
@app.post("/api/transcribe/youtube")
async def transcribe_youtube(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """
    Submit YouTube URL for transcription (legacy endpoint for backward compatibility)
    Uses DOM scraping method to extract transcript segments
    """
    # Use the same logic as the main endpoint  
    return await submit_transcription_job(request, background_tasks)

# Add the proven API endpoint for job status
@app.get("/api/jobs/{job_id}/status")
async def get_job_status_proven(job_id: str):
    """Get transcription job status using proven endpoint structure"""
    try:
        job_data = redis_client.get(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return json.loads(job_data)
    
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Keep legacy endpoint for backward compatibility
@app.get("/api/transcribe/{job_id}")
async def get_job_status(job_id: str):
    """Get transcription job status (legacy endpoint)"""
    return await get_job_status_proven(job_id)

@app.get("/api/stats")
async def get_stats():
    """Get service statistics"""
    try:
        # Get all job keys
        job_keys = redis_client.keys("job:*")
        
        stats = {
            "total_jobs": len(job_keys),
            "service": "transcription",
            "timestamp": datetime.now().isoformat()
        }
        
        if job_keys:
            # Count by status
            status_counts = {}
            for key in job_keys:
                job_data = json.loads(redis_client.get(key))
                status = job_data.get("status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            stats["status_breakdown"] = status_counts
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"error": "Could not retrieve stats"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)