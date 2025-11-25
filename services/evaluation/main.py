#!/usr/bin/env python3
"""
Evaluation Service Stub
Temporary stub until evaluation logic is extracted from analysis service
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

app = FastAPI(
    title="AIBOA Evaluation Service (Stub)",
    version="0.1.0",
    description="Stub service - Evaluation logic currently in Analysis service"
)

class EvaluationRequest(BaseModel):
    """Stub evaluation request"""
    analysis_id: str
    framework: str = "cbil_comprehensive"
    metadata: Optional[Dict[str, Any]] = {}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "evaluation",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "note": "Stub service - Evaluation logic in Analysis service"
    }

@app.post("/api/evaluate")
async def evaluate_stub(request: EvaluationRequest):
    """
    Stub evaluation endpoint
    
    NOTE: This is a stub. Actual evaluation logic is in the Analysis service.
    The gateway should route evaluation requests to the Analysis service.
    """
    return {
        "message": "Evaluation stub - Please use Analysis service for evaluation",
        "analysis_id": request.analysis_id,
        "framework": request.framework,
        "redirect_to": "http://analysis:8000/api/evaluate",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AIBOA Evaluation Service (Stub)",
        "version": "0.1.0",
        "status": "running",
        "note": "This is a stub service. Evaluation logic is in Analysis service."
    }
