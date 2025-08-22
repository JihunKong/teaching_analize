"""
YouTube Transcript Handler using youtube-transcript-api
This module handles YouTube transcript extraction without requiring OAuth
"""
import os
import re
import logging
from typing import Optional, List, Dict
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or None if not found
    """
    # Parse URL
    parsed = urlparse(url)
    
    # Handle youtu.be format
    if parsed.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed.path[1:]
    
    # Handle youtube.com format
    if parsed.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed.path == '/watch':
            query = parse_qs(parsed.query)
            return query.get('v', [None])[0]
        elif parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
        elif parsed.path.startswith('/v/'):
            return parsed.path.split('/')[2]
    
    # Fallback to regex
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def get_youtube_transcript(url: str, language: str = "ko") -> Optional[Dict]:
    """
    Get YouTube transcript using youtube-transcript-api
    
    Args:
        url: YouTube video URL
        language: Preferred language code
        
    Returns:
        Dictionary with transcript text and metadata, or None if failed
    """
    try:
        # Try importing youtube-transcript-api
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            TranscriptsDisabled,
            NoTranscriptFound,
            VideoUnavailable
        )
    except ImportError:
        logger.warning("youtube-transcript-api not installed, falling back to yt-dlp")
        return None
    
    video_id = extract_video_id(url)
    if not video_id:
        logger.error(f"Could not extract video ID from URL: {url}")
        return None
    
    try:
        # Try to get transcript in requested language
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to find manual transcript in requested language
        try:
            transcript = transcript_list.find_transcript([language])
            logger.info(f"Found manual transcript in {language}")
        except NoTranscriptFound:
            # Try to find generated transcript in requested language
            try:
                transcript = transcript_list.find_generated_transcript([language])
                logger.info(f"Found auto-generated transcript in {language}")
            except NoTranscriptFound:
                # Fallback to any available transcript
                try:
                    # Try English as fallback
                    transcript = transcript_list.find_transcript(['en'])
                    logger.info(f"Using English transcript as fallback")
                except NoTranscriptFound:
                    # Get first available transcript
                    transcripts = list(transcript_list)
                    if transcripts:
                        transcript = transcripts[0]
                        logger.info(f"Using first available transcript: {transcript.language}")
                    else:
                        logger.error("No transcripts available")
                        return None
        
        # Fetch the actual transcript
        transcript_data = transcript.fetch()
        
        # Combine all text
        full_text = " ".join([entry['text'] for entry in transcript_data])
        
        # Create segments with timestamps
        segments = []
        for entry in transcript_data:
            segments.append({
                "start": entry['start'],
                "duration": entry['duration'],
                "text": entry['text']
            })
        
        return {
            "text": full_text,
            "segments": segments,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "is_translatable": transcript.is_translatable,
            "video_id": video_id
        }
        
    except TranscriptsDisabled:
        logger.error(f"Transcripts are disabled for video {video_id}")
        return None
    except VideoUnavailable:
        logger.error(f"Video {video_id} is unavailable")
        return None
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        return None


def get_youtube_transcript_with_fallback(url: str, language: str = "ko") -> Optional[Dict]:
    """
    Get YouTube transcript with multiple fallback options
    
    Args:
        url: YouTube video URL
        language: Preferred language code
        
    Returns:
        Dictionary with transcript text and metadata, or None if all methods fail
    """
    # Method 1: Try youtube-transcript-api (fastest)
    logger.info("시도 1: youtube-transcript-api 사용")
    result = get_youtube_transcript(url, language)
    if result:
        logger.info("✅ youtube-transcript-api 성공")
        return result
    
    # Method 2: Try HTML scraping (more reliable for blocked videos)
    logger.info("시도 2: HTML 스크래핑 사용")
    try:
        from youtube_html_scraper import get_youtube_transcript_html_scraping
        result = get_youtube_transcript_html_scraping(url, language)
        if result:
            logger.info("✅ HTML 스크래핑 성공")
            return result
    except ImportError:
        logger.warning("HTML 스크래퍼 모듈을 찾을 수 없습니다")
    except Exception as e:
        logger.error(f"HTML 스크래핑 실패: {e}")
    
    # All methods failed
    logger.warning("모든 전사 추출 방법 실패")
    return None