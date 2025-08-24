from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ExportFormat(str, Enum):
    JSON = "json"
    SRT = "srt"
    TXT = "txt"

class TranscriptionRequest(BaseModel):
    """Request model for file transcription"""
    language: str = Field(default="ko", description="Language code (ko, en, ja, etc.)")
    model: str = Field(default="whisper-1", description="Whisper model to use")
    prompt: Optional[str] = Field(None, description="Optional prompt to guide transcription")
    temperature: float = Field(default=0.0, description="Sampling temperature")
    
class YouTubeTranscriptionRequest(BaseModel):
    """Request model for YouTube transcription"""
    url: HttpUrl = Field(..., description="YouTube video URL")
    language: str = Field(default="ko", description="Language code")
    use_captions: bool = Field(default=False, description="Try to use YouTube captions first")
    
class TranscriptionJobResponse(BaseModel):
    """Response model for transcription job"""
    job_id: str
    status: JobStatus
    message: str = Field(default="Job created successfully")
    created_at: datetime
    
class TranscriptionStatusResponse(BaseModel):
    """Response model for job status check"""
    job_id: str
    status: JobStatus
    progress: Optional[int] = Field(None, description="Progress percentage")
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
class TranscriptionResultResponse(BaseModel):
    """Response model for completed transcription"""
    job_id: str
    status: JobStatus
    text: str
    language: str
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    word_count: int
    processing_time: float
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="Timestamped segments")
    
class TranscriptionExportResponse(BaseModel):
    """Response model for export"""
    job_id: str
    format: ExportFormat
    content: str
    filename: str
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "Transcription Service"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int