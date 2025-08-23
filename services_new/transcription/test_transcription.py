#!/usr/bin/env python3
"""
Test script for the robust YouTube transcription system
Tests all three methods with various types of YouTube videos
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test cases including different types of YouTube videos
TEST_CASES = [
    {
        "name": "Standard video with auto-captions",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "expected_method": "youtube_transcript_api",
        "description": "Should work with YouTube Transcript API"
    },
    {
        "name": "Video with disabled transcripts (fallback test)",
        "url": "https://www.youtube.com/watch?v=-OLCt6WScEY",
        "expected_method": ["whisper_api", "browser_scraping"],
        "description": "Should fallback to Whisper API or browser automation"
    },
    {
        "name": "Educational content (Korean)",
        "url": "https://www.youtube.com/watch?v=-OLCt6WScEY&list=PLugIxwJYmOhl_8KO3GHx9gp6VKMmbsTfw",
        "expected_method": ["youtube_transcript_api", "whisper_api", "browser_scraping"],
        "description": "Test case from TRANSCRIPT_METHOD.md"
    },
    {
        "name": "Short URL format",
        "url": "https://youtu.be/dQw4w9WgXcQ",
        "expected_method": "youtube_transcript_api",
        "description": "Test URL parsing for youtu.be format"
    }
]

async def test_method_1_youtube_api(video_url: str) -> Dict[str, Any]:
    """Test Method 1: YouTube Transcript API"""
    try:
        from main import extract_video_id
        from youtube_transcript_api import YouTubeTranscriptApi
        
        logger.info(f"[Method 1] Testing YouTube API with {video_url}")
        
        video_id = extract_video_id(video_url)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try Korean first, then English
        for lang in ['ko', 'en']:
            try:
                transcript = transcript_list.find_transcript([lang])
                transcript_data = transcript.fetch()
                full_text = " ".join([entry['text'] for entry in transcript_data])
                
                return {
                    "success": True,
                    "method": "youtube_transcript_api",
                    "language": lang,
                    "character_count": len(full_text),
                    "word_count": len(full_text.split()),
                    "sample_text": full_text[:100] + "..." if len(full_text) > 100 else full_text
                }
            except:
                continue
        
        return {"success": False, "error": "No transcripts found in supported languages"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_method_2_whisper_api(video_url: str) -> Dict[str, Any]:
    """Test Method 2: OpenAI Whisper API"""
    try:
        from whisper_transcriber import transcribe_with_whisper
        
        logger.info(f"[Method 2] Testing Whisper API with {video_url}")
        
        result = await transcribe_with_whisper(video_url, language="ko")
        
        if result["success"]:
            return {
                "success": True,
                "method": "whisper_api",
                "character_count": result["character_count"],
                "word_count": result["word_count"],
                "sample_text": result["transcript"][:100] + "..." if len(result["transcript"]) > 100 else result["transcript"],
                "processing_time": result.get("processing_time", 0)
            }
        else:
            return {"success": False, "error": result["error"]}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_method_3_browser_automation(video_url: str) -> Dict[str, Any]:
    """Test Method 3: Browser Automation"""
    try:
        from browser_transcriber import transcribe_with_browser
        
        logger.info(f"[Method 3] Testing Browser Automation with {video_url}")
        
        result = await transcribe_with_browser(video_url, language="ko")
        
        if result["success"]:
            return {
                "success": True,
                "method": "browser_scraping",
                "character_count": result["character_count"],
                "word_count": result["word_count"],
                "sample_text": result["transcript"][:100] + "..." if len(result["transcript"]) > 100 else result["transcript"],
                "processing_time": result.get("processing_time", 0),
                "metadata": result.get("metadata", {})
            }
        else:
            return {"success": False, "error": result["error"]}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_multi_method_fallback(video_url: str) -> Dict[str, Any]:
    """Test the complete multi-method fallback system"""
    try:
        from main import get_transcript_with_fallbacks, extract_video_id
        
        logger.info(f"[Multi-method] Testing complete fallback system with {video_url}")
        
        video_id = extract_video_id(video_url)
        result = await get_transcript_with_fallbacks(video_id, "ko", video_url)
        
        if result["success"]:
            return {
                "success": True,
                "method": result["method_used"],
                "character_count": result["character_count"],
                "word_count": result["word_count"],
                "sample_text": result["transcript"][:100] + "..." if len(result["transcript"]) > 100 else result["transcript"]
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "detailed_errors": result.get("detailed_errors", {})
            }
    
    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_api_endpoints():
    """Test API endpoints"""
    import requests
    import time
    
    logger.info("Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{base_url}/health", timeout=10)
        logger.info(f"Health check: {health_response.status_code}")
        
        # Test job submission (proven endpoint)
        job_data = {
            "youtube_url": test_video,
            "language": "en",
            "export_format": "json"
        }
        
        submit_response = requests.post(f"{base_url}/api/jobs/submit", json=job_data, timeout=10)
        if submit_response.status_code == 200:
            job_info = submit_response.json()
            job_id = job_info["job_id"]
            logger.info(f"Job submitted: {job_id}")
            
            # Monitor job status
            for i in range(60):  # Wait up to 10 minutes
                status_response = requests.get(f"{base_url}/api/jobs/{job_id}/status", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    logger.info(f"Job status: {status_data['status']} - {status_data.get('message', '')}")
                    
                    if status_data["status"] in ["SUCCESS", "FAILURE"]:
                        return {
                            "api_test": True,
                            "job_id": job_id,
                            "final_status": status_data["status"],
                            "result": status_data.get("result", {})
                        }
                
                time.sleep(10)
            
            return {"api_test": False, "error": "Job timeout"}
        else:
            return {"api_test": False, "error": f"Submit failed: {submit_response.status_code}"}
    
    except Exception as e:
        return {"api_test": False, "error": str(e)}

async def run_comprehensive_tests():
    """Run comprehensive tests on all methods and cases"""
    logger.info("Starting comprehensive transcription tests...")
    
    results = {}
    
    for test_case in TEST_CASES:
        logger.info(f"\\n{'='*60}")
        logger.info(f"Testing: {test_case['name']}")
        logger.info(f"URL: {test_case['url']}")
        logger.info(f"Description: {test_case['description']}")
        logger.info(f"{'='*60}")
        
        case_results = {
            "test_case": test_case,
            "methods": {}
        }
        
        # Test Method 1: YouTube API
        logger.info("\\n--- Testing Method 1: YouTube Transcript API ---")
        method1_result = await test_method_1_youtube_api(test_case["url"])
        case_results["methods"]["youtube_api"] = method1_result
        
        if method1_result["success"]:
            logger.info(f"✅ Method 1 SUCCESS: {method1_result['character_count']} chars")
            logger.info(f"Sample: {method1_result.get('sample_text', 'N/A')}")
        else:
            logger.warning(f"❌ Method 1 FAILED: {method1_result['error']}")
        
        # Test Method 2: Whisper API (only if Method 1 failed or for comparison)
        if not method1_result["success"] or test_case["name"] == "Video with disabled transcripts (fallback test)":
            logger.info("\\n--- Testing Method 2: OpenAI Whisper API ---")
            method2_result = await test_method_2_whisper_api(test_case["url"])
            case_results["methods"]["whisper_api"] = method2_result
            
            if method2_result["success"]:
                logger.info(f"✅ Method 2 SUCCESS: {method2_result['character_count']} chars in {method2_result.get('processing_time', 0):.1f}s")
                logger.info(f"Sample: {method2_result.get('sample_text', 'N/A')}")
            else:
                logger.warning(f"❌ Method 2 FAILED: {method2_result['error']}")
        
        # Test Method 3: Browser Automation (only for fallback cases)
        if test_case["name"] == "Video with disabled transcripts (fallback test)":
            logger.info("\\n--- Testing Method 3: Browser Automation ---")
            method3_result = await test_method_3_browser_automation(test_case["url"])
            case_results["methods"]["browser_automation"] = method3_result
            
            if method3_result["success"]:
                logger.info(f"✅ Method 3 SUCCESS: {method3_result['character_count']} chars in {method3_result.get('processing_time', 0):.1f}s")
                logger.info(f"Sample: {method3_result.get('sample_text', 'N/A')}")
                logger.info(f"Metadata: {method3_result.get('metadata', {})}")
            else:
                logger.warning(f"❌ Method 3 FAILED: {method3_result['error']}")
        
        # Test Multi-method Fallback System
        logger.info("\\n--- Testing Multi-method Fallback System ---")
        multi_method_result = await test_multi_method_fallback(test_case["url"])
        case_results["multi_method"] = multi_method_result
        
        if multi_method_result["success"]:
            logger.info(f"🎯 MULTI-METHOD SUCCESS: {multi_method_result['character_count']} chars using {multi_method_result['method']}")
            logger.info(f"Sample: {multi_method_result.get('sample_text', 'N/A')}")
        else:
            logger.error(f"💥 MULTI-METHOD FAILED: {multi_method_result['error']}")
            if "detailed_errors" in multi_method_result:
                logger.error(f"Detailed errors: {multi_method_result['detailed_errors']}")
        
        results[test_case["name"]] = case_results
        
        # Wait between tests to avoid rate limiting
        await asyncio.sleep(2)
    
    # Test API endpoints if service is running
    logger.info("\\n" + "="*60)
    logger.info("Testing API Endpoints")
    logger.info("="*60)
    
    api_result = await test_api_endpoints()
    results["api_test"] = api_result
    
    if api_result.get("api_test"):
        logger.info("🌐 API TEST SUCCESS")
    else:
        logger.warning(f"🌐 API TEST FAILED: {api_result.get('error', 'Unknown error')}")
    
    return results

def print_test_summary(results: Dict[str, Any]):
    """Print a comprehensive test summary"""
    logger.info("\\n" + "="*80)
    logger.info("COMPREHENSIVE TEST SUMMARY")
    logger.info("="*80)
    
    total_tests = len([k for k in results.keys() if k != "api_test"])
    successful_tests = 0
    
    for test_name, test_data in results.items():
        if test_name == "api_test":
            continue
            
        logger.info(f"\\n📋 {test_name}")
        logger.info("-" * len(test_name))
        
        multi_method = test_data.get("multi_method", {})
        if multi_method.get("success"):
            logger.info(f"✅ PASSED - Method: {multi_method['method']}")
            logger.info(f"   Characters: {multi_method['character_count']}")
            logger.info(f"   Words: {multi_method['word_count']}")
            successful_tests += 1
        else:
            logger.info(f"❌ FAILED - Error: {multi_method.get('error', 'Unknown error')}")
            
            # Show which individual methods worked
            methods = test_data.get("methods", {})
            for method_name, method_result in methods.items():
                status = "✅" if method_result.get("success") else "❌"
                logger.info(f"   {status} {method_name}: {method_result.get('error', 'Success') if not method_result.get('success') else 'OK'}")
    
    # API Test Summary
    api_result = results.get("api_test", {})
    if api_result.get("api_test"):
        logger.info(f"\\n🌐 API Integration: ✅ PASSED")
    else:
        logger.info(f"\\n🌐 API Integration: ❌ FAILED - {api_result.get('error', 'Unknown')}")
    
    logger.info(f"\\n📊 FINAL SCORE: {successful_tests}/{total_tests} tests passed ({successful_tests/total_tests*100:.1f}%)")
    
    if successful_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - Robust transcription system is working correctly!")
    else:
        logger.warning("⚠️  Some tests failed - Review the implementation")

async def main():
    """Main test runner"""
    start_time = time.time()
    
    logger.info("🚀 Starting YouTube Transcription System Tests")
    logger.info("Testing the robust multi-method approach from TRANSCRIPT_METHOD.md")
    
    try:
        results = await run_comprehensive_tests()
        print_test_summary(results)
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("\\n📄 Detailed results saved to test_results.json")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        raise
    
    finally:
        total_time = time.time() - start_time
        logger.info(f"\\n⏱️  Total test time: {total_time:.1f} seconds")

if __name__ == "__main__":
    asyncio.run(main())