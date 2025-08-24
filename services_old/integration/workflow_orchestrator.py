#!/usr/bin/env python3
"""
Workflow Orchestrator
전사 서비스와 분석 서비스를 연결하는 통합 워크플로우
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

import aiohttp
import json
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

class WorkflowStep(BaseModel):
    step_name: str
    status: WorkflowStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class WorkflowResult(BaseModel):
    workflow_id: str
    status: WorkflowStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    steps: List[WorkflowStep]
    youtube_url: Optional[str] = None
    transcript_id: Optional[str] = None
    analysis_id: Optional[str] = None
    final_results: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

class WorkflowOrchestrator:
    """
    전사-분석 통합 워크플로우 오케스트레이터
    
    기능:
    - YouTube URL → 전사 → 교육 분석 파이프라인
    - 비동기 작업 추적 및 상태 관리
    - 실패 시 재시도 및 에러 핸들링
    - 결과 통합 및 리포트 생성
    """
    
    def __init__(
        self,
        transcription_service_url: str = "https://teachinganalize-production.up.railway.app",
        analysis_service_url: str = "http://localhost:8001",
        api_key: str = "test-api-key"
    ):
        self.transcription_url = transcription_service_url.rstrip('/')
        self.analysis_url = analysis_service_url.rstrip('/')
        self.api_key = api_key
        
        # 재시도 설정
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.max_wait_time = 300  # 5 minutes
        
        # 활성 워크플로우 추적
        self.active_workflows: Dict[str, WorkflowResult] = {}
    
    async def start_youtube_analysis_workflow(
        self,
        youtube_url: str,
        workflow_id: Optional[str] = None,
        language: str = "ko",
        analysis_types: List[str] = ["comprehensive"]
    ) -> str:
        """
        YouTube URL 전체 분석 워크플로우 시작
        
        Args:
            youtube_url: YouTube URL
            workflow_id: 워크플로우 ID (없으면 자동 생성)
            language: 전사 언어
            analysis_types: 분석 유형 목록
            
        Returns:
            str: 워크플로우 ID
        """
        if not workflow_id:
            workflow_id = f"workflow_{int(time.time())}_{hash(youtube_url) % 10000}"
        
        logger.info(f"🚀 Starting YouTube analysis workflow: {workflow_id}")
        
        # 워크플로우 초기화
        workflow = WorkflowResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            created_at=datetime.now(),
            youtube_url=youtube_url,
            steps=[
                WorkflowStep(step_name="transcription", status=WorkflowStatus.PENDING),
                WorkflowStep(step_name="analysis", status=WorkflowStatus.PENDING),
                WorkflowStep(step_name="integration", status=WorkflowStatus.PENDING)
            ]
        )
        
        self.active_workflows[workflow_id] = workflow
        
        # 백그라운드에서 워크플로우 실행
        asyncio.create_task(self._execute_workflow(workflow_id, youtube_url, language, analysis_types))
        
        return workflow_id
    
    async def _execute_workflow(
        self,
        workflow_id: str,
        youtube_url: str,
        language: str,
        analysis_types: List[str]
    ):
        """워크플로우 실행"""
        workflow = self.active_workflows[workflow_id]
        start_time = time.time()
        
        try:
            # Step 1: 전사 처리
            logger.info(f"📝 Step 1: Starting transcription for {workflow_id}")
            await self._update_step_status(workflow_id, "transcription", WorkflowStatus.TRANSCRIBING)
            
            transcript_result = await self._process_transcription(youtube_url, language)
            await self._update_step_result(workflow_id, "transcription", WorkflowStatus.COMPLETED, transcript_result)
            
            workflow.transcript_id = transcript_result.get("transcript_id")
            transcript_text = transcript_result.get("transcript_text", "")
            
            # Step 2: 교육 분석
            logger.info(f"🎯 Step 2: Starting analysis for {workflow_id}")
            await self._update_step_status(workflow_id, "analysis", WorkflowStatus.ANALYZING)
            
            analysis_results = []
            for analysis_type in analysis_types:
                result = await self._process_analysis(transcript_text, analysis_type)
                analysis_results.append(result)
            
            await self._update_step_result(workflow_id, "analysis", WorkflowStatus.COMPLETED, {
                "analysis_results": analysis_results,
                "analysis_count": len(analysis_results)
            })
            
            # Step 3: 결과 통합
            logger.info(f"📊 Step 3: Integrating results for {workflow_id}")
            await self._update_step_status(workflow_id, "integration", WorkflowStatus.ANALYZING)
            
            integrated_results = await self._integrate_results(transcript_result, analysis_results)
            await self._update_step_result(workflow_id, "integration", WorkflowStatus.COMPLETED, integrated_results)
            
            # 워크플로우 완료
            end_time = time.time()
            processing_time = end_time - start_time
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.processing_time = processing_time
            workflow.final_results = integrated_results
            
            logger.info(f"✅ Workflow completed: {workflow_id} in {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {workflow_id}, {e}")
            workflow.status = WorkflowStatus.FAILED
            
            # 실패한 단계 찾기
            for step in workflow.steps:
                if step.status in [WorkflowStatus.TRANSCRIBING, WorkflowStatus.ANALYZING]:
                    step.status = WorkflowStatus.FAILED
                    step.error_message = str(e)
                    break
    
    async def _process_transcription(self, youtube_url: str, language: str) -> Dict[str, Any]:
        """전사 처리"""
        headers = {"X-API-Key": self.api_key}
        
        # YouTube 전사 요청
        payload = {
            "url": youtube_url,
            "language": language
        }
        
        async with aiohttp.ClientSession() as session:
            # 전사 작업 시작
            async with session.post(
                f"{self.transcription_url}/api/transcribe/youtube",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Transcription request failed: {response.status}, {error_text}")
                
                transcription_response = await response.json()
                job_id = transcription_response["job_id"]
            
            # 전사 완료 대기
            transcript_result = await self._wait_for_transcription(session, job_id, headers)
            
            return {
                "job_id": job_id,
                "transcript_id": transcript_result.get("id"),
                "transcript_text": transcript_result.get("content", ""),
                "metadata": transcript_result.get("metadata", {})
            }
    
    async def _wait_for_transcription(
        self,
        session: aiohttp.ClientSession,
        job_id: str,
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """전사 완료 대기"""
        start_time = time.time()
        
        while time.time() - start_time < self.max_wait_time:
            async with session.get(
                f"{self.transcription_url}/api/transcribe/{job_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result["status"] == "completed":
                        return result["result"]
                    elif result["status"] == "failed":
                        raise Exception(f"Transcription failed: {result.get('error')}")
                    
                    # 진행 중이면 대기
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise Exception(f"Failed to check transcription status: {response.status}")
        
        raise Exception("Transcription timeout")
    
    async def _process_analysis(self, transcript_text: str, analysis_type: str) -> Dict[str, Any]:
        """교육 분석 처리"""
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "transcript": transcript_text,
            "lesson_plan": None  # 추후 확장 가능
        }
        
        # 분석 유형별 엔드포인트 매핑
        endpoint_mapping = {
            "teaching-coach": "/api/analyze/teaching-coach",
            "dialogue-patterns": "/api/analyze/dialogue-patterns", 
            "cbil-evaluation": "/api/analyze/cbil-evaluation",
            "comprehensive": "/api/analyze/comprehensive"
        }
        
        endpoint = endpoint_mapping.get(analysis_type, "/api/analyze/comprehensive")
        
        async with aiohttp.ClientSession() as session:
            # 분석 요청
            async with session.post(
                f"{self.analysis_url}{endpoint}",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Analysis request failed: {response.status}, {error_text}")
                
                analysis_response = await response.json()
                analysis_id = analysis_response["analysis_id"]
            
            # 분석 완료 대기
            analysis_result = await self._wait_for_analysis(session, analysis_id)
            
            return {
                "analysis_type": analysis_type,
                "analysis_id": analysis_id,
                "results": analysis_result
            }
    
    async def _wait_for_analysis(
        self,
        session: aiohttp.ClientSession,
        analysis_id: str
    ) -> Dict[str, Any]:
        """분석 완료 대기"""
        start_time = time.time()
        
        while time.time() - start_time < self.max_wait_time:
            async with session.get(
                f"{self.analysis_url}/api/analysis/{analysis_id}"
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result["status"] == "completed":
                        return result["results"]
                    elif result["status"] == "failed":
                        raise Exception(f"Analysis failed: {result.get('error_message')}")
                    
                    # 진행 중이면 대기
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise Exception(f"Failed to check analysis status: {response.status}")
        
        raise Exception("Analysis timeout")
    
    async def _integrate_results(
        self,
        transcript_result: Dict[str, Any],
        analysis_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """결과 통합"""
        integrated = {
            "transcription": {
                "transcript_id": transcript_result.get("transcript_id"),
                "content": transcript_result.get("transcript_text", "")[:500] + "...",  # 미리보기
                "metadata": transcript_result.get("metadata", {})
            },
            "analyses": {},
            "summary": {
                "total_analyses": len(analysis_results),
                "processing_timestamp": datetime.now().isoformat(),
                "key_insights": []
            }
        }
        
        # 분석 결과 통합
        for analysis in analysis_results:
            analysis_type = analysis["analysis_type"]
            integrated["analyses"][analysis_type] = analysis["results"]
        
        # 종합 인사이트 생성 (간단한 버전)
        if "comprehensive" in integrated["analyses"]:
            comprehensive = integrated["analyses"]["comprehensive"]
            
            if "key_insights" in comprehensive:
                integrated["summary"]["key_insights"] = comprehensive["key_insights"]
            
            if "executive_summary" in comprehensive:
                integrated["summary"]["executive_summary"] = comprehensive["executive_summary"]
        
        return integrated
    
    async def _update_step_status(self, workflow_id: str, step_name: str, status: WorkflowStatus):
        """단계 상태 업데이트"""
        workflow = self.active_workflows[workflow_id]
        
        for step in workflow.steps:
            if step.step_name == step_name:
                step.status = status
                if status in [WorkflowStatus.TRANSCRIBING, WorkflowStatus.ANALYZING]:
                    step.started_at = datetime.now()
                break
    
    async def _update_step_result(
        self,
        workflow_id: str,
        step_name: str,
        status: WorkflowStatus,
        result: Dict[str, Any]
    ):
        """단계 결과 업데이트"""
        workflow = self.active_workflows[workflow_id]
        
        for step in workflow.steps:
            if step.step_name == step_name:
                step.status = status
                step.completed_at = datetime.now()
                step.result = result
                break
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowResult]:
        """워크플로우 상태 조회"""
        return self.active_workflows.get(workflow_id)
    
    def list_active_workflows(self) -> List[str]:
        """활성 워크플로우 목록"""
        return list(self.active_workflows.keys())
    
    def cleanup_completed_workflows(self, older_than_hours: int = 24):
        """완료된 워크플로우 정리"""
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        
        to_remove = []
        for workflow_id, workflow in self.active_workflows.items():
            if (workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED] and
                workflow.created_at.timestamp() < cutoff_time):
                to_remove.append(workflow_id)
        
        for workflow_id in to_remove:
            del self.active_workflows[workflow_id]
        
        logger.info(f"🧹 Cleaned up {len(to_remove)} old workflows")