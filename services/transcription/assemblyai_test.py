#!/usr/bin/env python3
"""
AssemblyAI API Test for YouTube Transcription
"""

import os
import requests
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AssemblyAITranscriber:
    """AssemblyAI API client for YouTube transcription"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ASSEMBLYAI_API_KEY')
        self.base_url = "https://api.assemblyai.com/v2"
        
        if not self.api_key:
            raise ValueError("AssemblyAI API key is required")
        
        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }
    
    def transcribe_youtube_url(self, video_url: str, language_code: str = "ko") -> Optional[str]:
        """
        Transcribe YouTube video directly from URL
        """
        try:
            # Submit transcription request
            transcript_request = {
                "audio_url": video_url,
                "language_code": language_code,
                "speaker_labels": True,  # Enable speaker detection
                "auto_chapters": True,   # Enable chapter detection
            }
            
            logger.info(f"Submitting transcription request for: {video_url}")
            
            response = requests.post(
                f"{self.base_url}/transcript",
                json=transcript_request,
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to submit request: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            transcript_data = response.json()
            transcript_id = transcript_data["id"]
            
            logger.info(f"Transcription job submitted with ID: {transcript_id}")
            
            # Poll for completion
            return self.wait_for_completion(transcript_id)
            
        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {e}")
            return None
    
    def wait_for_completion(self, transcript_id: str, max_wait: int = 600) -> Optional[str]:
        """
        Wait for transcription to complete and return the text
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(
                    f"{self.base_url}/transcript/{transcript_id}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to check status: {response.status_code}")
                    break
                
                result = response.json()
                status = result["status"]
                
                logger.info(f"Transcription status: {status}")
                
                if status == "completed":
                    transcript_text = result.get("text", "")
                    logger.info(f"Transcription completed! Length: {len(transcript_text)} characters")
                    return transcript_text
                
                elif status == "error":
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"Transcription failed: {error_msg}")
                    break
                
                elif status in ["queued", "processing"]:
                    # Still processing, wait and retry
                    time.sleep(10)
                    continue
                
                else:
                    logger.warning(f"Unknown status: {status}")
                    break
                    
            except Exception as e:
                logger.error(f"Error checking transcription status: {e}")
                break
        
        logger.error("Transcription timed out or failed")
        return None

# Test function
if __name__ == "__main__":
    # This requires AssemblyAI API key
    # You can get a free trial at https://www.assemblyai.com/
    
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    
    if not api_key:
        print("❌ No AssemblyAI API key found")
        print("🔑 Get a free trial key at: https://www.assemblyai.com/")
        print("💡 Set environment variable: export ASSEMBLYAI_API_KEY='your_key'")
        print()
        print("📋 Demo response for MVP:")
        print({
            "success": True,
            "service": "AssemblyAI",
            "text": "안녕하세요, 오늘 수업을 시작하겠습니다. 먼저 지난 시간에 배운 내용을 복습해보겠습니다.",
            "length": 87,
            "language": "ko"
        })
    else:
        print("🧪 Testing AssemblyAI with real API key...")
        
        transcriber = AssemblyAITranscriber(api_key)
        video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
        
        result = transcriber.transcribe_youtube_url(video_url, "ko")
        
        if result:
            print(f"✅ Success! Transcript: {result[:200]}...")
        else:
            print("❌ Failed to get transcript")