#!/usr/bin/env python3
"""
Test script for the updated browser transcriber with exact DOM selectors
"""

import asyncio
import logging
import sys
import os

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services_new'))

from transcription.browser_transcriber import BrowserTranscriber

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_browser_transcriber():
    """Test the browser transcriber with a real YouTube video"""
    
    # Test with a sample YouTube video (replace with the URL you want to test)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your test URL
    
    logger.info(f"Testing browser transcriber with URL: {test_url}")
    
    try:
        async with BrowserTranscriber() as transcriber:
            result = await transcriber.transcribe_youtube_video(test_url, "ko")
            
            if result["success"]:
                logger.info("✅ Transcription successful!")
                logger.info(f"Video ID: {result['video_id']}")
                logger.info(f"Character count: {result['character_count']}")
                logger.info(f"Word count: {result['word_count']}")
                logger.info(f"Method used: {result['method_used']}")
                logger.info(f"Processing time: {result['processing_time']:.2f}s")
                logger.info(f"Number of segments: {len(result.get('segments', []))}")
                
                # Show first few segments
                if result.get('segments'):
                    logger.info("First 3 segments:")
                    for i, segment in enumerate(result['segments'][:3]):
                        logger.info(f"  {i+1}. [{segment.get('start', 0):.1f}s] {segment['text'][:100]}...")
                
                # Show beginning of transcript
                transcript = result['transcript']
                logger.info(f"Transcript preview: {transcript[:200]}...")
            else:
                logger.error("❌ Transcription failed!")
                logger.error(f"Error: {result.get('error')}")
                
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Browser Transcriber Test")
    print("=" * 50)
    
    # Check if a URL is provided as command line argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        test_url = sys.argv[1]
        print(f"Using provided URL: {test_url}")
        
        async def test_with_url():
            try:
                async with BrowserTranscriber() as transcriber:
                    result = await transcriber.transcribe_youtube_video(test_url, "ko")
                    
                    if result["success"]:
                        print("✅ SUCCESS!")
                        print(f"Characters: {result['character_count']}")
                        print(f"Segments: {len(result.get('segments', []))}")
                        print(f"Time: {result['processing_time']:.2f}s")
                        print(f"Preview: {result['transcript'][:200]}...")
                    else:
                        print("❌ FAILED!")
                        print(f"Error: {result.get('error')}")
            except Exception as e:
                print(f"❌ EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
        
        asyncio.run(test_with_url())
    else:
        print("Usage: python test_browser_transcriber.py <youtube_url>")
        print("Example: python test_browser_transcriber.py https://www.youtube.com/watch?v=VIDEO_ID")