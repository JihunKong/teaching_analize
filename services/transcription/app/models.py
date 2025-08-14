from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionMethod(str, Enum):
    WHISPER = "whisper"
    YOUTUBE_CAPTIONS = "youtube_captions"
    LOCAL_WHISPER = "local_whisper"

class OutputFormat(str, Enum):
    JSON = "json"
    SRT = "srt"
    TXT = "txt"
    VTT = "vtt"

class HealthCheck(BaseModel):
    status: str
    service: str
    timestamp: str

class TranscriptionRequest(BaseModel):
    language: str = Field(default="ko", description="Language code for transcription")
    method: TranscriptionMethod = Field(default=TranscriptionMethod.WHISPER)
    include_timestamps: bool = Field(default=True)
    speaker_diarization: bool = Field(default=False)
    
class YouTubeTranscriptionRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")
    language: str = Field(default="ko")
    prefer_captions: bool = Field(default=True, description="Prefer YouTube captions if available")

class TranscriptionJob(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None
    language: str
    method: TranscriptionMethod
    error_message: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)

class TranscriptionResult(BaseModel):
    job_id: str
    text: str
    segments: Optional[List[Dict[str, Any]]] = None
    language: str
    duration: float
    confidence: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None
    speakers: Optional[List[Dict[str, Any]]] = None

class TranscriptionExport(BaseModel):
    job_id: str
    format: OutputFormat
    content: str
    metadata: Dict[str, Any]

class JobListResponse(BaseModel):
    jobs: List[TranscriptionJob]
    total: int
    page: int
    page_size: int

class ErrorResponse(BaseModel):
    detail: str
    message: Optional[str] = None
    error_code: Optional[str] = None