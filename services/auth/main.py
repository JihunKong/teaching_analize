"""
AIBOA Authentication Service
Main FastAPI application for user authentication and authorization
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import uvicorn

from .config import settings, validate_configuration
from .database import get_database, init_database, health_check
from .schemas import ErrorResponse
from .models import User

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_file) if settings.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting AIBOA Authentication Service...")
    
    try:
        # Validate configuration
        validate_configuration()
        logger.info("Configuration validated successfully")
        
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
        
        # Log startup information
        logger.info(f"Service: {settings.app_name} v{settings.app_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info(f"Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'local'}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        logger.info("Shutting down AIBOA Authentication Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Authentication and authorization service for AIBOA platform",
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    openapi_url="/openapi.json" if not settings.is_production() else None,
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    **settings.get_cors_config()
)

# Add trusted host middleware for production
if settings.is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this based on your deployment
    )


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            success=False,
            message="Invalid request data",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()},
            timestamp=datetime.now()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"error": str(exc)} if settings.debug else None,
            timestamp=datetime.now()
        ).dict()
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check_endpoint():
    """Health check endpoint"""
    try:
        db_health = health_check()
        
        return {
            "status": "healthy" if db_health.get("database") == "healthy" else "unhealthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": datetime.now().isoformat(),
            "database": db_health,
            "uptime": "unknown"  # Could implement uptime tracking
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": settings.app_name,
                "version": settings.app_version,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check endpoint"""
    from .database import get_database_info
    
    try:
        db_health = health_check()
        db_info = get_database_info()
        
        return {
            "status": "healthy" if db_health.get("database") == "healthy" else "unhealthy",
            "service": {
                "name": settings.app_name,
                "version": settings.app_version,
                "environment": settings.environment,
                "debug": settings.debug
            },
            "database": {
                "health": db_health,
                "info": db_info
            },
            "configuration": {
                "cors_enabled": bool(settings.cors_origins),
                "rate_limiting": settings.rate_limit_enabled,
                "email_configured": settings.is_email_configured(),
                "analytics_enabled": settings.enable_analytics
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# Authentication routes
from .routes import auth, users, admin, dashboard

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs_url": "/docs" if not settings.is_production() else None,
        "health_url": "/health",
        "timestamp": datetime.now().isoformat()
    }


# API information endpoint
@app.get("/info", tags=["Info"])
async def api_info():
    """API information endpoint"""
    return {
        "api": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        },
        "endpoints": {
            "auth": {
                "login": "/auth/login",
                "logout": "/auth/logout",
                "refresh": "/auth/refresh",
                "profile": "/auth/profile",
                "forgot_password": "/auth/forgot-password",
                "reset_password": "/auth/reset-password"
            },
            "users": {
                "list": "/users/",
                "create": "/users/",
                "get": "/users/{user_id}",
                "update": "/users/{user_id}",
                "delete": "/users/{user_id}"
            },
            "admin": {
                "users": "/admin/users/",
                "statistics": "/admin/statistics",
                "analytics": "/admin/analytics",
                "logs": "/admin/logs"
            },
            "dashboard": {
                "summary": "/dashboard/summary",
                "coach": "/dashboard/coach",
                "admin": "/dashboard/admin"
            }
        },
        "features": {
            "jwt_authentication": True,
            "role_based_access": True,
            "password_reset": settings.is_email_configured(),
            "user_management": True,
            "analytics": settings.enable_analytics,
            "rate_limiting": settings.rate_limit_enabled
        }
    }


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"Response: {response.status_code} "
        f"in {process_time:.3f}s"
    )
    
    return response


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=True
    )