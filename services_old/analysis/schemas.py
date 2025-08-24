from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CBILLevel(int, Enum):
    SIMPLE_CONFIRMATION = 1
    FACT_RECALL = 2
    CONCEPT_EXPLANATION = 3
    ANALYTICAL_THINKING = 4
    COMPREHENSIVE_UNDERSTANDING = 5
    EVALUATIVE_JUDGMENT = 6
    CREATIVE_APPLICATION = 7

class TextAnalysisRequest(BaseModel):
    """Request model for direct text analysis"""
    text: str = Field(..., description="Text to analyze (Korean teaching transcript)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    subject: Optional[str] = Field(None, description="Subject (국어, 수학, 영어, etc.)")
    grade: Optional[int] = Field(None, description="Grade level")
    teacher_name: Optional[str] = Field(None, description="Teacher name")
    
class TranscriptAnalysisRequest(BaseModel):
    """Request model for analyzing transcription result"""
    transcript_job_id: str = Field(..., description="Transcription job ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    subject: Optional[str] = Field(None, description="Subject")
    grade: Optional[int] = Field(None, description="Grade level")
    
class AnalysisJobResponse(BaseModel):
    """Response model for analysis job creation"""
    job_id: str
    status: AnalysisStatus
    message: str = Field(default="Analysis job created successfully")
    created_at: datetime
    
class AnalysisStatusResponse(BaseModel):
    """Response model for job status check"""
    job_id: str
    status: AnalysisStatus
    progress: Optional[int] = Field(None, description="Progress percentage")
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
class UtteranceAnalysisResult(BaseModel):
    """Individual utterance analysis result"""
    utterance_number: int
    text: str
    speaker: Optional[str] = None
    cbil_level: int
    cbil_level_name: str
    confidence: float
    reasoning: str
    keywords: Optional[List[str]] = None
    
class CBILDistribution(BaseModel):
    """CBIL level distribution statistics"""
    level_1: int = Field(description="단순 확인 count")
    level_2: int = Field(description="사실 회상 count")
    level_3: int = Field(description="개념 설명 count")
    level_4: int = Field(description="분석적 사고 count")
    level_5: int = Field(description="종합적 이해 count")
    level_6: int = Field(description="평가적 판단 count")
    level_7: int = Field(description="창의적 적용 count")
    
class AnalysisResultResponse(BaseModel):
    """Response model for completed analysis"""
    job_id: str
    status: AnalysisStatus
    total_utterances: int
    average_cbil_level: float
    cbil_distribution: CBILDistribution
    utterances: List[UtteranceAnalysisResult]
    statistics: Dict[str, Any]
    processing_time: float
    report_available: bool = False
    
class ReportResponse(BaseModel):
    """Response model for report generation"""
    job_id: str
    report_url: str
    filename: str
    generated_at: datetime
    
class StatisticsResponse(BaseModel):
    """Response model for statistics dashboard"""
    total_analyses: int
    total_utterances: int
    average_cbil_by_subject: Dict[str, float]
    recent_trends: Dict[str, Any]
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    service: str = "Analysis Service"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.now)
    
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int

# CBIL Level descriptions in Korean
CBIL_DESCRIPTIONS = {
    1: "단순 확인 - 예/아니오, 단답형 응답 요구",
    2: "사실 회상 - 배운 내용을 기억하여 답하기",
    3: "개념 설명 - 개념이나 원리를 설명하기",
    4: "분석적 사고 - 비교, 분류, 관계 파악하기",
    5: "종합적 이해 - 여러 개념을 통합하여 이해하기",
    6: "평가적 판단 - 비판적 사고로 평가하기",
    7: "창의적 적용 - 새로운 상황에 창의적으로 적용하기"
}