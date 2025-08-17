"""
User management routes for AIBOA Authentication Service
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..database import get_database
from ..models import User, UserRole, UserActivityLog
from ..schemas import (
    User as UserSchema, UserCreate, UserUpdate, UserListResponse,
    BaseResponse, PaginationParams, FilterParams
)
from ..utils.auth import get_password_hash, check_user_permissions
from .auth import get_current_user, log_user_activity
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def check_permission(current_user: User, required_permission: str, resource: str = "users"):
    """Check if user has required permission"""
    if current_user.role == "admin":
        return True
    
    # Get user role permissions
    role_permissions = {
        "coach": {
            "users": ["read"],  # Can only read user info
        },
        "regular_user": {
            "users": [],  # No user management permissions
        }
    }
    
    user_permissions = role_permissions.get(current_user.role, {})
    return check_user_permissions(user_permissions, required_permission, resource)


@router.get("/", response_model=UserListResponse)
async def list_users(
    request: Request,
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    List users with pagination and filtering
    
    Only admins and coaches can access this endpoint
    """
    try:
        # Check permissions
        if not check_permission(current_user, "read", "users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to list users"
            )
        
        # Build query
        query = db.query(User)
        
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
        
        # For non-admin users, limit what they can see
        if current_user.role != "admin":
            # Coaches can only see regular users and other coaches
            query = query.filter(User.role.in_(["regular_user", "coach"]))
        
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
        
        # Log user list access
        log_user_activity(
            db, current_user.id, "USER_LIST_ACCESS",
            {
                "total_users": total,
                "page": pagination.page,
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get user by ID
    
    Users can access their own info, admins can access any user
    """
    try:
        # Check if user is accessing their own info or has admin privileges
        if user_id != current_user.id and not check_permission(current_user, "read", "users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access user info"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # For non-admin users, restrict access to admin users
        if current_user.role != "admin" and user.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Log user access
        if user_id != current_user.id:
            log_user_activity(
                db, current_user.id, "USER_ACCESS",
                {"accessed_user_id": user_id},
                request
            )
        
        return UserSchema.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Update user
    
    Users can update their own basic info, admins can update any user
    """
    try:
        # Get user to update
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check permissions
        is_self_update = user_id == current_user.id
        is_admin = current_user.role == "admin"
        
        if not is_self_update and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update user"
            )
        
        # Restrict what non-admins can update
        allowed_fields = ["full_name", "profile_image_url", "preferences"]
        if not is_admin:
            # Non-admins can only update basic profile fields
            restricted_fields = ["role", "status", "email_verified"]
            for field in restricted_fields:
                if getattr(user_data, field) is not None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Cannot update field: {field}"
                    )
        else:
            # Admins can update additional fields
            allowed_fields.extend(["role", "status", "email_verified"])
        
        # Update user fields
        updated_fields = {}
        for field in allowed_fields:
            value = getattr(user_data, field)
            if value is not None:
                setattr(user, field, value)
                updated_fields[field] = value
        
        if updated_fields:
            user.updated_at = datetime.utcnow()
            
            # Log user update
            log_user_activity(
                db, current_user.id, "USER_UPDATE",
                {
                    "updated_user_id": user_id,
                    "updated_fields": list(updated_fields.keys()),
                    "is_self_update": is_self_update
                },
                request
            )
            
            db.commit()
            logger.info(f"User {user_id} updated by {current_user.email}")
        
        return UserSchema.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.delete("/{user_id}", response_model=BaseResponse)
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Delete (deactivate) user
    
    Only admins can delete users, and they cannot delete themselves
    """
    try:
        # Check permissions
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete users"
            )
        
        # Cannot delete self
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Cannot delete other admin users (for safety)
        if user.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete admin users"
            )
        
        # Soft delete - just deactivate the user
        user.status = "deleted"
        user.updated_at = datetime.utcnow()
        
        # Revoke all user sessions
        from ..models import UserSession
        db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({
            "is_active": False,
            "revoked_at": datetime.utcnow()
        })
        
        # Log user deletion
        log_user_activity(
            db, current_user.id, "USER_DELETE",
            {"deleted_user_id": user_id, "deleted_user_email": user.email},
            request
        )
        
        db.commit()
        
        logger.info(f"User {user_id} ({user.email}) deleted by {current_user.email}")
        
        return BaseResponse(message="User deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.get("/{user_id}/activities")
async def get_user_activities(
    user_id: int,
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get user activity logs
    
    Users can access their own activities, admins can access any user's activities
    """
    try:
        # Check permissions
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access user activities"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get activities
        query = db.query(UserActivityLog).filter(UserActivityLog.user_id == user_id)
        total = query.count()
        
        offset = (page - 1) * size
        activities = query.order_by(UserActivityLog.created_at.desc()).offset(offset).limit(size).all()
        
        # Log activity access (if not self)
        if user_id != current_user.id:
            log_user_activity(
                db, current_user.id, "USER_ACTIVITIES_ACCESS",
                {"accessed_user_id": user_id},
                request
            )
        
        return {
            "activities": [
                {
                    "id": activity.id,
                    "action": activity.action,
                    "resource_type": activity.resource_type,
                    "resource_id": activity.resource_id,
                    "details": activity.details,
                    "ip_address": str(activity.ip_address) if activity.ip_address else None,
                    "created_at": activity.created_at
                }
                for activity in activities
            ],
            "total": total,
            "page": page,
            "size": size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user activities error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activities"
        )


@router.post("/{user_id}/reset-password", response_model=BaseResponse)
async def admin_reset_password(
    user_id: int,
    new_password: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Admin password reset for a user
    
    Only admins can reset other users' passwords
    """
    try:
        # Check permissions
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can reset user passwords"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Cannot reset other admin passwords (for security)
        if user.role == "admin" and user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reset other admin passwords"
            )
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Revoke all user sessions (force re-login)
        from ..models import UserSession
        db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).update({
            "is_active": False,
            "revoked_at": datetime.utcnow()
        })
        
        # Log password reset
        log_user_activity(
            db, current_user.id, "ADMIN_PASSWORD_RESET",
            {"reset_user_id": user_id, "reset_user_email": user.email},
            request
        )
        
        # Also log for the affected user
        log_user_activity(
            db, user_id, "PASSWORD_RESET_BY_ADMIN",
            {"admin_user_id": current_user.id},
            request
        )
        
        db.commit()
        
        logger.info(f"Password reset for user {user_id} by admin {current_user.email}")
        
        return BaseResponse(message="Password reset successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.get("/roles/", response_model=List[dict])
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    List available user roles
    
    Available to all authenticated users
    """
    try:
        roles = db.query(UserRole).filter(UserRole.is_active == True).all()
        
        return [
            {
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description
            }
            for role in roles
        ]
        
    except Exception as e:
        logger.error(f"List roles error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve roles"
        )