"""
Core services for AIBOA Workflow Service
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

from .config import settings
from .models import (
    WorkflowSession, WorkflowStatus, SourceType, TranscriptionResult, 
    AnalysisResult, ProgressUpdate, WorkflowMetrics
)
from .schemas import WorkflowCreateRequest

logger = logging.getLogger(__name__)


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
    
    async def transcribe_file(self, file_path: str, language: str = "ko") -> Dict[str, Any]:
        """Start file transcription"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                with open(file_path, "rb") as f:
                    files = {"file": f}
                    data = {
                        "language": language,
                        "export_format": "json"
                    }
                    response = await client.post(
                        f"{settings.transcription_service_url}/api/transcribe/upload",
                        headers={"X-API-Key": settings.transcription_api_key},
                        files=files,
                        data=data
                    )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"File transcription error: {e}")
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
    
    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """Get analysis status"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{settings.analysis_service_url}/api/analyze/{analysis_id}",
                    headers={"X-API-Key": settings.analysis_api_key}
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Get analysis status error: {e}")
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
    
    async def create_workflow(self, user_id: int, workflow_data: WorkflowCreateRequest, 
                            request_ip: str = None) -> WorkflowSession:
        """Create a new workflow session"""
        
        # Create workflow session
        workflow = WorkflowSession(
            user_id=user_id,
            session_name=workflow_data.session_name or f"Workflow {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=SourceType(workflow_data.source_type),
            language=workflow_data.language,
            analysis_framework=workflow_data.analysis_framework
        )
        
        # Set source-specific data
        if workflow_data.source_type == "youtube":
            workflow.source_url = str(workflow_data.source_url)
        elif workflow_data.source_type == "upload":
            # Save uploaded file
            file_path = await self._save_uploaded_file(
                workflow_data.file_data, 
                workflow_data.filename or "upload.mp3",
                workflow.id
            )
            workflow.file_path = file_path
        
        # Add metadata
        workflow.metadata = {
            "source_type": workflow_data.source_type,
            "request_ip": request_ip,
            "description": workflow_data.description,
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
        
        return task
    
    async def _execute_workflow(self, workflow: WorkflowSession):
        """Execute the complete workflow"""
        try:
            workflow.set_status(WorkflowStatus.TRANSCRIBING)
            await self.progress_tracker.update_progress(
                workflow.id, transcription_progress=0, 
                message="Starting transcription..."
            )
            
            # Step 1: Transcription
            transcription_result = await self._handle_transcription(workflow)
            workflow.transcription_result = transcription_result
            
            await self.progress_tracker.update_progress(
                workflow.id, transcription_progress=100,
                message="Transcription completed, starting analysis..."
            )
            
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
            logger.info(f"Workflow {workflow.id} completed successfully")
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            logger.error(f"Workflow {workflow.id} failed: {e}")
            workflow.add_error(error_msg)
            await self.progress_tracker.update_progress(
                workflow.id, message=f"Error: {error_msg}"
            )
        finally:
            # Cleanup
            self.active_tasks.pop(workflow.id, None)
    
    async def _handle_transcription(self, workflow: WorkflowSession) -> TranscriptionResult:
        """Handle transcription phase"""
        if workflow.source_type == SourceType.YOUTUBE:
            # Start YouTube transcription
            response = await self.external_client.transcribe_youtube(
                workflow.source_url, workflow.language
            )
            job_id = response.get("job_id")
            
        elif workflow.source_type == SourceType.UPLOAD:
            # Start file transcription
            response = await self.external_client.transcribe_file(
                workflow.file_path, workflow.language
            )
            job_id = response.get("job_id")
        
        else:
            raise ValueError(f"Unsupported source type: {workflow.source_type}")
        
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
                
                # Update progress
                await self.progress_tracker.update_progress(
                    workflow.id, transcription_progress=progress,
                    message=f"Transcribing... {progress}%"
                )
                
                if status == "completed":
                    # Extract transcription result
                    transcript_data = status_response.get("transcript", {})
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
                logger.warning(f"Transcription polling error (attempt {poll_count}): {e}")
                continue
        
        raise Exception("Transcription timeout - job did not complete within expected time")
    
    async def _handle_analysis(self, workflow: WorkflowSession, text: str) -> AnalysisResult:
        """Handle analysis phase"""
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
    
    async def _save_uploaded_file(self, file_data: str, filename: str, workflow_id: str) -> str:
        """Save base64 encoded file data to temporary file"""
        try:
            # Decode base64 data
            file_content = base64.b64decode(file_data)
            
            # Create upload directory if not exists
            upload_dir = os.path.join(settings.upload_path, workflow_id)
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"Saved uploaded file: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise
    
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
    
    async def export_results(self, workflow_id: str, user_id: int, format: str) -> Tuple[bytes, str, str]:
        """Export workflow results in specified format"""
        workflow = await self.get_workflow_status(workflow_id, user_id)
        if not workflow:
            raise ValueError("Workflow not found")
        
        if workflow.status != WorkflowStatus.COMPLETED:
            raise ValueError("Workflow not completed")
        
        # Generate export data based on format
        if format == "json":
            return await self._export_json(workflow)
        elif format == "txt":
            return await self._export_txt(workflow)
        elif format == "pdf":
            return await self._export_pdf(workflow)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def _export_json(self, workflow: WorkflowSession) -> Tuple[bytes, str, str]:
        """Export workflow as JSON"""
        export_data = {
            "workflow": workflow.to_dict(),
            "export_timestamp": datetime.now().isoformat(),
            "export_format": "json"
        }
        
        content = json.dumps(export_data, indent=2, ensure_ascii=False)
        filename = f"workflow_{workflow.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        return content.encode('utf-8'), filename, "application/json"
    
    async def _export_txt(self, workflow: WorkflowSession) -> Tuple[bytes, str, str]:
        """Export workflow as plain text"""
        lines = [
            f"AIBOA Workflow Report - {workflow.session_name}",
            "=" * 50,
            f"Created: {workflow.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Status: {workflow.status.value}",
            f"Language: {workflow.language}",
            f"Framework: {workflow.analysis_framework}",
            "",
            "TRANSCRIPTION RESULT:",
            "-" * 30,
        ]
        
        if workflow.transcription_result:
            lines.extend([
                workflow.transcription_result.text,
                "",
                f"Word Count: {workflow.transcription_result.word_count}",
                f"Duration: {workflow.transcription_result.duration_seconds}s",
                ""
            ])
        
        lines.extend([
            "ANALYSIS RESULT:",
            "-" * 30,
        ])
        
        if workflow.analysis_result:
            lines.extend([
                f"Overall Score: {workflow.analysis_result.overall_score}",
                f"Primary Level: {workflow.analysis_result.primary_level}",
                f"Processing Time: {workflow.analysis_result.processing_time_seconds}s",
                "",
                "Detailed Results:",
                json.dumps(workflow.analysis_result.detailed_results, indent=2, ensure_ascii=False)
            ])
        
        content = "\n".join(lines)
        filename = f"workflow_{workflow.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        return content.encode('utf-8'), filename, "text/plain"
    
    async def _export_pdf(self, workflow: WorkflowSession) -> Tuple[bytes, str, str]:
        """Export workflow as PDF (placeholder implementation)"""
        # This would require a PDF generation library like reportlab
        # For now, return a simple text-based PDF placeholder
        content = f"PDF Export for Workflow {workflow.id}\n\nThis would be a formatted PDF report."
        filename = f"workflow_{workflow.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return content.encode('utf-8'), filename, "application/pdf"


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
            "external_services": await self._check_external_services()
        }
    
    async def _check_external_services(self) -> Dict[str, str]:
        """Check external service health"""
        services = {
            "transcription": settings.transcription_service_url,
            "analysis": settings.analysis_service_url,
            "auth": settings.auth_service_url
        }
        
        status = {}
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            for service_name, url in services.items():
                try:
                    response = await client.get(f"{url}/health")
                    status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
                except Exception:
                    status[service_name] = "unreachable"
        
        return status