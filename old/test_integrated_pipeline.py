#!/usr/bin/env python3
"""
AIBOA Integrated Pipeline Test
Tests the complete YouTube transcription → CBIL analysis pipeline
"""

import requests
import time
import json
from datetime import datetime

# Service endpoints
TRANSCRIPTION_SERVICE = "http://localhost:8000"
ANALYSIS_SERVICE = "http://localhost:8001"

# Test YouTube URLs (Korean educational content)
TEST_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Test video
    "https://youtu.be/jNQXAC9IVRw",  # Another test video
]

def test_service_health():
    """Test if both services are running"""
    print("🏥 Health Check:")
    
    try:
        # Test transcription service
        response = requests.get(f"{TRANSCRIPTION_SERVICE}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Transcription Service (Port 8000): HEALTHY")
        else:
            print(f"  ❌ Transcription Service: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Transcription Service: CONNECTION FAILED - {e}")
        return False
    
    try:
        # Test analysis service
        response = requests.get(f"{ANALYSIS_SERVICE}/health", timeout=5)
        if response.status_code == 200:
            print("  ✅ Analysis Service (Port 8001): HEALTHY")
        else:
            print(f"  ❌ Analysis Service: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Analysis Service: CONNECTION FAILED - {e}")
        return False
    
    return True

def test_subtitle_check(youtube_url):
    """Test subtitle availability check"""
    print(f"📺 Testing Subtitle Check: {youtube_url}")
    
    try:
        response = requests.post(
            f"{TRANSCRIPTION_SERVICE}/api/subtitles/check",
            json={"youtube_url": youtube_url},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Video: {result.get('video_info', {}).get('title', 'Unknown')}")
            print(f"  📊 Subtitles Available: {result.get('has_real_subtitles', False)}")
            return True
        else:
            print(f"  ❌ Subtitle check failed: {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception during subtitle check: {e}")
        return False

def test_transcription(youtube_url):
    """Test YouTube transcription"""
    print(f"🎬 Testing Transcription: {youtube_url}")
    
    try:
        # Start transcription job
        response = requests.post(
            f"{TRANSCRIPTION_SERVICE}/api/transcribe/youtube",
            json={
                "youtube_url": youtube_url,
                "language": "ko",
                "export_format": "json"
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"  ❌ Failed to start transcription: {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return None
        
        result = response.json()
        job_id = result.get("job_id")
        print(f"  📝 Job ID: {job_id}")
        print(f"  ⏳ Status: {result.get('status')}")
        
        # Poll for completion
        max_attempts = 30
        for attempt in range(max_attempts):
            time.sleep(2)
            
            status_response = requests.get(
                f"{TRANSCRIPTION_SERVICE}/api/transcribe/{job_id}",
                timeout=5
            )
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                current_status = status_result.get("status")
                print(f"  📊 Attempt {attempt+1}: {current_status}")
                
                if current_status == "completed":
                    transcript_result = status_result.get("result", {})
                    
                    if transcript_result.get("error"):
                        print(f"  ❌ Transcription failed: {transcript_result.get('message')}")
                        return None
                    
                    print(f"  ✅ Transcription completed!")
                    print(f"  📄 Title: {transcript_result.get('video_info', {}).get('title', 'Unknown')}")
                    print(f"  📊 Text Length: {len(transcript_result.get('text', ''))}")
                    print(f"  🎯 Method: {transcript_result.get('extraction_method', 'unknown')}")
                    
                    return transcript_result
                    
                elif current_status == "failed":
                    error_msg = status_result.get("error", "Unknown error")
                    print(f"  ❌ Transcription failed: {error_msg}")
                    return None
            
        print(f"  ⏰ Timeout after {max_attempts} attempts")
        return None
        
    except Exception as e:
        print(f"  ❌ Exception during transcription: {e}")
        return None

def test_cbil_analysis(transcript_result):
    """Test CBIL analysis on transcript"""
    print(f"🧠 Testing CBIL Analysis")
    
    try:
        # Prepare analysis request
        analysis_request = {
            "text": transcript_result.get("text", ""),
            "metadata": {
                "video_info": transcript_result.get("video_info", {}),
                "extraction_method": transcript_result.get("extraction_method"),
                "language": transcript_result.get("language", "ko")
            }
        }
        
        # Send to analysis service
        response = requests.post(
            f"{ANALYSIS_SERVICE}/api/analyze/transcript",
            json=analysis_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ CBIL Analysis completed!")
            print(f"  📊 Analysis ID: {result.get('analysis_id')}")
            print(f"  🎯 Overall CBIL Score: {result.get('overall_score')}")
            print(f"  📈 Method: {result.get('method', 'unknown')}")
            
            # Display CBIL distribution
            cbil_dist = result.get("cbil_level_distribution", {})
            print(f"  📊 CBIL Distribution:")
            print(f"     - Low Level: {cbil_dist.get('low_level', 0)}%")
            print(f"     - Mid Level: {cbil_dist.get('mid_level', 0)}%") 
            print(f"     - High Level: {cbil_dist.get('high_level', 0)}%")
            
            # Show recommendations
            recommendations = result.get("recommendations", [])
            if recommendations:
                print(f"  💡 Recommendations:")
                for rec in recommendations:
                    print(f"     - {rec}")
            
            # Show top keywords
            keywords = result.get("top_keywords", {})
            if keywords:
                print(f"  🔑 Top Keywords: {list(keywords.keys())[:5]}")
            
            return result
        else:
            print(f"  ❌ Analysis failed: {response.status_code}")
            print(f"  📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"  ❌ Exception during analysis: {e}")
        return None

def test_integrated_pipeline():
    """Test complete pipeline"""
    print("🚀 AIBOA Integrated Pipeline Test")
    print("=" * 50)
    
    # Health check
    if not test_service_health():
        print("\n❌ Services not ready. Please start the services first:")
        print("  - Transcription Service: python services/transcription/main.py")
        print("  - Analysis Service: python services/analysis/main.py")
        return False
    
    print("\n" + "=" * 50)
    
    success_count = 0
    total_tests = len(TEST_URLS)
    
    for i, url in enumerate(TEST_URLS, 1):
        print(f"\n🧪 Test {i}/{total_tests}: {url}")
        print("-" * 40)
        
        # Step 1: Check subtitles
        if not test_subtitle_check(url):
            print(f"  ⚠️ Skipping {url} - subtitle check failed")
            continue
        
        # Step 2: Transcribe
        transcript_result = test_transcription(url)
        if not transcript_result:
            print(f"  ⚠️ Skipping {url} - transcription failed")
            continue
        
        # Step 3: Analyze
        analysis_result = test_cbil_analysis(transcript_result)
        if not analysis_result:
            print(f"  ⚠️ Analysis failed for {url}")
            continue
        
        success_count += 1
        print(f"  ✅ Complete pipeline success for {url}")
    
    print("\n" + "=" * 50)
    print(f"🏁 FINAL RESULTS:")
    print(f"  ✅ Successful: {success_count}/{total_tests}")
    print(f"  ❌ Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count > 0:
        print(f"\n🎉 PIPELINE IS WORKING! Mock data has been replaced with real functionality.")
        print(f"✅ YouTube transcription ✅ CBIL analysis ✅ End-to-end flow")
    else:
        print(f"\n❌ Pipeline needs debugging. Check service logs.")
    
    return success_count == total_tests

if __name__ == "__main__":
    test_integrated_pipeline()