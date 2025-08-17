"""
Configuration settings for AIBOA Authentication Service
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = Field(default="AIBOA Authentication Service", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8002, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/aiboa",
        env="DATABASE_URL"
    )
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Security
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    password_reset_expire_hours: int = Field(default=24, env="PASSWORD_RESET_EXPIRE_HOURS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # seconds
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    cors_methods: List[str] = Field(default=["*"], env="CORS_METHODS")
    cors_headers: List[str] = Field(default=["*"], env="CORS_HEADERS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Email Configuration (for password reset)
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_use_tls: bool = Field(default=True, env="SMTP_USE_TLS")
    email_from: Optional[str] = Field(default=None, env="EMAIL_FROM")
    
    # External Services
    transcription_service_url: str = Field(
        default="http://localhost:8000",
        env="TRANSCRIPTION_SERVICE_URL"
    )
    analysis_service_url: str = Field(
        default="http://localhost:8001",
        env="ANALYSIS_SERVICE_URL"
    )
    
    # API Keys for service communication
    transcription_api_key: Optional[str] = Field(default=None, env="TRANSCRIPTION_API_KEY")
    analysis_api_key: Optional[str] = Field(default=None, env="ANALYSIS_API_KEY")
    
    # File Upload
    upload_max_size: int = Field(default=500 * 1024 * 1024, env="UPLOAD_MAX_SIZE")  # 500MB
    allowed_file_types: List[str] = Field(
        default=["mp3", "mp4", "wav", "m4a", "webm"],
        env="ALLOWED_FILE_TYPES"
    )
    upload_path: str = Field(default="/tmp/uploads", env="UPLOAD_PATH")
    
    # Session Management
    max_sessions_per_user: int = Field(default=5, env="MAX_SESSIONS_PER_USER")
    session_cleanup_interval: int = Field(default=3600, env="SESSION_CLEANUP_INTERVAL")  # seconds
    
    # User Management
    default_user_role: str = Field(default="regular_user", env="DEFAULT_USER_ROLE")
    auto_verify_email: bool = Field(default=False, env="AUTO_VERIFY_EMAIL")
    allow_self_registration: bool = Field(default=False, env="ALLOW_SELF_REGISTRATION")
    
    # Analytics and Monitoring
    enable_analytics: bool = Field(default=True, env="ENABLE_ANALYTICS")
    analytics_retention_days: int = Field(default=90, env="ANALYTICS_RETENTION_DAYS")
    
    # Health Check
    health_check_enabled: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")  # seconds
    
    # Testing
    testing: bool = Field(default=False, env="TESTING")
    test_database_url: Optional[str] = Field(default=None, env="TEST_DATABASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("cors_methods", pre=True)
    def parse_cors_methods(cls, v):
        """Parse CORS methods from string or list"""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("cors_headers", pre=True)
    def parse_cors_headers(cls, v):
        """Parse CORS headers from string or list"""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from string or list"""
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(",")]
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator("log_format")
    def validate_log_format(cls, v):
        """Validate log format"""
        valid_formats = ["json", "text"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of: {valid_formats}")
        return v.lower()
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment"""
        valid_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == "testing" or self.testing
    
    def get_database_url(self) -> str:
        """Get the appropriate database URL"""
        if self.is_testing() and self.test_database_url:
            return self.test_database_url
        return self.database_url
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration dictionary"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_credentials,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers
        }
    
    def get_email_config(self) -> dict:
        """Get email configuration dictionary"""
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "smtp_username": self.smtp_username,
            "smtp_password": self.smtp_password,
            "smtp_use_tls": self.smtp_use_tls,
            "email_from": self.email_from or self.smtp_username
        }
    
    def is_email_configured(self) -> bool:
        """Check if email is properly configured"""
        return all([
            self.smtp_host,
            self.smtp_username,
            self.smtp_password,
            self.email_from or self.smtp_username
        ])


# Create global settings instance
settings = Settings()


# Configuration validation
def validate_configuration():
    """Validate critical configuration settings"""
    errors = []
    
    # Check required settings
    if not settings.secret_key:
        errors.append("SECRET_KEY is required")
    
    if settings.is_production():
        # Production-specific validations
        if settings.debug:
            errors.append("DEBUG should be False in production")
        
        if settings.database_url == "postgresql://postgres:password@localhost:5432/aiboa":
            errors.append("Default database URL should not be used in production")
        
        if len(settings.secret_key) < 32:
            errors.append("SECRET_KEY should be at least 32 characters in production")
        
        if "*" in settings.cors_origins:
            errors.append("CORS should not allow all origins in production")
    
    # Check database URL format
    if not settings.database_url.startswith(("postgresql://", "sqlite:///")):
        errors.append("DATABASE_URL must be a valid PostgreSQL or SQLite URL")
    
    # Check token expiration times
    if settings.access_token_expire_minutes < 1:
        errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be at least 1")
    
    if settings.refresh_token_expire_days < 1:
        errors.append("REFRESH_TOKEN_EXPIRE_DAYS must be at least 1")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")


# Export commonly used settings
__all__ = [
    "settings",
    "Settings",
    "validate_configuration"
]