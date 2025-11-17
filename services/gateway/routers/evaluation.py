"""
Evaluation Service Router
Proxies requests to the evaluation service (Module 3)
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/evaluate",
    tags=["evaluation"]
)


# Request models
class EvaluationRequest(BaseModel):
    utterances: List[Dict[str, Any]]
    evaluation_id: str
    context: Dict[str, Any] = {}


async def get_http_client():
    """Get HTTP client with timeout"""
    return httpx.AsyncClient(timeout=settings.service_timeout)


@router.post("/")
async def evaluate_teaching(request: EvaluationRequest):
    """
    Evaluate teaching quality

    Proxies to evaluation service
    """
    try:
        async with await get_http_client() as client:
            response = await client.post(
                f"{settings.evaluation_service_url}/api/evaluate",
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
        logger.error(f"Evaluation service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Evaluation service unavailable"
        )


@router.get("/{evaluation_id}")
async def get_evaluation_result(evaluation_id: str):
    """
    Get evaluation result

    Proxies to evaluation service
    """
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.evaluation_service_url}/api/evaluate/{evaluation_id}"
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Evaluation not found")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json()
                )

    except httpx.RequestError as e:
        logger.error(f"Evaluation service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="Evaluation service unavailable"
        )


@router.get("/health")
async def check_evaluation_service():
    """Check evaluation service health"""
    try:
        async with await get_http_client() as client:
            response = await client.get(
                f"{settings.evaluation_service_url}/health",
                timeout=5.0
            )
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
