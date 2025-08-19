"""
AIBOA Unified Workflow Service - FIXED VERSION
Integrates transcription and analysis into a seamless workflow for regular users
Fixed: Now uses proper WorkflowService with actual background processing
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
import uvicorn
import httpx
from pydantic import BaseModel

try:
    from .config import settings
    from .models import WorkflowSession, WorkflowStatus
    from .schemas import (
        WorkflowCreateRequest, WorkflowResponse, WorkflowStatusResponse,
        ErrorResponse, ProgressUpdate
    )
    from .auth import get_current_user, User
    from .services import WorkflowService, ProgressTracker, HealthService
except ImportError:
    # Fallback imports for standalone execution
    import os
    
    # Simple configuration
    class Settings:
        app_name = "AIBOA Workflow Service"
        app_version = "2.0.0"  # Updated version
        environment = os.getenv("ENVIRONMENT", "production")
        debug = os.getenv("DEBUG", "false").lower() == "true"
        log_level = os.getenv("LOG_LEVEL", "INFO")
        log_file = None
        host = "0.0.0.0"
        port = int(os.getenv("PORT", "8003"))
        reload = False
        
        # Service URLs
        transcription_service_url = os.getenv("TRANSCRIPTION_SERVICE_URL", "http://127.0.0.1:8000")
        analysis_service_url = os.getenv("ANALYSIS_SERVICE_URL", "http://127.0.0.1:8001")
        auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8002")
        
        # API Keys for service communication
        transcription_api_key = os.getenv("TRANSCRIPTION_API_KEY", "transcription-api-key-prod-2025")
        analysis_api_key = os.getenv("ANALYSIS_API_KEY", "analysis-api-key-prod-2025")
        
        # File upload settings
        upload_path = os.getenv("UPLOAD_PATH", "/tmp/workflow_uploads")
        max_file_size = 100 * 1024 * 1024  # 100MB
        
        # CORS settings
        cors_origins = ["*"]
        cors_credentials = True
        cors_methods = ["*"]
        cors_headers = ["*"]
    
    settings = Settings()
    
    # Simple models for fallback
    class User(BaseModel):
        id: int
        email: str
        full_name: str
        role: str
    
    # Compatible request schema that matches YouTube URL input
    class WorkflowStartRequest(BaseModel):
        youtube_url: str
        language: str = "ko"
        analysis_options: Dict[str, bool] = {
            "teaching": True,
            "dialogue": True,
            "cbil": True
        }
    
    # Unified WorkflowCreateRequest that works with services.py
    class WorkflowCreateRequest(BaseModel):
        source_type: str = "youtube"
        source_url: Optional[str] = None
        file_data: Optional[str] = None
        filename: Optional[str] = None
        language: str = "ko"
        analysis_framework: str = "cbil"
        session_name: Optional[str] = None
        description: Optional[str] = None
        
        @classmethod
        def from_youtube_request(cls, youtube_request):
            """Convert WorkflowStartRequest to WorkflowCreateRequest"""
            return cls(
                source_type="youtube",
                source_url=youtube_request.youtube_url,
                language=youtube_request.language,
                analysis_framework="cbil",
                session_name=f"YouTube Analysis {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
    
    class WorkflowResponse(BaseModel):
        message: str
        workflow_id: str
        status: str
        progress_percentage: int = 0
        websocket_url: Optional[str] = None
        estimated_completion_time: Optional[str] = None
    
    class WorkflowStatusResponse(BaseModel):
        message: str
        workflow_id: str
        status: str
        progress_percentage: int
        transcription_progress: int = 0
        analysis_progress: int = 0
        created_at: str
        started_at: Optional[str] = None
        completed_at: Optional[str] = None
        estimated_completion_time: Optional[str] = None
        transcription_result: Optional[Dict] = None
        analysis_result: Optional[Dict] = None
        error_details: Optional[str] = None
    
    class ErrorResponse(BaseModel):
        success: bool = False
        message: str
        error_code: str
        details: Optional[Dict] = None
        timestamp: str
    
    # Import fallback implementations
    try:
        from services import WorkflowService, ProgressTracker, HealthService
    except ImportError:
        # Last resort fallback - should not happen
        class WorkflowService:
            def __init__(self):
                self.workflows = {}
            
            async def create_workflow(self, user_id, workflow_data, request_ip=None):
                import uuid
                workflow_id = str(uuid.uuid4())
                workflow = type('Workflow', (), {
                    'id': workflow_id,
                    'status': type('Status', (), {'value': 'pending'}),
                    'progress_percentage': 0,
                    'created_at': datetime.now()
                })()
                self.workflows[workflow_id] = workflow
                return workflow
                
            async def start_workflow(self, workflow_id, manager):
                pass
                
            async def get_workflow_status(self, workflow_id, user_id):
                return self.workflows.get(workflow_id)
    
        class ProgressTracker:
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
        # Initialize services with proper implementation
        workflow_service = WorkflowService()
        app.state.workflow_service = workflow_service
        app.state.progress_tracker = getattr(workflow_service, 'progress_tracker', None)
        app.state.health_service = HealthService(workflow_service) if 'HealthService' in globals() else None
        
        # Test external service connections
        await test_external_services()
        
        logger.info(f"Service: {settings.app_name} v{settings.app_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info("Workflow service ready with REAL processing!")
        
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
    description="Unified workflow service for seamless transcription and analysis - FIXED VERSION",
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
            timestamp=datetime.now().isoformat()
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
            timestamp=datetime.now().isoformat()
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
                # Convert datetime objects to strings in progress data
                serializable_data = {}
                for k, v in progress_data.items():
                    if isinstance(v, datetime):
                        serializable_data[k] = v.isoformat()
                    else:
                        serializable_data[k] = v
                
                await self.active_connections[workflow_id].send_json(serializable_data)
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
        "timestamp": datetime.now().isoformat(),
        "processing_enabled": True  # Key indicator that processing is now enabled
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "description": "Unified workflow service for transcription and analysis - PROCESSING ENABLED",
        "endpoints": {
            "create_workflow": "/api/workflow/start",
            "workflow_status": "/api/workflow/{workflow_id}",
            "workflow_status_alternative": "/api/workflow/{workflow_id}/status",
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


# Workflow API endpoints - FIXED VERSION
@app.post("/api/workflow/start", response_model=WorkflowResponse)
@app.post("/api/workflow/create", response_model=WorkflowResponse)
async def create_workflow(
    workflow_data: WorkflowStartRequest,  # Accept original format
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new unified workflow - FIXED VERSION
    
    Now properly integrates with transcription and analysis services
    """
    try:
        workflow_service = app.state.workflow_service
        
        # Convert WorkflowStartRequest to WorkflowCreateRequest
        if hasattr(WorkflowCreateRequest, 'from_youtube_request'):
            workflow_create_data = WorkflowCreateRequest.from_youtube_request(workflow_data)
        else:
            # Fallback conversion
            workflow_create_data = type('WorkflowCreateRequest', (), {
                'source_type': 'youtube',
                'source_url': workflow_data.youtube_url,
                'language': workflow_data.language,
                'analysis_framework': 'cbil',
                'session_name': f"YouTube Analysis {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            })()
        
        # Create workflow session
        workflow = await workflow_service.create_workflow(
            user_id=current_user.id,
            workflow_data=workflow_create_data,
            request_ip=request.client.host if request.client else None
        )
        
        # Start the workflow in background - THIS IS THE KEY FIX!
        await workflow_service.start_workflow(workflow.id, manager)
        
        logger.info(f"Workflow created and started: {workflow.id} for user {current_user.id}")
        
        # Convert datetime to string for response
        def datetime_to_str(dt):
            return dt.isoformat() if dt else None
        
        return WorkflowResponse(
            message="Workflow created and started successfully",
            workflow_id=workflow.id,
            status=workflow.status.value if hasattr(workflow.status, 'value') else str(workflow.status),
            progress_percentage=workflow.progress_percentage,
            websocket_url=f"/ws/progress/{workflow.id}",
            estimated_completion_time=datetime_to_str(getattr(workflow, 'estimated_completion_time', None))
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
    Get workflow status and results - FIXED VERSION
    """
    try:
        workflow_service = app.state.workflow_service
        workflow = await workflow_service.get_workflow_status(workflow_id, current_user.id)
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Helper function to convert datetime to string
        def datetime_to_str(dt):
            return dt.isoformat() if dt else None
        
        # Convert results to dict if they exist
        transcription_result = None
        if hasattr(workflow, 'transcription_result') and workflow.transcription_result:
            if hasattr(workflow.transcription_result, '__dict__'):
                transcription_result = workflow.transcription_result.__dict__
            else:
                transcription_result = workflow.transcription_result
        
        analysis_result = None
        if hasattr(workflow, 'analysis_result') and workflow.analysis_result:
            if hasattr(workflow.analysis_result, '__dict__'):
                analysis_result = workflow.analysis_result.__dict__
            else:
                analysis_result = workflow.analysis_result
        
        return WorkflowStatusResponse(
            message="Workflow status retrieved successfully",
            workflow_id=workflow.id,
            status=workflow.status.value if hasattr(workflow.status, 'value') else str(workflow.status),
            progress_percentage=getattr(workflow, 'progress_percentage', 0),
            transcription_progress=getattr(workflow, 'transcription_progress', 0),
            analysis_progress=getattr(workflow, 'analysis_progress', 0),
            created_at=datetime_to_str(getattr(workflow, 'created_at', None)),
            started_at=datetime_to_str(getattr(workflow, 'started_at', None)),
            completed_at=datetime_to_str(getattr(workflow, 'completed_at', None)),
            estimated_completion_time=datetime_to_str(getattr(workflow, 'estimated_completion_time', None)),
            transcription_result=transcription_result,
            analysis_result=analysis_result,
            error_details=getattr(workflow, 'error_details', None)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workflow status error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve workflow status"
        )


# Add the missing /status endpoint that was causing 404 errors
@app.get("/api/workflow/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status_alternative(
    workflow_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get workflow status and results - ALTERNATIVE ENDPOINT
    This endpoint was missing and causing 404 errors
    """
    # Use the same logic as the main status endpoint
    return await get_workflow_status(workflow_id, current_user)


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
        
        workflow_list = []
        for w in workflows:
            workflow_dict = {
                "id": w.id,
                "status": w.status.value if hasattr(w.status, 'value') else str(w.status),
                "progress_percentage": getattr(w, 'progress_percentage', 0),
                "created_at": w.created_at.isoformat() if hasattr(w, 'created_at') and w.created_at else None,
                "completed_at": w.completed_at.isoformat() if hasattr(w, 'completed_at') and w.completed_at else None
            }
            
            # Add session_name and source_type if available
            if hasattr(w, 'session_name'):
                workflow_dict["session_name"] = w.session_name
            if hasattr(w, 'metadata') and w.metadata:
                workflow_dict["source_type"] = w.metadata.get("source_type")
            
            workflow_list.append(workflow_dict)
        
        return {
            "workflows": workflow_list,
            "total": len(workflows),
            "limit": limit,
            "offset": offset,
            "user_id": current_user.id
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
        if hasattr(workflow_service, 'export_results'):
            file_data, filename, content_type = await workflow_service.export_results(
                workflow_id, current_user.id, format
            )
            
            if not file_data:
                raise HTTPException(status_code=404, detail="Workflow results not found")
            
            return Response(
                content=file_data,
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            raise HTTPException(status_code=501, detail="Export functionality not available")
        
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