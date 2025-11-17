"""
Enhanced Database Models for AIBOA Analysis Service
Supports all 13 analysis frameworks and research data accumulation
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/aiboa")

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Disable connection pooling for better compatibility
    echo=False,
    pool_pre_ping=True  # Verify connections before use
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database Models for Research Data Accumulation
class TranscriptDB(Base):
    """Store transcript data for research purposes"""
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(String, unique=True, index=True, nullable=False)

    # Video/Audio source information
    source_type = Column(String, nullable=False)  # 'youtube', 'upload', 'live'
    source_url = Column(String)  # YouTube URL or file path
    video_id = Column(String, index=True)  # YouTube video ID or file ID

    # Transcription metadata
    language = Column(String, default="ko")
    method_used = Column(String)  # 'browser_scraping', 'whisper', 'youtube_api'
    character_count = Column(Integer)
    word_count = Column(Integer)
    duration_seconds = Column(Float)

    # Educational context
    teacher_name = Column(String)
    subject = Column(String, index=True)
    grade_level = Column(String, index=True)
    school_type = Column(String)  # 'elementary', 'middle', 'high', 'university'
    lesson_title = Column(String)
    lesson_objectives = Column(Text)

    # Content
    transcript_text = Column(Text, nullable=False)
    segments_json = Column(JSON)  # Timestamped segments

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Privacy and research flags
    anonymized = Column(Boolean, default=True)
    research_consent = Column(Boolean, default=False)
    public_dataset = Column(Boolean, default=False)

    # Composite index for fast cache lookups (added 2025-01-11 for transcript caching)
    __table_args__ = (
        Index('idx_video_language', 'video_id', 'language'),
    )

class AnalysisResultDB(Base):
    """Enhanced analysis results supporting all 13 frameworks"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True, nullable=False)
    transcript_id = Column(String, index=True)  # Link to transcript
    
    # Analysis framework
    framework = Column(String, index=True, nullable=False)  # cbil, student_discussion, etc.
    framework_version = Column(String, default="1.0")
    
    # Analysis configuration
    temperature = Column(Float, default=0.3)  # LLM temperature used
    model_used = Column(String, default="solar-pro")
    prompt_version = Column(String)
    
    # Results
    analysis_text = Column(Text, nullable=False)  # Full analysis result
    structured_results = Column(JSON)  # Parsed/structured data
    scores = Column(JSON)  # Framework-specific scoring
    recommendations = Column(JSON)  # List of recommendations
    
    # Quality metrics
    confidence_score = Column(Float)  # Overall confidence in analysis
    processing_time = Column(Float)  # Time taken to process
    character_count = Column(Integer)  # Characters in input text
    word_count = Column(Integer)  # Words in input text
    
    # Educational metadata (copied from transcript)
    teacher_name = Column(String, index=True)
    subject = Column(String, index=True)
    grade_level = Column(String, index=True)
    school_type = Column(String, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    
    # Research flags
    research_approved = Column(Boolean, default=False)
    anonymized = Column(Boolean, default=True)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "analysis_id": self.analysis_id,
            "transcript_id": self.transcript_id,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "analysis_text": self.analysis_text,
            "structured_results": self.structured_results,
            "scores": self.scores,
            "recommendations": self.recommendations,
            "teacher_name": self.teacher_name,
            "subject": self.subject,
            "grade_level": self.grade_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "confidence_score": self.confidence_score,
            "processing_time": self.processing_time
        }

class TeacherProfileDB(Base):
    """Enhanced teacher profiles for research tracking"""
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, unique=True, index=True, nullable=False)
    
    # Basic information
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    anonymized_id = Column(String, unique=True)  # For research purposes
    
    # Demographics (optional, for research)
    years_experience = Column(Integer)
    education_level = Column(String)  # bachelor, master, doctorate
    certifications = Column(JSON)  # List of teaching certifications
    
    # Teaching context
    subjects = Column(JSON)  # List of subjects taught
    grade_levels = Column(JSON)  # List of grade levels taught
    school_type = Column(String)  # elementary, middle, high, university
    school_district = Column(String)  # Anonymized district identifier
    
    # Analysis history
    total_analyses = Column(Integer, default=0)
    frameworks_used = Column(JSON)  # List of frameworks used
    first_analysis = Column(DateTime)
    last_analysis = Column(DateTime)
    
    # Research participation
    research_consent = Column(Boolean, default=False)
    data_sharing_consent = Column(Boolean, default=False)
    anonymization_level = Column(String, default="full")  # full, partial, none
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class FrameworkUsageDB(Base):
    """Track framework usage for research and improvement"""
    __tablename__ = "framework_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Framework information
    framework = Column(String, index=True, nullable=False)
    framework_version = Column(String, default="1.0")
    
    # Usage statistics
    total_uses = Column(Integer, default=1)
    successful_analyses = Column(Integer, default=0)
    failed_analyses = Column(Integer, default=0)
    average_processing_time = Column(Float)
    average_confidence = Column(Float)
    
    # User patterns
    unique_users = Column(Integer, default=1)
    subjects_analyzed = Column(JSON)  # Histogram of subjects
    grade_levels_analyzed = Column(JSON)  # Histogram of grade levels
    
    # Quality metrics
    user_satisfaction = Column(Float)  # If we collect feedback
    report_downloads = Column(Integer, default=0)
    
    # Timestamps
    first_used = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class ResearchDatasetDB(Base):
    """Curated datasets for research purposes"""
    __tablename__ = "research_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String, unique=True, index=True, nullable=False)
    
    # Dataset metadata
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String, default="1.0")
    total_transcripts = Column(Integer, default=0)
    total_analyses = Column(Integer, default=0)
    
    # Filtering criteria
    subjects_included = Column(JSON)  # List of subjects
    grade_levels_included = Column(JSON)  # List of grade levels
    frameworks_included = Column(JSON)  # List of frameworks
    date_range_start = Column(DateTime)
    date_range_end = Column(DateTime)
    
    # Quality criteria
    min_confidence_score = Column(Float, default=0.7)
    min_transcript_length = Column(Integer, default=100)  # Minimum words
    max_transcript_length = Column(Integer, default=10000)  # Maximum words
    
    # Access control
    public_access = Column(Boolean, default=False)
    researcher_access = Column(Boolean, default=True)
    commercial_access = Column(Boolean, default=False)
    
    # Export information
    last_exported = Column(DateTime)
    export_format = Column(String)  # json, csv, parquet
    export_path = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# Database utility functions
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        return False

def store_transcript(db: Session, transcript_data: Dict[str, Any]) -> TranscriptDB:
    """Store transcript data for research purposes"""
    try:
        # Create transcript record
        transcript_record = TranscriptDB(
            transcript_id=transcript_data.get("transcript_id"),
            source_type=transcript_data.get("source_type", "youtube"),
            source_url=transcript_data.get("source_url"),
            video_id=transcript_data.get("video_id"),
            language=transcript_data.get("language", "ko"),
            method_used=transcript_data.get("method_used", "browser_scraping"),
            character_count=len(transcript_data.get("transcript_text", "")),
            word_count=len(transcript_data.get("transcript_text", "").split()),
            transcript_text=transcript_data.get("transcript_text"),
            segments_json=transcript_data.get("segments"),
            teacher_name=transcript_data.get("teacher_name"),
            subject=transcript_data.get("subject"),
            grade_level=transcript_data.get("grade_level"),
            school_type=transcript_data.get("school_type"),
            lesson_title=transcript_data.get("lesson_title"),
            anonymized=transcript_data.get("anonymized", True),
            research_consent=transcript_data.get("research_consent", False)
        )
        
        db.add(transcript_record)
        db.commit()
        db.refresh(transcript_record)
        
        logger.info(f"Stored transcript: {transcript_record.transcript_id}")
        return transcript_record
        
    except Exception as e:
        logger.error(f"Failed to store transcript: {str(e)}")
        db.rollback()
        raise

def store_analysis(db: Session, analysis_data: Dict[str, Any]) -> AnalysisResultDB:
    """Store analysis result for research purposes"""
    try:
        # Create analysis record
        analysis_record = AnalysisResultDB(
            analysis_id=analysis_data.get("analysis_id"),
            transcript_id=analysis_data.get("transcript_id"),
            framework=analysis_data.get("framework"),
            temperature=analysis_data.get("temperature", 0.3),
            model_used=analysis_data.get("model_used", "solar-pro"),
            analysis_text=analysis_data.get("analysis_text", ""),
            structured_results=analysis_data.get("structured_results"),
            scores=analysis_data.get("scores"),
            recommendations=analysis_data.get("recommendations"),
            processing_time=analysis_data.get("processing_time"),
            character_count=analysis_data.get("character_count", 0),
            word_count=analysis_data.get("word_count", 0),
            teacher_name=analysis_data.get("teacher_name"),
            subject=analysis_data.get("subject"),
            grade_level=analysis_data.get("grade_level"),
            school_type=analysis_data.get("school_type"),
            completed_at=datetime.utcnow(),
            anonymized=analysis_data.get("anonymized", True),
            research_approved=analysis_data.get("research_approved", False)
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
        
        logger.info(f"Stored analysis: {analysis_record.analysis_id}")
        return analysis_record
        
    except Exception as e:
        logger.error(f"Failed to store analysis: {str(e)}")
        db.rollback()
        raise

def update_framework_usage(db: Session, framework: str) -> None:
    """Update framework usage statistics"""
    try:
        usage_record = db.query(FrameworkUsageDB).filter(
            FrameworkUsageDB.framework == framework
        ).first()
        
        if usage_record:
            usage_record.total_uses += 1
            usage_record.last_used = datetime.utcnow()
        else:
            usage_record = FrameworkUsageDB(
                framework=framework,
                total_uses=1,
                first_used=datetime.utcnow(),
                last_used=datetime.utcnow()
            )
            db.add(usage_record)
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to update framework usage: {str(e)}")
        db.rollback()

def get_research_statistics(db: Session) -> Dict[str, Any]:
    """Get research statistics for dashboard"""
    try:
        stats = {
            "total_transcripts": db.query(TranscriptDB).count(),
            "total_analyses": db.query(AnalysisResultDB).count(),
            "frameworks_used": db.query(FrameworkUsageDB).count(),
            "unique_teachers": db.query(TeacherProfileDB).count(),
            "subjects_analyzed": [],
            "grade_levels_analyzed": [],
            "research_consented": db.query(TranscriptDB).filter(
                TranscriptDB.research_consent == True
            ).count()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get research statistics: {str(e)}")
        return {}

# Initialize database on import
if __name__ != "__main__":
    try:
        init_database()
    except Exception as e:
        logger.warning(f"Database initialization skipped: {str(e)}")