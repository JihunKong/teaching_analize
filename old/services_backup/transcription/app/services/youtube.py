from typing import Optional, Dict, Any, List
import yt_dlp
import os
import re
import logging
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'force_generic_extractor': False
        }
        
    def validate_url(self, url: str) -> bool:
        """Validate if the URL is a valid YouTube URL"""
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube\.com/(watch\?v=|embed/|v/)|youtu\.be/)[\w-]+'
        )
        return bool(youtube_regex.match(url))
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/)([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video metadata"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                
                return {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader"),
                    "upload_date": info.get("upload_date"),
                    "description": info.get("description"),
                    "thumbnail": info.get("thumbnail"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "categories": info.get("categories", []),
                    "tags": info.get("tags", [])
                }
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            raise
    
    async def get_captions(
        self, 
        url: str, 
        language: str = "ko",
        auto_captions: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Extract captions/subtitles from YouTube video
        
        Args:
            url: YouTube video URL
            language: Language code for captions
            auto_captions: Whether to use auto-generated captions if manual not available
            
        Returns:
            Dictionary with transcript text and segments, or None if not available
        """
        try:
            ydl_opts = {
                **self.ydl_opts,
                'writesubtitles': True,
                'writeautomaticsub': auto_captions,
                'subtitleslangs': [language],
                'skip_download': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                
                # Check for manual subtitles first
                subtitles = info.get('subtitles', {})
                if language in subtitles:
                    return await self._download_and_parse_captions(
                        subtitles[language], 
                        info.get('duration', 0)
                    )
                
                # Check for automatic captions
                if auto_captions:
                    auto_subs = info.get('automatic_captions', {})
                    if language in auto_subs:
                        return await self._download_and_parse_captions(
                            auto_subs[language],
                            info.get('duration', 0),
                            is_auto=True
                        )
                    
                    # Try Korean variants
                    korean_variants = ['ko', 'ko-KR', 'kor']
                    for variant in korean_variants:
                        if variant in auto_subs:
                            return await self._download_and_parse_captions(
                                auto_subs[variant],
                                info.get('duration', 0),
                                is_auto=True
                            )
                
                logger.info(f"No captions available for language: {language}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get captions: {str(e)}")
            return None
    
    async def _download_and_parse_captions(
        self, 
        caption_info: List[Dict], 
        duration: float,
        is_auto: bool = False
    ) -> Dict[str, Any]:
        """Download and parse caption data"""
        import aiohttp
        import xml.etree.ElementTree as ET
        
        # Prefer srv3 format (contains timestamps)
        caption_url = None
        for fmt in caption_info:
            if fmt.get('ext') == 'srv3' or fmt.get('ext') == 'ttml':
                caption_url = fmt.get('url')
                break
        
        if not caption_url and caption_info:
            caption_url = caption_info[0].get('url')
        
        if not caption_url:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(caption_url) as response:
                    caption_data = await response.text()
            
            # Parse caption data
            segments = self._parse_caption_data(caption_data)
            
            # Combine all text
            full_text = " ".join([seg["text"] for seg in segments])
            
            return {
                "text": full_text,
                "segments": segments,
                "language": "ko",
                "duration": duration,
                "source": "youtube_auto_captions" if is_auto else "youtube_captions"
            }
            
        except Exception as e:
            logger.error(f"Failed to download/parse captions: {str(e)}")
            return None
    
    def _parse_caption_data(self, caption_data: str) -> List[Dict[str, Any]]:
        """Parse caption data from various formats"""
        segments = []
        
        # Try parsing as srv3/ttml (XML format)
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(caption_data)
            
            # Handle different XML formats
            for elem in root.iter():
                if elem.tag.endswith('text') or elem.tag == 'p':
                    text = elem.text
                    if text:
                        segment = {
                            "text": text.strip(),
                            "start": self._parse_time(elem.get('start') or elem.get('begin')),
                            "end": self._parse_time(elem.get('dur') or elem.get('end'))
                        }
                        if segment["start"] is not None:
                            segments.append(segment)
                            
        except Exception:
            # Try parsing as WebVTT or SRT
            lines = caption_data.split('\n')
            current_segment = {}
            
            for line in lines:
                line = line.strip()
                
                # Skip headers
                if line in ['WEBVTT', ''] or line.startswith('NOTE'):
                    continue
                
                # Time codes (SRT/VTT format)
                if '-->' in line:
                    times = line.split('-->')
                    if len(times) == 2:
                        current_segment['start'] = self._parse_time(times[0].strip())
                        current_segment['end'] = self._parse_time(times[1].strip())
                
                # Text content
                elif line and not line.isdigit():
                    if 'text' in current_segment:
                        current_segment['text'] += ' ' + line
                    else:
                        current_segment['text'] = line
                    
                    # If we have a complete segment, add it
                    if 'start' in current_segment and 'text' in current_segment:
                        segments.append(current_segment)
                        current_segment = {}
        
        return segments
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[float]:
        """Parse time string to seconds"""
        if not time_str:
            return None
        
        # Remove any extra formatting
        time_str = time_str.strip().split()[0]
        
        # Handle different time formats
        if ',' in time_str:  # SRT format
            time_str = time_str.replace(',', '.')
        
        try:
            # Try HH:MM:SS.mmm format
            if ':' in time_str:
                parts = time_str.split(':')
                if len(parts) == 3:
                    h, m, s = parts
                    return float(h) * 3600 + float(m) * 60 + float(s)
                elif len(parts) == 2:
                    m, s = parts
                    return float(m) * 60 + float(s)
            else:
                # Assume seconds
                return float(time_str)
        except:
            return None
    
    async def download_audio(
        self, 
        url: str, 
        output_dir: str = "/tmp",
        job_id: Optional[str] = None
    ) -> str:
        """
        Download audio from YouTube video
        
        Args:
            url: YouTube video URL
            output_dir: Directory to save the audio file
            job_id: Optional job ID for naming the file
            
        Returns:
            Path to the downloaded audio file
        """
        try:
            output_path = os.path.join(
                output_dir, 
                f"{job_id or 'youtube_audio'}.%(ext)s"
            )
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                
                # Get the actual output filename
                filename = ydl.prepare_filename(info)
                # Replace extension with mp3
                audio_path = os.path.splitext(filename)[0] + '.mp3'
                
                if os.path.exists(audio_path):
                    logger.info(f"Audio downloaded successfully: {audio_path}")
                    return audio_path
                else:
                    raise FileNotFoundError(f"Downloaded audio file not found: {audio_path}")
                    
        except Exception as e:
            logger.error(f"Failed to download audio: {str(e)}")
            raise
    
    async def download_video(
        self,
        url: str,
        output_dir: str = "/tmp",
        job_id: Optional[str] = None,
        quality: str = "720p"
    ) -> str:
        """Download video from YouTube"""
        try:
            output_path = os.path.join(
                output_dir,
                f"{job_id or 'youtube_video'}.%(ext)s"
            )
            
            ydl_opts = {
                'format': f'best[height<={quality[:-1]}]/best',
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=True)
                
                # Get the actual output filename
                video_path = ydl.prepare_filename(info)
                
                if os.path.exists(video_path):
                    logger.info(f"Video downloaded successfully: {video_path}")
                    return video_path
                else:
                    raise FileNotFoundError(f"Downloaded video file not found: {video_path}")
                    
        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            raise