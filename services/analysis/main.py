#!/usr/bin/env python3
"""
AIBOA Analysis Service
Multiple framework analysis using OpenAI GPT-4o-mini API
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, validator
import redis
import json
import requests

# Import report generators
from html_report_generator import HTMLReportGenerator
from pdf_report_generator import PDFReportGenerator, is_pdf_generation_available
from diagnostic_report_generator import DiagnosticReportGenerator

# Import Module 4 advanced generators
from advanced_pdf_generator import AdvancedPDFGenerator
from visualization import Matrix3DVisualizer
from exporters import ExcelReportExporter

# Import database
from database import (
    get_db, store_analysis, update_framework_usage, get_research_statistics,
    init_database, AnalysisResultDB
)
from sqlalchemy.orm import Session

# Import Module 3 evaluation components
from core.evaluation_service import EvaluationService
from core.cbil_integration import CBILIntegration

# Import semantic cache for consistency guarantee
from utils.semantic_cache import SemanticCache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to query analysis from database
def get_analysis_from_database(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve analysis result from PostgreSQL database by job_id.
    Used as fallback when Redis cache expires.

    Returns:
        Dict with analysis result in the same format as Redis, or None if not found
    """
    try:
        db = next(get_db())
        analysis_record = db.query(AnalysisResultDB).filter(
            AnalysisResultDB.uuid == job_id
        ).first()

        if not analysis_record:
            logger.info(f"Analysis {job_id} not found in database")
            db.close()
            return None

        # Reconstruct result format matching Redis structure
        result = {
            "framework": analysis_record.framework,
            "evaluation_type": analysis_record.framework,
            "analysis_text": analysis_record.results.get("analysis_text", ""),
            "structured_results": analysis_record.results.get("structured_results"),
            "scores": analysis_record.results.get("scores"),
            "recommendations": analysis_record.results.get("recommendations"),
            "overall_score": analysis_record.overall_score,
            "primary_level": analysis_record.primary_level,
            "processing_time": analysis_record.processing_time_seconds,
            "metadata": analysis_record.analysis_metadata or {}
        }

        db.close()
        logger.info(f"Successfully retrieved analysis {job_id} from database (Redis fallback)")
        return result

    except Exception as e:
        logger.error(f"Failed to retrieve analysis {job_id} from database: {str(e)}")
        return None

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

# Initialize Semantic Cache for consistency guarantee
# Caches first LLM classification result to ensure 100% reproducibility
semantic_cache = SemanticCache(redis_client)
logger.info("✓ Semantic Cache initialized for guaranteed consistency")

# OpenAI API configuration
# Read Upstage configuration
UPSTAGE_BASE_URL = os.getenv('UPSTAGE_BASE_URL', 'https://api.upstage.ai/v1')
GPT_MODEL = os.getenv('GPT_MODEL', 'solar-pro2')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")

# Import OpenAI
from openai import OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY, base_url=UPSTAGE_BASE_URL) if OPENAI_API_KEY else None

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
    },

    "cbil_comprehensive": {
        "name": "CBIL + Module 3 종합 분석",
        "description": "CBIL 7단계 + 3D 매트릭스 + 정량지표 + 패턴매칭 + AI 코칭",
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
    }
}

def call_openai_api(prompt: str) -> str:
    """
    Call OpenAI GPT-5-mini API
    ⚠️ MODEL: Upstage Solar Pro 2 (Changed 2025-01-11) - DO NOT REVERT TO gpt-4o-mini

    Note:
        GPT-5 uses default temperature=1.0 (cannot be customized)
        Consistency guaranteed by majority voting and structured prompts
    """
    if not openai_client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.")

    try:
        response = openai_client.chat.completions.create(
            model=GPT_MODEL,  # ⚠️ CRITICAL: Upstage Solar Pro 2
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_completion_tokens=4000  # Upstage Solar Pro 2 temperature=0=1.0
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"OpenAI API call failed: {str(e)}")
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
        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL
        
        # Get framework configuration
        if framework not in ANALYSIS_FRAMEWORKS:
            raise ValueError(f"Unknown framework: {framework}")
        
        framework_config = ANALYSIS_FRAMEWORKS[framework]
        prompt = framework_config["prompt"].format(text=text)
        
        # Call OpenAI API (Upstage Solar Pro 2 temperature=0=1.0)
        start_time = datetime.now()
        analysis_result = call_openai_api(prompt)
        processing_time = (datetime.now() - start_time).total_seconds()
        
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
                "input_text": text,
                "analysis_id": job_id,
                "framework": framework,
                "temperature": 1.0,  # Upstage Solar Pro 2 temperature=0
                "model_used": GPT_MODEL,  # ⚠️ Updated to Upstage Solar Pro 2
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
        
        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL
        
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed: {str(e)}")
        job_data.update({
            "status": "failed",
            "message": f"Analysis failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        })
        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL

async def process_comprehensive_cbil_analysis(
    job_id: str,
    text: str,
    metadata: Dict[str, Any]
):
    """
    Background task for comprehensive CBIL + Module 3 analysis

    Workflow:
    1. Call OpenAI API for CBIL 7-stage analysis
    2. Parse utterances from transcript
    3. Call Module 3 evaluation with CBIL integration
    4. Generate comprehensive coaching
    """
    try:
        # Update job status
        job_data = {
            "job_id": job_id,
            "status": "processing",
            "message": "Step 1/3: Running CBIL 7-stage analysis...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL

        # Step 1: Call OpenAI API for CBIL analysis
        logger.info(f"Job {job_id}: Starting CBIL analysis")
        framework_config = ANALYSIS_FRAMEWORKS["cbil"]
        cbil_prompt = framework_config["prompt"].format(text=text)

        start_time = datetime.now()
        cbil_analysis_text = call_openai_api(cbil_prompt)  # Upstage Solar Pro 2 temperature=0=1.0
        cbil_processing_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"Job {job_id}: CBIL analysis completed in {cbil_processing_time:.2f}s")

        # Step 2: Parse utterances from transcript
        job_data["message"] = "Step 2/3: Parsing utterances and building 3D matrix..."
        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL

        # Simple utterance parsing (split by sentences for now)
        # In production, this should use proper speaker diarization from Module 1
        import re
        sentences = re.split(r'[.!?]\s+', text)
        utterances = [
            {
                "id": f"utt_{i:04d}",
                "text": sentence.strip(),
                "timestamp": f"00:{i//60:02d}:{i%60:02d}"
            }
            for i, sentence in enumerate(sentences) if sentence.strip()
        ]

        logger.info(f"Job {job_id}: Parsed {len(utterances)} utterances")

        # Step 3: Run Module 3 evaluation with CBIL integration
        job_data["message"] = "Step 3/3: Running Module 3 evaluation with CBIL integration..."
        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL

        # Initialize EvaluationService with semantic cache for consistency
        evaluation_service = EvaluationService(semantic_cache=semantic_cache)

        # Context from metadata
        context = {
            "subject": metadata.get("subject", "일반"),
            "grade_level": metadata.get("grade_level", "미지정"),
            "duration": metadata.get("duration", len(utterances))
        }

        # Call evaluate_with_cbil with error handling
        logger.info(f"Job {job_id}: Starting CBIL-integrated evaluation")
        try:
            evaluation_result = await evaluation_service.evaluate_with_cbil(
                utterances=utterances,
                cbil_analysis_text=cbil_analysis_text,
                evaluation_id=job_id,
                context=context,
                include_raw_data=False
            )

            total_processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Job {job_id}: Comprehensive evaluation completed in {total_processing_time:.2f}s")

            # Convert result to dictionary
            result_dict = evaluation_service.to_dict(evaluation_result)

            # Add CBIL analysis text to result
            result_dict["cbil_analysis_text"] = cbil_analysis_text
            result_dict["framework"] = "cbil_comprehensive"
            result_dict["framework_name"] = ANALYSIS_FRAMEWORKS["cbil_comprehensive"]["name"]
            result_dict["input_text"] = text  # Add original transcript for frontend display

        except AttributeError as e:
            logger.error(f"Job {job_id}: CBIL integration method missing: {e}")
            raise ValueError(f"CBIL evaluation failed - method not found: {e}")
        except Exception as e:
            logger.error(f"Job {job_id}: Unexpected error in CBIL evaluation: {e}")
            logger.exception("Full traceback:")
            raise ValueError(f"CBIL evaluation failed: {str(e)}")

        # Success
        job_data.update({
            "status": "completed",
            "message": "Comprehensive CBIL analysis completed successfully",
            "result": result_dict,
            "updated_at": datetime.now().isoformat(),
            "processing_time": total_processing_time
        })

        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL
        logger.info(f"Job {job_id}: Results stored in Redis")

        # Store in database
        try:
            db = next(get_db())

            db_analysis_data = {
                "analysis_id": job_id,
                "framework": "cbil_comprehensive",
                "input_text": text,
                "temperature": 1.0,  # Upstage Solar Pro 2 temperature=0
                "model_used": GPT_MODEL,  # ⚠️ Updated to Upstage Solar Pro 2
                "analysis_text": cbil_analysis_text,
                "character_count": len(text),
                "word_count": len(text.split()),
                "processing_time": total_processing_time,
                "anonymized": True,
                "research_approved": metadata.get("research_consent", False)
            }

            if metadata:
                db_analysis_data.update({
                    "teacher_name": metadata.get("teacher_name"),
                    "subject": metadata.get("subject"),
                    "grade_level": metadata.get("grade_level"),
                    "school_type": metadata.get("school_type")
                })

            store_analysis(db, db_analysis_data)
            update_framework_usage(db, "cbil_comprehensive")
            db.close()

            logger.info(f"Job {job_id}: Stored in database for research")

        except Exception as e:
            logger.error(f"Job {job_id}: Failed to store in database: {str(e)}")

    except Exception as e:
        logger.error(f"Job {job_id}: Comprehensive analysis failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

        job_data.update({
            "status": "failed",
            "message": f"Comprehensive analysis failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        })
        redis_client.setex(f"analysis_job:{job_id}", 604800, json.dumps(job_data))  # 7 days TTL

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "analysis", 
        "timestamp": datetime.now().isoformat(),
        "available_frameworks": list(ANALYSIS_FRAMEWORKS.keys())
    }

@app.get("/api/analyze/frameworks")
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

        # Determine TTL based on framework (comprehensive analysis takes longer)
        ttl = 7200 if request.framework == "cbil_comprehensive" else 3600

        # Store in Redis
        redis_client.setex(f"analysis_job:{job_id}", ttl, json.dumps(job_data))

        # Add appropriate background task based on framework
        if request.framework == "cbil_comprehensive":
            # Use comprehensive CBIL + Module 3 analysis
            background_tasks.add_task(
                process_comprehensive_cbil_analysis,
                job_id,
                request.text,
                request.metadata or {}
            )
        else:
            # Use standard OpenAI API analysis
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
    """Analyze transcript result from transcription service (legacy endpoint)"""
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

class TranscriptAnalysisRequest(BaseModel):
    transcript_id: str
    framework: str = "cbil"
    metadata: Optional[Dict[str, Any]] = {}

async def fetch_transcript_from_service(transcript_id: str) -> Dict[str, Any]:
    """Fetch transcript data directly from transcription service"""
    try:
        transcription_service_url = os.getenv("TRANSCRIPTION_SERVICE_URL", "http://localhost:8000")
        response = requests.get(f"{transcription_service_url}/api/transcripts/{transcript_id}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Transcript not found")
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch transcript from service")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to transcription service: {str(e)}")
        raise HTTPException(status_code=503, detail="Transcription service unavailable")

@app.post("/api/analyze/transcript-by-id")
async def analyze_transcript_by_id(
    request: TranscriptAnalysisRequest,
    background_tasks: BackgroundTasks = None
):
    """Analyze transcript by fetching data directly from transcription service"""
    try:
        # Fetch transcript from transcription service
        logger.info(f"Fetching transcript {request.transcript_id} from transcription service")
        transcript_data = await fetch_transcript_from_service(request.transcript_id)
        
        if not transcript_data.get("success"):
            raise HTTPException(status_code=400, detail="Failed to fetch transcript data")
        
        # Extract text and prepare metadata
        text = transcript_data.get("transcript_text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text found in transcript")
        
        # Combine provided metadata with transcript metadata
        metadata = {
            "transcript_id": request.transcript_id,
            "source_url": transcript_data.get("source_url"),
            "video_id": transcript_data.get("video_id"),
            "language": transcript_data.get("language"),
            "transcription_method": transcript_data.get("method_used"),
            "character_count": transcript_data.get("character_count"),
            "word_count": transcript_data.get("word_count"),
            "teacher_name": transcript_data.get("teacher_name"),
            "subject": transcript_data.get("subject"),
            "grade_level": transcript_data.get("grade_level"),
            **(request.metadata or {})
        }
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            text=text,
            framework=request.framework,
            metadata=metadata
        )
        
        logger.info(f"Starting analysis for transcript {request.transcript_id} using {request.framework} framework")
        
        # Submit for analysis
        return await analyze_text(analysis_request, background_tasks)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing transcript by ID {request.transcript_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Initialize report generators
report_generator = HTMLReportGenerator()
pdf_generator = PDFReportGenerator()
diagnostic_report_generator = DiagnosticReportGenerator()

# Initialize Module 4 advanced generators
advanced_pdf_gen = AdvancedPDFGenerator()
matrix_3d_viz = Matrix3DVisualizer()
excel_exporter = ExcelReportExporter()

@app.get("/api/reports/html/{job_id}", response_class=HTMLResponse)
async def get_html_report(job_id: str):
    """Generate HTML report for completed analysis with Redis → Database fallback"""
    try:
        # Try Redis first (fast path)
        job_data = redis_client.get(f"analysis_job:{job_id}")

        if job_data:
            # Found in Redis - use cached data
            job = json.loads(job_data)

            if job.get("status") != "completed":
                raise HTTPException(status_code=400, detail="Analysis not completed yet")

            if "result" not in job:
                raise HTTPException(status_code=400, detail="No analysis result found")

            result = job["result"]
            logger.info(f"Retrieved analysis {job_id} from Redis cache")
        else:
            # Not in Redis - try database fallback
            logger.info(f"Analysis {job_id} not in Redis, checking database...")
            result = get_analysis_from_database(job_id)

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Analysis job {job_id} not found in cache or database"
                )

            logger.info(f"Using database fallback for analysis {job_id}")

        # Result should already be a dict from Redis
        # Check both framework and evaluation_type fields
        framework = result.get("framework", "")
        evaluation_type = result.get("evaluation_type", "")

        # Use diagnostic report generator for cbil_comprehensive framework
        if "cbil_comprehensive" in framework or "cbil_comprehensive" in evaluation_type:
            logger.info(f"Using Diagnostic report generator for cbil_comprehensive framework")
            logger.info(f"Result type: {type(result)}")
            logger.info(f"Result keys: {result.keys() if isinstance(result, dict) else 'NOT A DICT'}")
            try:
                html_report = diagnostic_report_generator.generate_html_report(result)
            except Exception as gen_error:
                import traceback
                logger.error(f"Diagnostic report generation failed: {str(gen_error)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.error(f"Result structure: {json.dumps(result, indent=2, default=str)[:500]}")
                raise
        else:
            # Use standard HTML report generator for other frameworks
            html_report = report_generator.generate_html_report(result)

        return HTMLResponse(content=html_report, media_type="text/html")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/reports/diagnostic/{job_id}", response_class=HTMLResponse)
async def get_diagnostic_report(job_id: str):
    """
    Generate diagnostic professional diagnostic report for completed analysis

    This endpoint provides a medical body composition-style report with:
    - At-a-glance hero summary with overall score
    - Core metric score cards (top 3 metrics)
    - Strengths and areas for improvement
    - Priority coaching recommendations
    - Professional Diagnostic-inspired design system

    Only works for comprehensive analysis (cbil_comprehensive framework)
    """
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
        framework = result.get("framework", "")

        # Diagnostic reports are only available for comprehensive analysis
        if framework != "cbil_comprehensive":
            raise HTTPException(
                status_code=400,
                detail="Diagnostic reports are only available for comprehensive analysis (cbil_comprehensive framework)"
            )

        # Verify required data exists
        if "quantitative_metrics" not in result:
            raise HTTPException(
                status_code=400,
                detail="Quantitative metrics not found in analysis result"
            )

        # Generate diagnostic report
        logger.info(f"Generating Diagnostic report for job {job_id}")
        diagnostic_html = diagnostic_report_generator.generate_html_report(result)

        return HTMLResponse(content=diagnostic_html, media_type="text/html")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Diagnostic report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
        # For CBIL comprehensive, use coaching_feedback instead of raw analysis
        if framework == "cbil_comprehensive":
            # Use coaching feedback for rich recommendations
            coaching_data = result.get("coaching_feedback", {})
            analysis_text_for_extraction = result.get("cbil_analysis_text", "")
            recommendations_text = coaching_data.get("priority_actions", [])
        else:
            analysis_text_for_extraction = result.get("analysis", "")
            recommendations_text = analysis_text_for_extraction

        chart_data = report_generator.extract_chart_data(analysis_text_for_extraction, framework)
        recommendations = report_generator.generate_recommendations(recommendations_text, framework)
        
        return {
            "analysis_id": job_id,
            "framework": framework,
            "framework_name": result.get("framework_name", "분석"),
            "chart_data": chart_data,
            "chart_config": report_generator.generate_chart_js_config(chart_data),
            "recommendations": recommendations,
            "analysis_text": analysis_text_for_extraction,
            "coaching_feedback": result.get("coaching_feedback", {}) if framework == "cbil_comprehensive" else None,
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

@app.get("/api/reports/pdf-enhanced/{job_id}")
async def get_enhanced_pdf_report(job_id: str, include_cover: bool = True):
    """
    Generate enhanced PDF report with rendered charts (not placeholders)

    Uses AdvancedPDFGenerator with Matplotlib chart rendering
    """
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

        result = job["result"]
        framework = result.get("framework", "generic")

        # Only generate enhanced PDFs for cbil_comprehensive framework
        if framework != "cbil_comprehensive":
            raise HTTPException(
                status_code=400,
                detail="Enhanced PDF only available for cbil_comprehensive framework"
            )

        # Generate enhanced PDF with rendered charts
        logger.info(f"Generating enhanced PDF for job {job_id}")
        pdf_bytes = advanced_pdf_gen.generate_pdf_with_charts(
            result,
            include_cover=include_cover
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"CBIL_Enhanced_Report_{job_id[:8]}_{timestamp}.pdf"

        logger.info(f"Enhanced PDF generated successfully: {filename}")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating enhanced PDF: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Enhanced PDF generation failed: {str(e)}")

@app.get("/api/reports/visualization/3d-matrix/{job_id}", response_class=HTMLResponse)
async def get_3d_matrix_visualization(job_id: str):
    """
    Get interactive 3D matrix heatmap visualization

    Returns interactive Plotly 3D scatter plot showing Stage × Context × Level
    """
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

        # Only available for cbil_comprehensive framework
        if framework != "cbil_comprehensive":
            raise HTTPException(
                status_code=400,
                detail="3D matrix visualization only available for cbil_comprehensive framework"
            )

        # Extract matrix data from Module 2 results
        module2_result = result.get("module2_result")
        if not module2_result:
            raise HTTPException(
                status_code=400,
                detail="No Module 2 matrix data found in analysis result"
            )

        # Generate 3D visualization
        logger.info(f"Generating 3D matrix visualization for job {job_id}")
        html_content = matrix_3d_viz.generate_3d_heatmap(module2_result)

        logger.info(f"3D visualization generated successfully")

        return HTMLResponse(content=html_content, media_type="text/html")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating 3D visualization: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"3D visualization failed: {str(e)}")

@app.get("/api/reports/excel/{job_id}")
async def get_excel_report(job_id: str):
    """
    Generate Excel workbook with comprehensive analysis data

    Creates multi-sheet Excel file with:
    - Executive Summary
    - CBIL Scores
    - Module 3 Metrics
    - 3D Matrix Data
    - Pattern Matching
    - Coaching Feedback
    """
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

        # Generate Excel export
        logger.info(f"Generating Excel export for job {job_id}, framework: {framework}")
        excel_bytes = excel_exporter.export_to_excel(result)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        framework_name = framework.replace("_", "-")
        filename = f"Analysis_Report_{framework_name}_{job_id[:8]}_{timestamp}.xlsx"

        logger.info(f"Excel export generated successfully: {filename}")

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Excel export: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}")

@app.get("/api/reports/visualization/2d-heatmaps/{job_id}", response_class=HTMLResponse)
async def get_2d_heatmaps(job_id: str):
    """
    Get 2D heatmap slices by cognitive level

    Returns three 2D heatmaps showing Stage × Context for each Level (L1, L2, L3)
    """
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

        # Only available for cbil_comprehensive framework
        if framework != "cbil_comprehensive":
            raise HTTPException(
                status_code=400,
                detail="2D heatmaps only available for cbil_comprehensive framework"
            )

        # Extract matrix data from Module 2 results
        module2_result = result.get("module2_result")
        if not module2_result:
            raise HTTPException(
                status_code=400,
                detail="No Module 2 matrix data found in analysis result"
            )

        # Generate 2D heatmaps
        logger.info(f"Generating 2D heatmap slices for job {job_id}")
        html_content = matrix_3d_viz.generate_2d_heatmaps(module2_result)

        logger.info(f"2D heatmaps generated successfully")

        return HTMLResponse(content=html_content, media_type="text/html")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating 2D heatmaps: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"2D heatmap generation failed: {str(e)}")

@app.get("/api/reports/visualization/distributions/{job_id}", response_class=HTMLResponse)
async def get_distribution_charts(job_id: str):
    """
    Get distribution bar charts for Stage, Context, and Level

    Returns three bar charts showing percentage distributions across each dimension
    """
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

        # Only available for cbil_comprehensive framework
        if framework != "cbil_comprehensive":
            raise HTTPException(
                status_code=400,
                detail="Distribution charts only available for cbil_comprehensive framework"
            )

        # Extract matrix data from Module 2 results
        module2_result = result.get("module2_result")
        if not module2_result:
            raise HTTPException(
                status_code=400,
                detail="No Module 2 matrix data found in analysis result"
            )

        # Generate distribution charts
        logger.info(f"Generating distribution charts for job {job_id}")
        html_content = matrix_3d_viz.generate_distribution_charts(module2_result)

        logger.info(f"Distribution charts generated successfully")

        return HTMLResponse(content=html_content, media_type="text/html")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating distribution charts: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Distribution chart generation failed: {str(e)}")

# Report Generation Request Models
class ReportGenerationRequest(BaseModel):
    analysis_result: Dict[str, Any]
    template: str = "comprehensive"
    title: Optional[str] = None

class ComprehensiveReportRequest(BaseModel):
    analyses: List[Dict[str, Any]]
    configuration: Optional[Dict[str, Any]] = {}
    
    @validator('analyses')
    def validate_analyses(cls, v):
        if not v or len(v) < 1:
            raise ValueError('At least one analysis is required')
        if len(v) > 10:
            raise ValueError('Maximum 10 analyses can be combined')
        return v

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

@app.get("/api/reports/status/{job_id}")
async def get_report_status(job_id: str):
    """Get analysis job status for report generation"""
    try:
        job_data = redis_client.get(f"analysis_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Analysis job not found")
        
        return json.loads(job_data)
    
    except Exception as e:
        logger.error(f"Error getting report status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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

@app.post("/api/reports/generate/comprehensive", response_class=HTMLResponse)
async def generate_comprehensive_report(request: ComprehensiveReportRequest):
    """Generate comprehensive HTML report combining multiple analysis results"""
    try:
        # Extract analysis results directly from the request
        analysis_results = request.analyses
        
        if not analysis_results:
            raise HTTPException(
                status_code=400,
                detail="No analysis results provided"
            )
        
        # Extract configuration
        config = request.configuration or {}
        
        # Prepare report configuration with defaults
        report_config = {
            "report_type": config.get("type", "detailed"),
            "framework_weights": config.get("frameworkWeights", {}),
            "include_recommendations": config.get("includeRecommendations", True),
            "title": config.get("title", "종합 교육 분석 보고서")
        }
        
        logger.info(f"Generating comprehensive report with {len(analysis_results)} analyses")
        logger.info(f"Report config: {report_config}")
        
        # Generate comprehensive report
        html_report = report_generator.generate_comprehensive_report(
            analysis_results, 
            report_config
        )
        
        logger.info(f"Generated comprehensive report combining {len(analysis_results)} analyses")
        
        return HTMLResponse(
            content=html_report,
            headers={
                "Content-Type": "text/html; charset=utf-8",
                "Cache-Control": "no-cache",
                "X-Analysis-Count": str(len(analysis_results))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Comprehensive report generation failed: {str(e)}"
        )

@app.get("/api/reports/comprehensive/status/{job_ids}")
async def get_comprehensive_report_status(job_ids: str):
    """Get status of multiple analysis jobs for comprehensive reporting"""
    try:
        # Parse comma-separated job IDs
        job_id_list = [id.strip() for id in job_ids.split(',') if id.strip()]
        
        if len(job_id_list) > 10:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 10 job IDs can be checked at once"
            )
        
        job_statuses = []
        summary = {
            "total_jobs": len(job_id_list),
            "completed": 0,
            "processing": 0,
            "pending": 0,
            "failed": 0,
            "missing": 0,
            "ready_for_comprehensive": False
        }
        
        for job_id in job_id_list:
            try:
                job_data = redis_client.get(f"analysis_job:{job_id}")
                if not job_data:
                    job_statuses.append({
                        "job_id": job_id,
                        "status": "missing",
                        "message": "Job not found"
                    })
                    summary["missing"] += 1
                    continue
                
                job = json.loads(job_data)
                status = job.get("status", "unknown")
                
                job_status = {
                    "job_id": job_id,
                    "status": status,
                    "framework": job.get("framework"),
                    "message": job.get("message", ""),
                    "has_result": "result" in job,
                    "created_at": job.get("created_at"),
                    "updated_at": job.get("updated_at")
                }
                
                if status == "completed" and "result" in job:
                    framework_name = report_generator.FRAMEWORK_NAMES.get(
                        job.get("framework"), 
                        job.get("framework", "Unknown")
                    )
                    job_status["framework_name"] = framework_name
                    summary["completed"] += 1
                elif status == "processing":
                    summary["processing"] += 1
                elif status == "pending":
                    summary["pending"] += 1
                elif status == "failed":
                    summary["failed"] += 1
                
                job_statuses.append(job_status)
                
            except json.JSONDecodeError:
                job_statuses.append({
                    "job_id": job_id,
                    "status": "data_error",
                    "message": "Invalid job data format"
                })
                summary["failed"] += 1
            except Exception as e:
                logger.error(f"Error checking status of job {job_id}: {str(e)}")
                job_statuses.append({
                    "job_id": job_id,
                    "status": "error",
                    "message": str(e)
                })
                summary["failed"] += 1
        
        # Check if ready for comprehensive report
        summary["ready_for_comprehensive"] = (
            summary["completed"] > 0 and 
            summary["processing"] == 0 and 
            summary["pending"] == 0
        )
        
        return {
            "job_statuses": job_statuses,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking comprehensive report status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error checking job statuses")

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