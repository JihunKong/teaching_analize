#!/usr/bin/env python3
"""Railway deployment test - Simple FastAPI application"""

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
import os
import sys
import logging
from datetime import datetime

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AIBOA Teaching Analysis - Test",
    description="Simple test app to verify Railway deployment",
    version="1.0.0"
)

# Log startup information
@app.on_event("startup")
async def startup_event():
    port = os.getenv("PORT", "8000")
    logger.info(f"🚀 Starting server on port {port}")
    logger.info(f"📍 Environment PORT: {os.getenv('PORT', 'Not set')}")
    logger.info(f"🔧 Python version: {sys.version}")
    logger.info(f"📦 Working directory: {os.getcwd()}")
    logger.info(f"📂 Files in directory: {os.listdir('.')}")

@app.get("/")
async def root():
    """Root endpoint - basic service information"""
    return JSONResponse(
        content={
            "service": "AIBOA Teaching Analysis",
            "status": "running",
            "message": "Service is operational!",
            "timestamp": datetime.now().isoformat(),
            "port": os.getenv("PORT", "8000"),
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
    """Health check endpoint for Railway"""
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )

@app.get("/api/v1/status")
async def status():
    """Detailed status endpoint"""
    return JSONResponse(
        content={
            "status": "operational",
            "version": "1.0.0",
            "uptime": "just started",
            "endpoints": ["/", "/health", "/api/v1/status", "/debug"],
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )

@app.get("/debug")
async def debug():
    """Debug endpoint to see environment variables (remove in production)"""
    # Filter out sensitive information
    safe_env_vars = {
        k: v for k, v in os.environ.items() 
        if not any(secret in k.lower() for secret in ['key', 'secret', 'password', 'token'])
    }
    
    return JSONResponse(
        content={
            "message": "Debug information",
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "files_in_directory": os.listdir('.'),
            "environment_variables": safe_env_vars,
            "port_configured": os.getenv("PORT", "8000")
        },
        status_code=200
    )

# Add a catch-all for debugging
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(path_name: str):
    """Catch-all route for debugging - shows what paths are being requested"""
    return JSONResponse(
        content={
            "message": "Catch-all route",
            "requested_path": f"/{path_name}",
            "suggestion": "Try /health or /api/v1/status"
        },
        status_code=404
    )

# This allows running directly with python main.py for local testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Running directly with uvicorn on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
