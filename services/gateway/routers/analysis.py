"""
Analysis Service Router
Proxies requests to the analysis service (Modules 2 & 3)
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/analyze",
    tags=["analysis"]
)


# Request models
class AnalysisRequest(BaseModel):
    text: str
    framework: str = "cbil"  # cbil, student_discussion, lesson_coaching, cbil_comprehensive
    metadata: Optional[Dict[str, Any]] = {}


class TranscriptAnalysisRequest(BaseModel):
    transcript_id: str
    framework: str = "cbil"
    metadata: Optional[Dict[str, Any]] = {}


async def get_http_client():
    """Get HTTP client with timeout"""
    return httpx.AsyncClient(timeout=settings.service_timeout)


@router.post("/text")
async def analyze_text(request: AnalysisRequest):
    """
    Analyze text using selected framework

    Proxies to analysis service
    """
    try:
        async with await get_http_client() as client:
            response = await client.post(
                f"{settings.analysis_service_url}/api/analyze/text",
                json=request.dict()
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Analysis service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Analysis service unavailable"
        )


@router.post("/transcript-by-id")
async def analyze_transcript_by_id(request: TranscriptAnalysisRequest):
    """
    Analyze transcript by ID

    Proxies to analysis service
    """
    try:
        async with await get_http_client() as client:
            response = await client.post(
                f"{settings.analysis_service_url}/api/analyze/transcript-by-id",
                json=request.dict()
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Analysis service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Analysis service unavailable"
        )


@router.get("/{job_id}")
async def get_analysis_status(job_id: str):
    """
    Get analysis job status

    Proxies to analysis service
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/analyze/{job_id}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Analysis job not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Analysis service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Analysis service unavailable"
        )


@router.get("/frameworks")
async def list_frameworks():
    """
    List available analysis frameworks

    Proxies to analysis service
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/api/analyze/frameworks"
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Analysis service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Analysis service unavailable"
        )


@router.get("/health")
async def check_analysis_service():
    """Check analysis service health"""
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.analysis_service_url}/health",
                timeout=5.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
