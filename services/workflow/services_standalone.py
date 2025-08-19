"""
Core services for AIBOA Workflow Service - STANDALONE VERSION
Handles workflow orchestration, external service communication, and progress tracking
"""

import asyncio
import json
import base64
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import httpx
import logging

logger = logging.getLogger(__name__)

# Simple settings for standalone execution
class Settings:
    app_name = "AIBOA Workflow Service"
    transcription_service_url = os.getenv("TRANSCRIPTION_SERVICE_URL", "http://127.0.0.1:8000")
    analysis_service_url = os.getenv("ANALYSIS_SERVICE_URL", "http://127.0.0.1:8001")
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8002")
    transcription_api_key = os.getenv("TRANSCRIPTION_API_KEY", "transcription-api-key-prod-2025")
    analysis_api_key = os.getenv("ANALYSIS_API_KEY", "analysis-api-key-prod-2025")
    upload_path = os.getenv("UPLOAD_PATH", "/tmp/workflow_uploads")

settings = Settings()

# Simple models for standalone execution
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SourceType(Enum):
    YOUTUBE = "youtube"
    UPLOAD = "upload"

class TranscriptionResult:
    def __init__(self, job_id, text, language, duration_seconds=None, word_count=None, 
                 confidence_score=None, segments=None, metadata=None):
        self.job_id = job_id
        self.text = text
        self.language = language
        self.duration_seconds = duration_seconds
        self.word_count = word_count
        self.confidence_score = confidence_score
        self.segments = segments or []
        self.metadata = metadata or {}

class AnalysisResult:
    def __init__(self, analysis_id, framework, overall_score=None, primary_level=None,
                 detailed_results=None, statistics=None, processing_time_seconds=None,
                 word_count=None, sentence_count=None, metadata=None):
        self.analysis_id = analysis_id
        self.framework = framework
        self.overall_score = overall_score
        self.primary_level = primary_level
        self.detailed_results = detailed_results or {}
        self.statistics = statistics or {}
        self.processing_time_seconds = processing_time_seconds
        self.word_count = word_count
        self.sentence_count = sentence_count
        self.metadata = metadata or {}

class ProgressUpdate:
    def __init__(self, workflow_id, status, progress_percentage, transcription_progress, 
                 analysis_progress, message):
        self.workflow_id = workflow_id
        self.status = status
        self.progress_percentage = progress_percentage
        self.transcription_progress = transcription_progress
        self.analysis_progress = analysis_progress
        self.message = message
    
    def to_dict(self):
        return {
            "workflow_id": self.workflow_id,
            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),
            "progress_percentage": self.progress_percentage,
            "transcription_progress": self.transcription_progress,
            "analysis_progress": self.analysis_progress,
            "message": self.message
        }

class WorkflowSession:
    def __init__(self, user_id, session_name, source_type, language, analysis_framework):
        import uuid
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.session_name = session_name
        self.source_type = source_type
        self.language = language
        self.analysis_framework = analysis_framework
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.progress_percentage = 0
        self.transcription_progress = 0
        self.analysis_progress = 0
        self.source_url = None
        self.file_path = None
        self.metadata = {}
        self.transcription_result = None
        self.analysis_result = None
        self.error_details = None
        self.estimated_completion_time = None

    def set_status(self, status):
        self.status = status
        if status == WorkflowStatus.TRANSCRIBING and not self.started_at:
            self.started_at = datetime.now()
        elif status == WorkflowStatus.COMPLETED:
            self.completed_at = datetime.now()

    def update_progress(self, transcription_progress=None, analysis_progress=None):
        if transcription_progress is not None:
            self.transcription_progress = transcription_progress
        if analysis_progress is not None:
            self.analysis_progress = analysis_progress
        
        # Calculate overall progress (50% transcription + 50% analysis)
        self.progress_percentage = int((self.transcription_progress + self.analysis_progress) / 2)

    def add_error(self, error_message):
        self.status = WorkflowStatus.FAILED
        self.error_details = error_message
        self.completed_at = datetime.now()

class ExternalServiceClient:
    """Client for communicating with external services"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
    
    async def transcribe_youtube(self, url: str, language: str = "ko") -> Dict[str, Any]:
        """Start YouTube transcription"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{settings.transcription_service_url}/api/transcribe/youtube",
                    headers={"X-API-Key": settings.transcription_api_key},
                    json={
                        "youtube_url": url,
                        "language": language,
                        "export_format": "json"
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"YouTube transcription error: {e}")
                raise
    
    async def get_transcription_status(self, job_id: str) -> Dict[str, Any]:
        """Get transcription job status"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{settings.transcription_service_url}/api/transcribe/{job_id}",
                    headers={"X-API-Key": settings.transcription_api_key}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Get transcription status error: {e}")
                raise
    
    async def analyze_text(self, text: str, framework: str = "cbil") -> Dict[str, Any]:
        """Analyze text with specified framework"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{settings.analysis_service_url}/api/analyze/text",
                    headers={"X-API-Key": settings.analysis_api_key},
                    json={
                        "text": text,
                        "metadata": {"framework": framework}
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Text analysis error: {e}")
                raise

class ProgressTracker:
    """Tracks and manages workflow progress"""
    
    def __init__(self):
        self.active_workflows: Dict[str, WorkflowSession] = {}
        self.progress_callbacks: Dict[str, List[callable]] = {}
    
    def register_workflow(self, workflow: WorkflowSession):
        """Register a workflow for tracking"""
        self.active_workflows[workflow.id] = workflow
        self.progress_callbacks[workflow.id] = []
    
    def unregister_workflow(self, workflow_id: str):
        """Unregister a workflow"""
        self.active_workflows.pop(workflow_id, None)
        self.progress_callbacks.pop(workflow_id, None)
    
    def add_progress_callback(self, workflow_id: str, callback: callable):
        """Add a progress update callback"""
        if workflow_id in self.progress_callbacks:
            self.progress_callbacks[workflow_id].append(callback)
    
    async def update_progress(self, workflow_id: str, transcription_progress: int = None, 
                            analysis_progress: int = None, message: str = ""):
        """Update workflow progress and notify callbacks"""
        if workflow_id not in self.active_workflows:
            return
        
        workflow = self.active_workflows[workflow_id]
        workflow.update_progress(transcription_progress, analysis_progress)
        
        # Create progress update
        progress_update = ProgressUpdate(
            workflow_id=workflow_id,
            status=workflow.status,
            progress_percentage=workflow.progress_percentage,
            transcription_progress=workflow.transcription_progress,
            analysis_progress=workflow.analysis_progress,
            message=message
        )
        
        # Notify all callbacks
        for callback in self.progress_callbacks.get(workflow_id, []):
            try:
                await callback(progress_update)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowSession]:
        """Get workflow by ID"""
        return self.active_workflows.get(workflow_id)

class WorkflowService:
    """Main workflow orchestration service"""
    
    def __init__(self):
        self.external_client = ExternalServiceClient()
        self.progress_tracker = ProgressTracker()
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    async def create_workflow(self, user_id: int, workflow_data, 
                            request_ip: str = None) -> WorkflowSession:
        """Create a new workflow session"""
        
        # Create workflow session
        workflow = WorkflowSession(
            user_id=user_id,
            session_name=getattr(workflow_data, 'session_name', None) or f"Workflow {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=SourceType.YOUTUBE,  # Hardcoded for now
            language=getattr(workflow_data, 'language', 'ko'),
            analysis_framework=getattr(workflow_data, 'analysis_framework', 'cbil')
        )
        
        # Set source-specific data
        workflow.source_url = getattr(workflow_data, 'source_url', None)
        
        # Add metadata
        workflow.metadata = {
            "source_type": "youtube",
            "request_ip": request_ip,
            "created_via": "api"
        }
        
        # Register for progress tracking
        self.progress_tracker.register_workflow(workflow)
        
        logger.info(f"Created workflow {workflow.id} for user {user_id}")
        return workflow
    
    async def start_workflow(self, workflow_id: str, websocket_manager=None):
        """Start workflow execution in background"""
        workflow = self.progress_tracker.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        logger.info(f"🚀 Starting workflow execution: {workflow_id}")
        
        # Add WebSocket progress callback if manager provided
        if websocket_manager:
            async def websocket_callback(progress_update: ProgressUpdate):
                await websocket_manager.send_progress_update(
                    workflow_id, progress_update.to_dict()
                )
            self.progress_tracker.add_progress_callback(workflow_id, websocket_callback)
        
        # Start workflow task
        task = asyncio.create_task(self._execute_workflow(workflow))
        self.active_tasks[workflow_id] = task
        
        logger.info(f"✅ Workflow task started: {workflow_id}")
        return task
    
    async def _execute_workflow(self, workflow: WorkflowSession):
        """Execute the complete workflow"""
        logger.info(f"🔄 Executing workflow: {workflow.id}")
        
        try:
            workflow.set_status(WorkflowStatus.TRANSCRIBING)
            await self.progress_tracker.update_progress(
                workflow.id, transcription_progress=0, 
                message="Starting transcription..."
            )
            
            logger.info(f"📝 Starting transcription for: {workflow.source_url}")
            
            # Step 1: Transcription
            transcription_result = await self._handle_transcription(workflow)
            workflow.transcription_result = transcription_result
            
            await self.progress_tracker.update_progress(
                workflow.id, transcription_progress=100,
                message="Transcription completed, starting analysis..."
            )
            
            logger.info(f"🧠 Starting analysis for workflow: {workflow.id}")
            
            # Step 2: Analysis
            workflow.set_status(WorkflowStatus.ANALYZING)
            analysis_result = await self._handle_analysis(workflow, transcription_result.text)
            workflow.analysis_result = analysis_result
            
            await self.progress_tracker.update_progress(
                workflow.id, analysis_progress=100,
                message="Analysis completed successfully!"
            )
            
            # Complete workflow
            workflow.set_status(WorkflowStatus.COMPLETED)
            logger.info(f"✅ Workflow {workflow.id} completed successfully")
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(f"❌ Workflow {workflow.id} failed: {e}")
            workflow.add_error(error_msg)
            await self.progress_tracker.update_progress(
                workflow.id, message=f"Error: {error_msg}"
            )
        finally:
            # Cleanup
            self.active_tasks.pop(workflow.id, None)
    
    async def _handle_transcription(self, workflow: WorkflowSession) -> TranscriptionResult:
        """Handle transcription phase"""
        logger.info(f"🎵 Starting YouTube transcription for: {workflow.source_url}")
        
        # Start YouTube transcription
        response = await self.external_client.transcribe_youtube(
            workflow.source_url, workflow.language
        )
        job_id = response.get("job_id")
        logger.info(f"📋 Transcription job started: {job_id}")
        
        # Poll for transcription completion
        max_polls = 60  # 5 minutes with 5-second intervals
        poll_count = 0
        
        while poll_count < max_polls:
            await asyncio.sleep(5)  # Wait 5 seconds between polls
            poll_count += 1
            
            try:
                status_response = await self.external_client.get_transcription_status(job_id)
                status = status_response.get("status")
                progress = status_response.get("progress", 0)
                
                logger.info(f"📊 Transcription progress: {progress}% (status: {status})")
                
                # Update progress
                await self.progress_tracker.update_progress(
                    workflow.id, transcription_progress=progress,
                    message=f"Transcribing... {progress}%"
                )
                
                if status == "completed":
                    # Extract transcription result - FIX: use "result" instead of "transcript"
                    transcript_data = status_response.get("result", {})
                    logger.info(f"✅ Transcription completed: {len(transcript_data.get('text', ''))} characters")
                    return TranscriptionResult(
                        job_id=job_id,
                        text=transcript_data.get("text", ""),
                        language=workflow.language,
                        duration_seconds=transcript_data.get("duration_seconds"),
                        word_count=len(transcript_data.get("text", "").split()),
                        confidence_score=transcript_data.get("confidence_score"),
                        segments=transcript_data.get("segments", []),
                        metadata=transcript_data.get("metadata", {})
                    )
                
                elif status == "failed":
                    raise Exception(f"Transcription failed: {status_response.get('error', 'Unknown error')}")
                
            except Exception as e:
                if poll_count >= max_polls - 1:  # Last attempt
                    raise
                logger.warning(f"⚠️ Transcription polling error (attempt {poll_count}): {e}")
                continue
        
        raise Exception("Transcription timeout - job did not complete within expected time")
    
    async def _handle_analysis(self, workflow: WorkflowSession, text: str) -> AnalysisResult:
        """Handle analysis phase"""
        logger.info(f"🧠 Starting analysis for {len(text)} characters")
        
        # Start analysis
        await self.progress_tracker.update_progress(
            workflow.id, analysis_progress=10,
            message="Starting text analysis..."
        )
        
        response = await self.external_client.analyze_text(text, workflow.analysis_framework)
        
        # Update progress incrementally
        for progress in [30, 60, 80, 100]:
            await asyncio.sleep(1)  # Simulate processing time
            await self.progress_tracker.update_progress(
                workflow.id, analysis_progress=progress,
                message=f"Analyzing... {progress}%"
            )
        
        # Extract analysis result
        analysis_data = response.get("analysis", {})
        
        logger.info(f"✅ Analysis completed with score: {analysis_data.get('overall_score')}")
        
        return AnalysisResult(
            analysis_id=response.get("id", ""),
            framework=workflow.analysis_framework,
            overall_score=analysis_data.get("overall_score"),
            primary_level=analysis_data.get("primary_level"),
            detailed_results=analysis_data.get("detailed_results", {}),
            statistics=analysis_data.get("statistics", {}),
            processing_time_seconds=analysis_data.get("processing_time_seconds"),
            word_count=analysis_data.get("word_count"),
            sentence_count=analysis_data.get("sentence_count"),
            metadata=analysis_data.get("metadata", {})
        )
    
    async def get_workflow_status(self, workflow_id: str, user_id: int) -> Optional[WorkflowSession]:
        """Get workflow status"""
        workflow = self.progress_tracker.get_workflow(workflow_id)
        if workflow and workflow.user_id == user_id:
            return workflow
        return None
    
    async def cancel_workflow(self, workflow_id: str, user_id: int) -> bool:
        """Cancel a running workflow"""
        workflow = self.progress_tracker.get_workflow(workflow_id)
        if not workflow or workflow.user_id != user_id:
            return False
        
        # Cancel the task if running
        if workflow_id in self.active_tasks:
            task = self.active_tasks[workflow_id]
            task.cancel()
            self.active_tasks.pop(workflow_id, None)
        
        # Update workflow status
        workflow.set_status(WorkflowStatus.CANCELLED)
        await self.progress_tracker.update_progress(
            workflow_id, message="Workflow cancelled by user"
        )
        
        logger.info(f"Workflow {workflow_id} cancelled by user {user_id}")
        return True
    
    async def list_user_workflows(self, user_id: int, limit: int = 20, offset: int = 0) -> List[WorkflowSession]:
        """List user's workflows"""
        # In a real implementation, this would query a database
        # For now, return active workflows for the user
        user_workflows = [
            workflow for workflow in self.progress_tracker.active_workflows.values()
            if workflow.user_id == user_id
        ]
        
        # Apply pagination
        return user_workflows[offset:offset + limit]

class HealthService:
    """Service health monitoring"""
    
    def __init__(self, workflow_service: WorkflowService):
        self.workflow_service = workflow_service
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            "service": "healthy",
            "active_workflows": len(self.workflow_service.progress_tracker.active_workflows),
            "active_tasks": len(self.workflow_service.active_tasks),
            "timestamp": datetime.now().isoformat(),
        }