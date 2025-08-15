"""
API Client for AIBOA Backend Services
"""

import requests
import time
from typing import Dict, Any, Optional, BinaryIO
from utils.config import get_config, get_api_headers
import streamlit as st

class AIBOAClient:
    """Client for interacting with AIBOA backend services"""
    
    def __init__(self):
        config = get_config()
        self.transcription_url = config["TRANSCRIPTION_API_URL"]
        self.analysis_url = config["ANALYSIS_API_URL"]
        self.headers = get_api_headers()
        self.polling_interval = config["POLLING_INTERVAL"]
        self.job_timeout = config["JOB_TIMEOUT"]
    
    # Transcription Service Methods
    
    def upload_file_for_transcription(self, file: BinaryIO, filename: str, language: str = "ko") -> Dict[str, Any]:
        """Upload a file for transcription"""
        try:
            files = {"file": (filename, file, "application/octet-stream")}
            data = {"language": language}
            
            response = requests.post(
                f"{self.transcription_url}/api/transcribe/upload",
                files=files,
                data=data,
                headers={"X-API-Key": self.headers["X-API-Key"]}
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def transcribe_youtube(self, youtube_url: str, language: str = "ko") -> Dict[str, Any]:
        """Submit YouTube URL for transcription"""
        try:
            response = requests.post(
                f"{self.transcription_url}/api/transcribe/youtube",
                json={"youtube_url": youtube_url, "language": language},
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_transcription_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get transcription job status"""
        try:
            response = requests.get(
                f"{self.transcription_url}/api/transcribe/{job_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def wait_for_transcription(self, job_id: str, progress_callback=None) -> Dict[str, Any]:
        """Wait for transcription job to complete with optional progress callback"""
        start_time = time.time()
        
        while time.time() - start_time < self.job_timeout:
            result = self.get_transcription_job_status(job_id)
            
            if not result["success"]:
                return result
            
            status = result["data"].get("status")
            
            if progress_callback:
                progress_callback(status, result["data"])
            
            if status == "completed":
                return {"success": True, "data": result["data"]}
            elif status == "failed":
                return {"success": False, "error": result["data"].get("error", "Transcription failed")}
            
            time.sleep(self.polling_interval)
        
        return {"success": False, "error": "Transcription timeout"}
    
    # Analysis Service Methods
    
    def analyze_text(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze text for CBIL classification"""
        try:
            payload = {"text": text}
            if metadata:
                payload["metadata"] = metadata
            
            response = requests.post(
                f"{self.analysis_url}/api/analyze/text",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def analyze_transcript(self, transcript_id: str) -> Dict[str, Any]:
        """Analyze a transcription result"""
        try:
            response = requests.post(
                f"{self.analysis_url}/api/analyze/transcript",
                params={"transcript_id": transcript_id},
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """Get analysis result by ID"""
        try:
            response = requests.get(
                f"{self.analysis_url}/api/analysis/{analysis_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get platform statistics"""
        try:
            response = requests.get(
                f"{self.analysis_url}/api/statistics",
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    # Health Check Methods
    
    def check_transcription_health(self) -> bool:
        """Check if transcription service is healthy"""
        try:
            response = requests.get(f"{self.transcription_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_analysis_health(self) -> bool:
        """Check if analysis service is healthy"""
        try:
            response = requests.get(f"{self.analysis_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_all_services(self) -> Dict[str, bool]:
        """Check health of all services"""
        return {
            "transcription": self.check_transcription_health(),
            "analysis": self.check_analysis_health()
        }

# Helper functions for Streamlit integration

@st.cache_data(ttl=60)
def get_cached_statistics():
    """Get cached statistics (refreshes every 60 seconds)"""
    client = AIBOAClient()
    result = client.get_statistics()
    return result

def format_transcript_for_display(transcript_data: Dict[str, Any]) -> str:
    """Format transcript data for display"""
    if not transcript_data:
        return ""
    
    text = transcript_data.get("text", "")
    segments = transcript_data.get("segments", [])
    
    if segments:
        formatted = []
        for segment in segments:
            start = segment.get("start", 0)
            end = segment.get("end", 0)
            text = segment.get("text", "")
            formatted.append(f"[{start:.1f}s - {end:.1f}s] {text}")
        return "\n\n".join(formatted)
    
    return text

def format_cbil_scores(cbil_scores: Dict[int, float]) -> Dict[str, Any]:
    """Format CBIL scores for visualization"""
    config = get_config()
    cbil_levels = config["CBIL_LEVELS"]
    
    formatted = []
    for level, score in cbil_scores.items():
        level_info = cbil_levels.get(int(level), {})
        formatted.append({
            "level": level,
            "name": level_info.get("name", f"Level {level}"),
            "description": level_info.get("description", ""),
            "score": score,
            "percentage": score * 100,
            "color": level_info.get("color", "#888888")
        })
    
    return formatted