#!/usr/bin/env python3
"""
YouTube Transcript API with Proxy Support
"""

import requests
import re
import json
import logging
from typing import Optional, Dict, List, Any
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class YouTubeTranscriptAPIWithProxy:
    """YouTube Transcript API that supports proxy"""
    
    def __init__(self, proxy_dict: Optional[Dict[str, str]] = None):
        self.proxy_dict = proxy_dict
        self.session = requests.Session()
        if proxy_dict:
            self.session.proxies.update(proxy_dict)
            
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def get_transcript_data(self, video_id: str, language: str = 'ko') -> Optional[List[Dict]]:
        """
        Get transcript data directly from YouTube
        """
        try:
            # Get the video page first
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"Fetching video page: {video_url}")
            response = self.session.get(video_url, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch video page: {response.status_code}")
                return None
            
            html_content = response.text
            
            # Extract caption tracks from the page
            captions_pattern = r'"captions":.*?"playerCaptionsTracklistRenderer":\s*\{[^}]*"captionTracks":\s*(\[.*?\])'
            match = re.search(captions_pattern, html_content)
            
            if not match:
                logger.warning("No caption tracks found in video page")
                return None
            
            try:
                captions_data = json.loads(match.group(1))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse captions data: {e}")
                return None
            
            # Find the desired language or fall back to available ones
            caption_url = None
            target_lang = language.lower()
            
            # First try exact language match
            for track in captions_data:
                if track.get('languageCode', '').lower() == target_lang:
                    caption_url = track.get('baseUrl')
                    logger.info(f"Found {language} caption track")
                    break
            
            # If no exact match, try English
            if not caption_url and target_lang != 'en':
                for track in captions_data:
                    if track.get('languageCode', '').lower() == 'en':
                        caption_url = track.get('baseUrl')
                        logger.info("Using English captions as fallback")
                        break
            
            # If still no match, use the first available
            if not caption_url and captions_data:
                caption_url = captions_data[0].get('baseUrl')
                lang_code = captions_data[0].get('languageCode', 'unknown')
                logger.info(f"Using first available caption track: {lang_code}")
            
            if not caption_url:
                logger.error("No usable caption URL found")
                return None
            
            # Fetch the actual transcript
            logger.info(f"Fetching transcript from: {caption_url[:100]}...")
            
            transcript_response = self.session.get(caption_url, timeout=15)
            
            if transcript_response.status_code != 200:
                logger.error(f"Failed to fetch transcript: {transcript_response.status_code}")
                return None
            
            # Parse the XML response
            transcript_xml = transcript_response.text
            
            # Extract text from XML (simple approach)
            text_pattern = r'<text start="([^"]*)" dur="([^"]*)"[^>]*>([^<]*)</text>'
            matches = re.findall(text_pattern, transcript_xml)
            
            transcript_data = []
            for start, duration, text in matches:
                try:
                    transcript_data.append({
                        'start': float(start),
                        'duration': float(duration),
                        'text': text.strip()
                    })
                except ValueError:
                    continue
            
            logger.info(f"Successfully extracted {len(transcript_data)} transcript segments")
            return transcript_data
            
        except Exception as e:
            logger.error(f"Error getting transcript data: {e}")
            return None
    
    def get_transcript_text(self, video_url: str, language: str = 'ko') -> Optional[str]:
        """
        Get transcript as plain text
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            logger.error(f"Could not extract video ID from: {video_url}")
            return None
        
        transcript_data = self.get_transcript_data(video_id, language)
        if not transcript_data:
            return None
        
        # Join all text segments
        full_text = ' '.join([segment['text'] for segment in transcript_data if segment['text']])
        
        return full_text.strip() if full_text else None

# Test function
if __name__ == "__main__":
    # Test without proxy first
    print("Testing YouTube Transcript API with direct connection...")
    
    api = YouTubeTranscriptAPIWithProxy()
    video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
    
    transcript = api.get_transcript_text(video_url, "ko")
    
    if transcript:
        print(f"Success! Transcript length: {len(transcript)} characters")
        print(f"First 200 characters: {transcript[:200]}...")
    else:
        print("Failed to get transcript")