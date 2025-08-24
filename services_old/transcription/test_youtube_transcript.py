#!/usr/bin/env python3
"""
Test script for YouTube Transcript API functionality
"""

import sys
import logging
from youtube_handler import YouTubeHandler

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_youtube_transcript():
    """Test YouTube transcript extraction with a known video"""
    
    # Initialize handler
    handler = YouTubeHandler()
    
    # Test with a popular YouTube video that should have captions
    # Using a TED talk or educational video that typically has captions
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Famous Rick Roll video
        "https://youtu.be/dQw4w9WgXcQ",  # Same video, different format
        "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",  # TED talk example
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print(f"{'='*60}")
        
        try:
            # Test video ID extraction
            video_id = handler._extract_video_id(url)
            print(f"✓ Video ID extracted: {video_id}")
            
            # Test transcript extraction
            print("Attempting to extract transcript...")
            transcript = handler.get_transcript_via_api(url, "en")
            
            if transcript:
                print(f"✓ Transcript extracted successfully!")
                print(f"✓ Length: {len(transcript)} characters")
                print(f"✓ Preview: {transcript[:200]}...")
                
                # Test Korean transcript if available
                print("\nTrying Korean transcript...")
                ko_transcript = handler.get_transcript_via_api(url, "ko")
                if ko_transcript:
                    print(f"✓ Korean transcript also available!")
                    print(f"✓ Length: {len(ko_transcript)} characters")
                    print(f"✓ Preview: {ko_transcript[:200]}...")
                else:
                    print("⚠ Korean transcript not available")
                    
                return True  # Success - we found at least one working transcript
                
            else:
                print("✗ No transcript available for this video")
                
        except Exception as e:
            print(f"✗ Error testing {url}: {str(e)}")
    
    return False

def test_full_caption_extraction():
    """Test the full get_captions method"""
    handler = YouTubeHandler()
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"\n{'='*60}")
    print(f"Testing full caption extraction")
    print(f"{'='*60}")
    
    try:
        captions = handler.get_captions(test_url, "en")
        
        if captions:
            print(f"✓ Captions extracted successfully!")
            print(f"✓ Length: {len(captions)} characters")
            print(f"✓ Preview: {captions[:300]}...")
            return True
        else:
            print("✗ No captions extracted")
            return False
            
    except Exception as e:
        print(f"✗ Error in full caption extraction: {str(e)}")
        return False

if __name__ == "__main__":
    print("YouTube Transcript API Test")
    print("=" * 60)
    
    # Test transcript API
    transcript_success = test_youtube_transcript()
    
    # Test full caption method
    caption_success = test_full_caption_extraction()
    
    print(f"\n{'='*60}")
    print("TEST RESULTS")
    print(f"{'='*60}")
    print(f"Transcript API: {'✓ PASS' if transcript_success else '✗ FAIL'}")
    print(f"Full Captions:  {'✓ PASS' if caption_success else '✗ FAIL'}")
    
    if transcript_success or caption_success:
        print("\n🎉 YouTube Transcript functionality is working!")
        sys.exit(0)
    else:
        print("\n❌ YouTube Transcript functionality failed")
        sys.exit(1)