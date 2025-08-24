from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from typing import Generator
import enum
from config import settings

# Create engine
if settings.DATABASE_URL:
    # Railway PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
else:
    # Local SQLite for development
    engine = create_engine(
        "sqlite:///./analysis.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CBILLevel(int, enum.Enum):
    SIMPLE_CONFIRMATION = 1  # 단순 확인
    FACT_RECALL = 2          # 사실 회상
    CONCEPT_EXPLANATION = 3  # 개념 설명
    ANALYTICAL_THINKING = 4  # 분석적 사고
    COMPREHENSIVE_UNDERSTANDING = 5  # 종합적 이해
    EVALUATIVE_JUDGMENT = 6  # 평가적 판단
    CREATIVE_APPLICATION = 7 # 창의적 적용

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(String, primary_key=True)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    
    # Input
    text = Column(Text, nullable=False)
    transcript_job_id = Column(String, nullable=True)  # Link to transcription job
    source_type = Column(String, default="text")  # text, transcript, file
    
    # Metadata
    subject = Column(String, nullable=True)
    grade = Column(Integer, nullable=True)
    teacher_name = Column(String, nullable=True)
    class_date = Column(DateTime, nullable=True)
    
    # Results
    total_utterances = Column(Integer, nullable=True)
    analysis_results = Column(JSON, nullable=True)
    statistics = Column(JSON, nullable=True)
    report_path = Column(String, nullable=True)
    
    # CBIL Distribution
    level_1_count = Column(Integer, default=0)
    level_2_count = Column(Integer, default=0)
    level_3_count = Column(Integer, default=0)
    level_4_count = Column(Integer, default=0)
    level_5_count = Column(Integer, default=0)
    level_6_count = Column(Integer, default=0)
    level_7_count = Column(Integer, default=0)
    average_level = Column(Float, nullable=True)
    
    # Processing
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User info
    api_key = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    
    # Relationships
    utterances = relationship("UtteranceAnalysis", back_populates="job", cascade="all, delete-orphan")

class UtteranceAnalysis(Base):
    __tablename__ = "utterance_analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("analysis_jobs.id"))
    
    # Utterance data
    utterance_number = Column(Integer)
    text = Column(Text)
    speaker = Column(String, nullable=True)  # teacher, student, unknown
    timestamp = Column(Float, nullable=True)
    
    # CBIL Analysis
    cbil_level = Column(Integer)
    cbil_confidence = Column(Float)
    cbil_reasoning = Column(Text)
    
    # Features extracted
    features = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    
    # Relationship
    job = relationship("AnalysisJob", back_populates="utterances")

class AnalysisStatistics(Base):
    __tablename__ = "analysis_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Aggregated stats (updated periodically)
    total_analyses = Column(Integer, default=0)
    total_utterances = Column(Integer, default=0)
    
    # Average CBIL levels by subject
    math_avg_level = Column(Float, nullable=True)
    korean_avg_level = Column(Float, nullable=True)
    english_avg_level = Column(Float, nullable=True)
    science_avg_level = Column(Float, nullable=True)
    social_avg_level = Column(Float, nullable=True)
    
    # Usage stats
    daily_analyses = Column(Integer, default=0)
    weekly_analyses = Column(Integer, default=0)
    monthly_analyses = Column(Integer, default=0)
    
    # Updated timestamp
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)