"""
Pydantic schemas for AIBOA Authentication Service
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
import uuid


# ============================================
# Base Schemas
# ============================================

class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseResponse):
    """Error response schema"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# ============================================
# User Role Schemas
# ============================================

class UserRoleBase(BaseModel):
    """Base user role schema"""
    name: str = Field(..., max_length=50)
    display_name: str = Field(..., max_length=100)
    description: Optional[str] = None
    permissions: Dict[str, Any]
    is_active: bool = True


class UserRoleCreate(UserRoleBase):
    """Schema for creating a user role"""
    pass


class UserRoleUpdate(BaseModel):
    """Schema for updating a user role"""
    display_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class UserRole(UserRoleBase):
    """User role response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# ============================================
# User Schemas
# ============================================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(default="regular_user", max_length=50)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, max_length=100)
    email_verified: bool = False
    status: str = Field(default="active", max_length=50)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)
    email_verified: Optional[bool] = None
    profile_image_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserProfile(BaseModel):
    """Schema for user profile updates"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    profile_image_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class User(UserBase):
    """User response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: uuid.UUID
    status: str
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    login_count: int = 0
    profile_image_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserWithRole(User):
    """User with role information"""
    role_info: Optional[UserRole] = None


class UserListResponse(BaseResponse):
    """Response schema for user list"""
    users: List[User]
    total: int
    page: int
    size: int


# ============================================
# Authentication Schemas
# ============================================

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class LoginResponse(BaseResponse):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: User


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class RefreshTokenResponse(BaseResponse):
    """Refresh token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class LogoutRequest(BaseModel):
    """Logout request schema"""
    refresh_token: Optional[str] = None


# ============================================
# Password Management Schemas
# ============================================

class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class AdminPasswordResetRequest(BaseModel):
    """Admin password reset request schema"""
    user_id: int
    new_password: str = Field(..., min_length=8, max_length=100)


# ============================================
# Session Schemas
# ============================================

class UserSessionBase(BaseModel):
    """Base user session schema"""
    device_info: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class UserSession(UserSessionBase):
    """User session response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_token: str
    expires_at: datetime
    created_at: datetime
    is_active: bool


class UserSessionList(BaseResponse):
    """User session list response"""
    sessions: List[UserSession]


# ============================================
# Admin Schemas
# ============================================

class AdminUserCreate(UserCreate):
    """Schema for admin user creation"""
    created_by: Optional[int] = None
    send_email: bool = True


class SystemStatistics(BaseModel):
    """System statistics schema"""
    total_users: int
    regular_users: int
    coach_users: int
    admin_users: int
    active_users: int
    total_transcriptions: int
    total_analyses: int
    total_workflows: int
    avg_system_score: Optional[float] = None


class UserActivityLogBase(BaseModel):
    """Base user activity log schema"""
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None


class UserActivityLog(UserActivityLogBase):
    """User activity log response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime


class UserActivityLogList(BaseResponse):
    """User activity log list response"""
    logs: List[UserActivityLog]
    total: int
    page: int
    size: int


class UsageStatisticBase(BaseModel):
    """Base usage statistic schema"""
    metric_name: str
    metric_value: float
    aggregation_period: str
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UsageStatistic(UsageStatisticBase):
    """Usage statistic response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: Optional[int] = None
    created_at: datetime


class UsageStatisticList(BaseResponse):
    """Usage statistic list response"""
    statistics: List[UsageStatistic]
    total: int


# ============================================
# Workflow Schemas
# ============================================

class WorkflowSessionBase(BaseModel):
    """Base workflow session schema"""
    session_name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowSessionCreate(WorkflowSessionBase):
    """Schema for creating a workflow session"""
    pass


class WorkflowSessionUpdate(BaseModel):
    """Schema for updating a workflow session"""
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    transcription_progress: Optional[int] = None
    analysis_progress: Optional[int] = None
    estimated_completion_time: Optional[datetime] = None
    error_details: Optional[str] = None


class WorkflowSession(WorkflowSessionBase):
    """Workflow session response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    uuid: uuid.UUID
    user_id: int
    status: str
    transcription_job_id: Optional[int] = None
    analysis_result_id: Optional[int] = None
    progress_percentage: int = 0
    transcription_progress: int = 0
    analysis_progress: int = 0
    estimated_completion_time: Optional[datetime] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_details: Optional[str] = None


# ============================================
# Data Access Permission Schemas
# ============================================

class DataAccessPermissionBase(BaseModel):
    """Base data access permission schema"""
    resource_type: str
    resource_id: int
    user_id: int
    permission_type: str
    expires_at: Optional[datetime] = None


class DataAccessPermissionCreate(DataAccessPermissionBase):
    """Schema for creating data access permission"""
    granted_by: int


class DataAccessPermission(DataAccessPermissionBase):
    """Data access permission response schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    granted_by: Optional[int] = None
    granted_at: datetime
    is_active: bool


# ============================================
# Dashboard Schemas
# ============================================

class UserDashboardSummary(BaseModel):
    """User dashboard summary schema"""
    user_id: int
    full_name: str
    role: str
    total_transcriptions: int = 0
    total_analyses: int = 0
    total_workflows: int = 0
    avg_analysis_score: Optional[float] = None
    last_transcription_date: Optional[datetime] = None
    last_analysis_date: Optional[datetime] = None


class CoachDashboard(BaseModel):
    """Coach dashboard data schema"""
    summary: UserDashboardSummary
    recent_analyses: List[Dict[str, Any]] = Field(default_factory=list)
    performance_trends: List[Dict[str, Any]] = Field(default_factory=list)
    comparisons: Dict[str, Any] = Field(default_factory=dict)


class AdminDashboard(BaseModel):
    """Admin dashboard data schema"""
    system_stats: SystemStatistics
    recent_activities: List[UserActivityLog] = Field(default_factory=list)
    user_summaries: List[UserDashboardSummary] = Field(default_factory=list)
    usage_trends: List[UsageStatistic] = Field(default_factory=list)


# ============================================
# API Response Wrappers
# ============================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class FilterParams(BaseModel):
    """Common filter parameters"""
    search: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None