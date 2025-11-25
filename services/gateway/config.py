"""
API Gateway Configuration
Environment-based service URL configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Gateway configuration settings"""

    # Gateway settings
    app_name: str = "AIBOA API Gateway"
    app_version: str = "1.0.0"
    debug: bool = False

    # Service URLs
    transcription_service_url: str = os.getenv(
        "TRANSCRIPTION_SERVICE_URL",
        "http://transcription:8000"
    )
    analysis_service_url: str = os.getenv(
        "ANALYSIS_SERVICE_URL",
        "http://analysis:8000"
    )
    evaluation_service_url: str = os.getenv(
        "EVALUATION_SERVICE_URL",
        "http://evaluation:8000"
    )
    reporting_service_url: str = os.getenv(
        "REPORTING_SERVICE_URL",
        "http://reporting:8000"
    )

    # Redis configuration
    redis_host: str = os.getenv("REDIS_HOST", "redis")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    redis_db: int = 0

    # Security
    secret_key: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-this-in-production"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://frontend:3000"
    ]

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Timeouts
    service_timeout: int = 300  # 5 minutes for long-running tasks

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
