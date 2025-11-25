#!/usr/bin/env python3
"""
Test script specifically for testing the exact DOM selectors from the user
This script focuses on testing the new selectors with enhanced debugging
"""

import asyncio
import logging
import sys
import os

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services_new'))

from transcription.browser_transcriber import BrowserTranscriber

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_exact_selectors(url: str):
    """Test the exact DOM selectors with detailed debugging"""
    
    logger.info(f"🧪 Testing exact DOM selectors with URL: {url}")
    
    try:
        async with BrowserTranscriber() as transcriber:
            # Navigate to the URL
            await transcriber.page.goto(url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)
            
            # Wait for page to load
            page_loaded = await transcriber.wait_for_video_load()
            logger.info(f"Page loaded: {page_loaded}")
            
            # Test specific DOM element detection
            logger.info("🔍 Testing DOM element detection...")
            
            # Test 1: Check for .yt-spec-touch-feedback-shape__fill elements
            touch_feedback_elements = await transcriber.page.query_selector_all('.yt-spec-touch-feedback-shape__fill')
            logger.info(f"Found {len(touch_feedback_elements)} .yt-spec-touch-feedback-shape__fill elements")
            
            # Test 2: Check for transcript segments (should be empty before opening transcript)
            segment_elements = await transcriber.page.query_selector_all('.segment.style-scope.ytd-transcript-segment-renderer')
            logger.info(f"Found {len(segment_elements)} transcript segments (should be 0 before opening)")
            
            # Test 3: Try to find transcript button
            logger.info("🎯 Looking for transcript button...")
            transcript_found = await transcriber.click_transcript_button()
            logger.info(f"Transcript button found and clicked: {transcript_found}")
            
            if transcript_found:
                # Test 4: Now check for transcript segments after opening
                await asyncio.sleep(3)
                segment_elements = await transcriber.page.query_selector_all('.segment.style-scope.ytd-transcript-segment-renderer')
                logger.info(f"Found {len(segment_elements)} transcript segments after opening")
                
                if segment_elements:
                    # Test 5: Check the exact structure of first few segments
                    for i, segment in enumerate(segment_elements[:3]):
                        logger.info(f"📋 Analyzing segment {i+1}:")
                        
                        # Get the full HTML structure
                        html = await segment.innerHTML()
                        logger.info(f"  HTML: {html[:200]}...")
                        
                        # Test timestamp extraction
                        timestamp_elem = await segment.query_selector('.segment-timestamp.style-scope.ytd-transcript-segment-renderer')
                        if timestamp_elem:
                            timestamp_text = await timestamp_elem.inner_text()
                            logger.info(f"  Timestamp: '{timestamp_text}'")
                        else:
                            logger.warning(f"  ❌ No timestamp found in segment {i+1}")
                        
                        # Test text extraction
                        text_elem = await segment.query_selector('yt-formatted-string.segment-text.style-scope.ytd-transcript-segment-renderer')
                        if text_elem:
                            segment_text = await text_elem.inner_text()
                            logger.info(f"  Text: '{segment_text[:100]}...'")
                        else:
                            logger.warning(f"  ❌ No text found in segment {i+1}")
                
                # Test 6: Full transcript extraction
                logger.info("📄 Testing full transcript extraction...")
                transcript_data = await transcriber.extract_transcript_from_dom()
                
                if transcript_data:
                    logger.info(f"✅ Successfully extracted {len(transcript_data)} segments")
                    logger.info(f"Total characters: {sum(len(seg['text']) for seg in transcript_data)}")
                    
                    # Show first few segments
                    for i, seg in enumerate(transcript_data[:3]):
                        logger.info(f"Segment {i+1}: [{seg.get('start', 0):.1f}s] {seg['text'][:100]}...")
                else:
                    logger.error("❌ Failed to extract transcript data")
            
            # Take final screenshot for debugging
            await transcriber.page.screenshot(path="/tmp/final_test_screenshot.png")
            logger.info("📸 Final screenshot saved: /tmp/final_test_screenshot.png")
            
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        test_url = sys.argv[1]
        print(f"🧪 Testing DOM Selectors")
        print(f"URL: {test_url}")
        print("=" * 60)
        
        asyncio.run(test_exact_selectors(test_url))
    else:
        print("Usage: python test_dom_selectors.py <youtube_url>")
        print("This script tests the exact DOM selectors provided by the user")
        print("Example: python test_dom_selectors.py https://www.youtube.com/watch?v=VIDEO_ID")