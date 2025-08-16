"""
Configuration management for AIBOA frontend
"""

import os
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    """Get application configuration from environment variables"""
    
    return {
        # API URLs
        "TRANSCRIPTION_API_URL": os.getenv(
            "TRANSCRIPTION_API_URL", 
            "https://teachinganalize-production.up.railway.app"
        ),
        "ANALYSIS_API_URL": os.getenv(
            "ANALYSIS_API_URL",
            "https://amusedfriendship-production.up.railway.app"
        ),
        
        # API Authentication
        "API_KEY": os.getenv("API_KEY", "test-api-key"),
        
        # Application Settings
        "MAX_FILE_SIZE": int(os.getenv("MAX_FILE_SIZE", "200")),  # MB
        "POLLING_INTERVAL": int(os.getenv("POLLING_INTERVAL", "2")),  # seconds
        "JOB_TIMEOUT": int(os.getenv("JOB_TIMEOUT", "300")),  # seconds
        
        # UI Settings
        "THEME_PRIMARY_COLOR": os.getenv("THEME_PRIMARY_COLOR", "#1E88E5"),
        "THEME_BACKGROUND_COLOR": os.getenv("THEME_BACKGROUND_COLOR", "#FFFFFF"),
        
        # Feature Flags
        "ENABLE_YOUTUBE": os.getenv("ENABLE_YOUTUBE", "true").lower() == "true",
        "ENABLE_BATCH_UPLOAD": os.getenv("ENABLE_BATCH_UPLOAD", "false").lower() == "true",
        "ENABLE_PDF_EXPORT": os.getenv("ENABLE_PDF_EXPORT", "true").lower() == "true",
        
        # Supported Formats
        "SUPPORTED_VIDEO_FORMATS": ["mp4", "avi", "mov", "mkv"],
        "SUPPORTED_AUDIO_FORMATS": ["mp3", "wav", "m4a", "flac"],
        "SUPPORTED_LANGUAGES": {
            "ko": "Korean",
            "en": "English",
            "ja": "Japanese",
            "zh": "Chinese"
        },
        
        # CBIL Levels
        "CBIL_LEVELS": {
            1: {"name": "단순 확인", "description": "Simple confirmation", "color": "#FF6B6B"},
            2: {"name": "사실 회상", "description": "Fact recall", "color": "#FFA06B"},
            3: {"name": "개념 설명", "description": "Concept explanation", "color": "#FFD56B"},
            4: {"name": "분석적 사고", "description": "Analytical thinking", "color": "#A8E6CF"},
            5: {"name": "종합적 이해", "description": "Comprehensive understanding", "color": "#7FD1E4"},
            6: {"name": "평가적 판단", "description": "Evaluative judgment", "color": "#B19CD9"},
            7: {"name": "창의적 적용", "description": "Creative application", "color": "#FF88CC"}
        }
    }

def get_api_headers() -> Dict[str, str]:
    """Get headers for API requests"""
    config = get_config()
    return {
        "X-API-Key": config["API_KEY"],
        "Content-Type": "application/json"
    }

def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits"""
    config = get_config()
    max_size_bytes = config["MAX_FILE_SIZE"] * 1024 * 1024
    return file_size <= max_size_bytes

def validate_file_format(filename: str) -> tuple[bool, str]:
    """Validate if file format is supported"""
    config = get_config()
    extension = filename.lower().split('.')[-1]
    
    if extension in config["SUPPORTED_VIDEO_FORMATS"]:
        return True, "video"
    elif extension in config["SUPPORTED_AUDIO_FORMATS"]:
        return True, "audio"
    else:
        return False, "unsupported"