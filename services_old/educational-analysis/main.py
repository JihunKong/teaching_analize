#!/usr/bin/env python3
"""
Educational Analysis Service
교육 분석 AI 시스템 메인 FastAPI 애플리케이션
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('educational_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

# 모델 및 컴포넌트 임포트
from models.analysis_models import (
    AnalysisRequest, AnalysisResponse, AnalysisType, AnalysisStatus,
    TeachingCoachAnalysis, DialoguePatternsAnalysis, CBILEvaluationAnalysis,
    ComprehensiveAnalysis, ProcessingProgress
)

from agents.teaching_coach_agent import TeachingCoachAgent
from agents.dialogue_analyst_agent import DialogueAnalystAgent  
from agents.cbil_evaluator_agent import CBILEvaluatorAgent

from integrations.llm_gateway import LLMGateway
from analyzers.visualization_engine import VisualizationEngine

# 글로벌 상태 저장 (실제 구현에서는 Redis/DB 사용)
analysis_store: Dict[str, Dict[str, Any]] = {}

# 생명주기 이벤트
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 이벤트
    logger.info("🚀 Educational Analysis Service starting...")
    
    # 컴포넌트 초기화
    await initialize_components()
    
    # 디렉토리 생성
    os.makedirs("static/charts", exist_ok=True)
    
    yield
    
    # 종료 이벤트
    logger.info("🛑 Educational Analysis Service shutting down...")

# FastAPI 앱 생성
app = FastAPI(
    title="Educational Analysis Service",
    description="AI-powered educational analysis system with 3 specialized agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 글로벌 컴포넌트
llm_gateway: Optional[LLMGateway] = None
viz_engine: Optional[VisualizationEngine] = None
teaching_agent: Optional[TeachingCoachAgent] = None
dialogue_agent: Optional[DialogueAnalystAgent] = None
cbil_agent: Optional[CBILEvaluatorAgent] = None

async def initialize_components():
    """컴포넌트 초기화"""
    global llm_gateway, viz_engine, teaching_agent, dialogue_agent, cbil_agent
    
    try:
        # LLM 게이트웨이 초기화
        llm_gateway = LLMGateway()
        connectivity = await llm_gateway.test_connectivity()
        logger.info(f"🤖 LLM connectivity: {connectivity}")
        
        # 시각화 엔진 초기화
        viz_engine = VisualizationEngine(
            static_dir="static/charts",
            base_url=""  # 실제 배포시 도메인 설정
        )
        
        # 분석 에이전트들 초기화
        teaching_agent = TeachingCoachAgent(llm_gateway)
        dialogue_agent = DialogueAnalystAgent(llm_gateway, viz_engine)
        cbil_agent = CBILEvaluatorAgent(llm_gateway, viz_engine)
        
        logger.info("✅ All components initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Component initialization failed: {e}")
        raise

def get_components():
    """의존성 주입용 컴포넌트 반환"""
    if not all([llm_gateway, viz_engine, teaching_agent, dialogue_agent, cbil_agent]):
        raise HTTPException(status_code=503, detail="Service components not initialized")
    
    return {
        "llm_gateway": llm_gateway,
        "viz_engine": viz_engine,
        "teaching_agent": teaching_agent,
        "dialogue_agent": dialogue_agent,
        "cbil_agent": cbil_agent
    }

# ============= API 엔드포인트 =============

@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "educational-analysis",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "llm_gateway": llm_gateway is not None,
            "viz_engine": viz_engine is not None,
            "agents": all([teaching_agent, dialogue_agent, cbil_agent])
        }
    }

@app.get("/api/connectivity")
async def check_connectivity(components = Depends(get_components)):
    """LLM API 연결 상태 확인"""
    connectivity = await components["llm_gateway"].test_connectivity()
    return {
        "llm_connectivity": connectivity,
        "available_models": components["llm_gateway"].get_available_models()
    }

@app.post("/api/analyze/teaching-coach", response_model=AnalysisResponse)
async def analyze_teaching_coach(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    components = Depends(get_components)
):
    """교육 코칭 분석 (15개 항목)"""
    analysis_id = str(uuid.uuid4())
    
    # 분석 상태 초기화
    analysis_store[analysis_id] = {
        "analysis_id": analysis_id,
        "analysis_type": AnalysisType.TEACHING_COACH,
        "status": AnalysisStatus.PENDING,
        "created_at": datetime.now(),
        "transcript": request.transcript,
        "lesson_plan": request.lesson_plan
    }
    
    # 백그라운드에서 분석 실행
    background_tasks.add_task(
        run_teaching_coach_analysis,
        analysis_id,
        request.transcript,
        request.lesson_plan,
        components["teaching_agent"]
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        analysis_type=AnalysisType.TEACHING_COACH,
        status=AnalysisStatus.PENDING,
        created_at=datetime.now()
    )

@app.post("/api/analyze/dialogue-patterns", response_model=AnalysisResponse)
async def analyze_dialogue_patterns(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    components = Depends(get_components)
):
    """대화 패턴 분석 (정량적)"""
    analysis_id = str(uuid.uuid4())
    
    analysis_store[analysis_id] = {
        "analysis_id": analysis_id,
        "analysis_type": AnalysisType.DIALOGUE_PATTERNS,
        "status": AnalysisStatus.PENDING,
        "created_at": datetime.now(),
        "transcript": request.transcript
    }
    
    background_tasks.add_task(
        run_dialogue_analysis,
        analysis_id,
        request.transcript,
        components["dialogue_agent"]
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        analysis_type=AnalysisType.DIALOGUE_PATTERNS,
        status=AnalysisStatus.PENDING,
        created_at=datetime.now()
    )

@app.post("/api/analyze/cbil-evaluation", response_model=AnalysisResponse)
async def analyze_cbil_evaluation(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    components = Depends(get_components)
):
    """CBIL 7단계 분석"""
    analysis_id = str(uuid.uuid4())
    
    analysis_store[analysis_id] = {
        "analysis_id": analysis_id,
        "analysis_type": AnalysisType.CBIL_EVALUATION,
        "status": AnalysisStatus.PENDING,
        "created_at": datetime.now(),
        "transcript": request.transcript
    }
    
    background_tasks.add_task(
        run_cbil_analysis,
        analysis_id,
        request.transcript,
        components["cbil_agent"]
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        analysis_type=AnalysisType.CBIL_EVALUATION,
        status=AnalysisStatus.PENDING,
        created_at=datetime.now()
    )

@app.post("/api/analyze/comprehensive", response_model=AnalysisResponse)
async def analyze_comprehensive(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    components = Depends(get_components)
):
    """종합 분석 (3가지 모두 실행)"""
    analysis_id = str(uuid.uuid4())
    
    analysis_store[analysis_id] = {
        "analysis_id": analysis_id,
        "analysis_type": AnalysisType.COMPREHENSIVE,
        "status": AnalysisStatus.PENDING,
        "created_at": datetime.now(),
        "transcript": request.transcript,
        "lesson_plan": request.lesson_plan
    }
    
    background_tasks.add_task(
        run_comprehensive_analysis,
        analysis_id,
        request.transcript,
        request.lesson_plan,
        components
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        analysis_type=AnalysisType.COMPREHENSIVE,
        status=AnalysisStatus.PENDING,
        created_at=datetime.now()
    )

@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_result(analysis_id: str):
    """분석 결과 조회"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    data = analysis_store[analysis_id]
    
    return AnalysisResponse(
        analysis_id=data["analysis_id"],
        analysis_type=data["analysis_type"],
        status=data["status"],
        created_at=data["created_at"],
        completed_at=data.get("completed_at"),
        processing_time=data.get("processing_time"),
        results=data.get("results"),
        error_message=data.get("error_message")
    )

@app.get("/api/analysis/{analysis_id}/progress", response_model=ProcessingProgress)
async def get_analysis_progress(analysis_id: str):
    """분석 진행 상황 조회"""
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    data = analysis_store[analysis_id]
    
    # 진행률 계산 (간단한 구현)
    progress = 0
    if data["status"] == AnalysisStatus.PENDING:
        progress = 10
    elif data["status"] == AnalysisStatus.PROCESSING:
        progress = 50
    elif data["status"] == AnalysisStatus.COMPLETED:
        progress = 100
    
    return ProcessingProgress(
        analysis_id=analysis_id,
        progress_percentage=progress,
        current_step=data.get("current_step", f"분석 {data['status'].value}"),
        estimated_completion=data.get("estimated_completion")
    )

# ============= 백그라운드 태스크 함수들 =============

async def run_teaching_coach_analysis(
    analysis_id: str,
    transcript: str,
    lesson_plan: Optional[str],
    agent: TeachingCoachAgent
):
    """교육 코칭 분석 실행"""
    try:
        # 상태 업데이트
        analysis_store[analysis_id]["status"] = AnalysisStatus.PROCESSING
        analysis_store[analysis_id]["current_step"] = "교육 코칭 분석 중..."
        
        start_time = datetime.now()
        
        # 분석 실행
        result = await agent.analyze(transcript, lesson_plan)
        
        # 완료 처리
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.COMPLETED,
            "completed_at": end_time,
            "processing_time": processing_time,
            "results": result.dict()
        })
        
        logger.info(f"✅ Teaching coach analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ Teaching coach analysis failed: {analysis_id}, {e}")
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.FAILED,
            "error_message": str(e)
        })

async def run_dialogue_analysis(
    analysis_id: str,
    transcript: str,
    agent: DialogueAnalystAgent
):
    """대화 패턴 분석 실행"""
    try:
        analysis_store[analysis_id]["status"] = AnalysisStatus.PROCESSING
        analysis_store[analysis_id]["current_step"] = "대화 패턴 분석 중..."
        
        start_time = datetime.now()
        result = await agent.analyze(transcript)
        end_time = datetime.now()
        
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.COMPLETED,
            "completed_at": end_time,
            "processing_time": (end_time - start_time).total_seconds(),
            "results": result.dict()
        })
        
        logger.info(f"✅ Dialogue analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ Dialogue analysis failed: {analysis_id}, {e}")
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.FAILED,
            "error_message": str(e)
        })

async def run_cbil_analysis(
    analysis_id: str,
    transcript: str,
    agent: CBILEvaluatorAgent
):
    """CBIL 분석 실행"""
    try:
        analysis_store[analysis_id]["status"] = AnalysisStatus.PROCESSING
        analysis_store[analysis_id]["current_step"] = "CBIL 7단계 분석 중..."
        
        start_time = datetime.now()
        result = await agent.analyze(transcript)
        end_time = datetime.now()
        
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.COMPLETED,
            "completed_at": end_time,
            "processing_time": (end_time - start_time).total_seconds(),
            "results": result.dict()
        })
        
        logger.info(f"✅ CBIL analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ CBIL analysis failed: {analysis_id}, {e}")
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.FAILED,
            "error_message": str(e)
        })

async def run_comprehensive_analysis(
    analysis_id: str,
    transcript: str,
    lesson_plan: Optional[str],
    components: Dict[str, Any]
):
    """종합 분석 실행 (3가지 병렬)"""
    try:
        analysis_store[analysis_id]["status"] = AnalysisStatus.PROCESSING
        analysis_store[analysis_id]["current_step"] = "종합 분석 실행 중..."
        
        start_time = datetime.now()
        
        # 3가지 분석 병렬 실행
        import asyncio
        
        teaching_task = components["teaching_agent"].analyze(transcript, lesson_plan)
        dialogue_task = components["dialogue_agent"].analyze(transcript)
        cbil_task = components["cbil_agent"].analyze(transcript)
        
        teaching_result, dialogue_result, cbil_result = await asyncio.gather(
            teaching_task, dialogue_task, cbil_task
        )
        
        # 종합 분석 생성
        comprehensive_result = ComprehensiveAnalysis(
            teaching_coach=teaching_result,
            dialogue_patterns=dialogue_result,
            cbil_evaluation=cbil_result,
            executive_summary=generate_executive_summary(
                teaching_result, dialogue_result, cbil_result
            ),
            key_insights=extract_key_insights(
                teaching_result, dialogue_result, cbil_result
            ),
            priority_recommendations=generate_priority_recommendations(
                teaching_result, dialogue_result, cbil_result
            )
        )
        
        # 대시보드 생성
        if components["viz_engine"]:
            dashboard_url = await components["viz_engine"].create_comprehensive_dashboard(
                teaching_data=teaching_result.dict(),
                dialogue_data=dialogue_result.dict(),
                cbil_data=cbil_result.dict()
            )
            comprehensive_result.dashboard_url = dashboard_url
        
        end_time = datetime.now()
        
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.COMPLETED,
            "completed_at": end_time,
            "processing_time": (end_time - start_time).total_seconds(),
            "results": comprehensive_result.dict()
        })
        
        logger.info(f"✅ Comprehensive analysis completed: {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ Comprehensive analysis failed: {analysis_id}, {e}")
        analysis_store[analysis_id].update({
            "status": AnalysisStatus.FAILED,
            "error_message": str(e)
        })

# ============= 유틸리티 함수들 =============

def generate_executive_summary(
    teaching: TeachingCoachAnalysis,
    dialogue: DialoguePatternsAnalysis,
    cbil: CBILEvaluationAnalysis
) -> str:
    """경영진 요약 생성"""
    return f"""
    수업 종합 분석 요약:
    
    📋 교육 코칭: {teaching.mode} 기반, {len(teaching.strengths)}개 강점 영역 확인
    💬 대화 패턴: 총 {sum([getattr(dialogue.dialogue_types, attr).count for attr in ['adding', 'participating', 'responding', 'reserving', 'accepting', 'opposing', 'transforming'] if hasattr(dialogue.dialogue_types, attr)])}회 대화 참여
    🎓 CBIL 평가: 평균 {cbil.average_score}점, 개념 중심도 {cbil.concept_centered_percentage}%
    
    전반적으로 {'우수한' if cbil.average_score >= 2.5 else '양호한' if cbil.average_score >= 2.0 else '개선이 필요한'} 수준의 수업으로 평가됩니다.
    """.strip()

def extract_key_insights(
    teaching: TeachingCoachAnalysis,
    dialogue: DialoguePatternsAnalysis,
    cbil: CBILEvaluationAnalysis
) -> List[str]:
    """핵심 인사이트 추출"""
    insights = []
    
    # 교육 코칭 인사이트
    if len(teaching.strengths) >= 10:
        insights.append("교육 코칭 관점에서 대부분 영역이 우수한 수준")
    elif len(teaching.improvement_areas) >= 5:
        insights.append("교육 코칭 관점에서 개선이 필요한 영역이 다수 확인됨")
    
    # 대화 패턴 인사이트
    if dialogue.dominant_patterns:
        insights.append(f"대화 패턴: {dialogue.dominant_patterns[0]} 특성 강함")
    
    # CBIL 인사이트
    if cbil.concept_centered_percentage >= 70:
        insights.append("개념 중심 학습이 잘 구현됨")
    elif cbil.concept_centered_percentage < 50:
        insights.append("지식 중심에서 개념 중심으로의 전환 필요")
    
    return insights[:5]

def generate_priority_recommendations(
    teaching: TeachingCoachAnalysis,
    dialogue: DialoguePatternsAnalysis,
    cbil: CBILEvaluationAnalysis
) -> List[str]:
    """우선순위 권고사항 생성"""
    recommendations = []
    
    # 교육 코칭 권고
    if teaching.improvement_areas:
        recommendations.extend(teaching.improvement_areas[:2])
    
    # CBIL 권고  
    if cbil.improvement_recommendations:
        recommendations.extend(cbil.improvement_recommendations[:2])
    
    # 대화 패턴 권고
    total_dialogue = sum([
        getattr(dialogue.dialogue_types, attr).count 
        for attr in ['adding', 'participating', 'responding', 'reserving', 'accepting', 'opposing', 'transforming']
        if hasattr(dialogue.dialogue_types, attr)
    ])
    
    if total_dialogue < 10:
        recommendations.append("학생 참여를 높이는 대화 전략 강화 필요")
    
    return recommendations[:3]

# ============= 메인 실행 =============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # 전사 서비스와 다른 포트
        reload=True,
        log_level="info"
    )