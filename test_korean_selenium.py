#!/usr/bin/env python3
"""
Quick test of Selenium scraper with Korean video
"""

import sys
import logging

# Add the services path
sys.path.append('/Users/jihunkong/teaching_analize/services/transcription')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_korean_selenium():
    """Test the fixed Selenium scraper with Korean video"""
    logger.info("🧪 Testing Korean Video with Selenium (Fixed)")
    
    try:
        from selenium_youtube_scraper import scrape_youtube_transcript
        
        # Korean educational video
        test_video = "https://www.youtube.com/watch?v=-OLCt6WScEY"
        
        logger.info(f"Testing Korean video: {test_video}")
        transcript = scrape_youtube_transcript(test_video, headless=True)
        
        if transcript:
            logger.info(f"✅ Korean Video SUCCESS: Extracted {len(transcript)} characters")
            logger.info(f"📝 Korean Preview: {transcript[:300]}...")
            
            # Save to file for inspection
            with open('/Users/jihunkong/teaching_analize/korean_transcript_selenium.txt', 'w', encoding='utf-8') as f:
                f.write(transcript)
            logger.info("💾 Saved Korean transcript to korean_transcript_selenium.txt")
            return True
        else:
            logger.error("❌ Korean Video FAILED: No transcript extracted")
            return False
            
    except Exception as e:
        logger.error(f"❌ Korean Video ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_korean_selenium()
    print(f"\n🎯 Result: {'SUCCESS' if success else 'FAILED'}")