"""
Global configuration for AIBOA system
"""
import os
from pathlib import Path

class Settings:
    """Application settings"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    SOLAR_API_KEY = os.getenv("SOLAR_API_KEY", "")
    UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    API_KEY = os.getenv("API_KEY", "test-api-key")
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8080))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # File Storage
    BASE_DIR = Path(__file__).parent
    STORAGE_PATH = Path(os.getenv("RAILWAY_VOLUME_PATH", "/tmp/aiboa"))
    UPLOAD_DIR = STORAGE_PATH / "uploads"
    TRANSCRIPT_DIR = STORAGE_PATH / "transcripts"
    ANALYSIS_DIR = STORAGE_PATH / "analysis"
    REPORT_DIR = STORAGE_PATH / "reports"
    
    # File Limits
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    ALLOWED_EXTENSIONS = {
        "audio": [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"],
        "video": [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    }
    
    # Whisper Settings
    WHISPER_MODEL = "whisper-1"
    WHISPER_MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB (API limit)
    DEFAULT_LANGUAGE = "ko"
    
    # LLM Settings
    LLM_MODEL = "solar-mini"
    LLM_TEMPERATURE = 0.3
    LLM_MAX_TOKENS = 1000
    
    # CBIL Analysis Settings
    CBIL_LEVELS = {
        1: {"name": "단순 확인", "description": "Simple confirmation", "weight": 0.1},
        2: {"name": "사실 회상", "description": "Fact recall", "weight": 0.2},
        3: {"name": "개념 설명", "description": "Concept explanation", "weight": 0.3},
        4: {"name": "분석적 사고", "description": "Analytical thinking", "weight": 0.5},
        5: {"name": "종합적 이해", "description": "Comprehensive understanding", "weight": 0.7},
        6: {"name": "평가적 판단", "description": "Evaluative judgment", "weight": 0.85},
        7: {"name": "창의적 적용", "description": "Creative application", "weight": 1.0}
    }
    
    # Job Settings
    JOB_TIMEOUT = 600  # 10 minutes
    JOB_CLEANUP_DAYS = 7  # Clean up old jobs after 7 days
    
    def __init__(self):
        """Initialize settings and create directories"""
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        for dir_path in [self.UPLOAD_DIR, self.TRANSCRIPT_DIR, self.ANALYSIS_DIR, self.REPORT_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def is_configured(self) -> bool:
        """Check if essential API keys are configured"""
        return bool(self.OPENAI_API_KEY or self.UPSTAGE_API_KEY or self.SOLAR_API_KEY)
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return Path(filename).suffix.lower()
    
    def is_audio_file(self, filename: str) -> bool:
        """Check if file is an audio file"""
        ext = self.get_file_extension(filename)
        return ext in self.ALLOWED_EXTENSIONS["audio"]
    
    def is_video_file(self, filename: str) -> bool:
        """Check if file is a video file"""
        ext = self.get_file_extension(filename)
        return ext in self.ALLOWED_EXTENSIONS["video"]
    
    def is_media_file(self, filename: str) -> bool:
        """Check if file is a supported media file"""
        return self.is_audio_file(filename) or self.is_video_file(filename)

# Global settings instance
settings = Settings()