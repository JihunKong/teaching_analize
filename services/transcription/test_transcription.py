#!/usr/bin/env python3
"""
Test script for Selenium-based YouTube transcription system
IMPORTANT: This project uses ONLY Selenium browser automation for transcription.
NO API methods (youtube-transcript-api, whisper-api) are allowed.
"""

import asyncio
import json
import logging
import time
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test cases for Selenium browser automation
TEST_CASES = [
    {
        "name": "Standard Korean educational video",
        "url": "https://www.youtube.com/watch?v=-OLCt6WScEY",
        "expected_method": "selenium_browser",
        "description": "Korean classroom video - should extract via Selenium"
    },
    {
        "name": "Video with list parameter",
        "url": "https://www.youtube.com/watch?v=-OLCt6WScEY&list=PLugIxwJYmOhl_8KO3GHx9gp6VKMmbsTfw",
        "expected_method": "selenium_browser",
        "description": "Test URL parsing with playlist parameter"
    },
    {
        "name": "Short URL format",
        "url": "https://youtu.be/-OLCt6WScEY",
        "expected_method": "selenium_browser",
        "description": "Test URL parsing for youtu.be format"
    }
]

async def test_selenium_browser_automation(video_url: str) -> Dict[str, Any]:
    """Test Selenium Browser Automation Method (ONLY ALLOWED METHOD)"""
    try:
        from selenium_youtube_scraper import get_transcript_with_browser_scraping

        logger.info(f"[Selenium] Testing Browser Automation with {video_url}")
        start_time = time.time()

        result = await get_transcript_with_browser_scraping(video_url, language="ko")
        processing_time = time.time() - start_time

        if result["success"]:
            transcript_text = result["transcript"]
            return {
                "success": True,
                "method": "selenium_browser",
                "character_count": len(transcript_text),
                "word_count": len(transcript_text.split()),
                "sample_text": transcript_text[:100] + "..." if len(transcript_text) > 100 else transcript_text,
                "processing_time": processing_time,
                "metadata": result.get("metadata", {})
            }
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}

    except Exception as e:
        return {"success": False, "error": str(e)}

async def test_api_health():
    """Test API health endpoint (no transcription API calls)"""
    import requests

    logger.info("Testing API health check...")

    base_url = "http://localhost:8000"

    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        logger.info(f"Health check: {health_response.status_code}")

        if health_response.status_code == 200:
            return {"api_health": True, "status_code": 200}
        else:
            return {"api_health": False, "status_code": health_response.status_code}

    except Exception as e:
        return {"api_health": False, "error": str(e)}

async def run_comprehensive_tests():
    """Run comprehensive tests on Selenium browser automation"""
    logger.info("Starting Selenium-only transcription tests...")
    logger.info("ARCHITECTURE: This project uses ONLY Selenium browser automation")
    logger.info("NO API calls (youtube-transcript-api, whisper-api) are permitted")

    results = {}

    for test_case in TEST_CASES:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {test_case['name']}")
        logger.info(f"URL: {test_case['url']}")
        logger.info(f"Description: {test_case['description']}")
        logger.info(f"{'='*60}")

        case_results = {
            "test_case": test_case,
            "selenium_result": {}
        }

        # Test Selenium Browser Automation (ONLY METHOD)
        logger.info("\n--- Testing Selenium Browser Automation ---")
        selenium_result = await test_selenium_browser_automation(test_case["url"])
        case_results["selenium_result"] = selenium_result

        if selenium_result["success"]:
            logger.info(f"✅ Selenium SUCCESS: {selenium_result['character_count']} chars in {selenium_result.get('processing_time', 0):.1f}s")
            logger.info(f"Sample: {selenium_result.get('sample_text', 'N/A')}")
            logger.info(f"Metadata: {selenium_result.get('metadata', {})}")
        else:
            logger.error(f"❌ Selenium FAILED: {selenium_result['error']}")

        results[test_case["name"]] = case_results

        # Wait between tests to avoid rate limiting
        await asyncio.sleep(2)

    # Test API health check
    logger.info("\n" + "="*60)
    logger.info("Testing API Health")
    logger.info("="*60)

    api_health = await test_api_health()
    results["api_health"] = api_health

    if api_health.get("api_health"):
        logger.info("🌐 API HEALTH CHECK: ✅ PASSED")
    else:
        logger.warning(f"🌐 API HEALTH CHECK: ❌ FAILED - {api_health.get('error', 'Unknown error')}")

    return results

def print_test_summary(results: Dict[str, Any]):
    """Print a comprehensive test summary"""
    logger.info("\n" + "="*80)
    logger.info("SELENIUM TRANSCRIPTION TEST SUMMARY")
    logger.info("="*80)

    total_tests = len([k for k in results.keys() if k != "api_health"])
    successful_tests = 0

    for test_name, test_data in results.items():
        if test_name == "api_health":
            continue

        logger.info(f"\n📋 {test_name}")
        logger.info("-" * len(test_name))

        selenium_result = test_data.get("selenium_result", {})
        if selenium_result.get("success"):
            logger.info(f"✅ PASSED - Method: selenium_browser")
            logger.info(f"   Characters: {selenium_result['character_count']}")
            logger.info(f"   Words: {selenium_result['word_count']}")
            logger.info(f"   Time: {selenium_result.get('processing_time', 0):.1f}s")
            successful_tests += 1
        else:
            logger.info(f"❌ FAILED - Error: {selenium_result.get('error', 'Unknown error')}")

    # API Health Summary
    api_health = results.get("api_health", {})
    if api_health.get("api_health"):
        logger.info(f"\n🌐 API Health: ✅ PASSED")
    else:
        logger.info(f"\n🌐 API Health: ❌ FAILED - {api_health.get('error', 'Unknown')}")

    logger.info(f"\n📊 FINAL SCORE: {successful_tests}/{total_tests} tests passed ({successful_tests/total_tests*100:.1f}%)")

    if successful_tests == total_tests:
        logger.info("🎉 ALL TESTS PASSED - Selenium browser automation is working correctly!")
    else:
        logger.warning("⚠️  Some tests failed - Review the Selenium implementation")

async def main():
    """Main test runner"""
    start_time = time.time()

    logger.info("🚀 Starting Selenium-Only Transcription System Tests")
    logger.info("Architecture: Selenium browser automation ONLY (NO APIs)")

    try:
        results = await run_comprehensive_tests()
        print_test_summary(results)

        # Save detailed results
        with open("test_results_selenium.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("\n📄 Detailed results saved to test_results_selenium.json")

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        raise

    finally:
        total_time = time.time() - start_time
        logger.info(f"\n⏱️  Total test time: {total_time:.1f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
