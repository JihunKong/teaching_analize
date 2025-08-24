from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from ..models import TranscriptionJob, JobStatus, JobListResponse
from ..database import get_db

router = APIRouter()

@router.get("/{job_id}", response_model=TranscriptionJob)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = get_job_from_db(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.get("/", response_model=JobListResponse)
async def list_jobs(
    status: Optional[JobStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    # Query jobs from database with filters
    query = db.query(TranscriptionJobDB)
    
    if status:
        query = query.filter(TranscriptionJobDB.status == status)
    
    if created_after:
        query = query.filter(TranscriptionJobDB.created_at >= created_after)
    
    if created_before:
        query = query.filter(TranscriptionJobDB.created_at <= created_before)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    jobs = query.offset(offset).limit(page_size).all()
    
    return JobListResponse(
        jobs=[convert_db_to_model(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size
    )

@router.delete("/{job_id}")
async def cancel_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = get_job_from_db(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in [JobStatus.PENDING, JobStatus.PROCESSING]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Update job status to failed/cancelled
    job.status = JobStatus.FAILED
    job.error_message = "Job cancelled by user"
    job.updated_at = datetime.utcnow()
    db.commit()
    
    # TODO: Cancel Celery task if running
    
    return {"message": "Job cancelled successfully"}

@router.post("/{job_id}/retry")
async def retry_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    job = get_job_from_db(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.FAILED:
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed jobs. Current status: {job.status}"
        )
    
    # Reset job status
    job.status = JobStatus.PENDING
    job.error_message = None
    job.progress = 0
    job.updated_at = datetime.utcnow()
    db.commit()
    
    # TODO: Re-queue the job for processing
    
    return {"message": "Job queued for retry", "job_id": job_id}

@router.get("/stats/summary")
async def get_job_statistics(
    db: Session = Depends(get_db)
):
    # Get statistics for the last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    
    stats = {
        "total_jobs": db.query(TranscriptionJobDB).count(),
        "last_24_hours": {
            "completed": db.query(TranscriptionJobDB).filter(
                TranscriptionJobDB.status == JobStatus.COMPLETED,
                TranscriptionJobDB.completed_at >= since
            ).count(),
            "failed": db.query(TranscriptionJobDB).filter(
                TranscriptionJobDB.status == JobStatus.FAILED,
                TranscriptionJobDB.updated_at >= since
            ).count(),
            "pending": db.query(TranscriptionJobDB).filter(
                TranscriptionJobDB.status == JobStatus.PENDING
            ).count(),
            "processing": db.query(TranscriptionJobDB).filter(
                TranscriptionJobDB.status == JobStatus.PROCESSING
            ).count()
        },
        "average_processing_time": calculate_average_processing_time(db),
        "success_rate": calculate_success_rate(db)
    }
    
    return stats

# Helper functions
from ..database import TranscriptionJobDB

def get_job_from_db(db: Session, job_id: str):
    return db.query(TranscriptionJobDB).filter(TranscriptionJobDB.job_id == job_id).first()

def convert_db_to_model(db_job: TranscriptionJobDB) -> TranscriptionJob:
    return TranscriptionJob(
        job_id=db_job.job_id,
        status=db_job.status,
        created_at=db_job.created_at,
        updated_at=db_job.updated_at,
        completed_at=db_job.completed_at,
        file_name=db_job.file_name,
        file_size=db_job.file_size,
        duration=db_job.duration,
        language=db_job.language,
        method=db_job.method,
        error_message=db_job.error_message,
        progress=db_job.progress
    )

def calculate_average_processing_time(db: Session) -> float:
    # Calculate average time from pending to completed
    completed_jobs = db.query(TranscriptionJobDB).filter(
        TranscriptionJobDB.status == JobStatus.COMPLETED,
        TranscriptionJobDB.completed_at.isnot(None)
    ).limit(100).all()
    
    if not completed_jobs:
        return 0.0
    
    total_time = sum(
        (job.completed_at - job.created_at).total_seconds()
        for job in completed_jobs
    )
    
    return total_time / len(completed_jobs)

def calculate_success_rate(db: Session) -> float:
    total = db.query(TranscriptionJobDB).filter(
        TranscriptionJobDB.status.in_([JobStatus.COMPLETED, JobStatus.FAILED])
    ).count()
    
    if total == 0:
        return 100.0
    
    completed = db.query(TranscriptionJobDB).filter(
        TranscriptionJobDB.status == JobStatus.COMPLETED
    ).count()
    
    return (completed / total) * 100