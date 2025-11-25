#!/usr/bin/env python3
"""
AIBOA Transcription Service
YouTube 전사 서비스 - Selenium 브라우저 자동화 방식만 사용

사용자 요구사항:
- 절대로 API 방식을 사용하지 않음
- 오직 Selenium 브라우저 자동화만 사용
- 사용자가 제공한 정확한 버튼 selector만 사용
"""

import os
import uuid
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis
import json

from urllib.parse import urlparse, parse_qs

# Import database utilities
from database import get_db, store_transcript, init_database, TranscriptDB
from sqlalchemy.orm import Session

# Import cache manager for transcript caching
from utils.cache_manager import TranscriptCacheManager

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Selenium scraper as fallback
try:
    from selenium_youtube_scraper import SeleniumYouTubeScraper
    SELENIUM_AVAILABLE = True
    logger.info("Selenium scraper loaded successfully")
except ImportError as e:
    SELENIUM_AVAILABLE = False
    logger.warning(f"Selenium scraper not available: {e}")

# Disable Celery for now to avoid import issues
CELERY_AVAILABLE = False
# Skip problematic celery_tasks import completely

app = FastAPI(
    title="AIBOA Transcription Service",
    description="YouTube transcription service for educational analysis",
    version="2.0.0"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and verify Redis connection on startup"""
    # Database initialization
    try:
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # Don't fail startup if database initialization fails

    # Redis connection verification
    try:
        logger.info("Testing Redis connection...")
        redis_client.ping()
        redis_host = os.getenv('REDIS_HOST', 'redis')
        redis_port = os.getenv('REDIS_PORT', '6379')
        logger.info(f"✓ Redis connected successfully at {redis_host}:{redis_port}")
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {type(e).__name__} - {str(e)}")
        logger.error("Transcription service will continue but job status tracking may fail")

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

# Initialize cache manager for transcript caching (added 2025-01-11)
cache_manager = TranscriptCacheManager(redis_client)

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
    Browser scraping with Selenium (proven method) - Playwright disabled
    Method 1: Selenium browser automation (PROVEN WORKING)
    Method 2: Playwright browser automation (DISABLED - has visibility issues)
    """
    if not youtube_url:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    # Use ONLY browser scraping (as specified by user - no API methods)
    logger.info(f"Starting browser automation for transcript extraction: {video_id}")

    # Method 1: Try Selenium browser automation (PROVEN WORKING)
    if SELENIUM_AVAILABLE:
        try:
            logger.info("Method 1: Attempting Selenium browser automation (PROVEN METHOD)...")

            # Create Selenium scraper instance
            scraper = SeleniumYouTubeScraper(headless=True)

            # Run Selenium in a thread since it's not async
            import asyncio
            loop = asyncio.get_event_loop()
            transcript_data = await loop.run_in_executor(
                None,
                lambda: scraper.scrape_youtube_transcript(youtube_url)
            )

            # Clean up driver
            try:
                if scraper.driver:
                    scraper.driver.quit()
            except:
                pass

            # Handle dict return value from SeleniumYouTubeScraper (with segments)
            if transcript_data:
                if isinstance(transcript_data, dict):
                    # New format with segments
                    transcript_text = transcript_data.get('full_text', '')
                    segments = transcript_data.get('segments', [])
                    logger.info(f"✅ SUCCESS: Selenium transcribed {len(segments)} segments, {len(transcript_text)} characters")
                    return {
                        "success": True,
                        "video_url": youtube_url,
                        "video_id": video_id,
                        "transcript": transcript_text,
                        "segments": segments,  # Include segments in response
                        "language": language,
                        "character_count": len(transcript_text),
                        "word_count": len(transcript_text.split()),
                        "segment_count": len(segments),
                        "method_used": "selenium_browser",
                        "timestamp": time.time()
                    }
                elif isinstance(transcript_data, str):
                    # Backward compatibility: old format (string only)
                    transcript_text = transcript_data
                    logger.info(f"✅ SUCCESS: Selenium transcribed {len(transcript_text)} characters")
                    return {
                        "success": True,
                        "video_url": youtube_url,
                        "video_id": video_id,
                        "transcript": transcript_text,
                        "segments": [],  # Empty segments for backward compatibility
                        "language": language,
                        "character_count": len(transcript_text),
                        "word_count": len(transcript_text.split()),
                        "segment_count": 0,
                        "method_used": "selenium_browser",
                        "timestamp": time.time()
                    }
            else:
                logger.error("Selenium returned empty transcript")

        except Exception as e:
            logger.error(f"Selenium failed with exception: {str(e)}")
    else:
        logger.error("Selenium not available - cannot proceed")

    # Method 2: Try Playwright as last resort (DISABLED due to visibility issues)
    # Keeping code for reference but not executing
    logger.warning("Playwright disabled due to button visibility issues")

    # All methods failed
    return {
        "success": False,
        "error": "Selenium browser automation failed. This video may have disabled transcripts or require manual captions.",
        "video_id": video_id,
        "methods_tried": ["selenium_browser"] if SELENIUM_AVAILABLE else []
    }

async def process_transcription_job(job_id: str, youtube_url: str, language: str, export_format: str):
    """Background task for processing transcription using DOM scraping approach"""
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
        # Extended TTL to 24 hours (86400 seconds)
        redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))
        
        # Update to processing
        job_data.update({
            "status": "progress",
            "message": "Extracting transcript from video...",
            "updated_at": datetime.now().isoformat(),
            "progress": 50
        })
        redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))
        
        # Extract video ID and process with DOM scraping
        # Add 5-minute timeout to prevent infinite loops
        TRANSCRIPTION_TIMEOUT = 300  # 5 minutes
        video_id = extract_video_id(youtube_url)

        try:
            result = await asyncio.wait_for(
                get_transcript_with_browser_scraping(video_id, language, youtube_url),
                timeout=TRANSCRIPTION_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error(f"Transcription timeout for job {job_id} after {TRANSCRIPTION_TIMEOUT} seconds")
            result = {
                "success": False,
                "error": f"Transcription timeout - operation took longer than {TRANSCRIPTION_TIMEOUT // 60} minutes. This video may not have available transcripts."
            }
        
        if result["success"]:
            # Store transcript in database for permanent storage
            try:
                from database import SessionLocal
                db = SessionLocal()
                
                # Prepare transcript data for database storage
                transcript_data = {
                    "transcript_id": job_id,
                    "source_type": "youtube",
                    "source_url": youtube_url,
                    "video_id": video_id,
                    "language": language,
                    "method_used": result.get("method_used", "browser_automation"),
                    "transcript_text": result.get("transcript", ""),
                    "segments": result.get("segments", []),
                    "anonymized": True,
                    "research_consent": False
                }
                
                # Store in database
                store_transcript(db, transcript_data)
                db.close()

                logger.info(f"Transcript {job_id} stored in database successfully")

                # Store in Redis cache for fast subsequent access (added 2025-01-11)
                try:
                    cache_key = cache_manager.generate_youtube_key(video_id, language)
                    cache_data = {
                        "transcript_id": job_id,
                        "transcript": result.get("transcript", ""),
                        "segments": result.get("segments", []),
                        "video_id": video_id,
                        "language": language,
                        "method_used": result.get("method_used", "browser_automation"),
                        "character_count": len(result.get("transcript", "")),
                        "word_count": len(result.get("transcript", "").split()),
                        "created_at": datetime.now().isoformat(),
                        "success": True
                    }

                    # Store in Redis with 7-day TTL
                    cache_manager.set(cache_key, cache_data)
                    logger.info(f"Transcript {job_id} cached in Redis: {cache_key}")

                except Exception as cache_error:
                    logger.error(f"Failed to cache transcript: {str(cache_error)}")
                    # Don't fail the job if caching fails

            except Exception as db_error:
                logger.error(f"Failed to store transcript in database: {str(db_error)}")
                # Continue even if database storage fails - Redis still has the data
            
            # Success - update Redis cache
            job_data.update({
                "status": "success",
                "message": f"Transcription completed using {result.get('method_used', 'browser_automation')}",
                "result": result,
                "updated_at": datetime.now().isoformat(),
                "progress": 100
            })
        else:
            # Failure
            error_msg = result.get("error", "Transcription failed")
            
            job_data.update({
                "status": "failed",
                "message": error_msg,
                "updated_at": datetime.now().isoformat(),
                "progress": 0,
                "error_details": result.get("error", "Unknown error")
            })
        
        # Store updated job status with 24-hour TTL
        redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))
        
    except Exception as e:
        logger.error(f"Job {job_id} failed with exception: {str(e)}")
        job_data = {
            "job_id": job_id,
            "status": "failed",
            "message": f"Job failed with exception: {str(e)}",
            "updated_at": datetime.now().isoformat(),
            "progress": 0
        }
        redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))

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

    WITH CACHING (added 2025-01-11):
    - Checks Redis cache first for instant response
    - Falls back to PostgreSQL database if Redis misses
    - Only creates new transcription job if both caches miss
    """
    try:
        # Extract video ID for cache lookup
        video_id = extract_video_id(request.youtube_url)

        # Check cache before starting transcription job
        cache_key = cache_manager.generate_youtube_key(video_id, request.language)

        # Tier 1: Check Redis hot cache
        cached_transcript = cache_manager.get(cache_key)
        if cached_transcript:
            logger.info(f"Cache HIT (Redis) for video {video_id}")

            # Generate new job_id for status polling (even for cached results)
            job_id = str(uuid.uuid4())

            # Store job status in Redis for status polling
            job_data = {
                "job_id": job_id,
                "status": "completed",
                "message": "Retrieved from cache (instant response)",
                "result": cached_transcript,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "cache_hit": True,
                "cache_source": "redis"
            }
            redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))  # 24h TTL

            return {
                "job_id": job_id,
                "status": "completed",
                "message": "Retrieved from cache (instant response)",
                "result": cached_transcript,
                "cache_hit": True,
                "cache_source": "redis",
                "submitted_at": datetime.now().isoformat()
            }

        # Tier 2: Check PostgreSQL database
        from database import SessionLocal
        db = SessionLocal()
        try:
            db_record = db.query(TranscriptDB).filter(
                TranscriptDB.video_id == video_id,
                TranscriptDB.language == request.language
            ).first()

            if db_record:
                logger.info(f"Cache HIT (PostgreSQL) for video {video_id}")

                # Prepare result data
                cached_result = {
                    "transcript_id": db_record.transcript_id,
                    "transcript": db_record.transcript_text,
                    "segments": db_record.segments_json,
                    "video_id": db_record.video_id,
                    "language": db_record.language,
                    "method_used": db_record.method_used,
                    "character_count": db_record.character_count,
                    "word_count": db_record.word_count,
                    "created_at": db_record.created_at.isoformat() if db_record.created_at else None,
                    "success": True
                }

                # Populate Redis cache for next time
                cache_manager.set(cache_key, cached_result)

                # Generate new job_id for status polling (even for DB cached results)
                job_id = str(uuid.uuid4())

                # Store job status in Redis for status polling
                job_data = {
                    "job_id": job_id,
                    "status": "completed",
                    "message": "Retrieved from database cache",
                    "result": cached_result,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "cache_hit": True,
                    "cache_source": "database"
                }
                redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))  # 24h TTL

                return {
                    "job_id": job_id,
                    "status": "completed",
                    "message": "Retrieved from database cache",
                    "result": cached_result,
                    "cache_hit": True,
                    "cache_source": "database",
                    "submitted_at": datetime.now().isoformat()
                }
        finally:
            db.close()

        # Tier 3: Cache miss - proceed with new transcription
        logger.info(f"Cache MISS for video {video_id} - starting transcription")

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Initial job status (matches proven method)
        job_data = {
            "job_id": job_id,
            "status": "PENDING",
            "message": "Job submitted successfully",
            "submitted_at": datetime.now().isoformat(),
            "estimated_completion": str(time.time() + 120),  # Estimated 2 minutes
            "cache_hit": False
        }

        # Store in Redis
        redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))

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

    except HTTPException:
        # Re-raise HTTP exceptions as-is (404 Not Found)
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for job {job_id}: {str(e)}")
        logger.error(f"Raw data: {job_data[:200] if job_data else 'None'}")
        raise HTTPException(status_code=500, detail="Invalid job data format")
    except redis.RedisError as e:
        logger.error(f"Redis connection error: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=503, detail="Cache service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error getting job status for {job_id}: {type(e).__name__} - {str(e)}")
        logger.exception(e)  # Log full traceback
        raise HTTPException(status_code=500, detail="Internal server error")

# Keep legacy endpoint for backward compatibility
@app.get("/api/transcribe/{job_id}")
async def get_job_status(job_id: str):
    """Get transcription job status (legacy endpoint)"""
    return await get_job_status_proven(job_id)

@app.get("/api/transcripts/{transcript_id}")
async def get_transcript_by_id(transcript_id: str, db: Session = Depends(get_db)):
    """Get transcript data from database by transcript ID (for analysis service)"""
    try:
        # First try to get from database
        transcript_record = db.query(TranscriptDB).filter(
            TranscriptDB.transcript_id == transcript_id
        ).first()
        
        if transcript_record:
            return {
                "success": True,
                "transcript_id": transcript_record.transcript_id,
                "source_url": transcript_record.source_url,
                "video_id": transcript_record.video_id,
                "transcript_text": transcript_record.transcript_text,
                "language": transcript_record.language,
                "method_used": transcript_record.method_used,
                "character_count": transcript_record.character_count,
                "word_count": transcript_record.word_count,
                "segments": transcript_record.segments_json,
                "created_at": transcript_record.created_at.isoformat() if transcript_record.created_at else None,
                "teacher_name": transcript_record.teacher_name,
                "subject": transcript_record.subject,
                "grade_level": transcript_record.grade_level
            }
        
        # Fallback to Redis if not in database
        job_data = redis_client.get(f"job:{transcript_id}")
        if job_data:
            job_info = json.loads(job_data)
            if job_info.get("status") == "success" and "result" in job_info:
                result = job_info["result"]
                return {
                    "success": True,
                    "transcript_id": transcript_id,
                    "source_url": result.get("video_url"),
                    "video_id": result.get("video_id"),
                    "transcript_text": result.get("transcript", ""),
                    "language": result.get("language", "ko"),
                    "method_used": result.get("method_used", "unknown"),
                    "character_count": result.get("character_count", 0),
                    "word_count": result.get("word_count", 0),
                    "segments": result.get("segments", []),
                    "created_at": job_info.get("created_at")
                }
        
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcript {transcript_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get service statistics"""
    try:
        # Get Redis job stats
        job_keys = redis_client.keys("job:*")

        stats = {
            "total_jobs": len(job_keys),
            "service": "transcription",
            "method": "selenium_browser_automation",
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

        # Add database stats
        try:
            total_transcripts_in_db = db.query(TranscriptDB).count()
            stats["transcripts_in_database"] = total_transcripts_in_db
        except Exception as db_error:
            logger.error(f"Database stats error: {str(db_error)}")
            stats["transcripts_in_database"] = "unavailable"

        return stats

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"error": "Could not retrieve stats"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)