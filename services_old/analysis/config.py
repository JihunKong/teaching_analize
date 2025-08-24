from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import Optional

class Settings(BaseSettings):
    # Railway Environment
    PORT: int = Field(default=8080, env="PORT")
    RAILWAY_ENVIRONMENT: str = Field(default="development", env="RAILWAY_ENVIRONMENT")
    RAILWAY_VOLUME_PATH: str = Field(default="/data", env="RAILWAY_VOLUME_PATH")
    
    # Database
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Redis
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    UPSTAGE_API_KEY: Optional[str] = Field(default=None, env="UPSTAGE_API_KEY")
    SOLAR_API_KEY: Optional[str] = Field(default=None, env="SOLAR_API_KEY")
    API_KEY: Optional[str] = Field(default="test-api-key", env="API_KEY")
    
    # File Storage
    ANALYSIS_DIR: str = Field(default="/data/analysis", env="ANALYSIS_DIR")
    REPORT_DIR: str = Field(default="/data/reports", env="REPORT_DIR")
    
    # LLM Settings
    LLM_MODEL: str = Field(default="solar-mini", env="LLM_MODEL")
    LLM_TEMPERATURE: float = Field(default=0.3, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # CBIL Settings
    CBIL_CONFIDENCE_THRESHOLD: float = Field(default=0.7, env="CBIL_CONFIDENCE_THRESHOLD")
    
    # Service Settings
    SERVICE_NAME: str = Field(default="Analysis Service", env="SERVICE_NAME")
    SERVICE_VERSION: str = Field(default="1.0.0", env="SERVICE_VERSION")
    
    # Transcription Service URL
    TRANSCRIPTION_SERVICE_URL: str = Field(
        default="https://teachinganalize-production.up.railway.app",
        env="TRANSCRIPTION_SERVICE_URL"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_storage_path(self, subdir: str) -> str:
        """Get full path for storage subdirectory"""
        base_path = self.RAILWAY_VOLUME_PATH if os.path.exists(self.RAILWAY_VOLUME_PATH) else "/tmp"
        path = os.path.join(base_path, subdir)
        os.makedirs(path, exist_ok=True)
        return path

settings = Settings()