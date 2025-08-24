import os
import json
import gzip
import shutil
import aiofiles
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.base_path = os.getenv("RAILWAY_VOLUME_PATH", "/data")
        self.uploads_dir = os.path.join(self.base_path, "uploads")
        self.transcripts_dir = os.path.join(self.base_path, "transcripts")
        self.temp_dir = os.path.join(self.base_path, "temp")
        
        # Create directories if they don't exist
        for dir_path in [self.uploads_dir, self.transcripts_dir, self.temp_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Storage settings
        self.max_file_age_days = 30
        self.use_compression = True
        
    async def save_upload(self, file, job_id: str) -> str:
        """
        Save uploaded file to storage
        
        Args:
            file: UploadFile object
            job_id: Unique job identifier
            
        Returns:
            Path to saved file
        """
        try:
            # Create job directory
            job_dir = os.path.join(self.uploads_dir, job_id)
            Path(job_dir).mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = os.path.join(job_dir, file.filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save upload: {str(e)}")
            raise
    
    async def save_transcript(
        self, 
        job_id: str, 
        transcript: Dict[str, Any],
        compress: Optional[bool] = None
    ) -> str:
        """
        Save transcript to storage
        
        Args:
            job_id: Job identifier
            transcript: Transcript data
            compress: Whether to compress the file
            
        Returns:
            Path to saved transcript
        """
        try:
            # Create transcript directory
            transcript_dir = os.path.join(self.transcripts_dir, job_id)
            Path(transcript_dir).mkdir(parents=True, exist_ok=True)
            
            # Determine compression
            use_compression = compress if compress is not None else self.use_compression
            
            # File path
            file_name = "transcript.json.gz" if use_compression else "transcript.json"
            file_path = os.path.join(transcript_dir, file_name)
            
            # Save transcript
            if use_compression:
                # Compress and save
                json_bytes = json.dumps(transcript, ensure_ascii=False).encode('utf-8')
                with gzip.open(file_path, 'wb') as f:
                    f.write(json_bytes)
            else:
                # Save as regular JSON
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(transcript, ensure_ascii=False, indent=2))
            
            # Also save a plain text version for quick access
            text_path = os.path.join(transcript_dir, "transcript.txt")
            async with aiofiles.open(text_path, 'w', encoding='utf-8') as f:
                await f.write(transcript.get("text", ""))
            
            logger.info(f"Transcript saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save transcript: {str(e)}")
            raise
    
    async def load_transcript(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Load transcript from storage
        
        Args:
            job_id: Job identifier
            
        Returns:
            Transcript data or None if not found
        """
        try:
            transcript_dir = os.path.join(self.transcripts_dir, job_id)
            
            # Try compressed version first
            compressed_path = os.path.join(transcript_dir, "transcript.json.gz")
            if os.path.exists(compressed_path):
                with gzip.open(compressed_path, 'rt', encoding='utf-8') as f:
                    return json.load(f)
            
            # Try uncompressed version
            uncompressed_path = os.path.join(transcript_dir, "transcript.json")
            if os.path.exists(uncompressed_path):
                async with aiofiles.open(uncompressed_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    return json.loads(content)
            
            logger.warning(f"Transcript not found for job: {job_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load transcript: {str(e)}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            file_path: Path to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False
    
    async def delete_job_data(self, job_id: str) -> bool:
        """
        Delete all data associated with a job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete upload directory
            upload_dir = os.path.join(self.uploads_dir, job_id)
            if os.path.exists(upload_dir):
                shutil.rmtree(upload_dir)
            
            # Delete transcript directory
            transcript_dir = os.path.join(self.transcripts_dir, job_id)
            if os.path.exists(transcript_dir):
                shutil.rmtree(transcript_dir)
            
            logger.info(f"Job data deleted: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete job data: {str(e)}")
            return False
    
    async def cleanup_old_files(self, days: Optional[int] = None) -> int:
        """
        Clean up files older than specified days
        
        Args:
            days: Number of days (uses default if not specified)
            
        Returns:
            Number of files deleted
        """
        days = days or self.max_file_age_days
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        try:
            # Clean uploads
            for job_dir in os.listdir(self.uploads_dir):
                dir_path = os.path.join(self.uploads_dir, job_dir)
                if os.path.isdir(dir_path):
                    # Check directory modification time
                    mtime = datetime.fromtimestamp(os.path.getmtime(dir_path))
                    if mtime < cutoff_time:
                        shutil.rmtree(dir_path)
                        deleted_count += 1
                        logger.info(f"Deleted old upload: {job_dir}")
            
            # Clean transcripts
            for job_dir in os.listdir(self.transcripts_dir):
                dir_path = os.path.join(self.transcripts_dir, job_dir)
                if os.path.isdir(dir_path):
                    mtime = datetime.fromtimestamp(os.path.getmtime(dir_path))
                    if mtime < cutoff_time:
                        shutil.rmtree(dir_path)
                        deleted_count += 1
                        logger.info(f"Deleted old transcript: {job_dir}")
            
            # Clean temp files
            for temp_file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, temp_file)
                if os.path.isfile(file_path):
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mtime < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
            
            logger.info(f"Cleanup completed. Deleted {deleted_count} items.")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return deleted_count
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        def get_dir_size(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total += os.path.getsize(filepath)
            return total
        
        try:
            uploads_size = get_dir_size(self.uploads_dir)
            transcripts_size = get_dir_size(self.transcripts_dir)
            temp_size = get_dir_size(self.temp_dir)
            
            # Count files
            uploads_count = sum(1 for _ in Path(self.uploads_dir).rglob('*') if _.is_file())
            transcripts_count = sum(1 for _ in Path(self.transcripts_dir).rglob('*') if _.is_file())
            temp_count = sum(1 for _ in Path(self.temp_dir).rglob('*') if _.is_file())
            
            return {
                "uploads": {
                    "size_bytes": uploads_size,
                    "size_mb": uploads_size / (1024 * 1024),
                    "file_count": uploads_count
                },
                "transcripts": {
                    "size_bytes": transcripts_size,
                    "size_mb": transcripts_size / (1024 * 1024),
                    "file_count": transcripts_count
                },
                "temp": {
                    "size_bytes": temp_size,
                    "size_mb": temp_size / (1024 * 1024),
                    "file_count": temp_count
                },
                "total": {
                    "size_bytes": uploads_size + transcripts_size + temp_size,
                    "size_mb": (uploads_size + transcripts_size + temp_size) / (1024 * 1024),
                    "file_count": uploads_count + transcripts_count + temp_count
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {}
    
    async def export_transcript(
        self,
        job_id: str,
        format: str = "json"
    ) -> Optional[str]:
        """
        Export transcript in various formats
        
        Args:
            job_id: Job identifier
            format: Export format (json, srt, txt, vtt)
            
        Returns:
            Exported content as string
        """
        transcript = await self.load_transcript(job_id)
        if not transcript:
            return None
        
        if format == "json":
            return json.dumps(transcript, ensure_ascii=False, indent=2)
        
        elif format == "txt":
            return transcript.get("text", "")
        
        elif format == "srt":
            return self._convert_to_srt(transcript)
        
        elif format == "vtt":
            return self._convert_to_vtt(transcript)
        
        else:
            logger.warning(f"Unsupported export format: {format}")
            return None
    
    def _convert_to_srt(self, transcript: Dict[str, Any]) -> str:
        """Convert transcript to SRT format"""
        segments = transcript.get("segments", [])
        if not segments:
            return ""
        
        srt_lines = []
        for i, segment in enumerate(segments, 1):
            start = self._format_srt_timestamp(segment.get("start", 0))
            end = self._format_srt_timestamp(segment.get("end", 0))
            text = segment.get("text", "").strip()
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(text)
            srt_lines.append("")  # Empty line between segments
        
        return "\n".join(srt_lines)
    
    def _convert_to_vtt(self, transcript: Dict[str, Any]) -> str:
        """Convert transcript to WebVTT format"""
        segments = transcript.get("segments", [])
        if not segments:
            return "WEBVTT\n\n"
        
        vtt_lines = ["WEBVTT", ""]
        
        for segment in segments:
            start = self._format_vtt_timestamp(segment.get("start", 0))
            end = self._format_vtt_timestamp(segment.get("end", 0))
            text = segment.get("text", "").strip()
            
            vtt_lines.append(f"{start} --> {end}")
            vtt_lines.append(text)
            vtt_lines.append("")  # Empty line between segments
        
        return "\n".join(vtt_lines)
    
    def _format_srt_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")
    
    def _format_vtt_timestamp(self, seconds: float) -> str:
        """Format timestamp for WebVTT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"