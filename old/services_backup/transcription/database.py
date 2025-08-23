from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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
        "sqlite:///./transcription.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionType(str, enum.Enum):
    FILE = "file"
    YOUTUBE = "youtube"
    AUDIO = "audio"

class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"
    
    id = Column(String, primary_key=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    type = Column(SQLEnum(TranscriptionType), default=TranscriptionType.FILE)
    
    # Input
    file_path = Column(String, nullable=True)
    youtube_url = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    duration = Column(Float, nullable=True)
    
    # Processing
    language = Column(String, default="ko")
    model = Column(String, default="whisper-1")
    
    # Output
    transcript_text = Column(Text, nullable=True)
    transcript_json = Column(JSON, nullable=True)
    transcript_srt = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Metadata
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # User info
    api_key = Column(String, nullable=True)
    user_id = Column(String, nullable=True)

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