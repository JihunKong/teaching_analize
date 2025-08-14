from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from datetime import datetime
from typing import Optional
import logging

from .models import JobStatus, TranscriptionMethod

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/aiboa")

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for Railway
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database Models
class TranscriptionJobDB(Base):
    __tablename__ = "transcription_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    file_name = Column(String)
    file_size = Column(Integer)
    duration = Column(Float)
    language = Column(String, default="ko")
    method = Column(Enum(TranscriptionMethod), default=TranscriptionMethod.WHISPER)
    
    error_message = Column(Text)
    progress = Column(Integer, default=0)
    
    # Additional metadata
    transcript_path = Column(String)
    cost_estimate = Column(Float)
    user_id = Column(String)  # For future user management
    
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "duration": self.duration,
            "language": self.language,
            "method": self.method.value if self.method else None,
            "error_message": self.error_message,
            "progress": self.progress
        }

# Database initialization
async def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

# Dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions for job management
def create_job(
    db: Session,
    job_id: str,
    file_name: Optional[str] = None,
    file_size: Optional[int] = None,
    language: str = "ko",
    method: TranscriptionMethod = TranscriptionMethod.WHISPER
) -> TranscriptionJobDB:
    """Create a new job in the database"""
    job = TranscriptionJobDB(
        job_id=job_id,
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
        file_name=file_name,
        file_size=file_size,
        language=language,
        method=method,
        progress=0
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Created job: {job_id}")
    return job

def get_job(db: Session, job_id: str) -> Optional[TranscriptionJobDB]:
    """Get job by ID"""
    return db.query(TranscriptionJobDB).filter(
        TranscriptionJobDB.job_id == job_id
    ).first()

def update_job_status(
    job_id: str,
    status: str,
    error_message: Optional[str] = None,
    duration: Optional[float] = None,
    completed_at: Optional[datetime] = None
):
    """Update job status in database"""
    db = SessionLocal()
    try:
        job = db.query(TranscriptionJobDB).filter(
            TranscriptionJobDB.job_id == job_id
        ).first()
        
        if job:
            job.status = JobStatus(status)
            job.updated_at = datetime.utcnow()
            
            if error_message:
                job.error_message = error_message
            
            if duration:
                job.duration = duration
            
            if completed_at:
                job.completed_at = completed_at
            
            db.commit()
            logger.info(f"Updated job {job_id} status to {status}")
        else:
            logger.warning(f"Job {job_id} not found for status update")
            
    except Exception as e:
        logger.error(f"Failed to update job status: {str(e)}")
        db.rollback()
    finally:
        db.close()

def update_job_progress(job_id: str, progress: int):
    """Update job progress"""
    db = SessionLocal()
    try:
        job = db.query(TranscriptionJobDB).filter(
            TranscriptionJobDB.job_id == job_id
        ).first()
        
        if job:
            job.progress = min(100, max(0, progress))
            job.updated_at = datetime.utcnow()
            db.commit()
            logger.debug(f"Updated job {job_id} progress to {progress}%")
        else:
            logger.warning(f"Job {job_id} not found for progress update")
            
    except Exception as e:
        logger.error(f"Failed to update job progress: {str(e)}")
        db.rollback()
    finally:
        db.close()

def get_jobs_by_status(
    db: Session,
    status: JobStatus,
    limit: int = 100
) -> list[TranscriptionJobDB]:
    """Get jobs by status"""
    return db.query(TranscriptionJobDB).filter(
        TranscriptionJobDB.status == status
    ).limit(limit).all()

def get_recent_jobs(
    db: Session,
    limit: int = 10
) -> list[TranscriptionJobDB]:
    """Get recent jobs"""
    return db.query(TranscriptionJobDB).order_by(
        TranscriptionJobDB.created_at.desc()
    ).limit(limit).all()

def delete_old_jobs(db: Session, days: int = 30) -> int:
    """Delete jobs older than specified days"""
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    deleted = db.query(TranscriptionJobDB).filter(
        TranscriptionJobDB.created_at < cutoff_date
    ).delete()
    
    db.commit()
    logger.info(f"Deleted {deleted} old jobs")
    return deleted

# Statistics functions
def get_job_statistics(db: Session) -> dict:
    """Get job statistics"""
    from sqlalchemy import func
    
    total_jobs = db.query(func.count(TranscriptionJobDB.id)).scalar()
    
    completed_jobs = db.query(func.count(TranscriptionJobDB.id)).filter(
        TranscriptionJobDB.status == JobStatus.COMPLETED
    ).scalar()
    
    failed_jobs = db.query(func.count(TranscriptionJobDB.id)).filter(
        TranscriptionJobDB.status == JobStatus.FAILED
    ).scalar()
    
    pending_jobs = db.query(func.count(TranscriptionJobDB.id)).filter(
        TranscriptionJobDB.status == JobStatus.PENDING
    ).scalar()
    
    processing_jobs = db.query(func.count(TranscriptionJobDB.id)).filter(
        TranscriptionJobDB.status == JobStatus.PROCESSING
    ).scalar()
    
    avg_duration = db.query(func.avg(TranscriptionJobDB.duration)).filter(
        TranscriptionJobDB.duration.isnot(None)
    ).scalar()
    
    return {
        "total_jobs": total_jobs or 0,
        "completed_jobs": completed_jobs or 0,
        "failed_jobs": failed_jobs or 0,
        "pending_jobs": pending_jobs or 0,
        "processing_jobs": processing_jobs or 0,
        "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
        "average_duration": avg_duration or 0
    }