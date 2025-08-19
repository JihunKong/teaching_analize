from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
import uuid

app = FastAPI(
    title="AIBOA Analysis Service",
    description="CBIL Teaching Analysis Service",
    version="1.0.0-PRODUCTION"
)

# CBIL 7-level classification
CBIL_LEVELS = {
    1: {"name": "단순 확인", "description": "Simple confirmation", "weight": 0.1},
    2: {"name": "사실 회상", "description": "Fact recall", "weight": 0.2},
    3: {"name": "개념 설명", "description": "Concept explanation", "weight": 0.3},
    4: {"name": "분석적 사고", "description": "Analytical thinking", "weight": 0.5},
    5: {"name": "종합적 이해", "description": "Comprehensive understanding", "weight": 0.7},
    6: {"name": "평가적 판단", "description": "Evaluative judgment", "weight": 0.85},
    7: {"name": "창의적 적용", "description": "Creative application", "weight": 1.0}
}

# In-memory storage for MVP
analysis_results = {}

class AnalysisRequest(BaseModel):
    text: str
    metadata: Dict = {}

class AnalysisResult(BaseModel):
    id: str
    text: str
    cbil_scores: Dict[int, float]
    overall_score: float
    recommendations: List[str]
    created_at: datetime

def verify_api_key(x_api_key: str = Header(None)):
    """Strong API key verification - only allows internal service keys"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Only allow specific internal service API keys
    valid_keys = [
        "analysis-api-key-prod-2025",  # Workflow service key
        "internal-service-key-2025"    # Internal service key
    ]
    
    if x_api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True

@app.get("/")
async def root():
    return {
        "service": "AIBOA Analysis Service",
        "status": "running",
        "version": "1.0.0-PRODUCTION",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/health",
            "/api/analyze/text",
            "/api/analyze/transcript",
            "/api/analysis/{id}",
            "/api/statistics"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze/text")
async def analyze_text(request: AnalysisRequest, x_api_key: str = Header(None)):
    """Analyze text for CBIL classification"""
    verify_api_key(x_api_key)
    
    # Simulate CBIL analysis
    analysis_id = str(uuid.uuid4())
    
    # Mock CBIL scoring (in production, would use Solar LLM)
    cbil_scores = {
        1: 0.15,  # 단순 확인
        2: 0.25,  # 사실 회상
        3: 0.30,  # 개념 설명
        4: 0.20,  # 분석적 사고
        5: 0.08,  # 종합적 이해
        6: 0.02,  # 평가적 판단
        7: 0.00   # 창의적 적용
    }
    
    # Calculate overall score
    overall_score = sum(level * score for level, score in cbil_scores.items()) / sum(cbil_scores.values())
    
    # Generate recommendations
    recommendations = []
    if cbil_scores[7] < 0.1:
        recommendations.append("창의적 적용 질문을 더 추가하세요")
    if cbil_scores[6] < 0.1:
        recommendations.append("평가적 판단을 요구하는 질문을 포함하세요")
    if cbil_scores[1] + cbil_scores[2] > 0.5:
        recommendations.append("고차원적 사고를 요구하는 질문 비중을 늘리세요")
    
    result = AnalysisResult(
        id=analysis_id,
        text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
        cbil_scores=cbil_scores,
        overall_score=overall_score,
        recommendations=recommendations,
        created_at=datetime.now()
    )
    
    analysis_results[analysis_id] = result
    
    return {
        "analysis_id": analysis_id,
        "cbil_scores": cbil_scores,
        "overall_score": round(overall_score, 2),
        "recommendations": recommendations,
        "cbil_level_distribution": {
            "low_level": round(cbil_scores[1] + cbil_scores[2] + cbil_scores[3], 2),
            "mid_level": round(cbil_scores[4] + cbil_scores[5], 2),
            "high_level": round(cbil_scores[6] + cbil_scores[7], 2)
        }
    }

@app.post("/api/analyze/transcript")
async def analyze_transcript(transcript_id: str, x_api_key: str = Header(None)):
    """Analyze transcription result"""
    verify_api_key(x_api_key)
    
    # In production, would fetch transcript from Transcription Service
    return {
        "message": "Transcript analysis endpoint",
        "transcript_id": transcript_id,
        "status": "Feature coming soon"
    }

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str, x_api_key: str = Header(None)):
    """Get analysis result by ID"""
    verify_api_key(x_api_key)
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[analysis_id]
    return {
        "id": result.id,
        "text": result.text,
        "cbil_scores": result.cbil_scores,
        "overall_score": result.overall_score,
        "recommendations": result.recommendations,
        "created_at": result.created_at.isoformat()
    }

@app.get("/api/statistics")
async def get_statistics(x_api_key: str = Header(None)):
    """Get analysis statistics"""
    verify_api_key(x_api_key)
    
    total_analyses = len(analysis_results)
    
    if total_analyses == 0:
        return {
            "total_analyses": 0,
            "message": "No analyses performed yet"
        }
    
    # Calculate average scores
    all_scores = [r.overall_score for r in analysis_results.values()]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    return {
        "total_analyses": total_analyses,
        "average_cbil_score": round(avg_score, 2),
        "analyses_today": total_analyses,  # Simplified for MVP
        "cbil_levels": CBIL_LEVELS
    }