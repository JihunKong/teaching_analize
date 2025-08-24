#!/usr/bin/env python3
"""
Test script to verify the transcript extraction fix
Tests both Selenium and Playwright approaches with YouTube videos that have auto-generated transcripts
"""

import asyncio
import logging
import sys
import os

# Add the services path
sys.path.append('/Users/jihunkong/teaching_analize/services/transcription')
sys.path.append('/Users/jihunkong/teaching_analize/services_new/transcription')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_selenium_scraper():
    """Test the fixed Selenium scraper"""
    logger.info("🧪 Testing Selenium YouTube Scraper (Fixed)")
    
    try:
        from selenium_youtube_scraper import scrape_youtube_transcript
        
        # Test with a known YouTube video that has auto-generated transcripts
        test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - has transcripts
        
        logger.info(f"Testing with video: {test_video}")
        transcript = scrape_youtube_transcript(test_video, headless=True)
        
        if transcript:
            logger.info(f"✅ Selenium SUCCESS: Extracted {len(transcript)} characters")
            logger.info(f"📝 Preview: {transcript[:200]}...")
            return True
        else:
            logger.error("❌ Selenium FAILED: No transcript extracted")
            return False
            
    except Exception as e:
        logger.error(f"❌ Selenium ERROR: {e}")
        return False

async def test_playwright_scraper():
    """Test the fixed Playwright scraper"""
    logger.info("🧪 Testing Playwright YouTube Scraper (Fixed)")
    
    try:
        from browser_transcriber import transcribe_with_browser
        
        # Test with a known YouTube video that has auto-generated transcripts
        test_video = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - has transcripts
        
        logger.info(f"Testing with video: {test_video}")
        result = await transcribe_with_browser(test_video, language="en")
        
        if result.get("success"):
            transcript = result.get("transcript", "")
            logger.info(f"✅ Playwright SUCCESS: Extracted {len(transcript)} characters")
            logger.info(f"📝 Preview: {transcript[:200]}...")
            logger.info(f"🔧 Method used: {result.get('method_used')}")
            return True
        else:
            logger.error(f"❌ Playwright FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Playwright ERROR: {e}")
        return False

async def test_korean_video():
    """Test with a Korean YouTube video"""
    logger.info("🧪 Testing with Korean YouTube video")
    
    try:
        from browser_transcriber import transcribe_with_browser
        
        # Korean educational video that should have auto-generated transcripts
        test_video = "https://www.youtube.com/watch?v=-OLCt6WScEY"  # From the original request
        
        logger.info(f"Testing Korean video: {test_video}")
        result = await transcribe_with_browser(test_video, language="ko")
        
        if result.get("success"):
            transcript = result.get("transcript", "")
            logger.info(f"✅ Korean Video SUCCESS: Extracted {len(transcript)} characters")
            logger.info(f"📝 Korean Preview: {transcript[:200]}...")
            logger.info(f"🔧 Method used: {result.get('method_used')}")
            return True
        else:
            logger.error(f"❌ Korean Video FAILED: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Korean Video ERROR: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting YouTube Transcript Extraction Tests (CC vs Transcript Fix)")
    logger.info("=" * 80)
    
    results = []
    
    # Test 1: Selenium scraper
    logger.info("\n" + "="*50)
    logger.info("TEST 1: Selenium Scraper (Fixed)")
    logger.info("="*50)
    selenium_result = test_selenium_scraper()
    results.append(("Selenium", selenium_result))
    
    # Test 2: Playwright scraper
    logger.info("\n" + "="*50)
    logger.info("TEST 2: Playwright Scraper (Fixed)")
    logger.info("="*50)
    playwright_result = await test_playwright_scraper()
    results.append(("Playwright", playwright_result))
    
    # Test 3: Korean video
    logger.info("\n" + "="*50)
    logger.info("TEST 3: Korean Video Test")
    logger.info("="*50)
    korean_result = await test_korean_video()
    results.append(("Korean Video", korean_result))
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("="*80)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if success:
            success_count += 1
    
    logger.info(f"\n🎯 Overall Success Rate: {success_count}/{len(results)} tests passed")
    
    if success_count == len(results):
        logger.info("🎉 ALL TESTS PASSED! The transcript fix is working correctly.")
        logger.info("💡 Key Fix: Now looking for TRANSCRIPT buttons (스크립트), not CC/captions (자막)")
    elif success_count > 0:
        logger.info("⚠️  PARTIAL SUCCESS. Some methods are working.")
    else:
        logger.error("💥 ALL TESTS FAILED. Need to investigate further.")
    
    return success_count == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)