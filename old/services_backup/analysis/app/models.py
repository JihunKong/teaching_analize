from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CBILLevel(int, Enum):
    SIMPLE_CONFIRMATION = 1
    FACT_RECALL = 2
    CONCEPT_EXPLANATION = 3
    ANALYTICAL_THINKING = 4
    COMPREHENSIVE_UNDERSTANDING = 5
    EVALUATIVE_JUDGMENT = 6
    CREATIVE_APPLICATION = 7

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportFormat(str, Enum):
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    DOCX = "docx"

class HealthCheck(BaseModel):
    status: str
    service: str
    timestamp: str

class AnalysisRequest(BaseModel):
    text: str = Field(..., description="Text to analyze")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    language: str = Field(default="ko", description="Language of the text")
    context_window: int = Field(default=3, description="Number of utterances for context")
    detailed_analysis: bool = Field(default=True, description="Include detailed analysis")

class TranscriptAnalysisRequest(BaseModel):
    transcript_id: str = Field(..., description="Transcript ID from transcription service")
    transcription_service_url: Optional[str] = Field(
        default=None,
        description="URL of transcription service if not using default"
    )
    context_window: int = Field(default=3, description="Number of utterances for context")
    detailed_analysis: bool = Field(default=True, description="Include detailed analysis")

class Utterance(BaseModel):
    id: int
    speaker: Optional[str] = None
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
class CBILAnalysis(BaseModel):
    utterance_id: int
    text: str
    cbil_level: CBILLevel
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    keywords: List[str]
    context_considered: bool = False
    
class AnalysisResult(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    utterance_count: int
    analyses: List[CBILAnalysis]
    statistics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    
class Statistics(BaseModel):
    average_level: float
    median_level: float
    mode_level: int
    level_distribution: Dict[int, int]
    high_level_ratio: float  # Ratio of levels 5-7
    low_level_ratio: float   # Ratio of levels 1-3
    improvement_trend: Optional[str] = None  # "improving", "declining", "stable"
    key_moments: List[Dict[str, Any]]
    total_utterances: int
    analyzed_utterances: int
    
class Report(BaseModel):
    report_id: str
    analysis_id: str
    format: ReportFormat
    created_at: datetime
    file_path: Optional[str] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    
class ReportRequest(BaseModel):
    analysis_id: str
    format: ReportFormat = Field(default=ReportFormat.PDF)
    include_charts: bool = Field(default=True)
    include_recommendations: bool = Field(default=True)
    language: str = Field(default="ko")
    
class BatchAnalysisRequest(BaseModel):
    texts: List[str]
    batch_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
class BatchAnalysisResult(BaseModel):
    batch_id: str
    total_items: int
    completed_items: int
    failed_items: int
    results: List[AnalysisResult]
    
class ErrorResponse(BaseModel):
    detail: str
    message: Optional[str] = None
    error_code: Optional[str] = None
    
class CBILPromptTemplate(BaseModel):
    system_prompt: str
    user_prompt_template: str
    few_shot_examples: List[Dict[str, Any]]
    
class KeyMoment(BaseModel):
    utterance_id: int
    timestamp: Optional[float] = None
    type: str  # "level_jump", "sustained_high", "breakthrough", etc.
    description: str
    importance: float = Field(ge=0.0, le=1.0)
    
class TeachingPattern(BaseModel):
    pattern_type: str  # "questioning", "explaining", "facilitating", etc.
    frequency: int
    average_cbil_level: float
    effectiveness_score: float = Field(ge=0.0, le=1.0)
    
class AnalysisSummary(BaseModel):
    analysis_id: str
    total_time: float  # in seconds
    utterance_count: int
    average_cbil: float
    highest_level_achieved: int
    teaching_patterns: List[TeachingPattern]
    key_moments: List[KeyMoment]
    recommendations: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]