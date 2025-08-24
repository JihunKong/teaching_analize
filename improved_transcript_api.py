#!/usr/bin/env python3
"""
Improved YouTube transcript extractor with direct API approach
This combines the youtube-transcript-api library with Innertube API fallback
"""

import asyncio
import logging
import time
import json
import re
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

logger = logging.getLogger(__name__)

class ImprovedTranscriptExtractor:
    """
    Improved YouTube transcript extractor using direct API approaches
    Priority: Direct API > Innertube API > Browser automation fallback
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def extract_video_id(self, youtube_url: str) -> str:
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

    def try_direct_api_method(self, video_id: str, language: str = "ko") -> Optional[List[Dict[str, Any]]]:
        """
        Try to extract transcript using youtube-transcript-api library
        This is the most reliable method as of 2025
        """
        if not YOUTUBE_API_AVAILABLE:
            logger.warning("youtube-transcript-api not available")
            return None
        
        try:
            logger.info(f"Attempting direct API extraction for video ID: {video_id}")
            
            # Create API instance
            api = YouTubeTranscriptApi()
            
            # Handle both old and new API versions
            transcript = None
            is_new_api = hasattr(api, 'fetch')
            
            try:
                if is_new_api:
                    # New API (v0.7+)
                    transcript = api.fetch(video_id, languages=[language])
                    logger.info(f"Successfully retrieved transcript in {language} (new API)")
                else:
                    # Old API (v0.6.x)
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
                    logger.info(f"Successfully retrieved transcript in {language} (old API)")
            except:
                try:
                    if is_new_api:
                        transcript = api.fetch(video_id)
                        logger.info("Successfully retrieved transcript in fallback language (new API)")
                    else:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        logger.info("Successfully retrieved transcript in fallback language (old API)")
                except:
                    # Try auto-generated transcripts with common languages
                    for lang in ['en', 'ko', 'ja', 'zh', 'es', 'fr']:
                        try:
                            if is_new_api:
                                transcript = api.fetch(video_id, languages=[lang])
                            else:
                                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                            logger.info(f"Successfully retrieved transcript in {lang}")
                            break
                        except:
                            continue
                    else:
                        # Last resort - try without language specification
                        if is_new_api:
                            transcript = api.fetch(video_id)
                        else:
                            transcript = YouTubeTranscriptApi.get_transcript(video_id)
                        logger.info("Successfully retrieved transcript without language specification")
            
            # Convert to our standard format (handle both API versions)
            formatted_transcript = []
            if is_new_api and transcript:
                # New API returns FetchedTranscript with snippets
                for snippet in transcript.snippets:
                    formatted_transcript.append({
                        'text': snippet.text,
                        'start': snippet.start,
                        'duration': snippet.duration
                    })
            elif transcript:
                # Old API returns list directly
                for entry in transcript:
                    formatted_transcript.append({
                        'text': entry['text'],
                        'start': entry['start'],
                        'duration': entry['duration']
                    })
            
            logger.info(f"Direct API method extracted {len(formatted_transcript)} segments")
            return formatted_transcript
            
        except Exception as e:
            logger.error(f"Direct API method failed: {str(e)}")
            return None

    def try_innertube_api_method(self, video_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Try to extract transcript using Innertube API with Android client
        This is the backup method when direct API fails
        """
        try:
            logger.info(f"Attempting Innertube API extraction for video ID: {video_id}")
            
            # Step 1: Get the API key from YouTube page
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(video_url)
            response.raise_for_status()
            
            # Extract API key
            api_key_match = re.search(r'"INNERTUBE_API_KEY":\s*"([a-zA-Z0-9_-]+)"', response.text)
            if not api_key_match:
                logger.error("Could not extract Innertube API key")
                return None
            
            api_key = api_key_match.group(1)
            logger.info("Successfully extracted Innertube API key")
            
            # Step 2: Get player response using Android client
            endpoint = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
            payload = {
                "context": {
                    "client": {
                        "clientName": "ANDROID",
                        "clientVersion": "19.09.37",
                        "androidSdkVersion": 30,
                        "platform": "MOBILE",
                        "osName": "Android",
                        "osVersion": "14"
                    }
                },
                "videoId": video_id,
                "playbackContext": {
                    "contentPlaybackContext": {
                        "html5Preference": "HTML5_PREF_WANTS"
                    }
                }
            }
            
            response = self.session.post(
                endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            player_data = response.json()
            
            # Step 3: Extract caption tracks
            captions = player_data.get('captions', {})
            caption_tracks = captions.get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
            
            if not caption_tracks:
                logger.error("No caption tracks found in player response")
                return None
            
            # Find the best caption track (prefer Korean, then English, then auto-generated)
            selected_track = None
            for track in caption_tracks:
                lang_code = track.get('languageCode', '')
                if lang_code == 'ko':
                    selected_track = track
                    break
                elif lang_code == 'en' and not selected_track:
                    selected_track = track
                elif not selected_track:
                    selected_track = track
            
            if not selected_track:
                logger.error("No suitable caption track found")
                return None
            
            # Step 4: Fetch and parse transcript XML
            base_url = selected_track['baseUrl']
            # Remove format parameter to get clean XML
            base_url = re.sub(r'&fmt=\w+', '', base_url)
            
            transcript_response = self.session.get(base_url)
            transcript_response.raise_for_status()
            
            # Parse XML transcript
            transcript_xml = transcript_response.text
            transcript_data = self._parse_transcript_xml(transcript_xml)
            
            if transcript_data:
                logger.info(f"Innertube API method extracted {len(transcript_data)} segments")
                return transcript_data
            else:
                logger.error("Failed to parse transcript XML")
                return None
                
        except Exception as e:
            logger.error(f"Innertube API method failed: {str(e)}")
            return None

    def _parse_transcript_xml(self, xml_content: str) -> Optional[List[Dict[str, Any]]]:
        """Parse XML transcript content"""
        try:
            # Simple XML parsing using regex (avoiding xml2js dependency)
            text_pattern = r'<text start="([^"]+)" dur="([^"]+)"[^>]*>([^<]*)</text>'
            matches = re.findall(text_pattern, xml_content)
            
            transcript_data = []
            for start_time, duration, text in matches:
                # Clean up text (decode HTML entities)
                cleaned_text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
                
                transcript_data.append({
                    'text': cleaned_text.strip(),
                    'start': float(start_time),
                    'duration': float(duration)
                })
            
            return transcript_data if transcript_data else None
            
        except Exception as e:
            logger.error(f"Error parsing transcript XML: {e}")
            return None

    async def extract_transcript(self, youtube_url: str, language: str = "ko") -> Dict[str, Any]:
        """
        Main method to extract transcript with multiple fallback methods
        Priority: Direct API > Innertube API > Browser automation
        """
        start_time = time.time()
        
        try:
            video_id = self.extract_video_id(youtube_url)
            logger.info(f"Starting improved transcript extraction for video: {video_id}")
            
            # Method 1: Try direct API approach (most reliable)
            transcript_data = self.try_direct_api_method(video_id, language)
            method_used = "direct_api"
            
            # Method 2: Fallback to Innertube API
            if not transcript_data:
                logger.info("Direct API failed, trying Innertube API method")
                transcript_data = self.try_innertube_api_method(video_id)
                method_used = "innertube_api"
            
            # Method 3: Browser automation fallback would go here
            # (keeping the existing browser_transcriber as final fallback)
            
            if not transcript_data:
                return {
                    "success": False,
                    "error": "All transcript extraction methods failed",
                    "video_id": video_id,
                    "methods_tried": ["direct_api", "innertube_api"]
                }
            
            # Format result
            full_text = " ".join([entry['text'] for entry in transcript_data])
            processing_time = time.time() - start_time
            
            result = {
                "success": True,
                "video_url": youtube_url,
                "video_id": video_id,
                "transcript": full_text,
                "language": language,
                "character_count": len(full_text),
                "word_count": len(full_text.split()),
                "method_used": method_used,
                "timestamp": time.time(),
                "processing_time": processing_time,
                "segments": transcript_data,
                "segment_count": len(transcript_data)
            }
            
            logger.info(f"Successfully extracted transcript using {method_used} method in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Improved transcript extraction failed after {processing_time:.2f}s: {str(e)}")
            return {
                "success": False,
                "error": f"Improved transcript extraction failed: {str(e)}",
                "video_id": self.extract_video_id(youtube_url) if youtube_url else "unknown",
                "processing_time": processing_time
            }

# Convenience function for direct usage
async def extract_transcript_improved(youtube_url: str, language: str = "ko") -> Dict[str, Any]:
    """
    Convenience function to extract YouTube transcript using improved methods
    """
    extractor = ImprovedTranscriptExtractor()
    return await extractor.extract_transcript(youtube_url, language)

if __name__ == "__main__":
    # Test the improved extractor
    import asyncio
    
    async def test():
        test_url = "https://www.youtube.com/watch?v=F2cKZRUYHh0"
        result = await extract_transcript_improved(test_url, "ko")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test())