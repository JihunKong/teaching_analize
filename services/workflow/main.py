"""
AIBOA Unified Workflow Service
Integrates transcription and analysis into a seamless workflow for regular users
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import uvicorn
import httpx

try:
    from .config import settings
    from .models import WorkflowSession, WorkflowStatus
    from .schemas import (
        WorkflowCreateRequest, WorkflowResponse, WorkflowStatusResponse,
        ErrorResponse, ProgressUpdate
    )
    from .auth import get_current_user, User
    from .services import WorkflowService, ProgressTracker
except ImportError:
    # Fallback imports for standalone execution
    import os
    from datetime import datetime
    from typing import Dict, Any, Optional
    from pydantic import BaseModel
    
    # Simple configuration
    class Settings:
        app_name = "AIBOA Workflow Service"
        app_version = "1.0.0"
        environment = os.getenv("ENVIRONMENT", "production")
        debug = os.getenv("DEBUG", "false").lower() == "true"
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = None
        host = "0.0.0.0"
        port = 8003
        reload = False
        
        # Service URLs
        transcription_service_url = os.getenv("TRANSCRIPTION_SERVICE_URL", "http://127.0.0.1:8000")
        analysis_service_url = os.getenv("ANALYSIS_SERVICE_URL", "http://127.0.0.1:8001")
        auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8002")
        
        # CORS settings
        cors_origins = ["*"]
        cors_credentials = True
        cors_methods = ["*"]
        cors_headers = ["*"]
    
    settings = Settings()
    
    # Simple models
    class User(BaseModel):
        id: int
        email: str
        full_name: str
        role: str
    
    class WorkflowCreateRequest(BaseModel):
        youtube_url: str
        language: str = "ko"
        analysis_options: Dict[str, bool] = {
            "teaching": True,
            "dialogue": True,
            "cbil": True
        }
    
    class WorkflowResponse(BaseModel):
        message: str
        workflow_id: str
        status: str
        progress_percentage: int = 0
        websocket_url: Optional[str] = None
        estimated_completion_time: Optional[datetime] = None
    
    class WorkflowStatusResponse(BaseModel):
        message: str
        workflow_id: str
        status: str
        progress_percentage: int
        transcription_progress: int = 0
        analysis_progress: int = 0
        created_at: datetime
        started_at: Optional[datetime] = None
        completed_at: Optional[datetime] = None
        estimated_completion_time: Optional[datetime] = None
        transcription_result: Optional[Dict] = None
        analysis_result: Optional[Dict] = None
        error_details: Optional[str] = None
    
    class ErrorResponse(BaseModel):
        success: bool = False
        message: str
        error_code: str
        details: Optional[Dict] = None
        timestamp: datetime
    
    # Simple workflow service
    class WorkflowService:
        def __init__(self):
            self.workflows = {}
        
        async def create_workflow(self, user_id: int, workflow_data: WorkflowCreateRequest, request_ip: str = None):
            import uuid
            workflow_id = str(uuid.uuid4())
            
            workflow = {
                "id": workflow_id,
                "user_id": user_id,
                "status": "pending",
                "progress_percentage": 0,
                "created_at": datetime.now(),
                "workflow_data": workflow_data,
                "request_ip": request_ip
            }
            
            self.workflows[workflow_id] = workflow
            return type('Workflow', (), workflow)()
        
        async def start_workflow(self, workflow_id: str, manager):
            # Start workflow processing
            workflow = self.workflows.get(workflow_id)
            if workflow:
                workflow["status"] = "running"
                workflow["started_at"] = datetime.now()
        
        async def get_workflow_status(self, workflow_id: str, user_id: int):
            workflow = self.workflows.get(workflow_id)
            if workflow and workflow["user_id"] == user_id:
                return type('Workflow', (), workflow)()
            return None
        
        async def cancel_workflow(self, workflow_id: str, user_id: int):
            workflow = self.workflows.get(workflow_id)
            if workflow and workflow["user_id"] == user_id:
                workflow["status"] = "cancelled"
                return True
            return False
        
        async def list_user_workflows(self, user_id: int, limit: int, offset: int):
            user_workflows = [w for w in self.workflows.values() if w["user_id"] == user_id]
            return [type('Workflow', (), w)() for w in user_workflows[offset:offset+limit]]
        
        async def export_results(self, workflow_id: str, user_id: int, format: str):
            workflow = self.workflows.get(workflow_id)
            if workflow and workflow["user_id"] == user_id:
                import json
                data = json.dumps(workflow, default=str, indent=2)
                return data.encode(), f"workflow_{workflow_id}.json", "application/json"
            return None, None, None
    
    class ProgressTracker:
        def __init__(self):
            pass
    
    # Simple auth function
    async def get_current_user():
        # For demo purposes, return a test user
        return User(id=1, email="test@example.com", full_name="Test User", role="admin")

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting AIBOA Unified Workflow Service...")
    
    try:
        # Initialize services
        app.state.workflow_service = WorkflowService()
        app.state.progress_tracker = ProgressTracker()
        
        # Test external service connections
        await test_external_services()
        
        logger.info(f"Service: {settings.app_name} v{settings.app_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info("Workflow service ready!")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        logger.info("Shutting down AIBOA Unified Workflow Service...")


async def test_external_services():
    """Test connections to external services"""
    async with httpx.AsyncClient() as client:
        # Test transcription service
        try:
            response = await client.get(f"{settings.transcription_service_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Transcription service connection OK")
            else:
                logger.warning(f"⚠️ Transcription service returned {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Transcription service connection failed: {e}")
        
        # Test analysis service
        try:
            response = await client.get(f"{settings.analysis_service_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Analysis service connection OK")
            else:
                logger.warning(f"⚠️ Analysis service returned {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Analysis service connection failed: {e}")
        
        # Test auth service
        try:
            response = await client.get(f"{settings.auth_service_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Auth service connection OK")
            else:
                logger.warning(f"⚠️ Auth service returned {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Auth service connection failed: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Unified workflow service for seamless transcription and analysis",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            message="Invalid request data",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
            timestamp=datetime.now()
        ).dict()
    )


# WebSocket connection manager for real-time progress updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, workflow_id: str):
        await websocket.accept()
        self.active_connections[workflow_id] = websocket
        logger.info(f"WebSocket connected for workflow {workflow_id}")
    
    def disconnect(self, workflow_id: str):
        if workflow_id in self.active_connections:
            del self.active_connections[workflow_id]
            logger.info(f"WebSocket disconnected for workflow {workflow_id}")
    
    async def send_progress_update(self, workflow_id: str, progress_data: Dict[str, Any]):
        if workflow_id in self.active_connections:
            try:
                await self.active_connections[workflow_id].send_json(progress_data)
            except Exception as e:
                logger.error(f"Failed to send progress update: {e}")
                self.disconnect(workflow_id)


manager = ConnectionManager()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "description": "Unified workflow service for transcription and analysis",
        "endpoints": {
            "create_workflow": "/api/workflow/create",
            "workflow_status": "/api/workflow/{workflow_id}",
            "progress_websocket": "/ws/progress/{workflow_id}"
        },
        "timestamp": datetime.now().isoformat()
    }


# WebSocket endpoint for real-time progress
@app.websocket("/ws/progress/{workflow_id}")
async def websocket_progress(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time progress updates"""
    await manager.connect(websocket, workflow_id)
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Echo back any messages (for heartbeat)
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(workflow_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(workflow_id)


# Workflow API endpoints
@app.post("/api/workflow/create", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new unified workflow
    
    Supports both YouTube URL and file upload workflows
    """
    try:
        workflow_service = app.state.workflow_service
        
        # Create workflow session
        workflow = await workflow_service.create_workflow(
            user_id=current_user.id,
            workflow_data=workflow_data,
            request_ip=request.client.host if request.client else None
        )
        
        # Start the workflow in background
        await workflow_service.start_workflow(workflow.id, manager)
        
        logger.info(f"Workflow created: {workflow.id} for user {current_user.id}")
        
        return WorkflowResponse(
            message="Workflow created successfully",
            workflow_id=workflow.id,
            status=workflow.status.value,
            progress_percentage=workflow.progress_percentage,
            websocket_url=f"/ws/progress/{workflow.id}",
            estimated_completion_time=workflow.estimated_completion_time
        )
        
    except Exception as e:
        logger.error(f"Create workflow error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create workflow"
        )


@app.get("/api/workflow/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get workflow status and results
    """
    try:
        workflow_service = app.state.workflow_service
        workflow = await workflow_service.get_workflow_status(workflow_id, current_user.id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowStatusResponse(
            message="Workflow status retrieved successfully",
            workflow_id=workflow.id,
            status=workflow.status.value,
            progress_percentage=workflow.progress_percentage,
            transcription_progress=workflow.transcription_progress,
            analysis_progress=workflow.analysis_progress,
            created_at=workflow.created_at,
            started_at=workflow.started_at,
            completed_at=workflow.completed_at,
            estimated_completion_time=workflow.estimated_completion_time,
            transcription_result=workflow.transcription_result,
            analysis_result=workflow.analysis_result,
            error_details=workflow.error_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workflow status error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve workflow status"
        )


@app.delete("/api/workflow/{workflow_id}")
async def cancel_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a running workflow
    """
    try:
        workflow_service = app.state.workflow_service
        success = await workflow_service.cancel_workflow(workflow_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {"message": "Workflow cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel workflow error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel workflow"
        )


@app.get("/api/workflows")
async def list_user_workflows(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """
    List user's workflows with pagination
    """
    try:
        workflow_service = app.state.workflow_service
        workflows = await workflow_service.list_user_workflows(
            current_user.id, limit, offset
        )
        
        return {
            "workflows": [
                {
                    "id": w.id,
                    "session_name": w.session_name,
                    "status": w.status.value,
                    "progress_percentage": w.progress_percentage,
                    "created_at": w.created_at,
                    "completed_at": w.completed_at,
                    "source_type": w.metadata.get("source_type") if w.metadata else None
                }
                for w in workflows
            ],
            "total": len(workflows),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"List workflows error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve workflows"
        )


# Analysis export endpoints
@app.get("/api/workflow/{workflow_id}/results/download")
async def download_workflow_results(
    workflow_id: str,
    format: str = "json",  # json, pdf, txt
    current_user: User = Depends(get_current_user)
):
    """
    Download workflow results in various formats
    """
    try:
        workflow_service = app.state.workflow_service
        file_data, filename, content_type = await workflow_service.export_results(
            workflow_id, current_user.id, format
        )
        
        from fastapi.responses import Response
        return Response(
            content=file_data,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download results error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to download results"
        )


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"Response: {response.status_code} "
        f"in {process_time:.3f}s"
    )
    
    return response


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )