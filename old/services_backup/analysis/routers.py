from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import os
import sys
import logging
import asyncio
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config import settings

# Import real implementation modules
try:
    from .llm_client import SolarLLMClient
    from .cbil_analyzer import CBILAnalyzer
except ImportError:
    # Fallback if modules not found
    SolarLLMClient = None
    CBILAnalyzer = None

router = APIRouter(prefix="/api/analyze", tags=["analysis"])
logger = logging.getLogger(__name__)

# Initialize clients
solar_client = None
cbil_analyzer = None

if (settings.SOLAR_API_KEY or settings.UPSTAGE_API_KEY) and SolarLLMClient:
    solar_client = SolarLLMClient()
    logger.info("SolarLLMClient initialized")
else:
    logger.warning("SolarLLMClient not initialized - using mock mode")

if CBILAnalyzer:
    cbil_analyzer = CBILAnalyzer()
    logger.info("CBILAnalyzer initialized")

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
    enhanced: bool = False
    segments: Optional[List[Dict]] = None

def verify_api_key(x_api_key: str = Header(None)):
    """Simple API key verification"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    return True

@router.post("/text")
async def analyze_text(request: AnalysisRequest, x_api_key: str = Header(None)):
    """Analyze text for CBIL classification"""
    verify_api_key(x_api_key)
    
    analysis_id = str(uuid.uuid4())
    
    try:
        if cbil_analyzer and solar_client:
            # Real CBIL analysis
            logger.info(f"Starting real CBIL analysis for {analysis_id}")
            
            # Perform rule-based analysis first
            base_analysis = cbil_analyzer.analyze_utterance(request.text, request.metadata)
            
            # Initialize cbil_scores
            cbil_level = base_analysis.get("cbil_level", 3)
            confidence = base_analysis.get("confidence", 0.5)
            
            # Create score distribution based on analyzed level
            cbil_scores = {i: 0.0 for i in range(1, 8)}
            cbil_scores[cbil_level] = confidence
            # Add some distribution to neighboring levels
            if cbil_level > 1:
                cbil_scores[cbil_level - 1] = (1 - confidence) * 0.3
            if cbil_level < 7:
                cbil_scores[cbil_level + 1] = (1 - confidence) * 0.3
            
            # Enhance with LLM if available
            try:
                llm_result = await solar_client.analyze_cbil(request.text, request.metadata)
                
                # Merge results
                if llm_result.get("enhanced"):
                    cbil_scores = llm_result.get("cbil_scores", cbil_scores)
                    enhanced = True
                else:
                    enhanced = False
                    
            except Exception as e:
                logger.error(f"LLM enhancement failed: {str(e)}")
                enhanced = False
            
            # Generate recommendations based on analysis
            recommendations = []
            if cbil_scores.get(7, 0) < 0.1:
                recommendations.append("창의적 적용 질문을 더 추가하세요")
            if cbil_scores.get(6, 0) < 0.1:
                recommendations.append("평가적 판단을 요구하는 질문을 포함하세요")
            if cbil_scores.get(1, 0) + cbil_scores.get(2, 0) > 0.5:
                recommendations.append("고차원적 사고를 요구하는 질문 비중을 늘리세요")
            
            # Calculate overall score
            total_weight = sum(cbil_scores.values())
            if total_weight > 0:
                overall_score = sum(level * score for level, score in cbil_scores.items()) / total_weight
            else:
                overall_score = 3.0
            
        else:
            # Mock analysis
            logger.info(f"Using mock CBIL analysis for {analysis_id}")
            
            cbil_scores = {
                1: 0.15,  # 단순 확인
                2: 0.25,  # 사실 회상
                3: 0.30,  # 개념 설명
                4: 0.20,  # 분석적 사고
                5: 0.08,  # 종합적 이해
                6: 0.02,  # 평가적 판단
                7: 0.00   # 창의적 적용
            }
            
            overall_score = sum(level * score for level, score in cbil_scores.items()) / sum(cbil_scores.values())
            
            recommendations = [
                "API 키 설정 후 실제 AI 분석이 가능합니다",
                "SOLAR_API_KEY 또는 UPSTAGE_API_KEY를 Railway에 설정하세요",
                "실제 분석시 더 정확한 CBIL 레벨 판단이 가능합니다"
            ]
            
            enhanced = False
        
        # Store result
        result = AnalysisResult(
            id=analysis_id,
            text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
            cbil_scores=cbil_scores,
            overall_score=overall_score,
            recommendations=recommendations,
            created_at=datetime.now(),
            enhanced=enhanced
        )
        
        analysis_results[analysis_id] = result
        
        return {
            "analysis_id": analysis_id,
            "cbil_scores": cbil_scores,
            "overall_score": round(overall_score, 2),
            "recommendations": recommendations,
            "cbil_level_distribution": {
                "low_level": round(cbil_scores.get(1, 0) + cbil_scores.get(2, 0) + cbil_scores.get(3, 0), 2),
                "mid_level": round(cbil_scores.get(4, 0) + cbil_scores.get(5, 0), 2),
                "high_level": round(cbil_scores.get(6, 0) + cbil_scores.get(7, 0), 2)
            },
            "enhanced": enhanced,
            "message": "LLM 기반 분석 완료" if enhanced else "규칙 기반 분석 완료"
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/transcript")
async def analyze_transcript(transcript_data: Dict, x_api_key: str = Header(None)):
    """Analyze transcription result"""
    verify_api_key(x_api_key)
    
    # Extract text from transcript
    if "text" in transcript_data:
        text = transcript_data["text"]
    elif "segments" in transcript_data:
        text = " ".join(seg.get("text", "") for seg in transcript_data["segments"])
    else:
        raise HTTPException(status_code=400, detail="No text found in transcript")
    
    # Analyze the transcript text
    request = AnalysisRequest(text=text, metadata=transcript_data.get("metadata", {}))
    return await analyze_text(request, x_api_key)

@router.get("/results/{analysis_id}")
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
        "created_at": result.created_at.isoformat(),
        "enhanced": result.enhanced
    }

@router.get("/statistics")
async def get_statistics(x_api_key: str = Header(None)):
    """Get analysis statistics"""
    verify_api_key(x_api_key)
    
    total_analyses = len(analysis_results)
    
    if total_analyses == 0:
        return {
            "total_analyses": 0,
            "message": "No analyses performed yet",
            "cbil_levels": settings.CBIL_LEVELS
        }
    
    # Calculate average scores
    all_scores = [r.overall_score for r in analysis_results.values()]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    # Count enhanced analyses
    enhanced_count = sum(1 for r in analysis_results.values() if r.enhanced)
    
    return {
        "total_analyses": total_analyses,
        "average_cbil_score": round(avg_score, 2),
        "analyses_today": total_analyses,  # Simplified for MVP
        "enhanced_analyses": enhanced_count,
        "mock_analyses": total_analyses - enhanced_count,
        "cbil_levels": settings.CBIL_LEVELS
    }

@router.post("/batch")
async def analyze_batch(texts: List[str], x_api_key: str = Header(None)):
    """Analyze multiple texts in batch"""
    verify_api_key(x_api_key)
    
    results = []
    for text in texts[:10]:  # Limit to 10 for safety
        request = AnalysisRequest(text=text)
        result = await analyze_text(request, x_api_key)
        results.append(result)
        await asyncio.sleep(0.1)  # Rate limiting
    
    return {
        "batch_size": len(results),
        "results": results
    }