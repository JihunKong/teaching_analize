"""
Minimal Viable Product - Transcription Service
Phase 1: Health checks only to verify deployment
"""
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Transcription Service (MVP)",
    version="0.1.0-mvp",
    description="Minimal deployment for health verification"
)

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    port: str
    environment: str

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Transcription Service",
        "status": "running",
        "phase": "MVP",
        "port": os.environ.get("PORT", "unknown")
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Railway monitoring"""
    return HealthResponse(
        status="healthy",
        service="transcription",
        version="0.1.0-mvp",
        timestamp=datetime.now().isoformat(),
        port=os.environ.get("PORT", "unknown"),
        environment=os.environ.get("RAILWAY_ENVIRONMENT", "unknown")
    )

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "endpoints_available": ["/", "/health", "/api/status"],
        "database": "not_connected",
        "openai": "not_configured",
        "phase": "MVP - Health checks only"
    }

# Log startup
logger.info(f"Starting Transcription Service MVP on port {os.environ.get('PORT', 'unknown')}")
logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")