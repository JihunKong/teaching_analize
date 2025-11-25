"""
Transcription Service Router
Proxies requests to the transcription service (Module 1)
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/transcribe",
    tags=["transcription"]
)

# Request models
class TranscriptionRequest(BaseModel):
    youtube_url: str
    language: str = "ko"
    export_format: str = "json"


class TranscriptionStatusRequest(BaseModel):
    job_id: str


# HTTP client for service communication
async def get_http_client():
    """Get HTTP client with timeout"""
    return httpx.AsyncClient(timeout=settings.service_timeout)


@router.post("/youtube")
async def transcribe_youtube(request: TranscriptionRequest):
    """
    Transcribe YouTube video

    Proxies to transcription service
    """
    try:
        async with await get_http_client() as client:
            response = await client.post(
                f"{settings.transcription_service_url}/api/transcribe/youtube",
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
        logger.error(f"Transcription service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Transcription service unavailable"
        )


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """
    Get transcription job status

    Proxies to transcription service
    Matches analysis service pattern for consistency
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.transcription_service_url}/api/transcribe/{job_id}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Job not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Transcription service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Transcription service unavailable"
        )


@router.get("/status/{job_id}")
async def get_transcription_status(job_id: str):
    """
    Get transcription job status

    Proxies to transcription service
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.transcription_service_url}/api/transcribe/status/{job_id}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Job not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Transcription service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Transcription service unavailable"
        )


@router.get("/result/{job_id}")
async def get_transcription_result(job_id: str):
    """
    Get transcription result

    Proxies to transcription service
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.transcription_service_url}/api/transcribe/result/{job_id}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Result not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Transcription service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Transcription service unavailable"
        )


@router.get("/health")
async def check_transcription_service():
    """Check transcription service health"""
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.transcription_service_url}/health",
                timeout=5.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
