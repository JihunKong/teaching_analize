"""
Database models for AIBOA Authentication Service
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, DECIMAL, JSON, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class UserRole(Base):
    """User roles definition table"""
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    permissions = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationship
    users = relationship("User", back_populates="role_ref")


class User(Base):
    """Main users table with role-based access"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), ForeignKey("user_roles.name"), nullable=False, default="regular_user")
    status = Column(String(50), nullable=False, default="active")
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    login_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"))
    profile_image_url = Column(Text)
    preferences = Column(JSONB, default={})
    user_metadata = Column("metadata", JSONB, default={})
    
    # Teacher-specific fields
    school = Column(String(255))
    subject = Column(String(100))
    grade_level = Column(String(50))
    role_description = Column(Text)
    privacy_consent = Column(Boolean, default=False)
    created_by_admin = Column(Boolean, default=False)
    
    # Relationships
    role_ref = relationship("UserRole", back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    password_resets = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    creator = relationship("User", remote_side=[id])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for API responses"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "status": self.status,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "login_count": self.login_count,
            "profile_image_url": self.profile_image_url,
            "preferences": self.preferences or {},
            "school": self.school,
            "subject": self.subject,
            "grade_level": self.grade_level,
            "role_description": self.role_description,
            "privacy_consent": self.privacy_consent,
            "created_by_admin": self.created_by_admin
        }


class UserSession(Base):
    """User sessions for JWT token management"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True)
    device_info = Column(JSONB, default={})
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    ip_address = Column(INET)
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="sessions")


class PasswordResetToken(Base):
    """Password reset tokens"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="password_resets")


class TranscriptionJob(Base):
    """Enhanced transcription jobs with user ownership"""
    __tablename__ = "transcription_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    progress = Column(Integer, default=0)
    source_type = Column(String(50), nullable=False)  # 'youtube', 'upload'
    source_url = Column(Text)
    filename = Column(Text)
    language = Column(String(10), default="ko")
    export_format = Column(String(20), default="json")
    file_size = Column(BigInteger)
    duration_seconds = Column(Integer)
    transcript_text = Column(Text)
    user_metadata = Column("metadata", JSONB, default={})
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    is_public = Column(Boolean, default=False)
    shared_with = Column(JSONB, default=[])
    
    # Relationships
    user = relationship("User")
    analysis_results = relationship("AnalysisResult", back_populates="transcription_job")
    workflow_sessions = relationship("WorkflowSession", back_populates="transcription_job")


class AnalysisResult(Base):
    """Enhanced analysis results with user ownership"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transcription_job_id = Column(Integer, ForeignKey("transcription_jobs.id", ondelete="CASCADE"))
    analysis_type = Column(String(50), nullable=False, default="comprehensive")
    framework = Column(String(50), nullable=False, default="cbil")
    input_text = Column(Text, nullable=False)
    results = Column(JSONB, nullable=False)
    overall_score = Column(DECIMAL(5, 2))
    primary_level = Column(String(100))
    processing_time_seconds = Column(DECIMAL(8, 3))
    word_count = Column(Integer)
    sentence_count = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    is_public = Column(Boolean, default=False)
    shared_with = Column(JSONB, default=[])
    user_metadata = Column("metadata", JSONB, default={})
    
    # Relationships
    user = relationship("User")
    transcription_job = relationship("TranscriptionJob", back_populates="analysis_results")
    workflow_sessions = relationship("WorkflowSession", back_populates="analysis_result")


class WorkflowSession(Base):
    """Unified workflow sessions for integrated transcription + analysis"""
    __tablename__ = "workflow_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_name = Column(String(255))
    status = Column(String(50), nullable=False, default="initiated")  # initiated, transcribing, analyzing, completed, failed
    transcription_job_id = Column(Integer, ForeignKey("transcription_jobs.id"))
    analysis_result_id = Column(Integer, ForeignKey("analysis_results.id"))
    progress_percentage = Column(Integer, default=0)
    transcription_progress = Column(Integer, default=0)
    analysis_progress = Column(Integer, default=0)
    estimated_completion_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    user_metadata = Column("metadata", JSONB, default={})
    error_details = Column(Text)
    
    # Relationships
    user = relationship("User")
    transcription_job = relationship("TranscriptionJob", back_populates="workflow_sessions")
    analysis_result = relationship("AnalysisResult", back_populates="workflow_sessions")


class DataAccessPermission(Base):
    """Fine-grained data access permissions"""
    __tablename__ = "data_access_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False)  # 'transcription', 'analysis', 'workflow', 'report'
    resource_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_type = Column(String(50), nullable=False)  # 'read', 'write', 'share', 'delete'
    granted_by = Column(Integer, ForeignKey("users.id"))
    granted_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])


class UserActivityLog(Base):
    """User activity logs for admin monitoring"""
    __tablename__ = "user_activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSONB, default={})
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now())
    session_id = Column(String(255))
    
    # Relationships
    user = relationship("User")


class UsageStatistic(Base):
    """Usage statistics for analytics"""
    __tablename__ = "usage_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 4))
    aggregation_period = Column(String(20), nullable=False)  # 'daily', 'weekly', 'monthly'
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    user_metadata = Column("metadata", JSONB, default={})
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")


class GeneratedReport(Base):
    """Generated reports tracking"""
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    file_path = Column(Text)
    file_size = Column(BigInteger)
    parameters = Column(JSONB, default={})
    status = Column(String(50), default="generating")
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    downloaded_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")


class SystemSetting(Base):
    """System settings and configuration"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(JSONB, nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    updated_by = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    updater = relationship("User")