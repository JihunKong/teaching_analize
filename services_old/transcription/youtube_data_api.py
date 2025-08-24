#!/usr/bin/env python3
"""
YouTube Data API v3 for Caption Extraction
Uses official Google API to get video captions
"""

import os
import logging
import requests
import re
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class YouTubeDataAPI:
    """YouTube Data API v3 client for caption extraction"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        if not self.api_key:
            logger.warning("No YouTube API key provided. Caption extraction may be limited.")
    
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
        
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get basic video information"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/videos"
        params = {
            'part': 'snippet,contentDetails',
            'id': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    return data['items'][0]
            else:
                logger.error(f"YouTube API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            
        return None
    
    def list_captions(self, video_id: str) -> List[Dict]:
        """List available captions for a video"""
        if not self.api_key:
            logger.warning("No API key available for caption listing")
            return []
            
        url = f"{self.base_url}/captions"
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                logger.error(f"Caption list error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error listing captions: {e}")
            
        return []
    
    def download_caption(self, caption_id: str, format: str = 'srt') -> Optional[str]:
        """Download caption content"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/captions/{caption_id}"
        params = {
            'tfmt': format,  # srt, vtt, or ttml
            'key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Caption download error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error downloading caption: {e}")
            
        return None
    
    def get_transcript_text(self, video_url: str, language: str = 'ko') -> Optional[str]:
        """
        Get transcript text for a video
        """
        video_id = self.extract_video_id(video_url)
        if not video_id:
            logger.error(f"Could not extract video ID from: {video_url}")
            return None
        
        # First, get video info to verify it exists
        video_info = self.get_video_info(video_id)
        if not video_info:
            logger.error(f"Could not get video info for: {video_id}")
            return None
        
        logger.info(f"Video title: {video_info['snippet']['title']}")
        
        # List available captions
        captions = self.list_captions(video_id)
        
        if not captions:
            logger.warning(f"No captions found for video: {video_id}")
            return None
        
        logger.info(f"Found {len(captions)} caption tracks")
        
        # Find the best caption track
        target_caption = None
        
        # First try exact language match
        for caption in captions:
            snippet = caption['snippet']
            if snippet['language'].lower() == language.lower():
                target_caption = caption
                logger.info(f"Found {language} caption track")
                break
        
        # Fallback to English
        if not target_caption and language.lower() != 'en':
            for caption in captions:
                snippet = caption['snippet']
                if snippet['language'].lower() == 'en':
                    target_caption = caption
                    logger.info("Using English caption as fallback")
                    break
        
        # Use first available
        if not target_caption and captions:
            target_caption = captions[0]
            lang = target_caption['snippet']['language']
            logger.info(f"Using first available caption: {lang}")
        
        if not target_caption:
            logger.error("No suitable caption track found")
            return None
        
        # Download the caption
        caption_id = target_caption['id']
        caption_content = self.download_caption(caption_id, 'srt')
        
        if not caption_content:
            logger.error("Failed to download caption content")
            return None
        
        # Parse SRT and extract plain text
        transcript_text = self.parse_srt_to_text(caption_content)
        
        return transcript_text
    
    def parse_srt_to_text(self, srt_content: str) -> str:
        """Convert SRT format to plain text"""
        lines = srt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip sequence numbers and timestamps
            if (line.isdigit() or 
                '-->' in line or 
                not line):
                continue
            
            # Clean up text
            line = re.sub(r'<[^>]+>', '', line)  # Remove HTML tags
            line = re.sub(r'\[.*?\]', '', line)  # Remove speaker labels
            
            if line:
                text_lines.append(line)
        
        return ' '.join(text_lines)

# Alternative method without API key - try yt-dlp with different approach
class YouTubeDLPExtractor:
    """Alternative extraction using yt-dlp with better options"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_transcript_text(self, video_url: str, language: str = 'ko') -> Optional[str]:
        """Get transcript using yt-dlp with subtitle extraction"""
        import subprocess
        import tempfile
        import os
        
        video_id = self.extract_video_id(video_url)
        if not video_id:
            return None
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Use yt-dlp to extract subtitles only
                cmd = [
                    'yt-dlp',
                    '--write-auto-sub',
                    '--write-sub',
                    '--sub-lang', f'{language},en',
                    '--sub-format', 'vtt',
                    '--skip-download',
                    '--output', os.path.join(temp_dir, '%(title)s.%(ext)s'),
                    video_url
                ]
                
                self.logger.info(f"Running: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.logger.error(f"yt-dlp failed: {result.stderr}")
                    return None
                
                # Look for subtitle files
                for filename in os.listdir(temp_dir):
                    if filename.endswith('.vtt'):
                        vtt_path = os.path.join(temp_dir, filename)
                        with open(vtt_path, 'r', encoding='utf-8') as f:
                            vtt_content = f.read()
                        
                        # Parse VTT to text
                        return self.parse_vtt_to_text(vtt_content)
                
                self.logger.warning("No subtitle files found")
                return None
                
        except Exception as e:
            self.logger.error(f"yt-dlp extraction failed: {e}")
            return None
    
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
        
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def parse_vtt_to_text(self, vtt_content: str) -> str:
        """Convert VTT format to plain text"""
        lines = vtt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip VTT headers, timestamps, and empty lines
            if (line.startswith('WEBVTT') or
                '-->' in line or
                line.startswith('NOTE') or
                not line):
                continue
            
            # Clean up text
            line = re.sub(r'<[^>]+>', '', line)  # Remove HTML tags
            line = re.sub(r'\[.*?\]', '', line)  # Remove speaker labels
            
            if line:
                text_lines.append(line)
        
        return ' '.join(text_lines)

# Test function
if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
    
    print("=== Testing YouTube Data API ===")
    api_extractor = YouTubeDataAPI()
    
    if api_extractor.api_key:
        transcript = api_extractor.get_transcript_text(video_url, "ko")
        if transcript:
            print(f"API Success! Length: {len(transcript)} chars")
            print(f"Sample: {transcript[:200]}...")
        else:
            print("API method failed")
    else:
        print("No API key available")
    
    print("\n=== Testing yt-dlp method ===")
    dlp_extractor = YouTubeDLPExtractor()
    transcript = dlp_extractor.get_transcript_text(video_url, "ko")
    
    if transcript:
        print(f"yt-dlp Success! Length: {len(transcript)} chars")
        print(f"Sample: {transcript[:200]}...")
    else:
        print("yt-dlp method failed")