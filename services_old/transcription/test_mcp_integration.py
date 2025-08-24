#!/usr/bin/env python3
"""
Test MCP YouTube Transcript Integration
Tests the MCP server functionality and integration
"""

import sys
import logging
import asyncio
from mcp_youtube_client import MCPYouTubeClient, MCPYouTubeClientSync

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_health_check():
    """Test MCP server health check"""
    print("🏥 Testing MCP server health check...")
    
    client = MCPYouTubeClientSync()
    
    if client.health_check():
        print("✅ MCP server health check passed")
        return True
    else:
        print("❌ MCP server health check failed")
        return False

def test_transcript_extraction():
    """Test transcript extraction with known working video"""
    print("📝 Testing transcript extraction...")
    
    # Use a well-known video that should have captions
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - famous video
        "https://youtu.be/dQw4w9WgXcQ",  # Same video, different format
    ]
    
    client = MCPYouTubeClientSync()
    
    for url in test_urls:
        print(f"🔄 Testing URL: {url}")
        
        try:
            transcript = client.get_transcript(url, "en")
            
            if transcript:
                print(f"✅ Transcript extracted successfully!")
                print(f"   Length: {len(transcript)} characters")
                print(f"   Preview: {transcript[:150]}...")
                return True
            else:
                print(f"⚠️ No transcript available for {url}")
                
        except Exception as e:
            print(f"❌ Error extracting transcript from {url}: {e}")
    
    print("❌ All transcript extraction tests failed")
    return False

async def test_async_client():
    """Test async client functionality"""
    print("🔄 Testing async client...")
    
    async with MCPYouTubeClient() as client:
        # Health check
        health = await client.health_check()
        if not health:
            print("❌ Async health check failed")
            return False
        
        print("✅ Async health check passed")
        
        # Test transcript
        result = await client.get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "en")
        
        if result:
            print(f"✅ Async transcript extraction successful!")
            print(f"   Video ID: {result['video_id']}")
            print(f"   Language: {result['language']}")
            print(f"   Length: {len(result['transcript'])} characters")
            return True
        else:
            print("❌ Async transcript extraction failed")
            return False

def test_error_handling():
    """Test error handling with invalid URLs"""
    print("⚠️ Testing error handling...")
    
    client = MCPYouTubeClientSync()
    
    # Test with invalid URL
    invalid_urls = [
        "https://www.youtube.com/watch?v=invalid123",  # Invalid video ID
        "https://example.com/not-youtube",  # Not a YouTube URL
        "not-a-url-at-all",  # Invalid URL format
    ]
    
    for url in invalid_urls:
        print(f"🔄 Testing invalid URL: {url}")
        
        try:
            transcript = client.get_transcript(url, "en")
            
            if transcript is None:
                print(f"✅ Correctly handled invalid URL: {url}")
            else:
                print(f"⚠️ Unexpected success with invalid URL: {url}")
                
        except Exception as e:
            print(f"✅ Exception properly caught for {url}: {e}")
    
    return True

def main():
    """Run all tests"""
    print("🧪 MCP YouTube Transcript Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Transcript Extraction", test_transcript_extraction),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"🔬 Running: {test_name}")
        print("=" * 60)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Test async functionality
    print(f"\n{'=' * 60}")
    print("🔬 Running: Async Client Test")
    print("=" * 60)
    
    try:
        async_result = asyncio.run(test_async_client())
        results.append(("Async Client", async_result))
        
        if async_result:
            print("✅ Async Client: PASSED")
        else:
            print("❌ Async Client: FAILED")
            
    except Exception as e:
        print(f"❌ Async Client: ERROR - {e}")
        results.append(("Async Client", False))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP integration is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)