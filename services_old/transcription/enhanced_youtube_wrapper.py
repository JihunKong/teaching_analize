#!/usr/bin/env python3
"""
Enhanced YouTube Wrapper
Combines all anti-detection methods for robust YouTube access
"""

import os
import time
import logging
import random
from typing import Optional, Dict, Any, List
from youtube_handler import YouTubeHandler
from cookie_manager import CookieManager
import yt_dlp

logger = logging.getLogger(__name__)

class EnhancedYouTubeHandler(YouTubeHandler):
    """Enhanced YouTube handler with comprehensive anti-detection measures"""
    
    def __init__(self, download_dir: str = "/tmp/youtube"):
        super().__init__(download_dir)
        
        # Initialize cookie manager
        self.cookie_manager = CookieManager()
        
        # Anti-detection settings
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/116.0'
        ]
        
        # Request tracking for rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
    def _should_wait(self) -> bool:
        """Check if we should wait before making another request"""
        current_time = time.time()
        
        # Reset counter every hour
        if current_time - self.request_window_start > 3600:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Limit to 60 requests per hour
        if self.request_count >= 60:
            wait_time = 3600 - (current_time - self.request_window_start)
            if wait_time > 0:
                logger.warning(f"Rate limit reached, waiting {wait_time:.0f} seconds")
                time.sleep(wait_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Minimum 2 seconds between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < 2:
            wait_time = 2 - time_since_last + random.uniform(0, 1)  # Add random jitter
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        return True
    
    def _get_enhanced_ydl_opts(self, language: str = "ko") -> Dict[str, Any]:
        """Get enhanced yt-dlp options with all anti-detection measures"""
        
        # Wait if necessary
        self._should_wait()
        
        # Rotate user agent
        user_agent = random.choice(self.user_agents)
        
        # Get fresh cookie file
        cookie_file = self.cookie_manager.get_cookie_file_path()
        
        opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en', 'ko'],
            
            # Enhanced anti-detection
            'user_agent': user_agent,
            'referer': 'https://www.youtube.com/',
            'force_ipv4': True,
            'no_check_certificate': True,
            
            # Cookie support
            'cookiefile': cookie_file,
            
            # Aggressive rate limiting
            'sleep_interval': random.uniform(3, 7),
            'max_sleep_interval': 10,
            'sleep_interval_requests': random.uniform(1, 3),
            
            # Enhanced headers to mimic real browser
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            },
            
            # Retry settings
            'extractor_retries': 5,
            'fragment_retries': 5,
            'file_access_retries': 3,
            'retries': 3,
            
            # Use different extractor strategies
            'prefer_free_formats': True,
            'no_color': True,
            
            # Additional options to avoid detection
            'geo_bypass': True,
            'geo_bypass_country': 'US',
        }
        
        # Log the attempt
        logger.info(f"Using enhanced yt-dlp options with user-agent: {user_agent[:50]}...")
        if cookie_file:
            logger.info(f"Using cookies from: {cookie_file}")
        else:
            logger.warning("No cookies available - this may reduce success rate")
            
        return opts
    
    def get_captions_enhanced(self, url: str, language: str = "ko") -> Optional[str]:
        """
        Enhanced caption extraction with comprehensive fallback strategy
        """
        logger.info(f"Starting enhanced caption extraction for: {url}")
        
        # Method 1: YouTube Transcript API (fastest, most reliable)
        logger.info("🔄 Trying YouTube Transcript API...")
        try:
            transcript_text = self.get_transcript_via_api(url, language)
            if transcript_text:
                logger.info("✅ YouTube Transcript API successful!")
                return transcript_text
        except Exception as e:
            logger.info(f"❌ YouTube Transcript API failed: {e}")
        
        # Method 2: YouTube Data API v3 (if API key available)
        if self.youtube_api_key:
            logger.info("🔄 Trying YouTube Data API v3...")
            try:
                api_result = self.get_captions_via_api(url, language)
                if api_result:
                    logger.info("✅ YouTube Data API v3 successful!")
                    return api_result
            except Exception as e:
                logger.info(f"❌ YouTube Data API v3 failed: {e}")
        else:
            logger.info("⏭️ Skipping YouTube Data API v3 (no API key)")
        
        # Method 3: Enhanced yt-dlp with all anti-detection measures
        logger.info("🔄 Trying enhanced yt-dlp...")
        try:
            ydl_opts = self._get_enhanced_ydl_opts(language)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Try manual subtitles first
                if 'subtitles' in info:
                    for lang in [language, 'en', 'ko']:
                        if lang in info['subtitles']:
                            caption_text = self._download_subtitle(info['subtitles'][lang])
                            if caption_text:
                                logger.info(f"✅ Enhanced yt-dlp successful with {lang} manual subtitles!")
                                return caption_text
                
                # Try automatic captions
                if 'automatic_captions' in info:
                    for lang in [language, 'en', 'ko']:
                        if lang in info['automatic_captions']:
                            caption_text = self._download_subtitle(info['automatic_captions'][lang])
                            if caption_text:
                                logger.info(f"✅ Enhanced yt-dlp successful with {lang} auto captions!")
                                return caption_text
                
                logger.info("❌ Enhanced yt-dlp found no captions")
                
        except Exception as e:
            logger.error(f"❌ Enhanced yt-dlp failed: {e}")
        
        # Method 4: Fallback with minimal options (last resort)
        logger.info("🔄 Trying minimal yt-dlp fallback...")
        try:
            minimal_opts = {
                'quiet': True,
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'user_agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            }
            
            with yt_dlp.YoutubeDL(minimal_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Try any available subtitles
                for subtitle_type in ['subtitles', 'automatic_captions']:
                    if subtitle_type in info:
                        for lang_code, subtitle_list in info[subtitle_type].items():
                            caption_text = self._download_subtitle(subtitle_list)
                            if caption_text:
                                logger.info(f"✅ Minimal fallback successful with {lang_code}!")
                                return caption_text
                
        except Exception as e:
            logger.error(f"❌ Minimal fallback also failed: {e}")
        
        logger.error("❌ All caption extraction methods failed")
        return None
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the YouTube handler"""
        status = {
            "timestamp": time.time(),
            "cookie_status": self.cookie_manager.get_status_report(),
            "api_key_configured": bool(self.youtube_api_key),
            "download_dir": self.download_dir,
            "download_dir_writable": os.access(self.download_dir, os.W_OK),
            "rate_limit_status": {
                "requests_this_hour": self.request_count,
                "window_start": self.request_window_start,
                "last_request": self.last_request_time
            }
        }
        
        # Test basic functionality
        try:
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            video_id = self._extract_video_id(test_url)
            status["video_id_extraction"] = video_id is not None
        except Exception as e:
            status["video_id_extraction"] = False
            status["extraction_error"] = str(e)
        
        return status

def test_enhanced_handler():
    """Test the enhanced YouTube handler"""
    handler = EnhancedYouTubeHandler()
    
    print("Enhanced YouTube Handler Test")
    print("=" * 50)
    
    # Health check
    health = handler.health_check()
    print("Health Check:")
    for key, value in health.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 50)
    
    # Test caption extraction
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print(f"Testing caption extraction: {test_url}")
    
    captions = handler.get_captions_enhanced(test_url, "en")
    
    if captions:
        print(f"✅ SUCCESS: {len(captions)} characters extracted")
        print(f"Preview: {captions[:200]}...")
    else:
        print("❌ FAILED: No captions extracted")

if __name__ == "__main__":
    test_enhanced_handler()