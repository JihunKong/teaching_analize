#!/usr/bin/env python3
"""
Internal YouTube Test - Run this ON the AWS server
Tests YouTube functionality from inside AWS network
"""

import requests
import json
import time

SERVER_URL = "http://localhost:8000"  # Internal access
API_KEY = "transcription-api-key-prod-2025"

def test_internal_youtube():
    print("🧪 Internal YouTube Test on AWS Lightsail Server")
    print("=" * 50)
    
    # Test 1: Health check
    response = requests.get(f"{SERVER_URL}/health")
    print(f"Health Check: {response.json()}")
    
    # Test 2: Quick YouTube test with Rick Roll (short video)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    payload = {
        "youtube_url": test_url,
        "language": "en",
        "export_format": "json"
    }
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print(f"🎬 Testing YouTube URL: {test_url}")
    
    # Submit job
    response = requests.post(f"{SERVER_URL}/api/transcribe/youtube", json=payload, headers=headers)
    
    if response.status_code == 202:
        job_data = response.json()
        job_id = job_data.get("job_id")
        print(f"✅ Job submitted: {job_id}")
        
        # Poll for result (max 2 minutes)
        for i in range(24):  # 24 * 5 = 120 seconds
            time.sleep(5)
            status_response = requests.get(f"{SERVER_URL}/api/transcribe/{job_id}", headers=headers)
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                print(f"📊 Status: {status}")
                
                if status == "completed":
                    print("🎉 SUCCESS! YouTube transcription worked from AWS!")
                    print("✅ Migration objective achieved - YouTube is accessible from AWS IP")
                    transcript = status_data.get("transcript", "")
                    print(f"📄 Sample: {transcript[:100]}...")
                    return True
                elif status == "failed":
                    error = status_data.get("error", "Unknown error")
                    print(f"❌ Failed: {error}")
                    return False
                    
        print("⏰ Timeout after 2 minutes")
        return False
    else:
        print(f"❌ Request failed: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    test_internal_youtube()