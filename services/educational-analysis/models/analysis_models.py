#!/usr/bin/env python3
"""
Educational Analysis Data Models
Pydantic models for the 3 types of educational analysis
"""

from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AnalysisType(str, Enum):
    TEACHING_COACH = "teaching_coach"
    DIALOGUE_PATTERNS = "dialogue_patterns"
    CBIL_EVALUATION = "cbil_evaluation"
    COMPREHENSIVE = "comprehensive"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# ============= BASE MODELS =============

class AnalysisRequest(BaseModel):
    """Base analysis request model"""
    transcript: str = Field(..., min_length=10, description="Classroom transcript text")
    lesson_plan: Optional[str] = Field(None, description="Lesson plan (optional)")
    analysis_type: AnalysisType
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AnalysisResponse(BaseModel):
    """Base analysis response model"""
    analysis_id: str
    analysis_type: AnalysisType
    status: AnalysisStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# ============= TEACHING COACH MODELS =============

class TeachingCoachItem(BaseModel):
    """Individual teaching analysis item (1 of 15)"""
    item_number: int = Field(..., ge=1, le=15)
    title: str
    content: str = Field(..., min_length=270, max_length=350)
    assessment: str  # 일치도 판단
    evidence: List[str]  # 실제 발화/행동 근거

class TeachingCoachAnalysis(BaseModel):
    """15-item teaching coach analysis results"""
    mode: str = Field(..., description="비교모드 or 실행모드")
    items: List[TeachingCoachItem] = Field(..., min_items=15, max_items=15)
    overall_summary: str
    strengths: List[str]
    improvement_areas: List[str]

# ============= DIALOGUE PATTERNS MODELS =============

class FrequencyScale(BaseModel):
    """7-level frequency scale conversion"""
    count: int = Field(..., ge=0)
    scale: int = Field(..., ge=0, le=6)
    description: str  # "매우 가끔 (1~2회)" etc.

class QuestionTypeAnalysis(BaseModel):
    """Question type frequency analysis"""
    factual: FrequencyScale
    interpretive: FrequencyScale
    evaluative: FrequencyScale

class FollowupQuestionAnalysis(BaseModel):
    """Follow-up question type analysis"""
    clarification: FrequencyScale  # 명료화
    focusing: FrequencyScale       # 초점화
    elaboration: FrequencyScale    # 정교화
    expansion: FrequencyScale      # 확장화
    verification: FrequencyScale   # 입증화

class DialogueTypeAnalysis(BaseModel):
    """Classroom dialogue type analysis"""
    adding: FrequencyScale      # 추가하기
    participating: FrequencyScale  # 참여하기
    responding: FrequencyScale     # 반응하기
    reserving: FrequencyScale      # 유보하기
    accepting: FrequencyScale      # 수용하기
    opposing: FrequencyScale       # 반대하기
    transforming: FrequencyScale   # 변환하기

class DialoguePatternsAnalysis(BaseModel):
    """Complete dialogue patterns analysis"""
    question_types: QuestionTypeAnalysis
    followup_questions: FollowupQuestionAnalysis
    dialogue_types: DialogueTypeAnalysis
    chart_urls: List[str]  # Generated visualization URLs
    summary_text: str
    dominant_patterns: List[str]

# ============= CBIL EVALUATION MODELS =============

class CBILStepScore(BaseModel):
    """Individual CBIL step evaluation"""
    step_name: str
    step_number: int = Field(..., ge=1, le=7)
    score: int = Field(..., ge=0, le=3)
    description: str
    evidence: List[str]
    is_concept_centered: bool
    alternative_suggestion: Optional[str] = None

class CBILEvaluationAnalysis(BaseModel):
    """7-step CBIL evaluation results"""
    steps: List[CBILStepScore] = Field(..., min_items=7, max_items=7)
    total_score: int = Field(..., ge=0, le=21)
    average_score: float
    radar_chart_url: str
    overall_assessment: str
    concept_centered_percentage: float
    improvement_recommendations: List[str]

# ============= COMPREHENSIVE ANALYSIS =============

class ComprehensiveAnalysis(BaseModel):
    """All 3 analyses combined"""
    teaching_coach: TeachingCoachAnalysis
    dialogue_patterns: DialoguePatternsAnalysis
    cbil_evaluation: CBILEvaluationAnalysis
    executive_summary: str
    key_insights: List[str]
    priority_recommendations: List[str]

# ============= UTILITY MODELS =============

class VisualizationRequest(BaseModel):
    """Chart generation request"""
    chart_type: str  # "bar", "radar", "line", etc.
    data: Dict[str, Any]
    title: str
    labels: List[str]
    korean_font: bool = True

class ProcessingProgress(BaseModel):
    """Analysis processing progress"""
    analysis_id: str
    progress_percentage: int = Field(..., ge=0, le=100)
    current_step: str
    estimated_completion: Optional[datetime] = None
    
class ErrorDetail(BaseModel):
    """Detailed error information"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime