"""
Admin management routes for AIBOA Authentication Service
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..database import get_database
from ..models import (
    User, UserRole, UserActivityLog, UsageStatistic, 
    TranscriptionJob, AnalysisResult, WorkflowSession
)
from ..schemas import (
    AdminUserCreate, User as UserSchema, UserListResponse, 
    SystemStatistics, UserActivityLogList, BaseResponse,
    PaginationParams, FilterParams
)
from ..utils.auth import get_password_hash
from .auth import get_current_user, log_user_activity
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


@router.post("/users/", response_model=UserSchema)
async def create_user(
    user_data: AdminUserCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Create a new user (admin only)
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate role
        role = db.query(UserRole).filter(UserRole.name == user_data.role).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role"
            )
        
        # Create user
        user = User(
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            status=user_data.status,
            email_verified=user_data.email_verified,
            created_by=current_user.id
        )
        
        db.add(user)
        db.flush()  # Get the user ID
        
        # Log user creation
        log_user_activity(
            db, current_user.id, "USER_CREATE",
            {
                "created_user_id": user.id,
                "created_user_email": user.email,
                "created_user_role": user.role
            },
            request
        )
        
        db.commit()
        
        logger.info(f"User created: {user.email} by admin {current_user.email}")
        
        # TODO: Send welcome email if enabled
        if user_data.send_email:
            logger.info(f"Welcome email should be sent to {user.email}")
        
        return UserSchema.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/users/", response_model=UserListResponse)
async def admin_list_users(
    request: Request,
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    include_deleted: bool = Query(False, description="Include deleted users"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    List all users with admin privileges
    """
    try:
        # Build query
        query = db.query(User)
        
        # Include deleted users if requested
        if not include_deleted:
            query = query.filter(User.status != "deleted")
        
        # Apply filters
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        if filters.role:
            query = query.filter(User.role == filters.role)
        
        if filters.status:
            query = query.filter(User.status == filters.status)
        
        if filters.created_after:
            query = query.filter(User.created_at >= filters.created_after)
        
        if filters.created_before:
            query = query.filter(User.created_at <= filters.created_before)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        if pagination.sort_by:
            if hasattr(User, pagination.sort_by):
                sort_column = getattr(User, pagination.sort_by)
                if pagination.sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(User.created_at.desc())
        
        # Apply pagination
        offset = (pagination.page - 1) * pagination.size
        users = query.offset(offset).limit(pagination.size).all()
        
        # Log admin user list access
        log_user_activity(
            db, current_user.id, "ADMIN_USER_LIST_ACCESS",
            {
                "total_users": total,
                "page": pagination.page,
                "include_deleted": include_deleted,
                "filters": filters.dict(exclude_none=True)
            },
            request
        )
        
        return UserListResponse(
            message="Users retrieved successfully",
            users=[UserSchema.from_orm(user) for user in users],
            total=total,
            page=pagination.page,
            size=pagination.size
        )
        
    except Exception as e:
        logger.error(f"Admin list users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/statistics", response_model=SystemStatistics)
async def get_system_statistics(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get system-wide statistics
    """
    try:
        # User statistics
        total_users = db.query(User).filter(User.status != "deleted").count()
        regular_users = db.query(User).filter(
            and_(User.role == "regular_user", User.status != "deleted")
        ).count()
        coach_users = db.query(User).filter(
            and_(User.role == "coach", User.status != "deleted")
        ).count()
        admin_users = db.query(User).filter(
            and_(User.role == "admin", User.status != "deleted")
        ).count()
        active_users = db.query(User).filter(User.status == "active").count()
        
        # Content statistics
        total_transcriptions = db.query(TranscriptionJob).count()
        total_analyses = db.query(AnalysisResult).count()
        total_workflows = db.query(WorkflowSession).count()
        
        # Average analysis score
        avg_score_result = db.query(func.avg(AnalysisResult.overall_score)).scalar()
        avg_system_score = float(avg_score_result) if avg_score_result else None
        
        return SystemStatistics(
            total_users=total_users,
            regular_users=regular_users,
            coach_users=coach_users,
            admin_users=admin_users,
            active_users=active_users,
            total_transcriptions=total_transcriptions,
            total_analyses=total_analyses,
            total_workflows=total_workflows,
            avg_system_score=avg_system_score
        )
        
    except Exception as e:
        logger.error(f"Get statistics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


@router.get("/analytics")
async def get_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get detailed analytics for admin dashboard
    """
    try:
        # Date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # User registration trends
        user_registrations = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date,
                User.status != "deleted"
            )
        ).group_by(func.date(User.created_at)).order_by('date').all()
        
        # Activity trends
        activity_trends = db.query(
            func.date(UserActivityLog.created_at).label('date'),
            func.count(UserActivityLog.id).label('count')
        ).filter(
            and_(
                UserActivityLog.created_at >= start_date,
                UserActivityLog.created_at <= end_date
            )
        ).group_by(func.date(UserActivityLog.created_at)).order_by('date').all()
        
        # Transcription trends
        transcription_trends = db.query(
            func.date(TranscriptionJob.created_at).label('date'),
            func.count(TranscriptionJob.id).label('count')
        ).filter(
            and_(
                TranscriptionJob.created_at >= start_date,
                TranscriptionJob.created_at <= end_date
            )
        ).group_by(func.date(TranscriptionJob.created_at)).order_by('date').all()
        
        # Analysis trends
        analysis_trends = db.query(
            func.date(AnalysisResult.created_at).label('date'),
            func.count(AnalysisResult.id).label('count')
        ).filter(
            and_(
                AnalysisResult.created_at >= start_date,
                AnalysisResult.created_at <= end_date
            )
        ).group_by(func.date(AnalysisResult.created_at)).order_by('date').all()
        
        # Top active users
        top_users = db.query(
            User.id,
            User.full_name,
            User.email,
            User.role,
            func.count(UserActivityLog.id).label('activity_count')
        ).join(
            UserActivityLog, User.id == UserActivityLog.user_id
        ).filter(
            and_(
                UserActivityLog.created_at >= start_date,
                UserActivityLog.created_at <= end_date,
                User.status == "active"
            )
        ).group_by(
            User.id, User.full_name, User.email, User.role
        ).order_by(func.count(UserActivityLog.id).desc()).limit(10).all()
        
        # Most common actions
        common_actions = db.query(
            UserActivityLog.action,
            func.count(UserActivityLog.id).label('count')
        ).filter(
            and_(
                UserActivityLog.created_at >= start_date,
                UserActivityLog.created_at <= end_date
            )
        ).group_by(UserActivityLog.action).order_by(
            func.count(UserActivityLog.id).desc()
        ).limit(15).all()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "trends": {
                "user_registrations": [
                    {"date": str(row.date), "count": row.count}
                    for row in user_registrations
                ],
                "user_activity": [
                    {"date": str(row.date), "count": row.count}
                    for row in activity_trends
                ],
                "transcriptions": [
                    {"date": str(row.date), "count": row.count}
                    for row in transcription_trends
                ],
                "analyses": [
                    {"date": str(row.date), "count": row.count}
                    for row in analysis_trends
                ]
            },
            "top_users": [
                {
                    "id": row.id,
                    "full_name": row.full_name,
                    "email": row.email,
                    "role": row.role,
                    "activity_count": row.activity_count
                }
                for row in top_users
            ],
            "common_actions": [
                {"action": row.action, "count": row.count}
                for row in common_actions
            ]
        }
        
    except Exception as e:
        logger.error(f"Get analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.get("/logs", response_model=UserActivityLogList)
async def get_activity_logs(
    request: Request,
    pagination: PaginationParams = Depends(),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action"),
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get system activity logs
    """
    try:
        # Date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = db.query(UserActivityLog).filter(
            UserActivityLog.created_at >= start_date
        )
        
        # Apply filters
        if user_id:
            query = query.filter(UserActivityLog.user_id == user_id)
        
        if action:
            query = query.filter(UserActivityLog.action.ilike(f"%{action}%"))
        
        # Get total count
        total = query.count()
        
        # Apply sorting and pagination
        offset = (pagination.page - 1) * pagination.size
        logs = query.order_by(UserActivityLog.created_at.desc()).offset(offset).limit(pagination.size).all()
        
        # Log admin logs access
        log_user_activity(
            db, current_user.id, "ADMIN_LOGS_ACCESS",
            {
                "total_logs": total,
                "page": pagination.page,
                "filters": {"user_id": user_id, "action": action, "days": days}
            },
            request
        )
        
        return UserActivityLogList(
            message="Activity logs retrieved successfully",
            logs=[
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": log.details,
                    "ip_address": str(log.ip_address) if log.ip_address else None,
                    "user_agent": log.user_agent,
                    "created_at": log.created_at,
                    "session_id": log.session_id
                }
                for log in logs
            ],
            total=total,
            page=pagination.page,
            size=pagination.size
        )
        
    except Exception as e:
        logger.error(f"Get activity logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity logs"
        )


@router.get("/users/{user_id}/data")
async def get_user_data(
    user_id: int,
    include_transcriptions: bool = Query(True),
    include_analyses: bool = Query(True),
    include_workflows: bool = Query(True),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Get all data for a specific user (admin only)
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = {
            "user": UserSchema.from_orm(user),
            "summary": {
                "total_transcriptions": 0,
                "total_analyses": 0,
                "total_workflows": 0,
                "avg_analysis_score": None,
                "first_activity": None,
                "last_activity": None
            }
        }
        
        # Get transcriptions
        if include_transcriptions:
            transcriptions = db.query(TranscriptionJob).filter(
                TranscriptionJob.user_id == user_id
            ).order_by(TranscriptionJob.created_at.desc()).all()
            
            user_data["transcriptions"] = [
                {
                    "id": t.id,
                    "job_id": t.job_id,
                    "status": t.status,
                    "source_type": t.source_type,
                    "source_url": t.source_url,
                    "filename": t.filename,
                    "language": t.language,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at
                }
                for t in transcriptions
            ]
            user_data["summary"]["total_transcriptions"] = len(transcriptions)
        
        # Get analyses
        if include_analyses:
            analyses = db.query(AnalysisResult).filter(
                AnalysisResult.user_id == user_id
            ).order_by(AnalysisResult.created_at.desc()).all()
            
            user_data["analyses"] = [
                {
                    "id": a.id,
                    "analysis_type": a.analysis_type,
                    "framework": a.framework,
                    "overall_score": float(a.overall_score) if a.overall_score else None,
                    "primary_level": a.primary_level,
                    "word_count": a.word_count,
                    "sentence_count": a.sentence_count,
                    "created_at": a.created_at
                }
                for a in analyses
            ]
            user_data["summary"]["total_analyses"] = len(analyses)
            
            # Calculate average score
            scores = [float(a.overall_score) for a in analyses if a.overall_score]
            if scores:
                user_data["summary"]["avg_analysis_score"] = sum(scores) / len(scores)
        
        # Get workflows
        if include_workflows:
            workflows = db.query(WorkflowSession).filter(
                WorkflowSession.user_id == user_id
            ).order_by(WorkflowSession.created_at.desc()).all()
            
            user_data["workflows"] = [
                {
                    "id": w.id,
                    "session_name": w.session_name,
                    "status": w.status,
                    "progress_percentage": w.progress_percentage,
                    "created_at": w.created_at,
                    "completed_at": w.completed_at
                }
                for w in workflows
            ]
            user_data["summary"]["total_workflows"] = len(workflows)
        
        # Get activity summary
        first_activity = db.query(UserActivityLog).filter(
            UserActivityLog.user_id == user_id
        ).order_by(UserActivityLog.created_at.asc()).first()
        
        last_activity = db.query(UserActivityLog).filter(
            UserActivityLog.user_id == user_id
        ).order_by(UserActivityLog.created_at.desc()).first()
        
        if first_activity:
            user_data["summary"]["first_activity"] = first_activity.created_at
        if last_activity:
            user_data["summary"]["last_activity"] = last_activity.created_at
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user data error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user data"
        )


@router.post("/cleanup", response_model=BaseResponse)
async def cleanup_system(
    days: int = Query(30, ge=1, le=365, description="Days to keep data"),
    dry_run: bool = Query(True, description="Perform dry run without actual deletion"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """
    Cleanup old system data (admin only)
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cleanup_stats = {
            "old_sessions": 0,
            "old_password_resets": 0,
            "old_activity_logs": 0
        }
        
        if not dry_run:
            # Cleanup old inactive sessions
            from ..models import UserSession, PasswordResetToken
            
            # Delete old inactive sessions
            old_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == False,
                    UserSession.created_at < cutoff_date
                )
            )
            cleanup_stats["old_sessions"] = old_sessions.count()
            if not dry_run:
                old_sessions.delete()
            
            # Delete old password reset tokens
            old_resets = db.query(PasswordResetToken).filter(
                PasswordResetToken.created_at < cutoff_date
            )
            cleanup_stats["old_password_resets"] = old_resets.count()
            if not dry_run:
                old_resets.delete()
            
            # Optionally cleanup old activity logs (be careful with this)
            if days > 90:  # Only cleanup activity logs if keeping more than 90 days
                very_old_date = datetime.utcnow() - timedelta(days=days * 2)
                old_logs = db.query(UserActivityLog).filter(
                    UserActivityLog.created_at < very_old_date
                )
                cleanup_stats["old_activity_logs"] = old_logs.count()
                if not dry_run:
                    old_logs.delete()
            
            if not dry_run:
                db.commit()
                
                # Log cleanup action
                log_user_activity(
                    db, current_user.id, "SYSTEM_CLEANUP",
                    {
                        "days": days,
                        "cleanup_stats": cleanup_stats,
                        "cutoff_date": cutoff_date.isoformat()
                    }
                )
                db.commit()
        
        else:
            # Dry run - just count
            from ..models import UserSession, PasswordResetToken
            
            cleanup_stats["old_sessions"] = db.query(UserSession).filter(
                and_(
                    UserSession.is_active == False,
                    UserSession.created_at < cutoff_date
                )
            ).count()
            
            cleanup_stats["old_password_resets"] = db.query(PasswordResetToken).filter(
                PasswordResetToken.created_at < cutoff_date
            ).count()
            
            if days > 90:
                very_old_date = datetime.utcnow() - timedelta(days=days * 2)
                cleanup_stats["old_activity_logs"] = db.query(UserActivityLog).filter(
                    UserActivityLog.created_at < very_old_date
                ).count()
        
        return BaseResponse(
            message=f"Cleanup {'dry run' if dry_run else 'completed'} successfully",
            **cleanup_stats
        )
        
    except Exception as e:
        logger.error(f"System cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cleanup failed"
        )