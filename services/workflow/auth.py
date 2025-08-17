"""
Authentication utilities for AIBOA Workflow Service
Integrates with the authentication service for user verification
"""

import httpx
from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import logging

from .config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


class User(BaseModel):
    """User model for authentication"""
    id: int
    email: str
    full_name: str
    role: str
    status: str


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.auth_service_url = settings.auth_service_url
        self.timeout = httpx.Timeout(10.0)
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token with auth service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.auth_service_url}/auth/profile",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return User(**user_data)
                else:
                    logger.warning(f"Token verification failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    async def get_user_permissions(self, user: User) -> dict:
        """Get user permissions based on role"""
        # Define role-based permissions
        permissions = {
            "admin": {
                "workflow": ["create", "read", "update", "delete", "manage_all"],
                "export": ["all_formats"],
                "analytics": ["view_all"]
            },
            "coach": {
                "workflow": ["create", "read", "update", "delete"],
                "export": ["json", "pdf", "txt"],
                "analytics": ["view_own"]
            },
            "regular_user": {
                "workflow": ["create", "read"],
                "export": ["json", "txt"],
                "analytics": ["view_own"]
            }
        }
        
        return permissions.get(user.role, permissions["regular_user"])


# Global auth service instance
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user
    
    This dependency extracts the JWT token from the Authorization header,
    verifies it with the auth service, and returns the user information.
    """
    token = credentials.credentials
    
    # Verify token with auth service
    user = await auth_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active"
        )
    
    return user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current authenticated user (optional)"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_permission(required_permission: str, resource: str = "workflow"):
    """
    Dependency factory for requiring specific permissions
    
    Args:
        required_permission: Permission needed (e.g., 'create', 'read', 'delete')
        resource: Resource type (e.g., 'workflow', 'export', 'analytics')
    
    Returns:
        Dependency function that checks user permissions
    """
    
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # Get user permissions
        permissions = await auth_service.get_user_permissions(current_user)
        
        # Check if user has required permission for resource
        resource_permissions = permissions.get(resource, [])
        
        if required_permission not in resource_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {required_permission} access to {resource} required"
            )
        
        return current_user
    
    return permission_checker


def require_role(required_roles: list):
    """
    Dependency factory for requiring specific user roles
    
    Args:
        required_roles: List of allowed roles (e.g., ['admin', 'coach'])
    
    Returns:
        Dependency function that checks user role
    """
    
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: requires one of roles {required_roles}"
            )
        
        return current_user
    
    return role_checker


async def verify_workflow_access(
    workflow_user_id: int,
    current_user: User,
    action: str = "read"
) -> bool:
    """
    Verify if user can access a specific workflow
    
    Args:
        workflow_user_id: ID of the user who owns the workflow
        current_user: Current authenticated user
        action: Action being performed ('read', 'write', 'delete')
    
    Returns:
        True if access is allowed, False otherwise
    """
    # Admin can access all workflows
    if current_user.role == "admin":
        return True
    
    # Coach can read all workflows, but only modify their own
    if current_user.role == "coach":
        if action == "read":
            return True
        else:
            return workflow_user_id == current_user.id
    
    # Regular users can only access their own workflows
    return workflow_user_id == current_user.id


class WorkflowAccessChecker:
    """Helper class for checking workflow access permissions"""
    
    @staticmethod
    async def check_read_access(workflow_user_id: int, current_user: User) -> bool:
        """Check if user can read workflow"""
        return await verify_workflow_access(workflow_user_id, current_user, "read")
    
    @staticmethod
    async def check_write_access(workflow_user_id: int, current_user: User) -> bool:
        """Check if user can modify workflow"""
        return await verify_workflow_access(workflow_user_id, current_user, "write")
    
    @staticmethod
    async def check_delete_access(workflow_user_id: int, current_user: User) -> bool:
        """Check if user can delete workflow"""
        return await verify_workflow_access(workflow_user_id, current_user, "delete")
    
    @staticmethod
    async def require_workflow_access(workflow_user_id: int, current_user: User, action: str):
        """Require workflow access or raise HTTP exception"""
        if not await verify_workflow_access(workflow_user_id, current_user, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: cannot {action} this workflow"
            )


# Convenience dependency functions
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    return await require_role(["admin"])(current_user)


async def require_coach_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require coach or admin role"""
    return await require_role(["coach", "admin"])(current_user)


async def require_workflow_create_permission(current_user: User = Depends(get_current_user)) -> User:
    """Require workflow creation permission"""
    return await require_permission("create", "workflow")(current_user)


async def require_export_permission(format: str, current_user: User = Depends(get_current_user)) -> User:
    """Require export permission for specific format"""
    # Get user permissions
    permissions = await auth_service.get_user_permissions(current_user)
    export_permissions = permissions.get("export", [])
    
    # Check if user can export in this format
    if format not in export_permissions and "all_formats" not in export_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Export format '{format}' not allowed for your role"
        )
    
    return current_user


# Rate limiting helpers (if needed)
class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.user_requests = {}  # user_id -> [timestamp, ...]
    
    async def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        import time
        
        now = time.time()
        window_start = now - (self.window_minutes * 60)
        
        # Clean old requests
        if user_id in self.user_requests:
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id]
                if req_time > window_start
            ]
        else:
            self.user_requests[user_id] = []
        
        # Check if within limits
        if len(self.user_requests[user_id]) >= self.max_requests:
            return False
        
        # Add current request
        self.user_requests[user_id].append(now)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to check rate limits"""
    if not await rate_limiter.check_rate_limit(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return current_user