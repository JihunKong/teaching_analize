"""
Dashboard routes for AIBOA Authentication Service
Role-based dashboard data and analytics
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from database import get_database
from models import (
    User, TranscriptionJob, AnalysisResult, WorkflowSession, 
    UserActivityLog, UsageStatistic
)
from schemas import (
    UserDashboardSummary, CoachDashboard, AdminDashboard,
    SystemStatistics, BaseResponse
)
from routes.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get dashboard summary for current user
    Returns different data based on user role
    """
    try:
        # Base user summary
        user_summary = get_user_summary(db, current_user.id)
        
        if current_user.role == "admin":
            # Admin gets system-wide data
            return await get_admin_dashboard_data(db, current_user)
        elif current_user.role == "coach":
            # Coach gets enhanced personal data
            return await get_coach_dashboard_data(db, current_user, user_summary)
        else:
            # Regular user gets basic summary
            return await get_regular_user_dashboard_data(db, current_user, user_summary)
            
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data"
        )


def get_user_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """Get basic user activity summary"""
    # Count user's content
    total_transcriptions = db.query(TranscriptionJob).filter(
        TranscriptionJob.user_id == user_id
    ).count()
    
    total_analyses = db.query(AnalysisResult).filter(
        AnalysisResult.user_id == user_id
    ).count()
    
    total_workflows = db.query(WorkflowSession).filter(
        WorkflowSession.user_id == user_id
    ).count()
    
    # Get average analysis score
    avg_score_result = db.query(func.avg(AnalysisResult.overall_score)).filter(
        AnalysisResult.user_id == user_id
    ).scalar()
    avg_analysis_score = float(avg_score_result) if avg_score_result else None
    
    # Get latest activity dates
    latest_transcription = db.query(TranscriptionJob).filter(
        TranscriptionJob.user_id == user_id
    ).order_by(desc(TranscriptionJob.created_at)).first()
    
    latest_analysis = db.query(AnalysisResult).filter(
        AnalysisResult.user_id == user_id
    ).order_by(desc(AnalysisResult.created_at)).first()
    
    return {
        "total_transcriptions": total_transcriptions,
        "total_analyses": total_analyses,
        "total_workflows": total_workflows,
        "avg_analysis_score": avg_analysis_score,
        "last_transcription_date": latest_transcription.created_at if latest_transcription else None,
        "last_analysis_date": latest_analysis.created_at if latest_analysis else None
    }


async def get_regular_user_dashboard_data(
    db: Session, 
    current_user: User, 
    user_summary: Dict[str, Any]
) -> Dict[str, Any]:
    """Get dashboard data for regular users"""
    
    # Recent workflows (last 5)
    recent_workflows = db.query(WorkflowSession).filter(
        WorkflowSession.user_id == current_user.id
    ).order_by(desc(WorkflowSession.created_at)).limit(5).all()
    
    # Recent analyses with scores
    recent_analyses = db.query(AnalysisResult).filter(
        AnalysisResult.user_id == current_user.id
    ).order_by(desc(AnalysisResult.created_at)).limit(5).all()
    
    # Progress over last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_progress = db.query(
        func.date(AnalysisResult.created_at).label('date'),
        func.count(AnalysisResult.id).label('count'),
        func.avg(AnalysisResult.overall_score).label('avg_score')
    ).filter(
        and_(
            AnalysisResult.user_id == current_user.id,
            AnalysisResult.created_at >= thirty_days_ago
        )
    ).group_by(func.date(AnalysisResult.created_at)).order_by('date').all()
    
    return {
        "user_type": "regular_user",
        "summary": user_summary,
        "recent_workflows": [
            {
                "id": w.id,
                "session_name": w.session_name or "Unnamed Session",
                "status": w.status,
                "progress_percentage": w.progress_percentage,
                "created_at": w.created_at,
                "completed_at": w.completed_at
            }
            for w in recent_workflows
        ],
        "recent_analyses": [
            {
                "id": a.id,
                "overall_score": float(a.overall_score) if a.overall_score else None,
                "primary_level": a.primary_level,
                "word_count": a.word_count,
                "created_at": a.created_at
            }
            for a in recent_analyses
        ],
        "progress_chart": [
            {
                "date": str(row.date),
                "analyses_count": row.count,
                "avg_score": float(row.avg_score) if row.avg_score else None
            }
            for row in daily_progress
        ],
        "quick_stats": {
            "this_week_analyses": db.query(AnalysisResult).filter(
                and_(
                    AnalysisResult.user_id == current_user.id,
                    AnalysisResult.created_at >= datetime.utcnow() - timedelta(days=7)
                )
            ).count(),
            "this_month_analyses": db.query(AnalysisResult).filter(
                and_(
                    AnalysisResult.user_id == current_user.id,
                    AnalysisResult.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).count(),
            "in_progress_workflows": db.query(WorkflowSession).filter(
                and_(
                    WorkflowSession.user_id == current_user.id,
                    WorkflowSession.status.in_(["initiated", "transcribing", "analyzing"])
                )
            ).count()
        }
    }


async def get_coach_dashboard_data(
    db: Session, 
    current_user: User, 
    user_summary: Dict[str, Any]
) -> Dict[str, Any]:
    """Get enhanced dashboard data for coach users"""
    
    # Get regular user data first
    regular_data = await get_regular_user_dashboard_data(db, current_user, user_summary)
    
    # Performance trends over time (last 90 days)
    ninety_days_ago = datetime.utcnow() - timedelta(days=90)
    weekly_trends = db.query(
        func.date_trunc('week', AnalysisResult.created_at).label('week'),
        func.count(AnalysisResult.id).label('analyses_count'),
        func.avg(AnalysisResult.overall_score).label('avg_score'),
        func.avg(AnalysisResult.word_count).label('avg_words'),
        func.avg(AnalysisResult.processing_time_seconds).label('avg_processing_time')
    ).filter(
        and_(
            AnalysisResult.user_id == current_user.id,
            AnalysisResult.created_at >= ninety_days_ago
        )
    ).group_by(func.date_trunc('week', AnalysisResult.created_at)).order_by('week').all()
    
    # CBIL level distribution
    level_distribution = db.query(
        AnalysisResult.primary_level,
        func.count(AnalysisResult.id).label('count')
    ).filter(
        AnalysisResult.user_id == current_user.id
    ).group_by(AnalysisResult.primary_level).all()
    
    # Score ranges distribution
    score_ranges = db.query(
        func.case(
            (AnalysisResult.overall_score >= 80, 'Excellent (80-100)'),
            (AnalysisResult.overall_score >= 60, 'Good (60-79)'),
            (AnalysisResult.overall_score >= 40, 'Average (40-59)'),
            (AnalysisResult.overall_score >= 20, 'Below Average (20-39)'),
            else_='Low (0-19)'
        ).label('score_range'),
        func.count(AnalysisResult.id).label('count')
    ).filter(
        and_(
            AnalysisResult.user_id == current_user.id,
            AnalysisResult.overall_score.isnot(None)
        )
    ).group_by('score_range').all()
    
    # Get system averages for comparison (anonymized)
    system_avg_score = db.query(func.avg(AnalysisResult.overall_score)).scalar()
    system_avg_words = db.query(func.avg(AnalysisResult.word_count)).scalar()
    
    # Enhanced coach data
    coach_data = {
        **regular_data,
        "user_type": "coach",
        "performance_trends": [
            {
                "week": str(row.week),
                "analyses_count": row.analyses_count,
                "avg_score": float(row.avg_score) if row.avg_score else None,
                "avg_words": float(row.avg_words) if row.avg_words else None,
                "avg_processing_time": float(row.avg_processing_time) if row.avg_processing_time else None
            }
            for row in weekly_trends
        ],
        "level_distribution": [
            {
                "level": row.primary_level or "Unclassified",
                "count": row.count
            }
            for row in level_distribution
        ],
        "score_distribution": [
            {
                "range": row.score_range,
                "count": row.count
            }
            for row in score_ranges
        ],
        "comparisons": {
            "my_avg_score": user_summary["avg_analysis_score"],
            "system_avg_score": float(system_avg_score) if system_avg_score else None,
            "my_avg_words": db.query(func.avg(AnalysisResult.word_count)).filter(
                AnalysisResult.user_id == current_user.id
            ).scalar(),
            "system_avg_words": float(system_avg_words) if system_avg_words else None
        },
        "achievements": generate_user_achievements(db, current_user.id, user_summary),
        "recommendations": generate_user_recommendations(db, current_user.id, user_summary)
    }
    
    return coach_data


async def get_admin_dashboard_data(
    db: Session, 
    current_user: User
) -> Dict[str, Any]:
    """Get comprehensive dashboard data for admin users"""
    
    # System statistics
    total_users = db.query(User).filter(User.status != "deleted").count()
    active_users = db.query(User).filter(User.status == "active").count()
    total_transcriptions = db.query(TranscriptionJob).count()
    total_analyses = db.query(AnalysisResult).count()
    total_workflows = db.query(WorkflowSession).count()
    
    # User role distribution
    role_distribution = db.query(
        User.role,
        func.count(User.id).label('count')
    ).filter(User.status != "deleted").group_by(User.role).all()
    
    # Recent user registrations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_registrations = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        and_(
            User.created_at >= thirty_days_ago,
            User.status != "deleted"
        )
    ).group_by(func.date(User.created_at)).order_by('date').all()
    
    # System activity trends (last 30 days)
    activity_trends = db.query(
        func.date(UserActivityLog.created_at).label('date'),
        func.count(UserActivityLog.id).label('count')
    ).filter(
        UserActivityLog.created_at >= thirty_days_ago
    ).group_by(func.date(UserActivityLog.created_at)).order_by('date').all()
    
    # Most active users (last 30 days)
    active_users_data = db.query(
        User.id,
        User.full_name,
        User.email,
        User.role,
        func.count(UserActivityLog.id).label('activity_count')
    ).join(
        UserActivityLog, User.id == UserActivityLog.user_id
    ).filter(
        and_(
            UserActivityLog.created_at >= thirty_days_ago,
            User.status == "active"
        )
    ).group_by(
        User.id, User.full_name, User.email, User.role
    ).order_by(desc(func.count(UserActivityLog.id))).limit(10).all()
    
    # Content creation trends
    content_trends = db.query(
        func.date(TranscriptionJob.created_at).label('date'),
        func.count(TranscriptionJob.id).label('transcriptions'),
        func.count(AnalysisResult.id).label('analyses')
    ).outerjoin(
        AnalysisResult, func.date(TranscriptionJob.created_at) == func.date(AnalysisResult.created_at)
    ).filter(
        TranscriptionJob.created_at >= thirty_days_ago
    ).group_by(func.date(TranscriptionJob.created_at)).order_by('date').all()
    
    # System health metrics
    failed_jobs = db.query(TranscriptionJob).filter(
        and_(
            TranscriptionJob.status == "failed",
            TranscriptionJob.created_at >= thirty_days_ago
        )
    ).count()
    
    avg_processing_time = db.query(func.avg(AnalysisResult.processing_time_seconds)).filter(
        AnalysisResult.created_at >= thirty_days_ago
    ).scalar()
    
    # Recent activities (last 50)
    recent_activities = db.query(UserActivityLog).join(
        User, UserActivityLog.user_id == User.id
    ).order_by(desc(UserActivityLog.created_at)).limit(50).all()
    
    return {
        "user_type": "admin",
        "system_stats": {
            "total_users": total_users,
            "active_users": active_users,
            "total_transcriptions": total_transcriptions,
            "total_analyses": total_analyses,
            "total_workflows": total_workflows,
            "failed_jobs_30d": failed_jobs,
            "avg_processing_time": float(avg_processing_time) if avg_processing_time else None
        },
        "role_distribution": [
            {"role": row.role, "count": row.count}
            for row in role_distribution
        ],
        "trends": {
            "user_registrations": [
                {"date": str(row.date), "count": row.count}
                for row in recent_registrations
            ],
            "system_activity": [
                {"date": str(row.date), "count": row.count}
                for row in activity_trends
            ],
            "content_creation": [
                {
                    "date": str(row.date),
                    "transcriptions": row.transcriptions,
                    "analyses": row.analyses or 0
                }
                for row in content_trends
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
            for row in active_users_data
        ],
        "recent_activities": [
            {
                "id": activity.id,
                "user_id": activity.user_id,
                "action": activity.action,
                "resource_type": activity.resource_type,
                "created_at": activity.created_at,
                "ip_address": str(activity.ip_address) if activity.ip_address else None
            }
            for activity in recent_activities
        ],
        "alerts": generate_admin_alerts(db)
    }


def generate_user_achievements(db: Session, user_id: int, summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate achievement badges for users"""
    achievements = []
    
    # Analysis count achievements
    if summary["total_analyses"] >= 100:
        achievements.append({
            "title": "Century Club",
            "description": "Completed 100+ analyses",
            "icon": "🏆",
            "earned_date": None  # Could calculate from data
        })
    elif summary["total_analyses"] >= 50:
        achievements.append({
            "title": "Half Century",
            "description": "Completed 50+ analyses",
            "icon": "🥉",
            "earned_date": None
        })
    elif summary["total_analyses"] >= 10:
        achievements.append({
            "title": "Getting Started",
            "description": "Completed 10+ analyses",
            "icon": "🌟",
            "earned_date": None
        })
    
    # Score achievements
    if summary["avg_analysis_score"] and summary["avg_analysis_score"] >= 80:
        achievements.append({
            "title": "Excellence",
            "description": "Average score above 80",
            "icon": "💎",
            "earned_date": None
        })
    elif summary["avg_analysis_score"] and summary["avg_analysis_score"] >= 70:
        achievements.append({
            "title": "High Performer",
            "description": "Average score above 70",
            "icon": "⭐",
            "earned_date": None
        })
    
    # Consistency achievements
    recent_analyses = db.query(AnalysisResult).filter(
        and_(
            AnalysisResult.user_id == user_id,
            AnalysisResult.created_at >= datetime.utcnow() - timedelta(days=7)
        )
    ).count()
    
    if recent_analyses >= 5:
        achievements.append({
            "title": "Weekly Warrior",
            "description": "5+ analyses this week",
            "icon": "🔥",
            "earned_date": None
        })
    
    return achievements


def generate_user_recommendations(db: Session, user_id: int, summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate personalized recommendations for users"""
    recommendations = []
    
    # Based on analysis frequency
    recent_analyses = db.query(AnalysisResult).filter(
        and_(
            AnalysisResult.user_id == user_id,
            AnalysisResult.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    ).count()
    
    if recent_analyses < 5:
        recommendations.append({
            "title": "Stay Active",
            "description": "Try to analyze at least one lesson per week to improve consistency",
            "priority": "medium",
            "action": "Create new analysis"
        })
    
    # Based on average score
    if summary["avg_analysis_score"]:
        if summary["avg_analysis_score"] < 60:
            recommendations.append({
                "title": "Focus on Higher-Order Questions",
                "description": "Your analyses show potential for more analytical and evaluative questions",
                "priority": "high",
                "action": "Review CBIL framework"
            })
        elif summary["avg_analysis_score"] > 80:
            recommendations.append({
                "title": "Share Your Expertise",
                "description": "Your high-quality analyses could benefit other educators",
                "priority": "low",
                "action": "Consider coaching role"
            })
    
    # Based on content length
    avg_words = db.query(func.avg(AnalysisResult.word_count)).filter(
        AnalysisResult.user_id == user_id
    ).scalar()
    
    if avg_words and avg_words < 100:
        recommendations.append({
            "title": "Expand Your Content",
            "description": "Longer content typically provides more detailed analysis insights",
            "priority": "medium",
            "action": "Try longer lessons"
        })
    
    return recommendations


def generate_admin_alerts(db: Session) -> List[Dict[str, Any]]:
    """Generate system alerts for admin dashboard"""
    alerts = []
    now = datetime.utcnow()
    
    # Check for failed jobs in last 24 hours
    failed_jobs = db.query(TranscriptionJob).filter(
        and_(
            TranscriptionJob.status == "failed",
            TranscriptionJob.created_at >= now - timedelta(days=1)
        )
    ).count()
    
    if failed_jobs > 5:
        alerts.append({
            "type": "error",
            "title": "High Failure Rate",
            "message": f"{failed_jobs} transcription jobs failed in the last 24 hours",
            "action": "Check system logs"
        })
    
    # Check for inactive users
    inactive_users = db.query(User).filter(
        and_(
            User.status == "active",
            User.last_login < now - timedelta(days=30)
        )
    ).count()
    
    if inactive_users > 10:
        alerts.append({
            "type": "warning",
            "title": "Inactive Users",
            "message": f"{inactive_users} users haven't logged in for 30+ days",
            "action": "Consider engagement campaign"
        })
    
    # Check for new user registrations
    new_users = db.query(User).filter(
        and_(
            User.created_at >= now - timedelta(days=7),
            User.status != "deleted"
        )
    ).count()
    
    if new_users > 0:
        alerts.append({
            "type": "info",
            "title": "New Users",
            "message": f"{new_users} new users registered this week",
            "action": "Review onboarding"
        })
    
    # Check system performance
    avg_processing_time = db.query(func.avg(AnalysisResult.processing_time_seconds)).filter(
        AnalysisResult.created_at >= now - timedelta(days=1)
    ).scalar()
    
    if avg_processing_time and avg_processing_time > 10:
        alerts.append({
            "type": "warning",
            "title": "Slow Processing",
            "message": f"Average analysis time is {avg_processing_time:.1f}s",
            "action": "Check system resources"
        })
    
    return alerts


@router.get("/coach")
async def get_coach_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get coach-specific dashboard data
    Only accessible to coach and admin users
    """
    if current_user.role not in ["coach", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Coach or admin privileges required"
        )
    
    try:
        user_summary = get_user_summary(db, current_user.id)
        return await get_coach_dashboard_data(db, current_user, user_summary)
    except Exception as e:
        logger.error(f"Coach dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coach dashboard"
        )


@router.get("/admin")
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get admin-specific dashboard data
    Only accessible to admin users
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    try:
        return await get_admin_dashboard_data(db, current_user)
    except Exception as e:
        logger.error(f"Admin dashboard error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin dashboard"
        )