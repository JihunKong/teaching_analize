"""
3D Matrix Analysis Service - FastAPI Endpoints
Integrates with existing CBIL analysis service
"""

import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import redis

from core.matrix_builder import MatrixBuilder
from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

# Initialize 3D Matrix Builder
matrix_builder = MatrixBuilder()


class MatrixAnalysisRequest(BaseModel):
    """3D 매트릭스 분석 요청"""
    utterances: List[Dict[str, Any]]
    include_raw_data: bool = False
    metadata: Optional[Dict[str, Any]] = {}


class TranscriptMatrixRequest(BaseModel):
    """전사 결과로부터 3D 매트릭스 분석 요청"""
    transcript_id: str
    speaker_filter: Optional[str] = "teacher"  # "teacher", "student", "all"
    include_raw_data: bool = False
    metadata: Optional[Dict[str, Any]] = {}


def extract_utterances_from_transcript(
    transcript_data: Dict[str, Any],
    speaker_filter: str = "teacher"
) -> List[Dict[str, Any]]:
    """
    전사 결과에서 발화 리스트 추출

    Args:
        transcript_data: WhisperX transcription result
        speaker_filter: "teacher", "student", "all"

    Returns:
        [{"id": "...", "text": "...", "timestamp": "..."}, ...]
    """
    utterances = []

    # WhisperX 결과인 경우
    if "teacher_utterances" in transcript_data:
        if speaker_filter in ["teacher", "all"]:
            teacher_utts = transcript_data["teacher_utterances"]
            for i, utt in enumerate(teacher_utts):
                utterances.append({
                    "id": f"teacher_{i}",
                    "text": utt["text"],
                    "timestamp": f"{int(utt['start']//60):02d}:{int(utt['start']%60):02d}",
                    "speaker": "teacher"
                })

    # 일반 전사 결과인 경우
    elif "transcript_text" in transcript_data:
        text = transcript_data["transcript_text"]
        # 간단하게 문장 단위로 분리 (개선 가능)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        for i, sentence in enumerate(sentences):
            utterances.append({
                "id": f"utt_{i}",
                "text": sentence,
                "timestamp": None,
                "speaker": "unknown"
            })

    return utterances


async def process_matrix_analysis(
    job_id: str,
    utterances: List[Dict[str, Any]],
    include_raw_data: bool,
    metadata: Dict[str, Any]
):
    """Background task for 3D matrix analysis"""
    try:
        # Update job status
        job_data = {
            "job_id": job_id,
            "status": "processing",
            "message": "Building 3D matrix...",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        redis_client.setex(f"matrix_job:{job_id}", 3600, json.dumps(job_data))

        # Build 3D matrix
        start_time = datetime.now()
        result = await matrix_builder.build_3d_matrix(
            utterances=utterances,
            include_raw_data=include_raw_data
        )
        processing_time = (datetime.now() - start_time).total_seconds()

        # Prepare final result
        final_result = {
            "analysis_id": job_id,
            "analysis_type": "3d_matrix",
            **result,
            "metadata": metadata,
            "processing_time": processing_time,
            "created_at": datetime.now().isoformat()
        }

        # Success
        job_data.update({
            "status": "completed",
            "message": "3D matrix analysis completed successfully",
            "result": final_result,
            "updated_at": datetime.now().isoformat()
        })

        redis_client.setex(f"matrix_job:{job_id}", 3600, json.dumps(job_data))

        logger.info(f"3D matrix analysis {job_id} completed in {processing_time:.2f}s")

    except Exception as e:
        logger.error(f"Matrix analysis job {job_id} failed: {str(e)}")
        job_data.update({
            "status": "failed",
            "message": f"Analysis failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        })
        redis_client.setex(f"matrix_job:{job_id}", 3600, json.dumps(job_data))


# ================ API Endpoints ================

async def analyze_3d_matrix(request: MatrixAnalysisRequest, background_tasks: BackgroundTasks):
    """
    POST /api/analyze/3d-matrix
    3D 매트릭스 분석 실행
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
            "message": "3D matrix analysis job submitted",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Store in Redis
        redis_client.setex(f"matrix_job:{job_id}", 3600, json.dumps(job_data))

        # Add background task
        background_tasks.add_task(
            process_matrix_analysis,
            job_id,
            request.utterances,
            request.include_raw_data,
            request.metadata or {}
        )

        return {
            "analysis_id": job_id,
            "status": "pending",
            "message": "3D matrix analysis job submitted",
            "submitted_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error submitting 3D matrix analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def analyze_transcript_3d_matrix(
    request: TranscriptMatrixRequest,
    background_tasks: BackgroundTasks
):
    """
    POST /api/analyze/transcript/3d-matrix
    전사 결과로부터 3D 매트릭스 분석
    """
    try:
        # Fetch transcript from transcription service
        transcription_service_url = os.getenv("TRANSCRIPTION_SERVICE_URL", "http://transcription:8000")
        import requests
        response = requests.get(f"{transcription_service_url}/api/transcripts/{request.transcript_id}")

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Transcript not found")

        transcript_data = response.json()

        # Extract utterances
        utterances = extract_utterances_from_transcript(
            transcript_data,
            request.speaker_filter
        )

        if not utterances:
            raise HTTPException(status_code=400, detail="No utterances found in transcript")

        # Create matrix analysis request
        matrix_request = MatrixAnalysisRequest(
            utterances=utterances,
            include_raw_data=request.include_raw_data,
            metadata={
                "transcript_id": request.transcript_id,
                "speaker_filter": request.speaker_filter,
                **(request.metadata or {})
            }
        )

        # Submit for analysis
        return await analyze_3d_matrix(matrix_request, background_tasks)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing transcript for 3D matrix: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_matrix_analysis_status(job_id: str):
    """
    GET /api/analyze/3d-matrix/{job_id}
    3D 매트릭스 분석 상태 조회
    """
    try:
        job_data = redis_client.get(f"matrix_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Matrix analysis job not found")

        return json.loads(job_data)

    except Exception as e:
        logger.error(f"Error getting matrix analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_matrix_visualization_data(job_id: str):
    """
    GET /api/analyze/3d-matrix/{job_id}/visualization
    3D 매트릭스 시각화 데이터 반환
    """
    try:
        job_data = redis_client.get(f"matrix_job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Matrix analysis job not found")

        job = json.loads(job_data)

        if job.get("status") != "completed":
            raise HTTPException(status_code=400, detail="Analysis not completed yet")

        if "result" not in job:
            raise HTTPException(status_code=400, detail="No analysis result found")

        result = job["result"]
        matrix_data = result.get("matrix", {})
        statistics = result.get("statistics", {})

        # 시각화용 데이터 구성
        visualization_data = {
            "analysis_id": job_id,
            "heatmap_data": matrix_data.get("heatmap_data", []),
            "dimensions": matrix_data.get("dimensions", {}),
            "top_combinations": statistics.get("top_combinations", []),
            "stage_distribution": statistics.get("stage_stats", {}).get("stage_distribution", {}),
            "context_distribution": statistics.get("context_stats", {}).get("context_distribution", {}),
            "level_distribution": statistics.get("level_stats", {}).get("level_distribution", {}),
            "educational_complexity": statistics.get("educational_complexity", {}),
            "total_utterances": statistics.get("total_utterances", 0)
        }

        return visualization_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting visualization data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ============ 문서화용 설명 ============
"""
## 3D Matrix Analysis Endpoints

### POST /api/analyze/3d-matrix
직접 발화 리스트로부터 3D 매트릭스 분석 실행

Request:
```json
{
  "utterances": [
    {"id": "utt_001", "text": "오늘은 피타고라스 정리를 배워볼게요", "timestamp": "00:00:30"},
    {"id": "utt_002", "text": "이 공식을 사용해서 문제를 풀어보세요", "timestamp": "00:15:00"}
  ],
  "include_raw_data": false,
  "metadata": {"teacher_name": "김선생", "subject": "수학"}
}
```

### POST /api/analyze/transcript/3d-matrix
전사 결과로부터 3D 매트릭스 분석

Request:
```json
{
  "transcript_id": "abc123-def456-...",
  "speaker_filter": "teacher",
  "include_raw_data": false
}
```

### GET /api/analyze/3d-matrix/{job_id}
분석 상태 조회

### GET /api/analyze/3d-matrix/{job_id}/visualization
시각화 데이터 조회 (Chart.js, D3.js 등으로 렌더링 가능)

Returns:
```json
{
  "heatmap_data": [
    {"level": "L1", "matrix": [[5, 3, 2, 1, 0], ...]},
    {"level": "L2", "matrix": [[...]]},
    {"level": "L3", "matrix": [[...]]}
  ],
  "dimensions": {
    "stages": ["introduction", "development", "closing"],
    "contexts": ["explanation", "question", "feedback", "facilitation", "management"],
    "levels": ["L1", "L2", "L3"]
  },
  "top_combinations": [
    {"stage": "development", "context": "explanation", "level": "L2", "count": 25, "percentage": 35.7}
  ],
  "educational_complexity": {
    "cognitive_diversity": 0.75,
    "instructional_variety": 0.68,
    "progression_quality": 0.82,
    "overall_complexity": 0.75
  }
}
```
"""
