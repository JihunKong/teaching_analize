"""
Workflows Router
Orchestrates multi-service workflows
"""

import logging
import uuid
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
import httpx
import redis

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/workflow",
    tags=["workflows"]
)


# Request models
class FullAnalysisRequest(BaseModel):
    video_url: HttpUrl
    framework: str = "cbil_comprehensive"
    language: str = "ko"
    use_diarization: bool = True
    metadata: Optional[Dict[str, Any]] = {}


# Redis client
redis_client: Optional[redis.Redis] = None


def get_redis():
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                decode_responses=True
            )
            redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
            redis_client = None
    return redis_client


async def get_http_client():
    """Get HTTP client with timeout"""
    return httpx.AsyncClient(timeout=settings.service_timeout)


async def run_full_analysis_workflow(
    workflow_id: str,
    video_url: str,
    framework: str,
    language: str,
    use_diarization: bool,
    metadata: Dict[str, Any]
):
    """
    Execute full analysis workflow in background

    Steps:
    1. Transcription (Module 1)
    2. Analysis (Module 2 & 3)
    3. Report Generation (Module 4)
    """
    redis_conn = get_redis()

    def update_status(step: str, status: str, message: str, data: Dict = None):
        """Update workflow status in Redis"""
        workflow_data = {
            "workflow_id": workflow_id,
            "current_step": step,
            "status": status,
            "message": message,
            "updated_at": datetime.now().isoformat()
        }
        if data:
            workflow_data["data"] = data

        if redis_conn:
            redis_conn.setex(
                f"workflow:{workflow_id}",
                7200,  # 2 hour TTL
                json.dumps(workflow_data)
            )
        logger.info(f"Workflow {workflow_id} - {step}: {message}")

    try:
        # Step 1: Transcription
        update_status("transcription", "processing", "Starting transcription...")

        async with await get_http_client() as client:
            # Submit transcription job
            transcription_response = await client.post(
                f"{settings.transcription_service_url}/api/transcribe/youtube",
                json={
                    "youtube_url": str(video_url),  # Fixed: transcription service expects 'youtube_url'
                    "language": language,
                    "use_diarization": use_diarization,
                    "metadata": metadata
                }
            )

            if transcription_response.status_code != 200:
                raise Exception(f"Transcription failed: {transcription_response.text}")

            transcription_data = transcription_response.json()
            transcript_text = None  # Initialize
            transcription_job_id = None
            segments = []  # Initialize segments

            # Check if transcription completed immediately (cache hit)
            if "result" in transcription_data and "transcript" in transcription_data["result"]:
                # Immediate completion (cached result)
                transcript_text = transcription_data["result"]["transcript"]
                transcription_job_id = transcription_data.get("job_id") or transcription_data["result"].get("transcript_id")
                segments = transcription_data["result"].get("segments", [])

                update_status(
                    "transcription",
                    "completed",
                    "Transcription completed (cache hit)",
                    {"transcription_job_id": transcription_job_id}
                )
            else:
                # Async job - need to poll
                transcription_job_id = transcription_data.get("job_id")

                update_status(
                    "transcription",
                    "processing",
                    f"Transcription job submitted: {transcription_job_id}"
                )

                # Poll for transcription completion
                max_attempts = 240  # 20 minutes (5 sec intervals)
                attempt = 0

                while attempt < max_attempts:
                    status_response = await client.get(
                        f"{settings.transcription_service_url}/api/transcribe/status/{transcription_job_id}"
                    )

                    if status_response.status_code == 200:
                        status_data = status_response.json()

                        if status_data.get("status") == "completed":
                            # Get transcript
                            result_response = await client.get(
                                f"{settings.transcription_service_url}/api/transcribe/result/{transcription_job_id}"
                            )

                            if result_response.status_code == 200:
                                transcript_data = result_response.json()
                                transcript_text = transcript_data.get("transcript", "")
                                segments = transcript_data.get("segments", [])

                                # 세그먼트 최소 개수 검증 (엄격 모드)
                                if not segments or len(segments) < 10:
                                    segment_count = len(segments) if segments else 0
                                    logger.error(f"Insufficient segments from transcription: {segment_count}")
                                    update_status(
                                        "transcription",
                                        "error",
                                        f"전사 세그먼트 부족 (최소 10개 필요, 현재 {segment_count}개)",
                                        {"transcription_job_id": transcription_job_id}
                                    )
                                    raise Exception(f"Insufficient segments: {segment_count} (minimum 10 required)")

                                update_status(
                                    "transcription",
                                    "completed",
                                    f"Transcription completed ({len(segments)} segments)",
                                    {"transcription_job_id": transcription_job_id}
                                )
                                break

                        elif status_data.get("status") == "failed":
                            raise Exception("Transcription job failed")

                    await asyncio.sleep(5)
                    attempt += 1

                if attempt >= max_attempts:
                    raise Exception("Transcription timeout")

            # Step 2: Analysis
            update_status("analysis", "processing", "Starting analysis...")

            analysis_response = await client.post(
                f"{settings.analysis_service_url}/api/analyze/text",
                json={
                    "text": transcript_text,
                    "framework": framework,
                    "segments": segments,
                    "metadata": {
                        **metadata,
                        "transcription_job_id": transcription_job_id,
                        "video_url": str(video_url)
                    }
                }
            )

            if analysis_response.status_code != 200:
                raise Exception(f"Analysis failed: {analysis_response.text}")

            analysis_data = analysis_response.json()
            analysis_job_id = analysis_data.get("analysis_id")

            update_status(
                "analysis",
                "processing",
                f"Analysis job submitted: {analysis_job_id}"
            )

            # Poll for analysis completion
            max_attempts = 120
            attempt = 0

            while attempt < max_attempts:
                status_response = await client.get(
                    f"{settings.analysis_service_url}/api/analyze/{analysis_job_id}"
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()

                    if status_data.get("status") == "completed":
                        update_status(
                            "analysis",
                            "completed",
                            "Analysis completed",
                            {
                                "transcription_job_id": transcription_job_id,
                                "analysis_id": analysis_job_id  # Changed from analysis_job_id to match frontend expectation
                            }
                        )
                        break

                    elif status_data.get("status") == "failed":
                        raise Exception("Analysis job failed")

                await asyncio.sleep(5)
                attempt += 1

            if attempt >= max_attempts:
                raise Exception("Analysis timeout")

            # Step 3: Report Generation (already available)
            update_status(
                "report_generation",
                "completed",
                "Reports available",
                {
                    "transcription_job_id": transcription_job_id,
                    "analysis_id": analysis_job_id,  # Changed from analysis_job_id to match frontend expectation
                    "reports": {
                        "html": f"/api/reports/html/{analysis_job_id}",
                        "pdf": f"/api/reports/pdf/{analysis_job_id}",
                        "pdf_enhanced": f"/api/reports/pdf-enhanced/{analysis_job_id}",
                        "excel": f"/api/reports/excel/{analysis_job_id}",
                        "3d_matrix": f"/api/reports/visualization/3d-matrix/{analysis_job_id}"
                    }
                }
            )

            # Workflow complete
            update_status(
                "completed",
                "success",
                "Full analysis workflow completed successfully",
                {
                    "transcription_job_id": transcription_job_id,
                    "analysis_id": analysis_job_id  # Changed from analysis_job_id to match frontend expectation
                }
            )

    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {e}", exc_info=True)
        update_status(
            "failed",
            "error",
            f"Workflow failed: {str(e)}"
        )


@router.post("/full-analysis")
async def start_full_analysis(
    request: FullAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start full analysis workflow

    Orchestrates: Transcription → Analysis → Report Generation
    """
    # Generate workflow ID
    workflow_id = str(uuid.uuid4())

    # Initialize workflow status
    redis_conn = get_redis()
    if redis_conn:
        redis_conn.setex(
            f"workflow:{workflow_id}",
            7200,
            json.dumps({
                "workflow_id": workflow_id,
                "current_step": "pending",
                "status": "queued",
                "message": "Workflow queued for execution",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            })
        )

    # Start workflow in background
    background_tasks.add_task(
        run_full_analysis_workflow,
        workflow_id,
        str(request.video_url),
        request.framework,
        request.language,
        request.use_diarization,
        request.metadata or {}
    )

    return {
        "workflow_id": workflow_id,
        "status": "queued",
        "message": "Full analysis workflow started",
        "submitted_at": datetime.now().isoformat(),
        "status_endpoint": f"/api/workflow/status/{workflow_id}"
    }


@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get workflow status
    """
    redis_conn = get_redis()

    if not redis_conn:
        raise HTTPException(
            status_code=503,
            detail="Status tracking unavailable (Redis not connected)"
        )

    workflow_data = redis_conn.get(f"workflow:{workflow_id}")

    if not workflow_data:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found"
        )

    return json.loads(workflow_data)
