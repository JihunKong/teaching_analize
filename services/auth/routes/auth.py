"""
Authentication routes for AIBOA Authentication Service
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_database
from ..models import User, UserSession, PasswordResetToken, UserActivityLog
from ..schemas import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, PasswordChangeRequest, ForgotPasswordRequest, 
    ResetPasswordRequest, User as UserSchema, BaseResponse, ErrorResponse
)
from ..utils.auth import (
    verify_password, create_user_tokens, verify_token, 
    generate_password_reset_token, get_password_hash,
    generate_session_token
)
from ..config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


def log_user_activity(
    db: Session, 
    user_id: int, 
    action: str, 
    details: dict = None,
    request: Request = None
):
    """Log user activity"""
    try:
        activity_log = UserActivityLog(
            user_id=user_id,
            action=action,
            details=details or {},
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None
        )
        db.add(activity_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log user activity: {e}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active"
        )
    
    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_database)
) -> Optional[User]:
    """Get current authenticated user (optional)"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_database)
):
    """
    User login endpoint
    
    Authenticates user credentials and returns JWT tokens
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            # Log failed login attempt
            logger.warning(f"Login attempt with non-existent email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            # Log failed login attempt
            log_user_activity(
                db, user.id, "LOGIN_FAILED", 
                {"reason": "invalid_password"},
                request
            )
            logger.warning(f"Failed login attempt for user: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if user.status != "active":
            log_user_activity(
                db, user.id, "LOGIN_FAILED", 
                {"reason": "account_inactive"},
                request
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is not active"
            )
        
        # Create tokens
        tokens = create_user_tokens(user.id, user.email, user.role)
        
        # Create session record
        session = UserSession(
            user_id=user.id,
            session_token=generate_session_token(),
            refresh_token=tokens["refresh_token"],
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_info={
                "remember_me": login_data.remember_me,
                "login_time": datetime.utcnow().isoformat()
            }
        )
        db.add(session)
        
        # Update user login info
        user.last_login = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        
        # Log successful login
        log_user_activity(
            db, user.id, "LOGIN_SUCCESS", 
            {"remember_me": login_data.remember_me},
            request
        )
        
        db.commit()
        
        logger.info(f"Successful login for user: {user.email}")
        
        return LoginResponse(
            message="Login successful",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"],
            user=UserSchema.from_orm(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to internal error"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_database)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get user
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Check if refresh token exists in database
        session = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.refresh_token == refresh_data.refresh_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        tokens = create_user_tokens(user.id, user.email, user.role)
        
        # Update session with new refresh token
        session.refresh_token = tokens["refresh_token"]
        session.expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        # Log token refresh
        log_user_activity(
            db, user.id, "TOKEN_REFRESH", {},
            request
        )
        
        db.commit()
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return RefreshTokenResponse(
            message="Token refreshed successfully",
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=tokens["expires_in"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=BaseResponse)
async def logout(
    logout_data: LogoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    User logout endpoint
    
    Revokes user session and refresh token
    """
    try:
        # If refresh token provided, revoke specific session
        if logout_data.refresh_token:
            session = db.query(UserSession).filter(
                UserSession.user_id == current_user.id,
                UserSession.refresh_token == logout_data.refresh_token,
                UserSession.is_active == True
            ).first()
            
            if session:
                session.is_active = False
                session.revoked_at = datetime.utcnow()
        else:
            # Revoke all user sessions
            db.query(UserSession).filter(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True
            ).update({
                "is_active": False,
                "revoked_at": datetime.utcnow()
            })
        
        # Log logout
        log_user_activity(
            db, current_user.id, "LOGOUT", 
            {"revoked_all_sessions": not bool(logout_data.refresh_token)},
            request
        )
        
        db.commit()
        
        logger.info(f"User logged out: {current_user.email}")
        
        return BaseResponse(message="Logout successful")
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/profile", response_model=UserSchema)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    return UserSchema.from_orm(current_user)


@router.put("/profile", response_model=UserSchema)
async def update_profile(
    profile_data: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Update user profile
    """
    try:
        # Update allowed fields
        allowed_fields = ["full_name", "profile_image_url", "preferences"]
        updated_fields = {}
        
        for field in allowed_fields:
            if field in profile_data:
                setattr(current_user, field, profile_data[field])
                updated_fields[field] = profile_data[field]
        
        if updated_fields:
            current_user.updated_at = datetime.utcnow()
            
            # Log profile update
            log_user_activity(
                db, current_user.id, "PROFILE_UPDATE", 
                {"updated_fields": list(updated_fields.keys())},
                request
            )
            
            db.commit()
            logger.info(f"Profile updated for user: {current_user.email}")
        
        return UserSchema.from_orm(current_user)
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password", response_model=BaseResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.password_hash = get_password_hash(password_data.new_password)
        current_user.updated_at = datetime.utcnow()
        
        # Revoke all existing sessions (force re-login)
        db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).update({
            "is_active": False,
            "revoked_at": datetime.utcnow()
        })
        
        # Log password change
        log_user_activity(
            db, current_user.id, "PASSWORD_CHANGE", {},
            request
        )
        
        db.commit()
        
        logger.info(f"Password changed for user: {current_user.email}")
        
        return BaseResponse(message="Password changed successfully. Please login again.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.post("/forgot-password", response_model=BaseResponse)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_database)
):
    """
    Request password reset
    """
    try:
        # Find user
        user = db.query(User).filter(User.email == forgot_data.email).first()
        if not user:
            # Don't reveal if email exists
            return BaseResponse(
                message="If the email exists, a password reset link has been sent"
            )
        
        # Generate reset token
        reset_token = generate_password_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=settings.password_reset_expire_hours)
        
        # Save reset token
        password_reset = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        db.add(password_reset)
        
        # Log password reset request
        log_user_activity(
            db, user.id, "PASSWORD_RESET_REQUESTED", {},
            request
        )
        
        db.commit()
        
        # TODO: Send email with reset link
        # For now, just log the token
        logger.info(f"Password reset requested for {user.email}. Token: {reset_token}")
        
        return BaseResponse(
            message="If the email exists, a password reset link has been sent"
        )
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/reset-password", response_model=BaseResponse)
async def reset_password(
    reset_data: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_database)
):
    """
    Reset password using reset token
    """
    try:
        # Find valid reset token
        reset_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == reset_data.token,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        # Update password
        user.password_hash = get_password_hash(reset_data.new_password)
        user.updated_at = datetime.utcnow()
        
        # Mark reset token as used
        reset_token.used_at = datetime.utcnow()
        
        # Revoke all existing sessions
        db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).update({
            "is_active": False,
            "revoked_at": datetime.utcnow()
        })
        
        # Log password reset
        log_user_activity(
            db, user.id, "PASSWORD_RESET_COMPLETED", {},
            request
        )
        
        db.commit()
        
        logger.info(f"Password reset completed for user: {user.email}")
        
        return BaseResponse(message="Password reset successful. Please login with your new password.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Get user's active sessions
    """
    try:
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).order_by(UserSession.created_at.desc()).all()
        
        return {
            "sessions": [
                {
                    "id": session.id,
                    "created_at": session.created_at,
                    "ip_address": str(session.ip_address) if session.ip_address else None,
                    "user_agent": session.user_agent,
                    "expires_at": session.expires_at,
                    "device_info": session.device_info
                }
                for session in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Get sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Revoke a specific session
    """
    try:
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session.is_active = False
        session.revoked_at = datetime.utcnow()
        
        # Log session revocation
        log_user_activity(
            db, current_user.id, "SESSION_REVOKED", 
            {"session_id": session_id},
            request
        )
        
        db.commit()
        
        return BaseResponse(message="Session revoked successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session revocation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session"
        )