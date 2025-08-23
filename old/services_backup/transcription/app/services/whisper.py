import os
import openai
from typing import Dict, Any, Optional, List
import aiohttp
import asyncio
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set, Whisper service will not work")
        openai.api_key = self.api_key
        
        # Supported audio formats and their max sizes
        self.supported_formats = {
            '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', 
            '.wav', '.webm', '.flac', '.ogg', '.opus'
        }
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit for Whisper API
        
    async def transcribe(
        self,
        file_path: str,
        language: str = "ko",
        include_timestamps: bool = True,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API
        
        Args:
            file_path: Path to audio file
            language: Language code (e.g., "ko" for Korean)
            include_timestamps: Whether to include timestamps in segments
            prompt: Optional prompt to guide the transcription
            
        Returns:
            Dictionary containing transcription results
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                # Need to split the file
                return await self._transcribe_large_file(
                    file_path, language, include_timestamps, prompt
                )
            
            # Direct transcription for small files
            with open(file_path, "rb") as audio_file:
                response = await self._call_whisper_api(
                    audio_file,
                    language=language,
                    response_format="verbose_json" if include_timestamps else "json",
                    prompt=prompt
                )
                
            return self._process_response(response)
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise
    
    async def _call_whisper_api(
        self,
        audio_file,
        language: str,
        response_format: str = "verbose_json",
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make API call to OpenAI Whisper"""
        try:
            # Prepare parameters
            params = {
                "model": "whisper-1",
                "file": audio_file,
                "language": language,
                "response_format": response_format,
                "temperature": 0.2  # Lower temperature for more consistent results
            }
            
            if prompt:
                params["prompt"] = prompt
            
            # Make API call
            response = await asyncio.to_thread(
                openai.Audio.transcribe,
                **params
            )
            
            return response
            
        except openai.error.RateLimitError:
            logger.warning("Rate limit hit, waiting before retry...")
            await asyncio.sleep(5)
            return await self._call_whisper_api(
                audio_file, language, response_format, prompt
            )
        except Exception as e:
            logger.error(f"Whisper API call failed: {str(e)}")
            raise
    
    async def _transcribe_large_file(
        self,
        file_path: str,
        language: str,
        include_timestamps: bool,
        prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Handle transcription of files larger than 25MB by splitting"""
        from pydub import AudioSegment
        
        logger.info(f"Splitting large file: {file_path}")
        
        # Load audio file
        audio = AudioSegment.from_file(file_path)
        
        # Split into 10-minute chunks (well under 25MB limit)
        chunk_length = 10 * 60 * 1000  # 10 minutes in milliseconds
        chunks = []
        
        for i in range(0, len(audio), chunk_length):
            chunk = audio[i:i + chunk_length]
            chunks.append(chunk)
        
        # Transcribe each chunk
        all_segments = []
        full_text = []
        time_offset = 0
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Transcribing chunk {i+1}/{len(chunks)}")
            
            # Export chunk to temporary file
            temp_path = f"/tmp/chunk_{i}.mp3"
            chunk.export(temp_path, format="mp3")
            
            try:
                # Transcribe chunk
                with open(temp_path, "rb") as audio_file:
                    response = await self._call_whisper_api(
                        audio_file,
                        language=language,
                        response_format="verbose_json" if include_timestamps else "json",
                        prompt=prompt
                    )
                
                # Process response
                if include_timestamps and "segments" in response:
                    # Adjust timestamps for this chunk
                    for segment in response["segments"]:
                        segment["start"] += time_offset
                        segment["end"] += time_offset
                    all_segments.extend(response["segments"])
                
                full_text.append(response.get("text", ""))
                
                # Update time offset for next chunk
                time_offset += len(chunk) / 1000  # Convert to seconds
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Combine results
        result = {
            "text": " ".join(full_text),
            "language": language,
            "duration": len(audio) / 1000  # Total duration in seconds
        }
        
        if include_timestamps:
            result["segments"] = all_segments
        
        return result
    
    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process and format Whisper API response"""
        result = {
            "text": response.get("text", ""),
            "language": response.get("language", ""),
            "duration": response.get("duration", 0)
        }
        
        # Add segments if available
        if "segments" in response:
            result["segments"] = [
                {
                    "id": seg.get("id"),
                    "start": seg.get("start"),
                    "end": seg.get("end"),
                    "text": seg.get("text", "").strip(),
                    "tokens": seg.get("tokens", []),
                    "temperature": seg.get("temperature"),
                    "avg_logprob": seg.get("avg_logprob"),
                    "compression_ratio": seg.get("compression_ratio"),
                    "no_speech_prob": seg.get("no_speech_prob")
                }
                for seg in response["segments"]
            ]
        
        # Add word-level timestamps if available
        if "words" in response:
            result["words"] = response["words"]
        
        return result
    
    async def detect_language(self, file_path: str) -> str:
        """Detect the language of an audio file"""
        try:
            with open(file_path, "rb") as audio_file:
                # Use a small portion for language detection
                response = await self._call_whisper_api(
                    audio_file,
                    language=None,  # Let Whisper detect
                    response_format="json"
                )
                
            return response.get("language", "unknown")
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            return "unknown"
    
    def estimate_cost(self, duration_seconds: float) -> float:
        """
        Estimate the cost of transcription
        Whisper API pricing: $0.006 per minute
        """
        minutes = duration_seconds / 60
        return minutes * 0.006
    
    async def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """Validate audio file before transcription"""
        from pydub import AudioSegment
        
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File not found"}
            
            # Check file extension
            ext = Path(file_path).suffix.lower()
            if ext not in self.supported_formats:
                return {
                    "valid": False,
                    "error": f"Unsupported format: {ext}",
                    "supported_formats": list(self.supported_formats)
                }
            
            # Load audio to check properties
            audio = AudioSegment.from_file(file_path)
            
            # Get audio properties
            duration = len(audio) / 1000  # Convert to seconds
            channels = audio.channels
            frame_rate = audio.frame_rate
            
            return {
                "valid": True,
                "duration": duration,
                "channels": channels,
                "sample_rate": frame_rate,
                "estimated_cost": self.estimate_cost(duration)
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}