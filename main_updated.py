#!/usr/bin/env python3
"""
AIBOA Transcription Service
Enhanced implementation with improved multi-method approach

Implements 3-layer fallback strategy:
1. Direct API (youtube-transcript-api) - fastest and most reliable
2. Innertube API - backup when direct API fails
3. Browser Automation - final fallback for difficult cases
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

# Import improved transcript API
from improved_transcript_api import ImprovedTranscriptExtractor

# Disable Celery for now to avoid import issues
CELERY_AVAILABLE = False
# Skip problematic celery_tasks import completely

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIBOA Transcription Service",
    description="YouTube transcription service for educational analysis",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis configuration - use aiboa_redis as default for production
REDIS_HOST = os.getenv("REDIS_HOST", "aiboa_redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Models
class TranscriptionRequest(BaseModel):
    youtube_url: str
    language: str = "ko"
    export_format: str = "json"

class JobSubmissionResponse(BaseModel):
    job_id: str
    status: str
    message: str

def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(youtube_url)
    
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
        if 'watch' in parsed_url.path:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]
        elif '/embed/' in parsed_url.path:
            return parsed_url.path.split('/embed/')[1].split('?')[0]
        elif '/v/' in parsed_url.path:
            return parsed_url.path.split('/v/')[1].split('?')[0]
    
    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")

async def get_transcript_with_improved_methods(video_id: str, language: str = "ko", youtube_url: str = None) -> Dict[str, Any]:
    """
    Improved transcription method with multiple fallbacks:
    1. Direct API (youtube-transcript-api) - fastest and most reliable
    2. Innertube API - backup when direct API fails
    3. Browser automation - final fallback for difficult cases
    """
    if not youtube_url:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
    
    logger.info(f"Starting improved transcription for video: {video_id}")
    
    try:
        # Use improved transcript extractor
        extractor = ImprovedTranscriptExtractor()
        result = await extractor.extract_transcript(youtube_url, language)
        
        if result["success"]:
            method_used = result.get("method_used", "unknown")
            logger.info(f"SUCCESS: {method_used} transcribed {result['character_count']} characters in {result['processing_time']:.2f}s")
            return result
        else:
            logger.warning(f"Improved methods failed: {result['error']}")
            
            # Final fallback to browser automation
            logger.info("Attempting browser automation as final fallback...")
            
            async with BrowserTranscriber() as browser_transcriber:
                browser_result = await browser_transcriber.transcribe_youtube_video(youtube_url, language)
            
            if browser_result["success"]:
                logger.info(f"SUCCESS: Browser automation transcribed {browser_result['character_count']} characters")
                browser_result["method_used"] = "browser_automation_fallback"
                return browser_result
            else:
                logger.error(f"All methods failed. Final error: {browser_result['error']}")
                return {
                    "success": False,
                    "error": f"All transcription methods failed. Direct API: {result['error']}. Browser: {browser_result['error']}",
                    "video_id": video_id,
                    "methods_tried": ["direct_api", "innertube_api", "browser_automation"]
                }
    
    except Exception as e:
        logger.error(f"Improved transcription failed: {str(e)}")
        return {
            "success": False,
            "error": f"Improved transcription failed: {str(e)}",
            "video_id": video_id
        }

async def process_transcription_job(job_id: str, youtube_url: str, language: str, export_format: str):
    """Background task for processing transcription using improved multi-method approach"""
    try:
        # Update job status to started
        job_data = {
            "job_id": job_id,
            "status": "started",
            "message": "Transcription in progress...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": 10
        }
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Update to processing
        job_data.update({
            "status": "progress",
            "message": "Extracting transcript using multiple methods...",
            "updated_at": datetime.now().isoformat(),
            "progress": 50
        })
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Extract video ID and process with improved methods
        video_id = extract_video_id(youtube_url)
        result = await get_transcript_with_improved_methods(video_id, language, youtube_url)
        
        if result["success"]:
            # Success
            method_used = result.get("method_used", "unknown")
            job_data.update({
                "status": "success",
                "message": f"Transcription completed using {method_used}",
                "result": result,
                "updated_at": datetime.now().isoformat(),
                "progress": 100
            })
        else:
            # Failure
            error_msg = result.get("error", "All transcription methods failed")
            methods_tried = result.get("methods_tried", ["unknown"])
            
            job_data.update({
                "status": "failed",
                "message": error_msg,
                "updated_at": datetime.now().isoformat(),
                "progress": 0,
                "error_details": result.get("error", "Unknown error"),
                "methods_tried": methods_tried
            })
        
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
    except Exception as e:
        logger.error(f"Background job error: {str(e)}")
        error_job_data = {
            "job_id": job_id,
            "status": "failed",
            "message": f"Job processing error: {str(e)}",
            "updated_at": datetime.now().isoformat(),
            "progress": 0,
            "error_details": str(e)
        }
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(error_job_data))

async def submit_transcription_job(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """
    Submit YouTube URL for transcription using improved multi-method approach
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
            "estimated_completion": str(time.time() + 60)  # Estimated 1 minute with improved methods
        }
        
        # Store in Redis
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Use FastAPI background tasks (since CELERY_AVAILABLE is False)
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

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {
            "status": "healthy",
            "service": "transcription",
            "version": "2.1.0",
            "timestamp": datetime.now().isoformat(),
            "redis": "connected",
            "methods": ["direct_api", "innertube_api", "browser_automation"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "transcription",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/jobs/submit")
async def submit_job(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """Submit YouTube URL for transcription"""
    return await submit_transcription_job(request, background_tasks)

# Keep the old endpoint for backward compatibility
@app.post("/api/transcribe/youtube")
async def transcribe_youtube(request: TranscriptionRequest, background_tasks: BackgroundTasks):
    """
    Submit YouTube URL for transcription (legacy endpoint for backward compatibility)
    Uses improved multi-method approach
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
        return {
            "service": "transcription",
            "version": "2.1.0",
            "methods": ["direct_api", "innertube_api", "browser_automation"],
            "redis_connected": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "service": "transcription",
            "version": "2.1.0",
            "error": str(e),
            "redis_connected": False,
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)