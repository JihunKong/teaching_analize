import os
import logging
from typing import Optional, Dict, Any, List
from openai import OpenAI
import ffmpeg
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class WhisperClient:
    """OpenAI Whisper API client for speech-to-text"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.max_file_size = 25 * 1024 * 1024  # 25MB limit for Whisper API
        
    def transcribe(
        self,
        file_path: str,
        language: str = "ko",
        prompt: Optional[str] = None,
        response_format: str = "verbose_json",
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using OpenAI Whisper API
        
        Args:
            file_path: Path to audio file
            language: Language code (ko, en, ja, etc.)
            prompt: Optional prompt to guide the model
            response_format: Output format (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature (0-1)
            
        Returns:
            Transcription result dictionary
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            
            if file_size > self.max_file_size:
                # Split large files
                logger.info(f"File size {file_size} exceeds limit, splitting...")
                return self._transcribe_large_file(
                    file_path, language, prompt, response_format, temperature
                )
            
            # Transcribe with Whisper API
            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    prompt=prompt,
                    response_format=response_format,
                    temperature=temperature
                )
            
            # Parse response based on format
            if response_format == "verbose_json":
                return {
                    "text": response.text,
                    "language": response.language if hasattr(response, 'language') else language,
                    "duration": response.duration if hasattr(response, 'duration') else None,
                    "segments": response.segments if hasattr(response, 'segments') else []
                }
            else:
                return {"text": str(response), "language": language}
                
        except Exception as e:
            logger.error(f"Whisper transcription failed: {str(e)}")
            raise
    
    def _transcribe_large_file(
        self,
        file_path: str,
        language: str,
        prompt: Optional[str],
        response_format: str,
        temperature: float
    ) -> Dict[str, Any]:
        """Handle large files by splitting into chunks"""
        
        chunks = self._split_audio(file_path)
        all_segments = []
        full_text = []
        total_duration = 0
        
        try:
            for i, chunk_path in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Use previous transcription as context
                chunk_prompt = prompt
                if i > 0 and full_text:
                    # Add last 100 chars as context
                    context = full_text[-1][-100:] if full_text[-1] else ""
                    chunk_prompt = f"{prompt}\n{context}" if prompt else context
                
                result = self.transcribe(
                    chunk_path,
                    language=language,
                    prompt=chunk_prompt,
                    response_format=response_format,
                    temperature=temperature
                )
                
                full_text.append(result["text"])
                if "segments" in result:
                    # Adjust timestamps for segments
                    for segment in result["segments"]:
                        segment["start"] = segment.get("start", 0) + total_duration
                        segment["end"] = segment.get("end", 0) + total_duration
                    all_segments.extend(result["segments"])
                
                if "duration" in result and result["duration"]:
                    total_duration += result["duration"]
        
        finally:
            # Clean up chunks
            for chunk in chunks:
                try:
                    os.remove(chunk)
                except:
                    pass
        
        return {
            "text": " ".join(full_text),
            "language": language,
            "duration": total_duration,
            "segments": all_segments
        }
    
    def _split_audio(self, file_path: str, chunk_duration: int = 600) -> List[str]:
        """
        Split audio file into chunks
        
        Args:
            file_path: Path to audio file
            chunk_duration: Duration of each chunk in seconds (default 10 minutes)
            
        Returns:
            List of chunk file paths
        """
        chunks = []
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Get audio duration
            probe = ffmpeg.probe(file_path)
            duration = float(probe['streams'][0]['duration'])
            
            # Calculate number of chunks
            num_chunks = int(duration / chunk_duration) + 1
            
            for i in range(num_chunks):
                start_time = i * chunk_duration
                chunk_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
                
                # Extract chunk using ffmpeg
                (
                    ffmpeg
                    .input(file_path, ss=start_time, t=chunk_duration)
                    .output(chunk_path, acodec='libmp3lame', ar=16000)
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                chunks.append(chunk_path)
                
        except Exception as e:
            logger.error(f"Failed to split audio: {str(e)}")
            # Clean up on error
            for chunk in chunks:
                try:
                    os.remove(chunk)
                except:
                    pass
            raise
        
        return chunks
    
    def convert_to_audio(self, video_path: str) -> str:
        """
        Convert video file to audio format suitable for Whisper
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to converted audio file
        """
        temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_audio.close()
        
        try:
            # Convert video to audio using ffmpeg
            (
                ffmpeg
                .input(video_path)
                .output(temp_audio.name, acodec='libmp3lame', ar=16000, ac=1)
                .overwrite_output()
                .run(quiet=True)
            )
            
            return temp_audio.name
            
        except Exception as e:
            logger.error(f"Failed to convert video to audio: {str(e)}")
            try:
                os.remove(temp_audio.name)
            except:
                pass
            raise