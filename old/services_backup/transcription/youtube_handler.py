import os
import logging
import tempfile
from typing import Optional, Dict, Any
import yt_dlp
from pathlib import Path
import re
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from cookie_manager import setup_cookies_for_youtube

logger = logging.getLogger(__name__)

# Import MCP client for bot detection bypass
try:
    from mcp_youtube_client import MCPYouTubeClientSync
    MCP_AVAILABLE = True
except ImportError:
    logger.warning("MCP YouTube client not available - falling back to direct methods")
    MCP_AVAILABLE = False

# Import rate limiter for intelligent request management
try:
    from rate_limiter import youtube_rate_limiter, rate_limited_retry
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    logger.warning("Rate limiter not available - proceeding without rate limiting")
    RATE_LIMITER_AVAILABLE = False

# Import proxy manager for bot detection bypass
try:
    from proxy_manager import default_proxy_manager
    PROXY_MANAGER_AVAILABLE = True
except ImportError:
    logger.warning("Proxy manager not available - proceeding without proxy support")
    PROXY_MANAGER_AVAILABLE = False

class YouTubeHandler:
    """Handle YouTube video download and caption extraction"""
    
    def __init__(self, download_dir: str = "/tmp/youtube"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY", "")
        
        # Setup cookies for better YouTube access
        self.cookie_file = setup_cookies_for_youtube()
        if self.cookie_file:
            logger.info(f"YouTube cookies configured: {self.cookie_file}")
        else:
            logger.info("No YouTube cookies available - proceeding without cookies")
        
        # MCP server configuration
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8888")
        self.mcp_client = None
        if MCP_AVAILABLE:
            try:
                self.mcp_client = MCPYouTubeClientSync(self.mcp_server_url)
                logger.info(f"MCP YouTube client initialized: {self.mcp_server_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize MCP client: {e}")
                self.mcp_client = None
        
        # Proxy manager setup
        self.proxy_manager = default_proxy_manager if PROXY_MANAGER_AVAILABLE else None
        if self.proxy_manager and self.proxy_manager.has_proxies():
            logger.info(f"Proxy manager initialized with {len(self.proxy_manager.proxies)} proxies")
        else:
            logger.info("No proxy manager or proxies available")
        
    def download_audio(self, url: str) -> tuple[str, Dict[str, Any]]:
        """
        Download audio from YouTube video
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple of (audio_file_path, metadata)
        """
        output_path = os.path.join(self.download_dir, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(url, download=False)
                
                # Download audio
                ydl.download([url])
                
                # Get the downloaded file path
                title = info.get('title', 'video').replace('/', '_')
                audio_file = os.path.join(self.download_dir, f"{title}.mp3")
                
                # Get metadata
                metadata = {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'description': info.get('description'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'video_id': info.get('id'),
                }
                
                return audio_file, metadata
                
        except Exception as e:
            logger.error(f"Failed to download YouTube audio: {str(e)}")
            raise
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
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
    
    def get_captions_via_api(self, url: str, language: str = "ko") -> Optional[str]:
        """
        Get captions using YouTube Data API v3
        
        Args:
            url: YouTube video URL
            language: Language code for captions
            
        Returns:
            Caption text if available, None otherwise
        """
        if not self.youtube_api_key:
            logger.info("YouTube API key not configured, falling back to yt-dlp")
            return None
        
        video_id = self._extract_video_id(url)
        if not video_id:
            logger.error(f"Could not extract video ID from URL: {url}")
            return None
        
        try:
            # Get caption list using YouTube API
            api_url = "https://www.googleapis.com/youtube/v3/captions"
            params = {
                "part": "snippet",
                "videoId": video_id,
                "key": self.youtube_api_key
            }
            
            response = requests.get(api_url, params=params)
            
            if response.status_code != 200:
                logger.error(f"YouTube API error: {response.status_code} - {response.text}")
                return None
            
            data = response.json()
            captions = data.get("items", [])
            
            # Find caption in requested language
            caption_id = None
            for caption in captions:
                snippet = caption.get("snippet", {})
                if snippet.get("language") == language:
                    caption_id = caption.get("id")
                    break
            
            # Fallback to English if requested language not found
            if not caption_id and language != "en":
                for caption in captions:
                    snippet = caption.get("snippet", {})
                    if snippet.get("language") == "en":
                        caption_id = caption.get("id")
                        logger.info(f"Captions in {language} not found, using English")
                        break
            
            if caption_id:
                # Note: Downloading captions requires OAuth, so we can't directly download
                # We know captions exist, so we can try yt-dlp with this knowledge
                logger.info(f"Captions found via API for video {video_id}, using yt-dlp to download")
                return None  # Let yt-dlp handle the download
            
            logger.info(f"No captions found via API for video {video_id}")
            return None
            
        except Exception as e:
            logger.error(f"YouTube API error: {str(e)}")
            return None
    
    @rate_limited_retry() if RATE_LIMITER_AVAILABLE else lambda f: f
    def get_transcript_via_api(self, url: str, language: str = "ko") -> Optional[str]:
        """
        Get transcript using YouTube Transcript API (most reliable method)
        
        Args:
            url: YouTube video URL
            language: Language code for transcript (ko, en, etc.)
            
        Returns:
            Transcript text if available, None otherwise
        """
        video_id = self._extract_video_id(url)
        if not video_id:
            logger.error(f"Could not extract video ID from URL: {url}")
            return None
        
        try:
            # First try exact language match
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
                
                # Convert transcript list to plain text
                full_text = ' '.join([item['text'] for item in transcript_list])
                
                logger.info(f"Successfully got {language} transcript for video {video_id}")
                return full_text
                
            except Exception as lang_error:
                logger.info(f"Transcript in {language} not available: {str(lang_error)}")
                
                # Try English as fallback
                if language != 'en':
                    try:
                        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                        
                        full_text = ' '.join([item['text'] for item in transcript_list])
                        
                        logger.info(f"Using English transcript as fallback for video {video_id}")
                        return full_text
                        
                    except Exception as en_error:
                        logger.info(f"English transcript also not available: {str(en_error)}")
                
                # Try with no language restriction (default)
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                    
                    full_text = ' '.join([item['text'] for item in transcript_list])
                    
                    logger.info(f"Using default transcript for video {video_id}")
                    return full_text
                        
                except Exception as any_error:
                    logger.error(f"No transcripts available: {str(any_error)}")
                    
        except Exception as e:
            logger.error(f"YouTube Transcript API error: {str(e)}")
            return None
        
        logger.info(f"No transcripts found for video {video_id}")
        return None
    
    def get_captions(self, url: str, language: str = "ko") -> Optional[str]:
        """
        Try to get captions/subtitles from YouTube video using the most reliable method
        
        Args:
            url: YouTube video URL
            language: Language code for captions
            
        Returns:
            Caption text if available, None otherwise
        """
        # First try MCP server (best for avoiding bot detection on servers)
        if self.mcp_client:
            logger.info("Trying MCP YouTube Transcript server...")
            try:
                if self.mcp_client.health_check():
                    # Apply rate limiting to MCP requests if available
                    if RATE_LIMITER_AVAILABLE:
                        mcp_transcript = youtube_rate_limiter.execute_sync(
                            self.mcp_client.get_transcript, url, language
                        )
                    else:
                        mcp_transcript = self.mcp_client.get_transcript(url, language)
                    
                    if mcp_transcript:
                        logger.info(f"✅ MCP server transcript successful: {len(mcp_transcript)} characters")
                        return mcp_transcript
                    else:
                        logger.info("MCP server returned no transcript")
                else:
                    logger.warning("MCP server health check failed")
            except Exception as e:
                logger.warning(f"MCP server error: {e}")
        else:
            logger.info("MCP client not available, skipping...")
        
        # Second try YouTube Transcript API (reliable and works without authentication)
        logger.info("Trying YouTube Transcript API...")
        transcript_text = self.get_transcript_via_api(url, language)
        if transcript_text:
            return transcript_text
        
        logger.info("YouTube Transcript API failed, trying YouTube Data API...")
        # Second try YouTube API if available
        if self.youtube_api_key:
            logger.info("Checking captions availability via YouTube API")
            api_result = self.get_captions_via_api(url, language)
            if api_result:
                return api_result
        
        # Try the new YouTube Data API implementation
        try:
            from youtube_data_api import YouTubeDataAPI
            api = YouTubeDataAPI()
            transcript_text = api.get_transcript_text(url, language)
            if transcript_text:
                logger.info(f"Successfully got transcript via YouTube Data API")
                return transcript_text
        except Exception as e:
            logger.error(f"YouTube Data API failed: {e}")
        
        logger.info("All API methods failed, trying yt-dlp as last resort...")
        # Use enhanced yt-dlp options with anti-detection measures
        ydl_opts = {
            'quiet': False,  # Show errors for debugging
            'no_warnings': False,
            'skip_download': True,  # Don't download video, only subtitles
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en', 'ko'],  # Try multiple languages
            
            # Anti-detection measures
            'force_ipv4': True,  # Force IPv4
            'no_check_certificate': True,  # Skip certificate verification
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            
            # Cookie support 
            'cookiefile': self.cookie_file,
        }
        
        # Add proxy support if available
        if self.proxy_manager and self.proxy_manager.has_proxies():
            proxy_url = self.proxy_manager.get_proxy_for_yt_dlp()
            if proxy_url:
                ydl_opts['proxy'] = proxy_url
                logger.info(f"Using proxy for yt-dlp: {proxy_url}")
        
        # Continue with additional options
        ydl_opts.update({
            # Rate limiting to avoid bot detection
            'sleep_interval': 2,  # Wait 2 seconds between requests
            'max_sleep_interval': 5,  # Maximum sleep interval
            'sleep_interval_requests': 1,  # Wait 1 second between HTTP requests
            
            # Additional headers to mimic browser behavior
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            
            # Use multiple extractor attempts
            'extractor_retries': 3,
            'fragment_retries': 3,
            
            # Format preferences
            'extract_flat': False,
            'format': 'best',
        })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check for subtitles
                subtitle_result = None
                if 'subtitles' in info:
                    # Try requested language first
                    if language in info['subtitles']:
                        subtitle_result = self._download_subtitle(info['subtitles'][language])
                        if subtitle_result:
                            logger.info(f"✅ Found {language} manual subtitles")
                    
                    # Try English as fallback
                    if not subtitle_result and 'en' in info['subtitles']:
                        logger.info(f"Korean subtitles not found, trying English")
                        subtitle_result = self._download_subtitle(info['subtitles']['en'])
                        if subtitle_result:
                            logger.info(f"✅ Found English manual subtitles")
                
                # Try automatic captions if no manual subtitles
                if not subtitle_result and 'automatic_captions' in info:
                    if language in info['automatic_captions']:
                        subtitle_result = self._download_subtitle(info['automatic_captions'][language])
                        if subtitle_result:
                            logger.info(f"✅ Found {language} auto captions")
                    
                    if not subtitle_result and 'en' in info['automatic_captions']:
                        logger.info(f"Korean auto-captions not found, trying English")
                        subtitle_result = self._download_subtitle(info['automatic_captions']['en'])
                        if subtitle_result:
                            logger.info(f"✅ Found English auto captions")
                
                # Mark proxy success if we got results
                if subtitle_result and self.proxy_manager:
                    self.proxy_manager.mark_proxy_success()
                    return subtitle_result
                elif not subtitle_result:
                    logger.info("No captions available for this video")
                    return None
                else:
                    return subtitle_result
                
        except Exception as e:
            # Mark proxy error on failure
            if self.proxy_manager:
                self.proxy_manager.mark_proxy_error()
            logger.error(f"Failed to get YouTube captions: {str(e)}")
            return None
    
    def _download_subtitle(self, subtitle_info: list) -> Optional[str]:
        """Download and parse subtitle content"""
        import requests
        
        # Find the best format (prefer vtt or srv3)
        for sub in subtitle_info:
            if sub.get('ext') in ['vtt', 'srv3', 'srt']:
                try:
                    response = requests.get(sub['url'])
                    if response.status_code == 200:
                        return self._parse_subtitle(response.text, sub.get('ext'))
                except Exception as e:
                    logger.error(f"Failed to download subtitle: {str(e)}")
                    continue
        
        return None
    
    def _parse_subtitle(self, content: str, format: str) -> str:
        """Parse subtitle content to plain text"""
        lines = []
        
        if format == 'vtt':
            # Parse WebVTT format
            for line in content.split('\n'):
                # Skip headers and timestamps
                if not line.startswith('WEBVTT') and '-->' not in line and line.strip():
                    # Remove HTML tags if present
                    import re
                    clean_line = re.sub('<[^<]+?>', '', line)
                    if clean_line.strip():
                        lines.append(clean_line.strip())
        
        elif format in ['srt', 'srv3']:
            # Parse SRT format
            import re
            blocks = content.split('\n\n')
            for block in blocks:
                block_lines = block.split('\n')
                for line in block_lines:
                    # Skip numbers and timestamps
                    if not re.match(r'^\d+$', line) and '-->' not in line and line.strip():
                        lines.append(line.strip())
        
        else:
            # Just return as-is for unknown formats
            lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        return ' '.join(lines)
    
    def _get_cookie_file(self) -> Optional[str]:
        """Find available cookie file for yt-dlp"""
        possible_locations = [
            '/data/youtube_cookies.txt',  # Railway volume
            '/tmp/youtube_cookies.txt',   # Temporary location
            './cookies.txt',              # Local directory
            '/app/cookies.txt',           # Docker app directory
            os.path.expanduser('~/cookies.txt'),  # Home directory
        ]
        
        for cookie_path in possible_locations:
            if os.path.exists(cookie_path):
                logger.info(f"Using cookie file: {cookie_path}")
                return cookie_path
        
        logger.info("No cookie file found, proceeding without cookies")
        return None
    
    def create_cookie_placeholder(self) -> str:
        """Create a placeholder cookie file with instructions"""
        cookie_content = """# YouTube Cookie File for yt-dlp
# 
# To use cookies for better YouTube access:
# 1. On your local computer, run: yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com"
# 2. Upload the generated cookies.txt file to this server
# 3. Place it in one of these locations:
#    - /data/youtube_cookies.txt (recommended for Railway)
#    - /tmp/youtube_cookies.txt
#    - ./cookies.txt
#
# This will help bypass YouTube bot detection by using browser cookies.
"""
        
        cookie_paths = ['/data/youtube_cookies.txt', '/tmp/youtube_cookies.txt']
        
        for path in cookie_paths:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w') as f:
                    f.write(cookie_content)
                logger.info(f"Created cookie placeholder at {path}")
                return path
            except Exception as e:
                logger.debug(f"Could not create cookie file at {path}: {e}")
        
        return '/tmp/youtube_cookies.txt'  # Fallback
    
    def cleanup(self, file_path: str):
        """Clean up downloaded files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {str(e)}")