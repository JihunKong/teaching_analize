#!/usr/bin/env python3
"""
Integration Service
전사-분석 통합 서비스 메인 애플리케이션
"""

import os
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, HttpUrl
import uvicorn

from workflow_orchestrator import WorkflowOrchestrator, WorkflowResult, WorkflowStatus

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('integration_service.log')
    ]
)
logger = logging.getLogger(__name__)

# 요청/응답 모델
class AnalysisRequest(BaseModel):
    youtube_url: HttpUrl
    language: str = "ko"
    analysis_types: List[str] = ["comprehensive"]
    workflow_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    message: str
    estimated_completion_time: Optional[str] = None

class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    current_step: Optional[str] = None
    progress_percentage: Optional[int] = None
    youtube_url: Optional[str] = None
    error_message: Optional[str] = None

class WorkflowResultResponse(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    results: Optional[dict] = None
    summary: Optional[dict] = None
    download_urls: Optional[dict] = None

# 글로벌 오케스트레이터
orchestrator: Optional[WorkflowOrchestrator] = None

# 생명주기 이벤트
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 이벤트
    logger.info("🚀 Integration Service starting...")
    
    global orchestrator
    orchestrator = WorkflowOrchestrator(
        transcription_service_url=os.getenv("TRANSCRIPTION_SERVICE_URL", "https://teachinganalize-production.up.railway.app"),
        analysis_service_url=os.getenv("ANALYSIS_SERVICE_URL", "http://localhost:8001"),
        api_key=os.getenv("API_KEY", "test-api-key")
    )
    
    logger.info("✅ Workflow orchestrator initialized")
    
    yield
    
    # 종료 이벤트
    logger.info("🛑 Integration Service shutting down...")

# FastAPI 앱 생성
app = FastAPI(
    title="Teaching Analysis Integration Service",
    description="YouTube 전사 및 교육 분석 통합 워크플로우 서비스",
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

# ============= API 엔드포인트 =============

@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "integration-service",
        "timestamp": datetime.now().isoformat(),
        "orchestrator_ready": orchestrator is not None
    }

@app.post("/api/analyze-youtube", response_model=AnalysisResponse)
async def analyze_youtube_video(request: AnalysisRequest):
    """
    YouTube 영상 전체 분석 워크플로우 시작
    
    전사 → 교육 분석 → 결과 통합까지 원스톱 처리
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        logger.info(f"📹 Starting YouTube analysis: {request.youtube_url}")
        
        # 워크플로우 시작
        workflow_id = await orchestrator.start_youtube_analysis_workflow(
            youtube_url=str(request.youtube_url),
            workflow_id=request.workflow_id,
            language=request.language,
            analysis_types=request.analysis_types
        )
        
        # 예상 완료 시간 계산 (대략적)
        estimated_minutes = 3 + len(request.analysis_types) * 2  # 전사 3분 + 분석당 2분
        estimated_time = f"약 {estimated_minutes}분 후"
        
        return AnalysisResponse(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            message=f"분석 워크플로우가 시작되었습니다. 워크플로우 ID: {workflow_id}",
            estimated_completion_time=estimated_time
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start YouTube analysis: {e}")
        raise HTTPException(status_code=500, detail=f"워크플로우 시작 실패: {str(e)}")

@app.get("/api/workflow/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """워크플로우 진행 상황 조회"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    workflow = orchestrator.get_workflow_status(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="워크플로우를 찾을 수 없습니다")
    
    # 현재 진행 단계 계산
    current_step = None
    progress_percentage = 0
    
    for i, step in enumerate(workflow.steps):
        if step.status == WorkflowStatus.TRANSCRIBING:
            current_step = "전사 처리 중..."
            progress_percentage = 20 + (i * 20)
        elif step.status == WorkflowStatus.ANALYZING:
            current_step = "교육 분석 중..."
            progress_percentage = 40 + (i * 20)
        elif step.status == WorkflowStatus.COMPLETED:
            progress_percentage = min(100, 30 + (i * 25))
    
    if workflow.status == WorkflowStatus.COMPLETED:
        current_step = "분석 완료"
        progress_percentage = 100
    elif workflow.status == WorkflowStatus.FAILED:
        current_step = "처리 실패"
        progress_percentage = 0
    
    # 에러 메시지 추출
    error_message = None
    if workflow.status == WorkflowStatus.FAILED:
        for step in workflow.steps:
            if step.error_message:
                error_message = step.error_message
                break
    
    return WorkflowStatusResponse(
        workflow_id=workflow.workflow_id,
        status=workflow.status,
        created_at=workflow.created_at,
        completed_at=workflow.completed_at,
        processing_time=workflow.processing_time,
        current_step=current_step,
        progress_percentage=progress_percentage,
        youtube_url=workflow.youtube_url,
        error_message=error_message
    )

@app.get("/api/workflow/{workflow_id}/results", response_model=WorkflowResultResponse)
async def get_workflow_results(workflow_id: str):
    """워크플로우 최종 결과 조회"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    workflow = orchestrator.get_workflow_status(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="워크플로우를 찾을 수 없습니다")
    
    if workflow.status != WorkflowStatus.COMPLETED:
        raise HTTPException(
            status_code=400, 
            detail=f"워크플로우가 아직 완료되지 않았습니다. 현재 상태: {workflow.status.value}"
        )
    
    # 요약 정보 생성
    summary = None
    if workflow.final_results:
        summary = workflow.final_results.get("summary", {})
        
        # 추가 통계 정보
        summary.update({
            "workflow_id": workflow_id,
            "processing_time": f"{workflow.processing_time:.2f}초" if workflow.processing_time else "알 수 없음",
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "youtube_url": workflow.youtube_url
        })
    
    # 다운로드 URL 생성 (실제 구현에서는 파일 서빙 시스템 필요)
    download_urls = {
        "transcript_json": f"/api/workflow/{workflow_id}/download/transcript.json",
        "analysis_pdf": f"/api/workflow/{workflow_id}/download/analysis_report.pdf",
        "dashboard_png": f"/api/workflow/{workflow_id}/download/dashboard.png"
    }
    
    return WorkflowResultResponse(
        workflow_id=workflow_id,
        status=workflow.status,
        results=workflow.final_results,
        summary=summary,
        download_urls=download_urls
    )

@app.get("/api/workflows")
async def list_workflows():
    """활성 워크플로우 목록 조회"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    active_workflows = orchestrator.list_active_workflows()
    
    workflows_info = []
    for workflow_id in active_workflows:
        workflow = orchestrator.get_workflow_status(workflow_id)
        if workflow:
            workflows_info.append({
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "youtube_url": workflow.youtube_url,
                "processing_time": workflow.processing_time
            })
    
    return {
        "active_workflows": len(workflows_info),
        "workflows": workflows_info
    }

@app.post("/api/workflows/cleanup")
async def cleanup_old_workflows(older_than_hours: int = 24):
    """완료된 워크플로우 정리"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    before_count = len(orchestrator.list_active_workflows())
    orchestrator.cleanup_completed_workflows(older_than_hours)
    after_count = len(orchestrator.list_active_workflows())
    
    cleaned_count = before_count - after_count
    
    return {
        "message": f"{cleaned_count}개의 오래된 워크플로우를 정리했습니다",
        "cleaned_workflows": cleaned_count,
        "remaining_workflows": after_count
    }

@app.get("/api/workflow/{workflow_id}/download/{file_type}")
async def download_workflow_file(workflow_id: str, file_type: str):
    """워크플로우 결과 파일 다운로드"""
    # 실제 구현에서는 파일 시스템이나 클라우드 스토리지에서 파일 제공
    # 현재는 플레이스홀더
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    workflow = orchestrator.get_workflow_status(workflow_id)
    if not workflow or workflow.status != WorkflowStatus.COMPLETED:
        raise HTTPException(status_code=404, detail="워크플로우 결과를 찾을 수 없습니다")
    
    # 파일 타입에 따른 처리
    supported_types = ["transcript.json", "analysis_report.pdf", "dashboard.png"]
    if file_type not in supported_types:
        raise HTTPException(status_code=400, detail=f"지원하지 않는 파일 타입: {file_type}")
    
    return {
        "message": "파일 다운로드 기능은 추후 구현 예정",
        "workflow_id": workflow_id,
        "file_type": file_type,
        "placeholder_data": workflow.final_results
    }

# ============= 개발용 엔드포인트 =============

@app.get("/api/test/services")
async def test_service_connectivity():
    """연결된 서비스들의 상태 테스트"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    import aiohttp
    
    results = {
        "transcription_service": {"url": orchestrator.transcription_url, "status": "unknown"},
        "analysis_service": {"url": orchestrator.analysis_url, "status": "unknown"}
    }
    
    # 전사 서비스 테스트
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{orchestrator.transcription_url}/health", timeout=10) as response:
                if response.status == 200:
                    results["transcription_service"]["status"] = "healthy"
                    results["transcription_service"]["response"] = await response.json()
                else:
                    results["transcription_service"]["status"] = f"error_{response.status}"
    except Exception as e:
        results["transcription_service"]["status"] = f"connection_failed: {str(e)}"
    
    # 분석 서비스 테스트
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{orchestrator.analysis_url}/health", timeout=10) as response:
                if response.status == 200:
                    results["analysis_service"]["status"] = "healthy"
                    results["analysis_service"]["response"] = await response.json()
                else:
                    results["analysis_service"]["status"] = f"error_{response.status}"
    except Exception as e:
        results["analysis_service"]["status"] = f"connection_failed: {str(e)}"
    
    return results

# ============= 메인 실행 =============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,  # 다른 서비스들과 다른 포트
        reload=True,
        log_level="info"
    )