"""
Evaluation Service FastAPI Endpoints
Comprehensive teaching evaluation API
"""

import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import HTTPException, BackgroundTasks
from pydantic import BaseModel
import redis

from core.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

# Initialize Evaluation Service
evaluation_service = EvaluationService()


class EvaluationRequest(BaseModel):
    """Evaluation request model"""
    utterances: List[Dict[str, Any]]
    context: Optional[Dict[str, Any]] = {}
    include_raw_data: bool = False
    metadata: Optional[Dict[str, Any]] = {}


class TranscriptEvaluationRequest(BaseModel):
    """Evaluation from transcript ID"""
    transcript_id: str
    speaker_filter: Optional[str] = "teacher"
    context: Optional[Dict[str, Any]] = {}
    include_raw_data: bool = False


async def process_evaluation(
    job_id: str,
    utterances: List[Dict[str, Any]],
    context: Dict[str, Any],
    include_raw_data: bool
):
    """Background task for comprehensive evaluation"""
    try:
        # Update job status
        job_data = {
            "job_id": job_id,
            "status": "processing",
            "message": "Running comprehensive evaluation...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        redis_client.setex(f"eval_job:{job_id}", 7200, json.dumps(job_data))

        # Run comprehensive evaluation
        start_time = datetime.now()
        result = await evaluation_service.evaluate_teaching(
            utterances=utterances,
            evaluation_id=job_id,
            context=context,
            include_raw_data=include_raw_data
        )
        processing_time = (datetime.now() - start_time).total_seconds()

        # Get summary
        summary = evaluation_service.get_summary(result)

        # Success
        job_data.update({
            "status": "completed",
            "message": "Comprehensive evaluation completed successfully",
            "result": evaluation_service.to_dict(result),
            "summary": summary,
            "updated_at": datetime.now().isoformat()
        })

        redis_client.setex(f"eval_job:{job_id}", 7200, json.dumps(job_data))

        logger.info(f"Evaluation {job_id} completed in {processing_time:.2f}s")

    except Exception as e:
        logger.error(f"Evaluation job {job_id} failed: {str(e)}")
        job_data.update({
            "status": "failed",
            "message": f"Evaluation failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        })
        redis_client.setex(f"eval_job:{job_id}", 7200, json.dumps(job_data))


# ================ API Endpoints ================

async def evaluate_teaching(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """
    POST /api/evaluate
    Comprehensive teaching evaluation from utterances
    """
    try:
        if not request.utterances:
            raise HTTPException(status_code=400, detail="No utterances provided")

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Initial job status
        job_data = {
            "job_id": job_id,
            "status": "pending",
            "message": "Comprehensive evaluation job submitted",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Store in Redis
        redis_client.setex(f"eval_job:{job_id}", 7200, json.dumps(job_data))

        # Add background task
        background_tasks.add_task(
            process_evaluation,
            job_id,
            request.utterances,
            request.context or {},
            request.include_raw_data
        )

        return {
            "evaluation_id": job_id,
            "status": "pending",
            "message": "Comprehensive evaluation job submitted",
            "submitted_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error submitting evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_evaluation_status(job_id: str):
    """
    GET /api/evaluate/{job_id}
    Get evaluation status and results
    """
    try:
        job_data = redis_client.get(f"eval_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Evaluation job not found")

        return json.loads(job_data)

    except Exception as e:
        logger.error(f"Error getting evaluation status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_evaluation_summary(job_id: str):
    """
    GET /api/evaluate/{job_id}/summary
    Get concise evaluation summary
    """
    try:
        job_data = redis_client.get(f"eval_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Evaluation job not found")

        job = json.loads(job_data)

        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Evaluation not completed yet")

        if "summary" not in job:
            raise HTTPException(status_code=400, detail="No summary available")

        return job["summary"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting evaluation summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_coaching_feedback(job_id: str):
    """
    GET /api/evaluate/{job_id}/coaching
    Get coaching feedback only
    """
    try:
        job_data = redis_client.get(f"eval_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Evaluation job not found")

        job = json.loads(job_data)

        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Evaluation not completed yet")

        if "result" not in job:
            raise HTTPException(status_code=400, detail="No result available")

        return job["result"]["coaching_feedback"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting coaching feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============ Documentation ============

"""
## Evaluation Service Endpoints

### POST /api/evaluate
Comprehensive teaching evaluation from utterances

Request:
```json
{
  "utterances": [
    {"id": "utt_001", "text": "Today we'll learn...", "timestamp": "00:00:30"},
    ...
  ],
  "context": {
    "subject": "Mathematics",
    "grade_level": "Grade 8",
    "duration": 45
  },
  "include_raw_data": false
}
```

Response:
```json
{
  "evaluation_id": "abc123-...",
  "status": "pending",
  "message": "Comprehensive evaluation job submitted",
  "submitted_at": "2025-11-09T15:30:00"
}
```

### GET /api/evaluate/{job_id}
Get full evaluation results

### GET /api/evaluate/{job_id}/summary
Get concise summary

### GET /api/evaluate/{job_id}/coaching
Get coaching feedback only

## Evaluation Workflow

1. **3D Matrix Analysis** (Stage × Context × Level)
2. **Quantitative Metrics** (15 metrics, 0-100 scores)
3. **Pattern Matching** (4 ideal patterns, cosine similarity)
4. **Coaching Generation** (OpenAI GPT-4, actionable feedback)

## Processing Time

- 10 utterances: 2-3 minutes
- 50 utterances: 8-12 minutes
- 100 utterances: 15-20 minutes

Includes OpenAI API calls for matrix classification + coaching generation.
"""
