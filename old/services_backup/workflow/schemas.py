"""
Pydantic schemas for AIBOA Workflow Service
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


# ============================================
# Base Schemas
# ============================================

class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Error response schema"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# ============================================
# Workflow Request Schemas
# ============================================

class WorkflowCreateRequest(BaseModel):
    """Request schema for creating a new workflow"""
    # Source configuration
    source_type: str = Field(..., regex="^(youtube|upload)$")
    source_url: Optional[HttpUrl] = None  # For YouTube
    file_data: Optional[str] = None  # Base64 encoded file data for upload
    filename: Optional[str] = None  # Original filename for upload
    
    # Processing configuration
    language: str = Field(default="ko", regex="^(ko|en|auto)$")
    analysis_framework: str = Field(default="cbil")
    
    # Optional metadata
    session_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('source_url')
    def validate_youtube_url(cls, v, values):
        """Validate YouTube URL if source_type is youtube"""
        if values.get('source_type') == 'youtube' and not v:
            raise ValueError('source_url is required for YouTube workflows')
        return v
    
    @validator('file_data')
    def validate_file_data(cls, v, values):
        """Validate file data if source_type is upload"""
        if values.get('source_type') == 'upload' and not v:
            raise ValueError('file_data is required for upload workflows')
        return v


# ============================================
# Workflow Response Schemas
# ============================================

class TranscriptionResultSchema(BaseModel):
    """Schema for transcription results"""
    job_id: str
    text: str
    language: str
    duration_seconds: Optional[int] = None
    word_count: Optional[int] = None
    confidence_score: Optional[float] = None
    segments: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalysisResultSchema(BaseModel):
    """Schema for analysis results"""
    analysis_id: str
    framework: str
    overall_score: Optional[float] = None
    primary_level: Optional[str] = None
    detailed_results: Dict[str, Any] = Field(default_factory=dict)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    processing_time_seconds: Optional[float] = None
    word_count: Optional[int] = None
    sentence_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseResponse):
    """Response schema for workflow creation"""
    workflow_id: str
    status: str
    progress_percentage: int = 0
    websocket_url: str
    estimated_completion_time: Optional[datetime] = None


class WorkflowStatusResponse(BaseResponse):
    """Response schema for workflow status"""
    workflow_id: str
    status: str
    progress_percentage: int
    transcription_progress: int
    analysis_progress: int
    
    # Timing information
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    
    # Results (only included when available)
    transcription_result: Optional[TranscriptionResultSchema] = None
    analysis_result: Optional[AnalysisResultSchema] = None
    
    # Error information
    error_details: Optional[str] = None


class WorkflowListResponse(BaseResponse):
    """Response schema for workflow list"""
    workflows: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int


# ============================================
# Progress Update Schemas
# ============================================

class ProgressUpdate(BaseModel):
    """Schema for progress updates"""
    type: str = "progress_update"
    workflow_id: str
    status: str
    progress_percentage: int
    transcription_progress: int
    analysis_progress: int
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Dict[str, Any] = Field(default_factory=dict)


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    type: str
    workflow_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)


# ============================================
# Export Schemas
# ============================================

class ExportRequest(BaseModel):
    """Request schema for exporting workflow results"""
    format: str = Field(..., regex="^(json|pdf|txt|docx)$")
    include_transcription: bool = True
    include_analysis: bool = True
    include_metadata: bool = False


class ExportResponse(BaseResponse):
    """Response schema for export operations"""
    download_url: str
    format: str
    file_size: int
    expires_at: datetime


# ============================================
# Analytics Schemas
# ============================================

class WorkflowMetricsSchema(BaseModel):
    """Schema for workflow metrics"""
    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    average_duration_minutes: float = 0.0
    average_transcription_time: float = 0.0
    average_analysis_time: float = 0.0
    success_rate: float = 0.0


class UserActivitySummary(BaseModel):
    """Schema for user activity summary"""
    user_id: int
    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    total_transcription_time: float = 0.0
    total_analysis_time: float = 0.0
    average_score: Optional[float] = None
    last_activity: Optional[datetime] = None
    favorite_language: Optional[str] = None


class SystemHealthSchema(BaseModel):
    """Schema for system health information"""
    service_status: str
    active_workflows: int
    queue_size: int
    avg_response_time: float
    error_rate: float
    last_health_check: datetime
    external_services: Dict[str, str]  # service_name -> status


# ============================================
# Advanced Features Schemas
# ============================================

class WorkflowTemplate(BaseModel):
    """Schema for workflow templates"""
    id: str
    name: str
    description: str
    default_language: str
    default_framework: str
    source_type: str
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_by: int
    is_public: bool = False


class WorkflowSchedule(BaseModel):
    """Schema for scheduled workflows"""
    id: str
    workflow_template_id: str
    user_id: int
    schedule_cron: str  # Cron expression
    is_active: bool = True
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    run_count: int = 0


class BatchWorkflowRequest(BaseModel):
    """Schema for batch workflow processing"""
    workflows: List[WorkflowCreateRequest]
    batch_name: Optional[str] = None
    process_sequentially: bool = False
    notify_on_completion: bool = True


class BatchWorkflowResponse(BaseResponse):
    """Response schema for batch workflow creation"""
    batch_id: str
    workflow_ids: List[str]
    total_workflows: int
    estimated_completion_time: Optional[datetime] = None


# ============================================
# Configuration Schemas
# ============================================

class ServiceConfiguration(BaseModel):
    """Schema for service configuration"""
    max_concurrent_workflows: int
    workflow_timeout_minutes: int
    supported_languages: List[str]
    supported_export_formats: List[str]
    max_file_size_mb: int
    cleanup_after_hours: int


class UserPreferences(BaseModel):
    """Schema for user workflow preferences"""
    default_language: str = "ko"
    default_framework: str = "cbil"
    auto_start_analysis: bool = True
    notification_enabled: bool = True
    preferred_export_format: str = "json"
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


# ============================================
# Validation Helpers
# ============================================

def validate_workflow_source(source_type: str, source_url: Optional[str], file_data: Optional[str]) -> bool:
    """Validate workflow source configuration"""
    if source_type == "youtube":
        return source_url is not None
    elif source_type == "upload":
        return file_data is not None
    return False


def validate_export_format(format: str) -> bool:
    """Validate export format"""
    return format in ["json", "pdf", "txt", "docx"]


def validate_language(language: str) -> bool:
    """Validate language code"""
    return language in ["ko", "en", "auto"]