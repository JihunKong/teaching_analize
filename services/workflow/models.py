"""
Data models for AIBOA Workflow Service
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


class WorkflowStatus(Enum):
    """Workflow status enumeration"""
    INITIATED = "initiated"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SourceType(Enum):
    """Source type enumeration"""
    YOUTUBE = "youtube"
    UPLOAD = "upload"


@dataclass
class TranscriptionResult:
    """Transcription result data"""
    job_id: str
    text: str
    language: str
    duration_seconds: Optional[int] = None
    word_count: Optional[int] = None
    confidence_score: Optional[float] = None
    segments: Optional[list] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """Analysis result data"""
    analysis_id: str
    framework: str
    overall_score: Optional[float] = None
    primary_level: Optional[str] = None
    detailed_results: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    processing_time_seconds: Optional[float] = None
    word_count: Optional[int] = None
    sentence_count: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowSession:
    """Main workflow session model"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 0
    session_name: Optional[str] = None
    status: WorkflowStatus = WorkflowStatus.INITIATED
    source_type: Optional[SourceType] = None
    
    # Progress tracking
    progress_percentage: int = 0
    transcription_progress: int = 0
    analysis_progress: int = 0
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    
    # Input data
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    language: str = "ko"
    analysis_framework: str = "cbil"
    
    # Results
    transcription_result: Optional[TranscriptionResult] = None
    analysis_result: Optional[AnalysisResult] = None
    
    # Error handling
    error_details: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_progress(self, transcription_progress: int = None, analysis_progress: int = None):
        """Update progress percentages"""
        if transcription_progress is not None:
            self.transcription_progress = max(0, min(100, transcription_progress))
        
        if analysis_progress is not None:
            self.analysis_progress = max(0, min(100, analysis_progress))
        
        # Calculate overall progress
        # Transcription: 60% of total, Analysis: 40% of total
        self.progress_percentage = int(
            (self.transcription_progress * 0.6) + (self.analysis_progress * 0.4)
        )
    
    def set_status(self, status: WorkflowStatus):
        """Set workflow status with automatic timestamp updates"""
        self.status = status
        
        if status == WorkflowStatus.TRANSCRIBING and not self.started_at:
            self.started_at = datetime.now()
        elif status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            self.completed_at = datetime.now()
    
    def add_error(self, error_message: str):
        """Add error details and increment retry count"""
        self.error_details = error_message
        self.retry_count += 1
        
        if self.retry_count >= self.max_retries:
            self.set_status(WorkflowStatus.FAILED)
    
    def can_retry(self) -> bool:
        """Check if workflow can be retried"""
        return (
            self.status == WorkflowStatus.FAILED and 
            self.retry_count < self.max_retries
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_name": self.session_name,
            "status": self.status.value,
            "source_type": self.source_type.value if self.source_type else None,
            "progress_percentage": self.progress_percentage,
            "transcription_progress": self.transcription_progress,
            "analysis_progress": self.analysis_progress,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_completion_time": self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
            "source_url": self.source_url,
            "language": self.language,
            "analysis_framework": self.analysis_framework,
            "transcription_result": self.transcription_result.__dict__ if self.transcription_result else None,
            "analysis_result": self.analysis_result.__dict__ if self.analysis_result else None,
            "error_details": self.error_details,
            "retry_count": self.retry_count,
            "metadata": self.metadata
        }


@dataclass
class ProgressUpdate:
    """Progress update for real-time communication"""
    workflow_id: str
    status: WorkflowStatus
    progress_percentage: int
    transcription_progress: int
    analysis_progress: int
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for WebSocket messages"""
        return {
            "type": "progress_update",
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "progress_percentage": self.progress_percentage,
            "transcription_progress": self.transcription_progress,
            "analysis_progress": self.analysis_progress,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details
        }


@dataclass
class WorkflowMetrics:
    """Workflow performance metrics"""
    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    average_duration_minutes: float = 0.0
    average_transcription_time: float = 0.0
    average_analysis_time: float = 0.0
    success_rate: float = 0.0
    
    def calculate_success_rate(self):
        """Calculate success rate percentage"""
        if self.total_workflows > 0:
            self.success_rate = (self.completed_workflows / self.total_workflows) * 100
        else:
            self.success_rate = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_workflows": self.total_workflows,
            "completed_workflows": self.completed_workflows,
            "failed_workflows": self.failed_workflows,
            "average_duration_minutes": round(self.average_duration_minutes, 2),
            "average_transcription_time": round(self.average_transcription_time, 2),
            "average_analysis_time": round(self.average_analysis_time, 2),
            "success_rate": round(self.success_rate, 2)
        }