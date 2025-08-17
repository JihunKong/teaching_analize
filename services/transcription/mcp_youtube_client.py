#!/usr/bin/env python3
"""
MCP YouTube Transcript Client
Interfaces with the MCP YouTube Transcript server for reliable caption extraction
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
import time

logger = logging.getLogger(__name__)

class MCPYouTubeClient:
    """Client for MCP YouTube Transcript server"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:8888"):
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=60)  # 60 second timeout
        
        # Rate limiting
        self.last_request_time = 0
        self.min_interval = 2.0  # Minimum 2 seconds between requests
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        parsed = urlparse(url)
        
        if parsed.hostname in ['www.youtube.com', 'youtube.com']:
            if parsed.path == '/watch':
                return parse_qs(parsed.query).get('v', [None])[0]
        elif parsed.hostname in ['youtu.be']:
            return parsed.path[1:]  # Remove leading slash
            
        return None
    
    async def _rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
                
            async with self.session.get(f"{self.mcp_server_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"MCP server health check failed: {e}")
            return False
    
    async def get_transcript(self, video_url: str, language: str = "en", 
                           next_cursor: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get transcript from YouTube video via MCP server
        
        Args:
            video_url: YouTube video URL
            language: Language code for transcript (default: "en")
            next_cursor: Cursor for pagination (for long videos)
            
        Returns:
            Dict with transcript data or None if failed
            Format: {
                "transcript": "full text",
                "segments": [{"start": 0.0, "duration": 2.5, "text": "..."}],
                "next_cursor": "cursor_for_next_page",
                "language": "en",
                "video_id": "abc123"
            }
        """
        await self._rate_limit()
        
        video_id = self._extract_video_id(video_url)
        if not video_id:
            logger.error(f"Could not extract video ID from URL: {video_url}")
            return None
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)
            
            # Prepare MCP request
            payload = {
                "method": "get_transcript",
                "params": {
                    "video_id": video_id,
                    "language": language
                }
            }
            
            if next_cursor:
                payload["params"]["next_cursor"] = next_cursor
            
            logger.info(f"Requesting transcript for video {video_id} (language: {language})")
            
            async with self.session.post(
                f"{self.mcp_server_url}/mcp",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"MCP server error {response.status}: {error_text}")
                    return None
                
                result = await response.json()
                
                if "error" in result:
                    logger.error(f"MCP server returned error: {result['error']}")
                    return None
                
                transcript_data = result.get("result", {})
                
                # Validate response structure
                if not transcript_data.get("transcript"):
                    logger.warning(f"No transcript data returned for video {video_id}")
                    return None
                
                logger.info(f"Successfully retrieved transcript for {video_id}: "
                          f"{len(transcript_data['transcript'])} characters")
                
                return {
                    "transcript": transcript_data["transcript"],
                    "segments": transcript_data.get("segments", []),
                    "next_cursor": transcript_data.get("next_cursor"),
                    "language": transcript_data.get("language", language),
                    "video_id": video_id,
                    "source": "mcp_server"
                }
                
        except asyncio.TimeoutError:
            logger.error(f"Timeout getting transcript for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {e}")
            return None
    
    async def get_full_transcript(self, video_url: str, language: str = "en") -> Optional[str]:
        """
        Get complete transcript, handling pagination for long videos
        
        Args:
            video_url: YouTube video URL
            language: Language code for transcript
            
        Returns:
            Complete transcript text or None if failed
        """
        full_transcript = []
        next_cursor = None
        max_pages = 10  # Safety limit to prevent infinite loops
        page_count = 0
        
        while page_count < max_pages:
            result = await self.get_transcript(video_url, language, next_cursor)
            
            if not result:
                if page_count == 0:
                    # Failed on first page
                    return None
                else:
                    # Partial success - return what we have
                    break
            
            full_transcript.append(result["transcript"])
            
            next_cursor = result.get("next_cursor")
            if not next_cursor:
                # No more pages
                break
                
            page_count += 1
            logger.info(f"Retrieved page {page_count + 1} of transcript")
        
        if not full_transcript:
            return None
        
        return " ".join(full_transcript)

class MCPYouTubeClientSync:
    """Synchronous wrapper for MCPYouTubeClient"""
    
    def __init__(self, mcp_server_url: str = "http://localhost:8888"):
        self.mcp_server_url = mcp_server_url
    
    def get_transcript(self, video_url: str, language: str = "en") -> Optional[str]:
        """
        Synchronous method to get transcript
        
        Args:
            video_url: YouTube video URL  
            language: Language code for transcript
            
        Returns:
            Complete transcript text or None if failed
        """
        async def _async_get():
            async with MCPYouTubeClient(self.mcp_server_url) as client:
                return await client.get_full_transcript(video_url, language)
        
        try:
            # Create new event loop or use existing one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, create a new loop in a thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, _async_get())
                        return future.result(timeout=120)  # 2 minute timeout
                else:
                    return loop.run_until_complete(_async_get())
            except RuntimeError:
                # No event loop, create new one
                return asyncio.run(_async_get())
                
        except Exception as e:
            logger.error(f"Error in synchronous transcript request: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        async def _async_health():
            async with MCPYouTubeClient(self.mcp_server_url) as client:
                return await client.health_check()
        
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    # We're already in an event loop, return False as MCP server isn't available
                    logger.info("Already in event loop, skipping MCP health check")
                    return False
            except RuntimeError:
                # No running loop, safe to use asyncio.run()
                pass
            
            return asyncio.run(_async_health())
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False

# Convenience function for simple usage
def get_youtube_transcript(video_url: str, language: str = "en", 
                          mcp_server_url: str = "http://localhost:8888") -> Optional[str]:
    """
    Simple function to get YouTube transcript via MCP server
    
    Args:
        video_url: YouTube video URL
        language: Language code (default: "en")
        mcp_server_url: MCP server URL
        
    Returns:
        Transcript text or None if failed
    """
    client = MCPYouTubeClientSync(mcp_server_url)
    return client.get_transcript(video_url, language)

if __name__ == "__main__":
    # Test the client
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mcp_youtube_client.py <youtube_url> [language]")
        sys.exit(1)
    
    url = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "en"
    
    print(f"Testing MCP client with URL: {url}")
    
    client = MCPYouTubeClientSync()
    
    # Health check
    if not client.health_check():
        print("❌ MCP server is not healthy")
        sys.exit(1)
    
    print("✅ MCP server is healthy")
    
    # Get transcript
    transcript = client.get_transcript(url, language)
    
    if transcript:
        print(f"✅ Transcript retrieved: {len(transcript)} characters")
        print(f"Preview: {transcript[:200]}...")
    else:
        print("❌ Failed to retrieve transcript")