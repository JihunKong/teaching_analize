from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from datetime import datetime
from typing import Optional
import logging

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
class AnalysisResultDB(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True, nullable=False)
    transcript_id = Column(String, index=True)  # Link to transcription job
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Analysis metadata
    teacher_name = Column(String)
    subject = Column(String)
    grade_level = Column(String)
    class_duration = Column(Integer)  # in minutes
    
    # CBIL Analysis Results
    cbil_distribution = Column(JSON)  # {level1: %, level2: %, ...}
    average_cbil_level = Column(Float)
    
    # Interaction patterns
    teacher_talk_ratio = Column(Float)  # Percentage of teacher talk
    student_talk_ratio = Column(Float)  # Percentage of student talk
    interaction_count = Column(Integer)
    
    # Question analysis
    total_questions = Column(Integer)
    open_questions = Column(Integer)
    closed_questions = Column(Integer)
    
    # Detailed analysis
    detailed_analysis = Column(JSON)  # Full analysis data
    recommendations = Column(JSON)  # List of recommendations
    
    # Report paths
    report_path = Column(String)
    visual_report_path = Column(String)
    
    def to_dict(self):
        return {
            "analysis_id": self.analysis_id,
            "transcript_id": self.transcript_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "teacher_name": self.teacher_name,
            "subject": self.subject,
            "grade_level": self.grade_level,
            "class_duration": self.class_duration,
            "cbil_distribution": self.cbil_distribution,
            "average_cbil_level": self.average_cbil_level,
            "teacher_talk_ratio": self.teacher_talk_ratio,
            "student_talk_ratio": self.student_talk_ratio,
            "interaction_count": self.interaction_count,
            "total_questions": self.total_questions,
            "open_questions": self.open_questions,
            "closed_questions": self.closed_questions,
            "recommendations": self.recommendations
        }

class TeacherProfileDB(Base):
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Teaching metadata
    subjects = Column(JSON)  # List of subjects
    grade_levels = Column(JSON)  # List of grade levels
    years_experience = Column(Integer)
    
    # Analysis history
    total_analyses = Column(Integer, default=0)
    average_cbil = Column(Float)
    improvement_trend = Column(JSON)  # Historical CBIL trends
    
    # Preferences
    preferred_language = Column(String, default="ko")
    notification_settings = Column(JSON)

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

# Helper functions for analysis management
def create_analysis(
    db: Session,
    analysis_id: str,
    transcript_id: Optional[str] = None,
    teacher_name: Optional[str] = None,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None
) -> AnalysisResultDB:
    """Create a new analysis record"""
    analysis = AnalysisResultDB(
        analysis_id=analysis_id,
        transcript_id=transcript_id,
        created_at=datetime.utcnow(),
        teacher_name=teacher_name,
        subject=subject,
        grade_level=grade_level
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    logger.info(f"Created analysis: {analysis_id}")
    return analysis

def get_analysis(db: Session, analysis_id: str) -> Optional[AnalysisResultDB]:
    """Get analysis by ID"""
    return db.query(AnalysisResultDB).filter(
        AnalysisResultDB.analysis_id == analysis_id
    ).first()

def update_analysis_results(
    db: Session,
    analysis_id: str,
    cbil_distribution: dict,
    average_cbil_level: float,
    teacher_talk_ratio: float,
    student_talk_ratio: float,
    detailed_analysis: dict,
    recommendations: list
):
    """Update analysis with results"""
    analysis = db.query(AnalysisResultDB).filter(
        AnalysisResultDB.analysis_id == analysis_id
    ).first()
    
    if analysis:
        analysis.cbil_distribution = cbil_distribution
        analysis.average_cbil_level = average_cbil_level
        analysis.teacher_talk_ratio = teacher_talk_ratio
        analysis.student_talk_ratio = student_talk_ratio
        analysis.detailed_analysis = detailed_analysis
        analysis.recommendations = recommendations
        analysis.updated_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Updated analysis results for {analysis_id}")
    else:
        logger.warning(f"Analysis {analysis_id} not found for update")

def get_recent_analyses(
    db: Session,
    limit: int = 10
) -> list[AnalysisResultDB]:
    """Get recent analyses"""
    return db.query(AnalysisResultDB).order_by(
        AnalysisResultDB.created_at.desc()
    ).limit(limit).all()

def get_teacher_analyses(
    db: Session,
    teacher_name: str,
    limit: int = 100
) -> list[AnalysisResultDB]:
    """Get analyses for a specific teacher"""
    return db.query(AnalysisResultDB).filter(
        AnalysisResultDB.teacher_name == teacher_name
    ).order_by(
        AnalysisResultDB.created_at.desc()
    ).limit(limit).all()