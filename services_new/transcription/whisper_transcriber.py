#!/usr/bin/env python3
"""
OpenAI Whisper API transcription module for YouTube videos
This implements the secondary fallback method from TRANSCRIPT_METHOD.md
"""

import logging
import time
import tempfile
import os
from typing import Dict, Any, Optional
import subprocess
import json

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

logger = logging.getLogger(__name__)

class WhisperTranscriber:
    """
    OpenAI Whisper API based transcription for YouTube videos
    This is the secondary fallback method when YouTube API fails but before browser automation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        return {
            'openai': OPENAI_AVAILABLE,
            'yt_dlp': YTDLP_AVAILABLE,
            'ffmpeg': self._check_ffmpeg()
        }
    
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def extract_video_id(self, youtube_url: str) -> str:
        """Extract video ID from YouTube URL"""
        from urllib.parse import urlparse, parse_qs
        
        parsed_url = urlparse(youtube_url)
        
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        elif parsed_url.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
            if 'watch' in parsed_url.path:
                query_params = parse_qs(parsed_url.query)
                return query_params.get('v', [''])[0]
            elif '/embed/' in parsed_url.path:
                return parsed_url.path.split('/embed/')[1].split('?')[0]
            elif '/v/' in parsed_url.path:
                return parsed_url.path.split('/v/')[1].split('?')[0]
        
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
    
    async def download_audio(self, youtube_url: str, output_path: str) -> Dict[str, Any]:
        """
        Download audio from YouTube video using yt-dlp
        Returns metadata and success status
        """
        try:
            if not YTDLP_AVAILABLE:
                return {
                    "success": False,
                    "error": "yt-dlp not available. Install with: pip install yt-dlp"
                }
            
            # Configure yt-dlp options for audio extraction
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': '192K',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(youtube_url, download=False)
                
                # Download audio
                ydl.download([youtube_url])
                
                # Check if file was created (yt-dlp might add .mp3 extension)
                actual_path = output_path
                if not os.path.exists(actual_path) and os.path.exists(output_path + '.mp3'):
                    actual_path = output_path + '.mp3'
                
                if not os.path.exists(actual_path):
                    return {
                        "success": False,
                        "error": "Audio file was not created"
                    }
                
                return {
                    "success": True,
                    "audio_path": actual_path,
                    "metadata": {
                        "title": info.get('title', ''),
                        "duration": info.get('duration', 0),
                        "uploader": info.get('uploader', ''),
                        "upload_date": info.get('upload_date', ''),
                        "view_count": info.get('view_count', 0)
                    }
                }
        
        except Exception as e:
            logger.error(f"Error downloading audio: {str(e)}")
            return {
                "success": False,
                "error": f"Audio download failed: {str(e)}"
            }
    
    def chunk_audio_file(self, audio_path: str, chunk_duration_minutes: int = 10) -> list:
        """
        Split audio file into chunks for Whisper API (25MB limit)
        Returns list of chunk file paths
        """
        try:
            chunk_paths = []
            base_name = os.path.splitext(audio_path)[0]
            
            # Get audio duration
            probe_cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                '-show_format', audio_path
            ]
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            audio_info = json.loads(result.stdout)
            total_duration = float(audio_info['format']['duration'])
            
            # Calculate number of chunks
            chunk_duration_seconds = chunk_duration_minutes * 60
            num_chunks = int(total_duration / chunk_duration_seconds) + 1
            
            for i in range(num_chunks):
                start_time = i * chunk_duration_seconds
                chunk_path = f"{base_name}_chunk_{i:03d}.mp3"
                
                # Extract chunk using ffmpeg
                chunk_cmd = [
                    'ffmpeg', '-i', audio_path, '-ss', str(start_time),
                    '-t', str(chunk_duration_seconds), '-acodec', 'mp3',
                    '-q:a', '2', chunk_path, '-y'
                ]
                
                subprocess.run(chunk_cmd, capture_output=True, check=True)
                
                # Check if chunk was created and has content
                if os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 1000:
                    chunk_paths.append(chunk_path)
                else:
                    # Remove empty chunk
                    if os.path.exists(chunk_path):
                        os.remove(chunk_path)
            
            return chunk_paths
        
        except Exception as e:
            logger.error(f"Error chunking audio: {str(e)}")
            return []
    
    async def transcribe_with_whisper_api(self, audio_path: str, language: str = "ko") -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API
        """
        try:
            if not OPENAI_AVAILABLE:
                return {
                    "success": False,
                    "error": "OpenAI library not available"
                }
            
            if not self.api_key:
                return {
                    "success": False,
                    "error": "OpenAI API key not provided"
                }
            
            # Check file size (Whisper has 25MB limit)
            file_size = os.path.getsize(audio_path)
            max_size = 25 * 1024 * 1024  # 25MB
            
            if file_size > max_size:
                logger.info(f"Audio file too large ({file_size/1024/1024:.1f}MB), chunking...")
                chunk_paths = self.chunk_audio_file(audio_path)
                
                if not chunk_paths:
                    return {
                        "success": False,
                        "error": "Failed to chunk audio file"
                    }
                
                # Transcribe each chunk
                all_transcripts = []
                for chunk_path in chunk_paths:
                    try:
                        with open(chunk_path, 'rb') as audio_file:
                            response = openai.Audio.transcribe(
                                model="whisper-1",
                                file=audio_file,
                                language=language if language != "ko" else "ko"
                            )
                            all_transcripts.append(response.text)
                    finally:
                        # Clean up chunk
                        if os.path.exists(chunk_path):
                            os.remove(chunk_path)
                
                transcript_text = " ".join(all_transcripts)
            
            else:
                # Transcribe single file
                with open(audio_path, 'rb') as audio_file:
                    response = openai.Audio.transcribe(
                        model="whisper-1",
                        file=audio_file,
                        language=language if language != "ko" else "ko"
                    )
                    transcript_text = response.text
            
            return {
                "success": True,
                "transcript": transcript_text,
                "character_count": len(transcript_text),
                "word_count": len(transcript_text.split()),
                "file_size_mb": file_size / 1024 / 1024
            }
        
        except Exception as e:
            logger.error(f"Whisper API transcription failed: {str(e)}")
            return {
                "success": False,
                "error": f"Whisper API transcription failed: {str(e)}"
            }
    
    async def transcribe_youtube_video(self, youtube_url: str, language: str = "ko") -> Dict[str, Any]:
        """
        Main method to transcribe YouTube video using OpenAI Whisper API
        This is the secondary fallback method from TRANSCRIPT_METHOD.md
        """
        start_time = time.time()
        temp_dir = None
        
        try:
            video_id = self.extract_video_id(youtube_url)
            logger.info(f"Starting Whisper API transcription for video: {video_id}")
            
            # Check dependencies
            deps = self.check_dependencies()
            missing_deps = [k for k, v in deps.items() if not v]
            
            if missing_deps:
                return {
                    "success": False,
                    "error": f"Missing dependencies: {', '.join(missing_deps)}",
                    "video_id": video_id
                }
            
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, f"audio_{video_id}")
            
            # Download audio
            download_result = await self.download_audio(youtube_url, audio_path)
            if not download_result["success"]:
                return {
                    "success": False,
                    "error": download_result["error"],
                    "video_id": video_id
                }
            
            audio_path = download_result["audio_path"]
            metadata = download_result.get("metadata", {})
            
            # Transcribe with Whisper API
            transcription_result = await self.transcribe_with_whisper_api(audio_path, language)
            
            if not transcription_result["success"]:
                return {
                    "success": False,
                    "error": transcription_result["error"],
                    "video_id": video_id,
                    "metadata": metadata
                }
            
            processing_time = time.time() - start_time
            
            result = {
                "success": True,
                "video_url": youtube_url,
                "video_id": video_id,
                "transcript": transcription_result["transcript"],
                "language": language,
                "character_count": transcription_result["character_count"],
                "word_count": transcription_result["word_count"],
                "method_used": "whisper_api",
                "timestamp": time.time(),
                "processing_time": processing_time,
                "metadata": metadata,
                "file_size_mb": transcription_result.get("file_size_mb", 0)
            }
            
            logger.info(f"Successfully transcribed {transcription_result['character_count']} characters using Whisper API in {processing_time:.2f}s")
            return result
        
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Whisper API transcription failed after {processing_time:.2f}s: {str(e)}")
            return {
                "success": False,
                "error": f"Whisper API transcription failed: {str(e)}",
                "video_id": self.extract_video_id(youtube_url) if youtube_url else "unknown",
                "processing_time": processing_time
            }
        
        finally:
            # Clean up temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp directory: {e}")

# Convenience function for direct usage
async def transcribe_with_whisper(youtube_url: str, language: str = "ko", api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to transcribe a YouTube video using OpenAI Whisper API
    This implements the secondary fallback method from TRANSCRIPT_METHOD.md
    """
    transcriber = WhisperTranscriber(api_key=api_key)
    return await transcriber.transcribe_youtube_video(youtube_url, language)