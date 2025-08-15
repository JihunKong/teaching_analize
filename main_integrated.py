#!/usr/bin/env python3
"""AIBOA Integrated Service - Transcription and Analysis"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import logging
from datetime import datetime

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

# Import routers
from transcription.routers import router as transcription_router
from analysis.routers import router as analysis_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AIBOA Integrated Service",
    description="AI-Based Observation and Analysis Platform for Teaching",
    version="2.0.0-INTEGRATED",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(transcription_router)
app.include_router(analysis_router)

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    port = os.getenv("PORT", "8080")
    logger.info(f"🚀 Starting AIBOA Integrated Service on port {port}")
    logger.info(f"📍 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    logger.info(f"🔧 Python version: {sys.version}")
    logger.info(f"✅ Transcription Service: Active")
    logger.info(f"✅ Analysis Service: Active")

@app.get("/")
async def root():
    """Root endpoint - service information"""
    return JSONResponse(
        content={
            "service": "AIBOA Integrated Platform",
            "status": "operational",
            "version": "2.0.0-INTEGRATED",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "transcription": {
                    "status": "active",
                    "endpoints": [
                        "/api/transcribe/upload",
                        "/api/transcribe/youtube",
                        "/api/transcribe/{job_id}"
                    ]
                },
                "analysis": {
                    "status": "active",
                    "endpoints": [
                        "/api/analyze/text",
                        "/api/analyze/transcript",
                        "/api/analyze/results/{id}",
                        "/api/analyze/statistics"
                    ]
                }
            },
            "documentation": {
                "interactive": "/docs",
                "redoc": "/redoc"
            },
            "environment": {
                "railway_environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
                "service_name": os.getenv("RAILWAY_SERVICE_NAME", "unknown"),
                "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", "unknown")
            }
        },
        status_code=200
    )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "transcription": "healthy",
                "analysis": "healthy"
            }
        },
        status_code=200
    )

@app.get("/api/status")
async def api_status():
    """Detailed API status"""
    return JSONResponse(
        content={
            "status": "operational",
            "version": "2.0.0",
            "features": {
                "transcription": {
                    "whisper_api": "ready",
                    "youtube_support": "ready",
                    "file_upload": "ready"
                },
                "analysis": {
                    "cbil_classification": "ready",
                    "solar_llm": "ready",
                    "report_generation": "ready"
                }
            },
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested endpoint does not exist",
            "documentation": "/docs"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Running directly with uvicorn on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")