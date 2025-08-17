"""
Authentication utilities for AIBOA Authentication Service
"""

import os
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from passlib.context import CryptContext
from jose import JWTError
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time (optional)
        
    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time (optional)
        
    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Refresh token creation error: {e}")
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        token_type: Expected token type ('access' or 'refresh')
        
    Returns:
        Optional[Dict[str, Any]]: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type. Expected: {token_type}, Got: {payload.get('type')}")
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            logger.warning("Token missing expiration")
            return None
            
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Token has expired")
            return None
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification error: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from JWT token
    
    Args:
        token: JWT token
        
    Returns:
        Optional[int]: User ID if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def generate_password_reset_token() -> str:
    """
    Generate a secure password reset token
    
    Returns:
        str: Password reset token
    """
    return secrets.token_urlsafe(32)


def generate_session_token() -> str:
    """
    Generate a secure session token
    
    Returns:
        str: Session token
    """
    return secrets.token_urlsafe(64)


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dict[str, Any]: Validation result with score and suggestions
    """
    issues = []
    score = 0
    
    # Length check
    if len(password) >= 8:
        score += 20
    else:
        issues.append("Password must be at least 8 characters long")
    
    if len(password) >= 12:
        score += 10
    
    # Character variety checks
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if has_lower:
        score += 15
    else:
        issues.append("Password should contain lowercase letters")
    
    if has_upper:
        score += 15
    else:
        issues.append("Password should contain uppercase letters")
    
    if has_digit:
        score += 15
    else:
        issues.append("Password should contain numbers")
    
    if has_special:
        score += 25
    else:
        issues.append("Password should contain special characters")
    
    # Common password check (basic)
    common_passwords = [
        "password", "123456", "qwerty", "abc123", "password123",
        "admin", "letmein", "welcome", "monkey", "dragon"
    ]
    
    if password.lower() in common_passwords:
        score -= 30
        issues.append("Password is too common")
    
    # Strength rating
    if score >= 80:
        strength = "strong"
    elif score >= 60:
        strength = "medium"
    elif score >= 40:
        strength = "weak"
    else:
        strength = "very_weak"
    
    return {
        "score": max(0, score),
        "strength": strength,
        "issues": issues,
        "is_valid": score >= 60 and len(issues) == 0
    }


def check_user_permissions(user_permissions: Dict[str, Any], required_permission: str, resource: str = "default") -> bool:
    """
    Check if user has required permissions
    
    Args:
        user_permissions: User's permission dictionary
        required_permission: Required permission (e.g., 'read', 'write', 'delete')
        resource: Resource type (e.g., 'users', 'analytics', 'system')
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    try:
        # Admin has all permissions
        if user_permissions.get("system", {}) and "configure" in user_permissions.get("system", []):
            return True
        
        # Check specific resource permissions
        resource_permissions = user_permissions.get(resource, [])
        if isinstance(resource_permissions, list):
            return required_permission in resource_permissions
        
        return False
        
    except Exception as e:
        logger.error(f"Permission check error: {e}")
        return False


def get_user_role_permissions(role: str) -> Dict[str, Any]:
    """
    Get default permissions for a user role
    
    Args:
        role: User role name
        
    Returns:
        Dict[str, Any]: Role permissions
    """
    role_permissions = {
        "admin": {
            "users": ["create", "read", "update", "delete"],
            "analytics": ["read"],
            "system": ["configure"],
            "data": ["read_all", "export"]
        },
        "coach": {
            "own_data": ["create", "read"],
            "dashboard": ["read"],
            "reports": ["generate"],
            "history": ["read"],
            "compare": ["read"]
        },
        "regular_user": {
            "transcription": ["create"],
            "analysis": ["create"],
            "results": ["read_own"],
            "workflow": ["unified"]
        }
    }
    
    return role_permissions.get(role, {})


def create_user_tokens(user_id: int, user_email: str, user_role: str) -> Dict[str, Any]:
    """
    Create both access and refresh tokens for a user
    
    Args:
        user_id: User's database ID
        user_email: User's email
        user_role: User's role
        
    Returns:
        Dict[str, Any]: Token information
    """
    # Token payload
    token_data = {
        "sub": user_id,
        "email": user_email,
        "role": user_role
    }
    
    # Create tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }


def decode_token_safely(token: str) -> Optional[Dict[str, Any]]:
    """
    Safely decode a token without verification (for debugging)
    
    Args:
        token: JWT token
        
    Returns:
        Optional[Dict[str, Any]]: Token payload if decodable, None otherwise
    """
    try:
        # Decode without verification for debugging
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired
    
    Args:
        token: JWT token
        
    Returns:
        bool: True if expired, False otherwise
    """
    payload = decode_token_safely(token)
    if not payload:
        return True
    
    exp = payload.get("exp")
    if exp is None:
        return True
    
    return datetime.utcnow() > datetime.fromtimestamp(exp)


def get_token_remaining_time(token: str) -> Optional[timedelta]:
    """
    Get remaining time for a token
    
    Args:
        token: JWT token
        
    Returns:
        Optional[timedelta]: Remaining time if token is valid, None otherwise
    """
    payload = decode_token_safely(token)
    if not payload:
        return None
    
    exp = payload.get("exp")
    if exp is None:
        return None
    
    expiry_time = datetime.fromtimestamp(exp)
    remaining = expiry_time - datetime.utcnow()
    
    return remaining if remaining > timedelta(0) else timedelta(0)