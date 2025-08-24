#!/usr/bin/env python3
"""
AIBOA Analysis Service
Multiple framework analysis using Solar2 Pro API
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
import redis
import json
import requests

# Import report generators
from html_report_generator import HTMLReportGenerator
from pdf_report_generator import PDFReportGenerator, is_pdf_generation_available

# Import database
from database import (
    get_db, store_analysis, update_framework_usage, get_research_statistics,
    init_database, AnalysisResultDB
)
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIBOA Analysis Service",
    description="Multiple framework analysis for educational discourse",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

# Solar API configuration
UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY', 'up_kcU1IMWm9wcC1rqplsIFMsEeqlUXN')
SOLAR_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"

class AnalysisRequest(BaseModel):
    text: str
    framework: str = "cbil"  # cbil, student_discussion, lesson_coaching, etc.
    metadata: Optional[Dict[str, Any]] = {}

class AnalysisFramework(BaseModel):
    id: str
    name: str
    description: str
    prompt_template: str

# Analysis Framework Definitions
ANALYSIS_FRAMEWORKS = {
    "cbil": {
        "name": "개념기반 탐구 수업(CBIL) 분석",
        "description": "7단계 CBIL 분석 및 평가",
        "prompt": """**CBIL 7단계 분석 - 점수 출력 필수**

📋 **중요 지시사항**
- 각 단계마다 반드시 "점수: X점" 형식으로 점수를 명시할 것
- 0점(없음), 1점(부족), 2점(보통), 3점(우수) 중 하나로 채점
- 7단계 모두 분석하고 점수 부여 필수

🎯 **분석 목적**
개념기반 탐구학습(CBIL) 7단계 실행 평가 및 점수 부여 (0~3점)

📝 **필수 출력 형식** (정확히 이 형식을 따를 것):

#### 1. Engage (흥미 유도 및 연결)
[수업 장면 분석 내용...]
**점수: X점**

#### 2. Focus (탐구 방향 설정)  
[수업 장면 분석 내용...]
**점수: X점**

#### 3. Investigate (자료 탐색 및 개념 형성)
[수업 장면 분석 내용...]
**점수: X점**

#### 4. Organize (증거 조직화)
[수업 장면 분석 내용...]
**점수: X점**

#### 5. Generalize (일반화)
[수업 장면 분석 내용...]
**점수: X점**

#### 6. Transfer (전이)
[수업 장면 분석 내용...]
**점수: X점**

#### 7. Reflect (성찰)
[수업 장면 분석 내용...]
**점수: X점**

🔍 **점수 기준**
- 3점: 개념 중심의 탐구 활동이 명확히 구현됨
- 2점: 부분적으로 개념 중심 요소가 나타남  
- 1점: 지식 중심이지만 개념 중심 요소 일부 존재
- 0점: 해당 단계가 나타나지 않음

⚠️ **주의**: 반드시 위 형식을 따라 7단계 모두 분석하고 각각 점수를 부여하시오.

**분석할 텍스트:**
{text}
"""
    },
    
    "student_discussion": {
        "name": "학생주도 질문과 대화 및 토론 수업(항상성)",
        "description": "학생 주도 토론 및 질문 분석",
        "prompt": """📋 분석 지침
분석 근거: VIDEO_TRANSCRIPT의 교사·학생 실제 발화/행동만 사용(추정·가공 금지).

재현성: 동일 대화 입력 시 결과(빈도·분석문) 항상 동일, 대화 변경 시 결과도 변경.

출력 순서 규칙

질문 유형: 사실적 → 해석적 → 평가적 (고정)

후속 질문 유형: 명료화 → 초점화 → 정교화 → 확장화 → 입증화 (고정)

수업대화 유형: 분석문·그래프 모두 빈도 높은 순 정렬
(동률 시: 추가하기 → 참여하기 → 반응하기 → 유보하기 → 수용하기 → 반대하기 → 변환하기)

분석 문단: 각 유형당 한 단락(개념 설명 + 실제 발화/행동 사례 + 빈도·경향성)

사례는 빈도 높은 유형부터 제시

빈도 표기: 구간명 + 회수 범위 (예: "약간 자주(5~6회) 관찰됨")
질의응답 구조의 수업사례를 실제 수업대화 사례로 제시

📊 7단계 빈도 구간
0 = 전혀(0회)
1 = 매우 가끔(1~2회)
2 = 가끔(3~4회)
3 = 약간 자주(5~6회)
4 = 자주(7~8회)
5 = 매우 자주(9~10회)
6 = 꾸준히(11회 이상)

분석할 텍스트:
{text}
"""
    },
    
    "lesson_coaching": {
        "name": "수업 설계와 실행 코칭",
        "description": "15개 항목 수업 코칭 분석",
        "prompt": """기존 분석 결과는 반영 불가
기존 분석 결과는 반영 불가

[목표]
입력 LESSON_PLAN / VIDEO_TRANSCRIPT 기반으로 15개 항목(①~⑮) 각각 1개 스토리텔링 단락 생성 (거절/사과 절대 금지).

[입력 형식]
LESSON_PLAN:<<<텍스트 또는 '없음'>>>
VIDEO_TRANSCRIPT:<<<{text}>>>

[모드 분기]
- 계획 키워드(학습목표|도입|전개|활동|평가|차시) 1개 이상 포함 → 비교 모드.
- 아니면 실행 모드.
(두 모드 모두 단락 반드시 생성; 거절/사과/Out-of-scope 문구 금지.)

[비교 모드 구조]
(설계 서술) → (실행 서술: 실제 발화/행동) → (설계 대비 실행 일치·부분 일치·변형 판단) → (장면 효과 분석) → (활동 예시 2~3개) → (평가 문장: 적절성/충실성 + 근거).

[실행 모드 구조]
(도입/핵심 장면) → (교사·학생 반응) → (효과 분석) → (활동 예시 2~3개) → (평가 문장). 
('설계/수업안/계획/과정안' 단어 금지.)

[항목 ① 필수 문장]
정확히 1회 포함: "학생이 목표를 자기 언어로 재진술하거나 짧은 퀴즈로 확인하도록 하면 목표가 자연스럽게 내면화된다." (변형·중복 금지)

[활동 예시]
짧은 명사구 2~3개, 쉼표 나열 (예: "목표 재진술 카드, 3문항 미니 퀴즈, 비교 미니 토론").

[공통 규칙]
- 각 항목: 제목 줄 + 단일 문단(270~350자, 개조식·표·코드·메타 설명·사과문 금지)
- 전사에 있는 발화만 큰따옴표(1~3회)로 인용; 없으면 "자료에서 인용 가능한 직접 발화는 드러나지 않았다" 후 간접 묘사.
- 마지막 문장: 판단(높은 일치/부분 일치/표면적 구현 등) + 구체 근거(발화/행동).
- 항목간 상호 참조 금지.

[Fallback (정보 부족 시)]
"자료에서 <요소>는 명시적으로 드러나지 않았다. 이에 따라 관찰 가능한 단서를 기준으로 제한적 해석을 제시한다." 
→ 이후 구조를 계속 완성.

[무조건 산출 & 금지 패턴]
다음 단어·구는 절대 출력하지 않는다: "죄송", "사과", "답변할 수 없습니다", "부적합한 질문", "관계없는", "out of scope", "cannot answer", "처리 불가".
허구 발화 생성 금지.

[출력 형식]
① (항목 제목)
(단락…)

② (항목 제목)
(단락…)
… ③~⑮ 동일. 다른 텍스트 출력 금지.

이제 위 규칙을 적용하여 결과만 출력하라.
"""
    }
}

def call_solar_api(prompt: str, temperature: float = 0.1) -> str:
    """Call Solar2 Pro API with low temperature for consistency"""
    headers = {
        "Authorization": f"Bearer {UPSTAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "solar-mini",
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": 4000
    }
    
    try:
        response = requests.post(SOLAR_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except Exception as e:
        logger.error(f"Solar API call failed: {str(e)}")
        raise

def process_analysis_job(job_id: str, text: str, framework: str, metadata: Dict[str, Any]):
    """Background task for processing analysis"""
    try:
        # Update job status
        job_data = {
            "job_id": job_id,
            "status": "processing",
            "message": f"Running {framework} analysis...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        redis_client.setex(f"analysis_job:{job_id}", 3600, json.dumps(job_data))
        
        # Get framework configuration
        if framework not in ANALYSIS_FRAMEWORKS:
            raise ValueError(f"Unknown framework: {framework}")
        
        framework_config = ANALYSIS_FRAMEWORKS[framework]
        prompt = framework_config["prompt"].format(text=text)
        
        # Call Solar API with temperature=0.3 for consistent analysis results
        analysis_result = call_solar_api(prompt, temperature=0.3)
        
        # Prepare result
        result = {
            "analysis_id": job_id,
            "framework": framework,
            "framework_name": framework_config["name"],
            "text": text,
            "analysis": analysis_result,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "character_count": len(text),
            "word_count": len(text.split())
        }
        
        # Store analysis in database for research
        try:
            db = next(get_db())
            
            # Prepare database record
            db_analysis_data = {
                "analysis_id": job_id,
                "framework": framework,
                "temperature": 0.3,
                "model_used": "solar-pro",
                "analysis_text": analysis_result,
                "character_count": len(text),
                "word_count": len(text.split()),
                "processing_time": processing_time,
                "anonymized": True,
                "research_approved": metadata.get("research_consent", False)
            }
            
            # Add metadata if available
            if metadata:
                db_analysis_data.update({
                    "teacher_name": metadata.get("teacher_name"),
                    "subject": metadata.get("subject"),
                    "grade_level": metadata.get("grade_level"),
                    "school_type": metadata.get("school_type")
                })
            
            # Store in database
            store_analysis(db, db_analysis_data)
            update_framework_usage(db, framework)
            
            db.close()
            logger.info(f"Analysis {job_id} stored in database for research")
            
        except Exception as e:
            logger.error(f"Failed to store analysis in database: {str(e)}")
            # Don't fail the job if database storage fails
        
        # Success
        job_data.update({
            "status": "completed",
            "message": "Analysis completed successfully",
            "result": result,
            "updated_at": datetime.now().isoformat()
        })
        
        redis_client.setex(f"analysis_job:{job_id}", 3600, json.dumps(job_data))
        
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed: {str(e)}")
        job_data.update({
            "status": "failed",
            "message": f"Analysis failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        })
        redis_client.setex(f"analysis_job:{job_id}", 3600, json.dumps(job_data))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "analysis", 
        "timestamp": datetime.now().isoformat(),
        "available_frameworks": list(ANALYSIS_FRAMEWORKS.keys())
    }

@app.get("/api/frameworks")
async def list_frameworks():
    """List available analysis frameworks"""
    frameworks = []
    for key, config in ANALYSIS_FRAMEWORKS.items():
        frameworks.append({
            "id": key,
            "name": config["name"],
            "description": config["description"]
        })
    return {"frameworks": frameworks}

@app.post("/api/analyze/text")
async def analyze_text(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Submit text for analysis"""
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initial job status
        job_data = {
            "job_id": job_id,
            "status": "pending",
            "message": "Analysis job submitted successfully",
            "framework": request.framework,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store in Redis
        redis_client.setex(f"analysis_job:{job_id}", 3600, json.dumps(job_data))
        
        # Add background task
        background_tasks.add_task(
            process_analysis_job,
            job_id,
            request.text,
            request.framework,
            request.metadata or {}
        )
        
        return {
            "analysis_id": job_id,
            "status": "pending",
            "message": "Analysis job submitted successfully",
            "framework": request.framework,
            "submitted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error submitting analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/analyze/{job_id}")
async def get_analysis_status(job_id: str):
    """Get analysis job status"""
    try:
        job_data = redis_client.get(f"analysis_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Analysis job not found")
        
        return json.loads(job_data)
    
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/analyze/transcript")
async def analyze_transcript(
    transcription_result: Dict[str, Any],
    framework: str = "cbil",
    background_tasks: BackgroundTasks = None
):
    """Analyze transcript result from transcription service"""
    try:
        # Extract text from transcription result
        if "result" in transcription_result and "transcript" in transcription_result["result"]:
            text = transcription_result["result"]["transcript"]
            metadata = {
                "video_url": transcription_result["result"].get("video_url"),
                "video_id": transcription_result["result"].get("video_id"),
                "language": transcription_result["result"].get("language"),
                "transcription_method": transcription_result["result"].get("method_used")
            }
        else:
            text = transcription_result.get("transcript", "")
            metadata = transcription_result.get("metadata", {})
        
        if not text:
            raise HTTPException(status_code=400, detail="No text found in transcription result")
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            text=text,
            framework=framework,
            metadata=metadata
        )
        
        # Submit for analysis
        return await analyze_text(analysis_request, background_tasks)
    
    except Exception as e:
        logger.error(f"Error analyzing transcript: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Initialize report generators
report_generator = HTMLReportGenerator()
pdf_generator = PDFReportGenerator()

@app.get("/api/reports/html/{job_id}", response_class=HTMLResponse)
async def get_html_report(job_id: str):
    """Generate HTML report for completed analysis"""
    try:
        job_data = redis_client.get(f"analysis_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Analysis job not found")
        
        job = json.loads(job_data)
        
        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        if "result" not in job:
            raise HTTPException(status_code=400, detail="No analysis result found")
        
        # Generate HTML report
        html_report = report_generator.generate_html_report(job["result"])
        return HTMLResponse(content=html_report, media_type="text/html")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reports/data/{job_id}")
async def get_report_data(job_id: str):
    """Get structured report data for frontend"""
    try:
        job_data = redis_client.get(f"analysis_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Analysis job not found")
        
        job = json.loads(job_data)
        
        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        if "result" not in job:
            raise HTTPException(status_code=400, detail="No analysis result found")
        
        result = job["result"]
        framework = result.get("framework", "generic")
        
        # Extract chart data and recommendations
        chart_data = report_generator.extract_chart_data(result.get("analysis", ""), framework)
        recommendations = report_generator.generate_recommendations(result.get("analysis", ""), framework)
        
        return {
            "analysis_id": job_id,
            "framework": framework,
            "framework_name": result.get("framework_name", "분석"),
            "chart_data": chart_data,
            "chart_config": report_generator.generate_chart_js_config(chart_data),
            "recommendations": recommendations,
            "analysis_text": result.get("analysis", ""),
            "metadata": {
                "character_count": result.get("character_count", 0),
                "word_count": result.get("word_count", 0),
                "created_at": result.get("created_at", "")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reports/pdf/{job_id}")
async def get_pdf_report(job_id: str):
    """Generate and download PDF report for completed analysis"""
    try:
        # Check if PDF generation is available
        if not is_pdf_generation_available():
            raise HTTPException(
                status_code=503, 
                detail="PDF generation is not available. WeasyPrint is not installed."
            )
        
        job_data = redis_client.get(f"analysis_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Analysis job not found")
        
        job = json.loads(job_data)
        
        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed yet")
        
        if "result" not in job:
            raise HTTPException(status_code=400, detail="No analysis result found")
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_pdf_report(job["result"])
        
        # Generate filename
        filename = pdf_generator.generate_pdf_filename(job["result"])
        
        # Return PDF as download
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

# Report Generation Request Models
class ReportGenerationRequest(BaseModel):
    analysis_result: Dict[str, Any]
    template: str = "comprehensive"
    title: Optional[str] = None

@app.post("/api/reports/generate/html", response_class=HTMLResponse)
async def generate_html_report(request: ReportGenerationRequest):
    """Generate HTML report from analysis data"""
    try:
        # Extract analysis data
        analysis_result = request.analysis_result
        
        # Prepare data for HTML generator
        report_data = {
            'framework': analysis_result.get('framework', 'generic'),
            'analysis': analysis_result.get('analysis', ''),
            'analysis_id': analysis_result.get('analysis_id', 'direct-generation'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'character_count': analysis_result.get('character_count', 0),
            'word_count': analysis_result.get('word_count', 0),
            'metadata': analysis_result.get('metadata', {})
        }
        
        # Generate HTML report
        html_content = report_generator.generate_html_report(report_data)
        
        logger.info(f"Generated HTML report for framework: {report_data['framework']}")
        
        return HTMLResponse(
            content=html_content,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/reports/status")
async def get_report_capabilities():
    """Get report generation capabilities"""
    return {
        "html_available": True,
        "pdf_available": is_pdf_generation_available(),
        "supported_formats": ["html", "pdf"] if is_pdf_generation_available() else ["html"],
        "frameworks_supported": list(report_generator.FRAMEWORK_NAMES.keys())
    }

@app.get("/api/stats")
async def get_stats():
    """Get service statistics"""
    try:
        # Get all job keys
        job_keys = redis_client.keys("analysis_job:*")
        
        stats = {
            "total_analyses": len(job_keys),
            "service": "analysis",
            "timestamp": datetime.now().isoformat(),
            "available_frameworks": len(ANALYSIS_FRAMEWORKS)
        }
        
        if job_keys:
            # Count by status and framework
            status_counts = {}
            framework_counts = {}
            
            for key in job_keys:
                job_data = json.loads(redis_client.get(key))
                status = job_data.get("status", "unknown")
                framework = job_data.get("framework", "unknown")
                
                status_counts[status] = status_counts.get(status, 0) + 1
                framework_counts[framework] = framework_counts.get(framework, 0) + 1
            
            stats["status_breakdown"] = status_counts
            stats["framework_breakdown"] = framework_counts
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {"error": "Could not retrieve stats"}

@app.get("/api/research/stats")
async def get_research_stats():
    """Get research and database statistics"""
    try:
        db = next(get_db())
        research_stats = get_research_statistics(db)
        db.close()
        
        # Add Redis stats
        redis_keys = redis_client.keys("analysis_job:*")
        research_stats["redis_jobs"] = len(redis_keys)
        research_stats["timestamp"] = datetime.now().isoformat()
        
        return research_stats
        
    except Exception as e:
        logger.error(f"Error getting research stats: {str(e)}")
        return {"error": "Could not retrieve research statistics"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)