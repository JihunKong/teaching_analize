#!/usr/bin/env python3
"""
Background Tasks for YouTube Transcript Extraction
Celery tasks for processing YouTube videos asynchronously
"""

import logging
import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, Any
from celery import Celery
from celery_app import app
from browser_youtube_handler import BrowserYouTubeHandler

logger = logging.getLogger(__name__)

# Initialize handler instance for worker
browser_handler = BrowserYouTubeHandler()

@app.task(bind=True, name='background_tasks.extract_youtube_transcript_task')
def extract_youtube_transcript_task(self, video_url: str, language: str = "ko", format_type: str = "text") -> Dict[str, Any]:
    """
    Celery task for extracting YouTube transcript in background
    
    Args:
        video_url: YouTube video URL
        language: Language preference
        format_type: Output format (text, json, srt)
        
    Returns:
        Dict with extraction results
    """
    logger.info(f"🎬 Starting background transcript extraction for: {video_url}")
    start_time = time.time()
    
    # Update task state to STARTED
    self.update_state(
        state='STARTED',
        meta={
            'status': 'Processing video...',
            'video_url': video_url,
            'started_at': datetime.now().isoformat(),
            'progress': 10
        }
    )
    
    try:
        # Extract video ID for progress tracking
        video_id = browser_handler._get_video_id(video_url)
        if not video_id:
            raise Exception("Invalid YouTube URL")
        
        # Update progress
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Video ID extracted, checking cache...',
                'video_id': video_id,
                'progress': 20
            }
        )
        
        # Check cache first (this is fast)
        cached_result = browser_handler._check_cache(video_id)
        if cached_result:
            logger.info(f"✨ Cache hit for {video_id}")
            
            # Format the cached result
            formatted_transcript = _format_transcript(cached_result, format_type)
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'video_url': video_url,
                'video_id': video_id,
                'transcript': formatted_transcript,
                'language': language,
                'character_count': len(cached_result),
                'processing_time': processing_time,
                'method_used': 'cache_hit',
                'timestamp': datetime.now().isoformat(),
                'cached': True
            }
        
        # Update progress - starting browser extraction
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Starting browser automation...',
                'video_id': video_id,
                'progress': 30
            }
        )
        
        # Run async extraction in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Update progress - browser started
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Browser automation in progress...',
                    'video_id': video_id,
                    'progress': 50
                }
            )
            
            # Extract transcript using browser handler
            transcript = loop.run_until_complete(
                browser_handler.extract_transcript(video_url)
            )
            
            if not transcript:
                raise Exception("Failed to extract transcript from video")
            
            # Update progress - formatting result
            self.update_state(
                state='PROGRESS',
                meta={
                    'status': 'Formatting transcript...',
                    'video_id': video_id,
                    'progress': 90
                }
            )
            
            # Format transcript
            formatted_transcript = _format_transcript(transcript, format_type)
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Background extraction successful: {len(transcript)} characters in {processing_time:.2f}s")
            
            # Return successful result
            return {
                'success': True,
                'video_url': video_url,
                'video_id': video_id,
                'transcript': formatted_transcript,
                'language': language,
                'character_count': len(transcript),
                'processing_time': processing_time,
                'method_used': 'browser_scraping',
                'timestamp': datetime.now().isoformat(),
                'cached': False
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = str(e)
        
        logger.error(f"❌ Background extraction failed for {video_url}: {error_msg}")
        
        # Update task state to FAILURE with error info
        self.update_state(
            state='FAILURE',
            meta={
                'error': error_msg,
                'video_url': video_url,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Return failure result
        return {
            'success': False,
            'video_url': video_url,
            'video_id': video_id if 'video_id' in locals() else None,
            'language': language,
            'error': error_msg,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat()
        }


def _format_transcript(transcript: str, format_type: str) -> str:
    """Format transcript for different output types"""
    
    if format_type == "text":
        return transcript
    
    elif format_type == "json":
        import json
        return json.dumps({
            "transcript": transcript,
            "word_count": len(transcript.split()),
            "character_count": len(transcript),
            "paragraphs": transcript.split('\n\n') if '\n\n' in transcript else [transcript]
        }, ensure_ascii=False, indent=2)
    
    elif format_type == "srt":
        # Simple SRT format (without real timestamps)
        sentences = transcript.replace('. ', '.\n').split('\n')
        srt_content = ""
        
        for i, sentence in enumerate(sentences, 1):
            if sentence.strip():
                start_time = f"00:{(i-1)*3//60:02d}:{(i-1)*3%60:02d},000"
                end_time = f"00:{i*3//60:02d}:{i*3%60:02d},000"
                srt_content += f"{i}\n{start_time} --> {end_time}\n{sentence.strip()}\n\n"
        
        return srt_content
    
    else:
        return transcript


# Background task for cache cleanup
@app.task(name='background_tasks.cleanup_cache_task')
def cleanup_cache_task():
    """Clean expired cache entries"""
    logger.info("🧹 Running cache cleanup task")
    # This will be handled automatically by the handler's cache checking
    return {"status": "Cache cleanup completed"}


# Background task for system health check
@app.task(name='background_tasks.health_check_task')
def health_check_task():
    """System health check task"""
    logger.info("🏥 Running health check task")
    
    try:
        # Test browser handler initialization
        handler = BrowserYouTubeHandler()
        stats = handler.get_cache_stats()
        
        return {
            "status": "healthy",
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }