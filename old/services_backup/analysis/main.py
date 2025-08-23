from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
import uuid
import os
import sys
import re
from services.solar_llm import get_solar_client, CBILAnalysisResult

# PDF 생성기 및 CBIL 분석기 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from reportlab_pdf_generator import EducationReportGenerator
from cbil_analyzer import CBILAnalyzer

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
    """API key verification - disabled for testing"""
    # API key verification disabled for testing
    return True
    
    # Original implementation (commented out for testing)
    # if not x_api_key:
    #     raise HTTPException(status_code=401, detail="API key required")
    # 
    # valid_keys = [
    #     "analysis-api-key-prod-2025",
    #     "internal-service-key-2025"
    # ]
    # 
    # if x_api_key not in valid_keys:
    #     raise HTTPException(status_code=401, detail="Invalid API key")
    # 
    # return True

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
    """Analyze text for CBIL classification using real AI analysis"""
    # Skip API key verification for testing
    # verify_api_key(x_api_key)
    
    analysis_id = str(uuid.uuid4())
    
    try:
        # Get Solar LLM client
        solar_client = get_solar_client()
        
        # Split text into sentences for analysis
        sentences = split_into_sentences(request.text)
        
        if not sentences:
            raise ValueError("No analyzable sentences found in text")
        
        # Perform comprehensive CBIL analysis
        analysis_result = solar_client.get_comprehensive_analysis(
            sentences, 
            context=request.metadata
        )
        
        if "error" in analysis_result:
            raise ValueError(analysis_result["error"])
        
        # Convert to legacy format for compatibility
        cbil_scores = {
            int(k): v/100 for k, v in analysis_result["cbil_distribution"]["percentages"].items()
        }
        
        overall_score = analysis_result["overall_metrics"]["weighted_cbil_score"]
        recommendations = analysis_result["recommendations"]
        
        # Store comprehensive result
        result = AnalysisResult(
            id=analysis_id,
            text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
            cbil_scores=cbil_scores,
            overall_score=overall_score,
            recommendations=recommendations,
            created_at=datetime.now()
        )
        
        # Store full analysis for detailed retrieval
        analysis_results[analysis_id] = {
            "summary": result,
            "full_analysis": analysis_result
        }
        
        return {
            "analysis_id": analysis_id,
            "cbil_scores": cbil_scores,
            "overall_score": round(overall_score, 2),
            "recommendations": recommendations,
            "cbil_level_distribution": analysis_result["level_categories"],
            "total_sentences": analysis_result["total_utterances"],
            "analysis_quality": analysis_result["overall_metrics"]["analysis_quality"],
            "top_keywords": analysis_result["top_keywords"],
            "method": analysis_result["analysis_method"]
        }
        
    except Exception as e:
        # Fallback to rule-based analysis
        print(f"⚠️ AI analysis failed, using fallback: {e}")
        return await analyze_text_fallback(request, analysis_id)
        
def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences for CBIL analysis"""
    # Korean sentence endings
    sentences = re.split(r'[.!?]\s*', text)
    
    # Filter out empty sentences and very short ones
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    
    return sentences

async def analyze_text_fallback(request: AnalysisRequest, analysis_id: str):
    """Fallback analysis using rule-based CBIL analyzer"""
    try:
        analyzer = CBILAnalyzer()
        sentences = split_into_sentences(request.text)
        
        if not sentences:
            sentences = [request.text]  # Use full text as single sentence
        
        results = analyzer.analyze_batch(sentences)
        
        # Calculate distribution
        level_counts = {i: 0 for i in range(1, 8)}
        for result in results:
            level_counts[result["cbil_level"]] += 1
        
        total = len(results)
        cbil_scores = {level: count/total for level, count in level_counts.items()}
        
        # Calculate overall score
        overall_score = sum(level * count for level, count in level_counts.items()) / total
        
        # Generate recommendations
        recommendations = []
        if cbil_scores[7] < 0.1:
            recommendations.append("💡 창의적 적용 질문을 더 추가하세요")
        if cbil_scores[6] < 0.1:
            recommendations.append("🎯 평가적 판단을 요구하는 질문을 포함하세요")
        if cbil_scores[1] + cbil_scores[2] > 0.5:
            recommendations.append("🔍 고차원적 사고를 요구하는 질문 비중을 늘리세요")
        
        if not recommendations:
            recommendations.append("📊 전반적으로 균형잡힌 질문 구성입니다")
        
        result = AnalysisResult(
            id=analysis_id,
            text=request.text[:200] + "..." if len(request.text) > 200 else request.text,
            cbil_scores=cbil_scores,
            overall_score=overall_score,
            recommendations=recommendations,
            created_at=datetime.now()
        )
        
        analysis_results[analysis_id] = {"summary": result}
        
        return {
            "analysis_id": analysis_id,
            "cbil_scores": cbil_scores,
            "overall_score": round(overall_score, 2),
            "recommendations": recommendations,
            "cbil_level_distribution": {
                "low_level": round(cbil_scores[1] + cbil_scores[2] + cbil_scores[3], 2),
                "mid_level": round(cbil_scores[4] + cbil_scores[5], 2),
                "high_level": round(cbil_scores[6] + cbil_scores[7], 2)
            },
            "total_sentences": total,
            "analysis_quality": "good",
            "method": "rule_based_fallback"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze/transcript")
async def analyze_transcript(request: dict, x_api_key: str = Header(None)):
    """Analyze transcription result from YouTube video"""
    # Skip API key verification for testing
    # verify_api_key(x_api_key)
    
    try:
        transcript_text = request.get("text", "")
        transcript_metadata = request.get("metadata", {})
        
        if not transcript_text:
            raise HTTPException(status_code=400, detail="No transcript text provided")
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            text=transcript_text,
            metadata=transcript_metadata
        )
        
        # Use existing text analysis function
        result = await analyze_text(analysis_request)
        
        # Add transcript-specific information
        result["transcript_analysis"] = True
        result["video_info"] = transcript_metadata.get("video_info", {})
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcript analysis failed: {str(e)}")

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str, x_api_key: str = Header(None)):
    """Get analysis result by ID"""
    # Skip API key verification for testing
    # verify_api_key(x_api_key)
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    stored_result = analysis_results[analysis_id]
    
    # Handle both old and new format
    if isinstance(stored_result, dict) and "summary" in stored_result:
        result = stored_result["summary"]
        full_analysis = stored_result.get("full_analysis", {})
        
        response = {
            "id": result.id,
            "text": result.text,
            "cbil_scores": result.cbil_scores,
            "overall_score": result.overall_score,
            "recommendations": result.recommendations,
            "created_at": result.created_at.isoformat()
        }
        
        # Add full analysis details if available
        if full_analysis:
            response.update({
                "detailed_analysis": full_analysis.get("detailed_results", []),
                "top_keywords": full_analysis.get("top_keywords", {}),
                "analysis_method": full_analysis.get("analysis_method", "unknown")
            })
        
        return response
    else:
        # Legacy format
        result = stored_result
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
    # Skip API key verification for testing
    # verify_api_key(x_api_key)
    
    total_analyses = len(analysis_results)
    
    if total_analyses == 0:
        return {
            "total_analyses": 0,
            "message": "No analyses performed yet",
            "service_status": "active",
            "cbil_levels": CBIL_LEVELS
        }
    
    # Calculate average scores from stored results
    all_scores = []
    ai_analyses = 0
    fallback_analyses = 0
    
    for stored_result in analysis_results.values():
        if isinstance(stored_result, dict) and "summary" in stored_result:
            all_scores.append(stored_result["summary"].overall_score)
            if stored_result.get("full_analysis", {}).get("analysis_method") == "solar_llm":
                ai_analyses += 1
            else:
                fallback_analyses += 1
        else:
            all_scores.append(stored_result.overall_score)
            fallback_analyses += 1
    
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    return {
        "total_analyses": total_analyses,
        "average_cbil_score": round(avg_score, 2),
        "analyses_today": total_analyses,
        "analysis_methods": {
            "ai_powered": ai_analyses,
            "rule_based": fallback_analyses
        },
        "service_status": "active",
        "ai_availability": not get_solar_client().use_fallback,
        "cbil_levels": CBIL_LEVELS
    }

@app.get("/api/analysis/{analysis_id}/report")
async def generate_pdf_report(analysis_id: str, x_api_key: str = Header(None)):
    """Generate PDF report for analysis"""
    verify_api_key(x_api_key)
    
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        stored_result = analysis_results[analysis_id]
        
        # Handle both old and new format
        if isinstance(stored_result, dict) and "summary" in stored_result:
            result = stored_result["summary"]
            full_analysis = stored_result.get("full_analysis", {})
        else:
            result = stored_result
            full_analysis = {}
        
        # PDF 생성기 초기화
        pdf_generator = EducationReportGenerator()
        
        # 분석 데이터 준비
        analysis_data = {
            'cbil_scores': {str(k): v for k, v in result.cbil_scores.items()},
            'overall_score': result.overall_score,
            'sentences': full_analysis.get("detailed_results", []) if full_analysis else result.text.split('. ')
        }
        
        # PDF 생성
        pdf_bytes = pdf_generator.generate_pdf_report(
            analysis_data, 
            f"CBIL 분석 결과 - {analysis_id[:8]}"
        )
        
        # PDF 응답 반환
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=aiboa_report_{analysis_id[:8]}.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 생성 실패: {str(e)}")

@app.get("/api/reports/sample")
async def generate_sample_report():
    """Generate sample PDF report for testing"""
    try:
        # PDF 생성기 초기화
        pdf_generator = EducationReportGenerator()
        
        # 샘플 데이터
        sample_data = {
            'cbil_scores': {
                '1': 0.12,  # 단순 확인
                '2': 0.18,  # 사실 회상  
                '3': 0.28,  # 개념 설명
                '4': 0.22,  # 분석적 사고
                '5': 0.12,  # 종합적 이해
                '6': 0.06,  # 평가적 판단
                '7': 0.02   # 창의적 적용
            },
            'overall_score': 3.2,
            'sentences': [
                "오늘은 새로운 개념에 대해 학습하겠습니다.",
                "지난 시간에 배운 내용을 기억하고 계시나요?",
                "이번 단원의 핵심 개념은 무엇일까요?",
                "실생활에서 어떻게 적용될 수 있을지 분석해 보겠습니다.",
                "배운 내용을 종합해서 새로운 문제를 해결해 보겠습니다."
            ] * 5
        }
        
        # PDF 생성
        pdf_bytes = pdf_generator.generate_pdf_report(
            sample_data, 
            "교육 컨설팅 샘플 분석 보고서"
        )
        
        # PDF 응답 반환
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=aiboa_sample_report.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"샘플 PDF 생성 실패: {str(e)}")