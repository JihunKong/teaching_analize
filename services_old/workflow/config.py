"""
Configuration settings for AIBOA Workflow Service
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = Field(default="AIBOA Workflow Service", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8003, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/aiboa",
        env="DATABASE_URL"
    )
    
    # External Services
    auth_service_url: str = Field(
        default="http://localhost:8002",
        env="AUTH_SERVICE_URL"
    )
    transcription_service_url: str = Field(
        default="http://localhost:8000",
        env="TRANSCRIPTION_SERVICE_URL"
    )
    analysis_service_url: str = Field(
        default="http://localhost:8001",
        env="ANALYSIS_SERVICE_URL"
    )
    
    # API Keys for service communication
    transcription_api_key: str = Field(
        default="transcription-api-key-prod-2025",
        env="TRANSCRIPTION_API_KEY"
    )
    analysis_api_key: str = Field(
        default="analysis-api-key-prod-2025",
        env="ANALYSIS_API_KEY"
    )
    
    # Redis for background tasks and caching
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://3.38.107.23"],
        env="CORS_ORIGINS"
    )
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods: List[str] = Field(default=["*"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="/var/log/aiboa/workflow.log", env="LOG_FILE")
    
    # File Upload and Processing
    max_file_size: int = Field(default=500 * 1024 * 1024, env="MAX_FILE_SIZE")  # 500MB
    upload_path: str = Field(default="/tmp/aiboa/uploads", env="UPLOAD_PATH")
    results_path: str = Field(default="/tmp/aiboa/results", env="RESULTS_PATH")
    
    # Workflow Configuration
    max_concurrent_workflows: int = Field(default=10, env="MAX_CONCURRENT_WORKFLOWS")
    workflow_timeout_minutes: int = Field(default=30, env="WORKFLOW_TIMEOUT_MINUTES")
    cleanup_completed_after_hours: int = Field(default=24, env="CLEANUP_COMPLETED_AFTER_HOURS")
    
    # Progress Tracking
    progress_update_interval: int = Field(default=5, env="PROGRESS_UPDATE_INTERVAL")  # seconds
    websocket_timeout: int = Field(default=300, env="WEBSOCKET_TIMEOUT")  # seconds
    
    # Language Support
    supported_languages: List[str] = Field(
        default=["ko", "en", "auto"],
        env="SUPPORTED_LANGUAGES"
    )
    default_language: str = Field(default="ko", env="DEFAULT_LANGUAGE")
    
    # Analysis Configuration
    default_analysis_framework: str = Field(default="cbil", env="DEFAULT_ANALYSIS_FRAMEWORK")
    analysis_timeout_minutes: int = Field(default=10, env="ANALYSIS_TIMEOUT_MINUTES")
    
    # Export Options
    supported_export_formats: List[str] = Field(
        default=["json", "pdf", "txt", "docx"],
        env="SUPPORTED_EXPORT_FORMATS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration dictionary"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_credentials,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers
        }


# Create global settings instance
settings = Settings()