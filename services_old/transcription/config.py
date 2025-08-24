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
    YOUTUBE_API_KEY: Optional[str] = Field(default=None, env="YOUTUBE_API_KEY")
    API_KEY: Optional[str] = Field(default="test-api-key", env="API_KEY")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="/data/uploads", env="UPLOAD_DIR")
    TRANSCRIPT_DIR: str = Field(default="/data/transcripts", env="TRANSCRIPT_DIR")
    MAX_FILE_SIZE: int = Field(default=500 * 1024 * 1024, env="MAX_FILE_SIZE")  # 500MB
    
    # Whisper Settings
    WHISPER_MODEL: str = Field(default="whisper-1", env="WHISPER_MODEL")
    DEFAULT_LANGUAGE: str = Field(default="ko", env="DEFAULT_LANGUAGE")
    
    # Service Settings
    SERVICE_NAME: str = Field(default="Transcription Service", env="SERVICE_NAME")
    SERVICE_VERSION: str = Field(default="1.0.0", env="SERVICE_VERSION")
    
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