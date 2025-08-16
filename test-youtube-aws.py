#!/usr/bin/env python3
"""
AIBOA YouTube Transcription Test on AWS Lightsail
Critical test to verify YouTube access works from AWS (main migration reason)
"""

import requests
import json
import time
import sys

# AWS Lightsail server configuration
SERVER_IP = "3.38.107.23"
TRANSCRIPTION_URL = f"http://{SERVER_IP}:8000"
API_KEY = "transcription-api-key-prod-2025"

# Test Korean educational video (short for quick testing)
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Short test video
KOREAN_EDUCATIONAL_URL = "https://www.youtube.com/watch?v=M7lc1UVf-VE"  # Korean education video

def test_health():
    """Test if transcription service is responding"""
    print("🏥 Testing transcription service health...")
    try:
        response = requests.get(f"{TRANSCRIPTION_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Transcription service is healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_youtube_transcription(youtube_url, test_name):
    """Test YouTube transcription functionality"""
    print(f"\n🎬 Testing YouTube transcription: {test_name}")
    print(f"🔗 URL: {youtube_url}")
    
    # Submit transcription job
    payload = {
        "youtube_url": youtube_url,
        "language": "ko",
        "export_format": "json"
    }
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        print("📤 Submitting transcription request...")
        response = requests.post(
            f"{TRANSCRIPTION_URL}/api/transcribe/youtube",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 202:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        job_data = response.json()
        job_id = job_data.get("job_id")
        print(f"✅ Job submitted successfully. Job ID: {job_id}")
        
        # Poll for completion
        max_attempts = 60  # 5 minutes maximum
        for attempt in range(max_attempts):
            print(f"⏳ Checking progress... ({attempt+1}/{max_attempts})")
            
            status_response = requests.get(
                f"{TRANSCRIPTION_URL}/api/transcribe/{job_id}",
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                
                print(f"📊 Status: {status}")
                
                if status == "completed":
                    print("🎉 YOUTUBE TRANSCRIPTION SUCCESSFUL!")
                    print(f"📄 Transcript preview: {status_data.get('transcript', '')[:200]}...")
                    return True
                    
                elif status == "failed":
                    error = status_data.get("error", "Unknown error")
                    print(f"❌ Transcription failed: {error}")
                    
                    # Check for specific blocking errors
                    if "blocked" in error.lower() or "forbidden" in error.lower():
                        print("🚨 POSSIBLE IP BLOCKING DETECTED!")
                        
                    return False
                    
                elif status in ["pending", "processing"]:
                    time.sleep(5)  # Wait 5 seconds before next check
                    continue
                else:
                    print(f"⚠️ Unknown status: {status}")
                    time.sleep(5)
                    
            else:
                print(f"❌ Status check failed: {status_response.status_code}")
                return False
                
        print("⏰ Timeout: Job did not complete within 5 minutes")
        return False
        
    except Exception as e:
        print(f"❌ Exception during transcription test: {e}")
        return False

def main():
    """Run comprehensive YouTube transcription tests"""
    print("🚀 AIBOA YouTube Transcription Test on AWS Lightsail")
    print(f"🖥️ Server: {SERVER_IP}")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("❌ Cannot proceed - service unhealthy")
        sys.exit(1)
    
    # Test 2: Short English video (fast test)
    success_1 = test_youtube_transcription(TEST_YOUTUBE_URL, "Short Test Video")
    
    # Test 3: Korean educational video (main use case)
    success_2 = test_youtube_transcription(KOREAN_EDUCATIONAL_URL, "Korean Educational Video")
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Health Check: {'✅ PASS' if test_health() else '❌ FAIL'}")
    print(f"Short Video: {'✅ PASS' if success_1 else '❌ FAIL'}")
    print(f"Korean Education: {'✅ PASS' if success_2 else '❌ FAIL'}")
    
    if success_1 and success_2:
        print("\n🎉 ALL TESTS PASSED! YouTube access is working from AWS!")
        print("✅ Migration from Railway successful - YouTube blocking resolved!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        if not success_1 and not success_2:
            print("🚨 Complete YouTube access failure - investigate server/API keys")
        else:
            print("⚠️ Partial failure - some videos work, others don't")
        sys.exit(1)

if __name__ == "__main__":
    main()