import os
import logging
import tempfile
from typing import Optional, Dict, Any
import yt_dlp
from pathlib import Path

logger = logging.getLogger(__name__)

class YouTubeHandler:
    """Handle YouTube video download and caption extraction"""
    
    def __init__(self, download_dir: str = "/tmp/youtube"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
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
    
    def get_captions(self, url: str, language: str = "ko") -> Optional[str]:
        """
        Try to get captions/subtitles from YouTube video
        
        Args:
            url: YouTube video URL
            language: Language code for captions
            
        Returns:
            Caption text if available, None otherwise
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en'],  # Try Korean first, then English
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Check for subtitles
                if 'subtitles' in info:
                    # Try requested language first
                    if language in info['subtitles']:
                        return self._download_subtitle(info['subtitles'][language])
                    
                    # Try English as fallback
                    if 'en' in info['subtitles']:
                        logger.info(f"Korean subtitles not found, using English")
                        return self._download_subtitle(info['subtitles']['en'])
                
                # Try automatic captions
                if 'automatic_captions' in info:
                    if language in info['automatic_captions']:
                        return self._download_subtitle(info['automatic_captions'][language])
                    
                    if 'en' in info['automatic_captions']:
                        logger.info(f"Korean auto-captions not found, using English")
                        return self._download_subtitle(info['automatic_captions']['en'])
                
                logger.info("No captions available for this video")
                return None
                
        except Exception as e:
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
    
    def cleanup(self, file_path: str):
        """Clean up downloaded files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup file {file_path}: {str(e)}")