#!/usr/bin/env python3
"""
AIBOA API Gateway
Unified API endpoint for all microservices
"""

import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import redis
from contextlib import asynccontextmanager

from config import settings
from routers import (
    transcription_router,
    analysis_router,
    evaluation_router,
    reporting_router,
    workflows_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global HTTP client for service communication
http_client: httpx.AsyncClient = None

# Redis client for caching and rate limiting
redis_client: redis.Redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for startup and shutdown
    """
    global http_client, redis_client

    # Startup
    logger.info("Starting AIBOA API Gateway...")

    # Initialize HTTP client
    http_client = httpx.AsyncClient(timeout=settings.service_timeout)
    logger.info("HTTP client initialized")

    # Initialize Redis client
    try:
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True
        )
        redis_client.ping()
        logger.info(f"Redis connected: {settings.redis_host}:{settings.redis_port}")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        redis_client = None

    logger.info("Gateway started successfully")

    yield

    # Shutdown
    logger.info("Shutting down API Gateway...")

    if http_client:
        await http_client.aclose()
        logger.info("HTTP client closed")

    logger.info("Gateway shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Unified API Gateway for AIBOA Teaching Analysis Platform",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcription_router)
app.include_router(analysis_router)
app.include_router(evaluation_router)
app.include_router(reporting_router)
app.include_router(workflows_router)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()

    # Log request
    logger.info(f"Incoming: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"Completed: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {duration:.3f}s"
    )

    return response


# Error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred",
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "service": "gateway",
        "version": settings.app_version,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health")
async def api_health_check():
    """API health check (alternative endpoint)"""
    return await health_check()


@app.get("/api/services/health")
async def check_all_services():
    """
    Check health of all backend services
    """
    services = {
        "transcription": settings.transcription_service_url,
        "analysis": settings.analysis_service_url,
        "evaluation": settings.evaluation_service_url,
        "reporting": settings.reporting_service_url
    }

    service_status = {}

    for service_name, service_url in services.items():
        try:
            response = await http_client.get(
                f"{service_url}/health",
                timeout=5.0
            )

            service_status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": service_url,
                "response_code": response.status_code
            }

        except Exception as e:
            service_status[service_name] = {
                "status": "unreachable",
                "url": service_url,
                "error": str(e)
            }

    # Determine overall status
    all_healthy = all(
        s["status"] == "healthy" for s in service_status.values()
    )

    return {
        "gateway_status": "healthy",
        "services": service_status,
        "overall_status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/frameworks")
async def list_frameworks():
    """
    List available analysis frameworks

    Convenience endpoint that proxies to analysis service
    """
    try:
        response = await http_client.get(
            f"{settings.analysis_service_url}/api/analyze/frameworks",
            timeout=5.0
        )

        if response.status_code == 200:
            return response.json()
        else:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": "Failed to fetch frameworks"}
            )

    except Exception as e:
        logger.error(f"Error fetching frameworks: {e}")
        return JSONResponse(
            status_code=503,
            content={"error": "Analysis service unavailable"}
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AIBOA API Gateway",
        "version": settings.app_version,
        "status": "running",
        "documentation": "/docs",
        "health_check": "/health",
        "services_health": "/api/services/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
