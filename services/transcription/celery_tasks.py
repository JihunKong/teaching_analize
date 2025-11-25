#!/usr/bin/env python3
"""
Celery tasks for AIBOA Transcription Service
Implements the proven async processing method from TRANSCRIPT_METHOD.md
"""

import os
import json
import logging
import time
import asyncio
from datetime import datetime
from typing import Dict, Any

import redis
from celery import current_task

from celery_app import celery_app
from main import get_transcript_with_browser_scraping, extract_video_id

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='transcription_service.process_video')
def process_transcription_task(self, job_id: str, youtube_url: str, language: str = "ko", export_format: str = "json"):
    """
    Celery task for processing YouTube video transcription
    This matches the proven async processing method from TRANSCRIPT_METHOD.md
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting Celery task for job {job_id}: {youtube_url}")
        
        # Update job status to STARTED (matches proven method status progression)
        job_data = {
            "job_id": job_id,
            "status": "STARTED",
            "message": "Browser automation in progress...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "progress": 10
        }
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Update progress to PROGRESS (matches proven method)
        self.update_state(
            state='PROGRESS',
            meta={'progress': 25, 'message': 'Extracting video information...'}
        )
        
        job_data.update({
            "status": "PROGRESS",
            "message": "Extracting video information...",
            "updated_at": datetime.now().isoformat(),
            "progress": 25
        })
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Extract video ID
        video_id = extract_video_id(youtube_url)
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={'progress': 50, 'message': 'Running transcription methods...'}
        )
        
        job_data.update({
            "status": "PROGRESS",
            "message": "Running transcription methods...",
            "updated_at": datetime.now().isoformat(),
            "progress": 50
        })
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Run the DOM scraping transcription (async function needs event loop)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                get_transcript_with_browser_scraping(video_id, language, youtube_url)
            )
        finally:
            loop.close()
        
        processing_time = time.time() - start_time
        
        if result["success"]:
            # Update progress to completion
            self.update_state(
                state='PROGRESS',
                meta={'progress': 100, 'message': f'Completed using {result["method_used"]}'}
            )
            
            # Final SUCCESS status (matches proven method)
            job_data.update({
                "status": "SUCCESS",
                "message": f"Transcription completed using {result['method_used']}",
                "result": {
                    **result,
                    "processing_time": processing_time,
                    "cached": False  # Matches proven method result structure
                },
                "updated_at": datetime.now().isoformat(),
                "progress": 100
            })
            
            logger.info(f"Job {job_id} completed successfully in {processing_time:.2f}s using {result['method_used']}")
            
        else:
            # All methods failed
            error_msg = result.get("error", "Unknown error")
            if "detailed_errors" in result:
                error_msg += f" - Methods tried: {list(result['detailed_errors'].keys())}"
            
            job_data.update({
                "status": "FAILURE",
                "message": error_msg,
                "error_details": result.get("detailed_errors", {}),
                "updated_at": datetime.now().isoformat(),
                "progress": 0,
                "processing_time": processing_time
            })
            
            logger.error(f"Job {job_id} failed after {processing_time:.2f}s: {error_msg}")
        
        # Store final result in Redis
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        return job_data
    
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Celery task exception: {str(e)}"
        
        logger.error(f"Job {job_id} failed with exception after {processing_time:.2f}s: {error_msg}")
        
        # Update job status to FAILURE
        job_data = {
            "job_id": job_id,
            "status": "FAILURE",
            "message": error_msg,
            "updated_at": datetime.now().isoformat(),
            "progress": 0,
            "processing_time": processing_time
        }
        
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
        
        # Re-raise exception for Celery
        raise self.retry(exc=e, countdown=60, max_retries=2)

@celery_app.task(name='transcription_service.cleanup_old_jobs')
def cleanup_old_jobs():
    """Clean up old completed jobs from Redis"""
    try:
        # Get all job keys
        job_keys = redis_client.keys("job:*")
        cleaned = 0
        
        for key in job_keys:
            try:
                job_data = json.loads(redis_client.get(key))
                
                # Clean up jobs older than 24 hours
                created_at = datetime.fromisoformat(job_data.get('created_at', datetime.now().isoformat()))
                age_hours = (datetime.now() - created_at).total_seconds() / 3600
                
                if age_hours > 24:
                    redis_client.delete(key)
                    cleaned += 1
            
            except Exception as e:
                logger.warning(f"Error cleaning up job {key}: {e}")
                # Delete corrupted job data
                redis_client.delete(key)
                cleaned += 1
        
        logger.info(f"Cleaned up {cleaned} old jobs")
        return {"cleaned_jobs": cleaned}
    
    except Exception as e:
        logger.error(f"Error during job cleanup: {e}")
        return {"error": str(e)}

@celery_app.task(name='transcription_service.health_check')
def health_check_task():
    """Health check task for monitoring"""
    try:
        # Test Redis connection
        redis_client.ping()
        
        # Test task processing
        test_time = time.time()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "test_time": test_time,
            "redis_connected": True
        }
    
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }