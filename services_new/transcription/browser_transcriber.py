#!/usr/bin/env python3
"""
Browser-based transcription module for YouTube videos with disabled transcripts
This implements the proven browser automation method from TRANSCRIPT_METHOD.md
"""

import asyncio
import logging
import time
import json
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

class BrowserTranscriber:
    """
    Browser-based transcription using Playwright for videos with disabled transcripts
    This is the fallback method that proved successful for handling difficult cases
    """
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        
    async def __aenter__(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Install with: pip install playwright")
        
        self.playwright = await async_playwright().start()
        
        # Launch browser with optimized settings for headless environment
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create context with user agent to avoid detection
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = await self.context.new_page()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def extract_video_id(self, youtube_url: str) -> str:
        """Extract video ID from YouTube URL"""
        parsed_url = urlparse(youtube_url)
        
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        elif parsed_url.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com'):
            if 'watch' in parsed_url.path:
                # Extract v parameter
                query_params = parsed_url.query.split('&')
                for param in query_params:
                    if param.startswith('v='):
                        return param.split('=')[1]
            elif '/embed/' in parsed_url.path:
                return parsed_url.path.split('/embed/')[1].split('?')[0]
            elif '/v/' in parsed_url.path:
                return parsed_url.path.split('/v/')[1].split('?')[0]
        
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
    
    async def wait_for_video_load(self) -> bool:
        """Wait for YouTube video to fully load"""
        try:
            # Wait for the video player to be present
            await self.page.wait_for_selector('video', timeout=30000)
            
            # Wait a bit more for everything to initialize
            await asyncio.sleep(3)
            
            # Check if video is actually loaded
            video_element = await self.page.query_selector('video')
            if video_element:
                duration = await video_element.get_attribute('duration')
                if duration and float(duration) > 0:
                    logger.info("Video loaded successfully")
                    return True
            
            return False
            
        except PlaywrightTimeoutError:
            logger.error("Timeout waiting for video to load")
            return False
    
    async def extract_transcript_from_dom(self) -> Optional[List[Dict[str, Any]]]:
        """
        Extract transcript segments directly from YouTube DOM structure:
        .segment.ytd-transcript-segment-renderer containing .segment-timestamp and yt-formatted-string.segment-text
        """
        try:
            logger.info("Starting direct DOM scraping for transcript segments")
            
            # Wait for the page to fully load and try to find transcript segments
            await asyncio.sleep(5)
            
            # Look for transcript segments directly in the DOM
            segment_selector = '.segment.ytd-transcript-segment-renderer'
            
            # Wait for transcript segments to be available
            try:
                await self.page.wait_for_selector(segment_selector, timeout=15000)
            except PlaywrightTimeoutError:
                logger.warning("No transcript segments found with direct selector, trying alternative approaches")
                
                # Try to click transcript/captions button if available
                transcript_buttons = [
                    '[data-testid="transcript-button"]',
                    'button[aria-label*="transcript" i]',
                    'button[aria-label*="자막" i]',
                    'yt-button-view-model[aria-label*="transcript" i]',
                    '[title*="transcript" i]',
                    '[title*="자막" i]'
                ]
                
                button_found = False
                for button_selector in transcript_buttons:
                    try:
                        button = await self.page.query_selector(button_selector)
                        if button:
                            logger.info(f"Found transcript button with selector: {button_selector}")
                            await button.click()
                            await asyncio.sleep(3)
                            button_found = True
                            break
                    except Exception as e:
                        logger.debug(f"Failed to click button {button_selector}: {e}")
                        continue
                
                if button_found:
                    # Wait for segments to appear after clicking
                    try:
                        await self.page.wait_for_selector(segment_selector, timeout=10000)
                    except PlaywrightTimeoutError:
                        logger.error("Transcript segments did not appear after clicking button")
                        return None
                else:
                    logger.error("No transcript button found, segments may not be available")
                    return None
            
            # Extract all transcript segments
            segments = await self.page.query_selector_all(segment_selector)
            
            if not segments:
                logger.warning("No transcript segments found in DOM")
                return None
            
            logger.info(f"Found {len(segments)} transcript segments")
            
            transcript_data = []
            for segment in segments:
                try:
                    # Extract timestamp from .segment-timestamp
                    timestamp_element = await segment.query_selector('.segment-timestamp')
                    timestamp_text = ""
                    if timestamp_element:
                        timestamp_text = await timestamp_element.inner_text()
                    
                    # Extract text from yt-formatted-string.segment-text
                    text_element = await segment.query_selector('yt-formatted-string.segment-text')
                    segment_text = ""
                    if text_element:
                        segment_text = await text_element.inner_text()
                    
                    # Only add if we have both timestamp and text
                    if timestamp_text and segment_text:
                        start_seconds = self.parse_timestamp(timestamp_text.strip())
                        if start_seconds is not None:
                            transcript_data.append({
                                'text': segment_text.strip(),
                                'start': start_seconds,
                                'duration': 3.0  # Default duration
                            })
                            logger.debug(f"Added segment: {timestamp_text} -> {segment_text[:50]}...")
                
                except Exception as e:
                    logger.debug(f"Error parsing segment: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(transcript_data)} transcript segments")
            return transcript_data if transcript_data else None
            
        except Exception as e:
            logger.error(f"Error extracting transcript from DOM: {e}")
            return None
    
    def parse_timestamp(self, timestamp_str: str) -> Optional[float]:
        """Parse timestamp string to seconds"""
        try:
            # Handle formats like "0:00", "1:23", "1:23:45"
            parts = timestamp_str.strip().split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                return None
        except ValueError:
            return None
    
    async def get_video_metadata(self) -> Dict[str, Any]:
        """Extract video metadata from YouTube page"""
        try:
            metadata = {}
            
            # Get video title
            title_selectors = ['h1.ytd-video-primary-info-renderer', 'h1 .ytd-video-primary-info-renderer', 'meta[name="title"]']
            for selector in title_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        if selector.startswith('meta'):
                            metadata['title'] = await element.get_attribute('content')
                        else:
                            metadata['title'] = await element.inner_text()
                        break
                except:
                    continue
            
            # Get video duration
            try:
                video_element = await self.page.query_selector('video')
                if video_element:
                    duration = await video_element.get_attribute('duration')
                    if duration:
                        metadata['duration'] = float(duration)
            except:
                pass
            
            # Get channel name
            channel_selectors = ['#channel-name a', '.ytd-video-owner-renderer a']
            for selector in channel_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        metadata['channel'] = await element.inner_text()
                        break
                except:
                    continue
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            return {}
    
    async def transcribe_youtube_video(self, youtube_url: str, language: str = "ko") -> Dict[str, Any]:
        """
        Main method to transcribe YouTube video using browser automation
        This is the proven fallback method for videos with disabled transcripts
        """
        start_time = time.time()
        
        try:
            video_id = self.extract_video_id(youtube_url)
            logger.info(f"Starting browser transcription for video: {video_id}")
            
            # Navigate to YouTube video
            await self.page.goto(youtube_url, wait_until='networkidle', timeout=30000)
            
            # Wait for video to load
            if not await self.wait_for_video_load():
                return {
                    "success": False,
                    "error": "Failed to load video in browser",
                    "video_id": video_id
                }
            
            # Get video metadata
            metadata = await self.get_video_metadata()
            
            # Try to extract transcript from DOM
            transcript_data = await self.extract_transcript_from_dom()
            
            if not transcript_data:
                return {
                    "success": False,
                    "error": "Could not extract transcript using browser automation",
                    "video_id": video_id,
                    "metadata": metadata
                }
            
            # Format transcript text
            full_text = " ".join([entry['text'] for entry in transcript_data])
            
            processing_time = time.time() - start_time
            
            result = {
                "success": True,
                "video_url": youtube_url,
                "video_id": video_id,
                "transcript": full_text,
                "language": language,
                "character_count": len(full_text),
                "word_count": len(full_text.split()),
                "method_used": "browser_scraping",
                "timestamp": time.time(),
                "processing_time": processing_time,
                "segments": transcript_data,
                "metadata": metadata
            }
            
            logger.info(f"Successfully transcribed {len(full_text)} characters using browser automation in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Browser transcription failed after {processing_time:.2f}s: {str(e)}")
            return {
                "success": False,
                "error": f"Browser transcription failed: {str(e)}",
                "video_id": self.extract_video_id(youtube_url) if youtube_url else "unknown",
                "processing_time": processing_time
            }

# Convenience function for direct usage
async def transcribe_with_browser(youtube_url: str, language: str = "ko") -> Dict[str, Any]:
    """
    Convenience function to transcribe a YouTube video using browser automation
    This implements the proven method from TRANSCRIPT_METHOD.md
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "success": False,
            "error": "Playwright not available. Install with: pip install playwright && playwright install chromium"
        }
    
    async with BrowserTranscriber() as transcriber:
        return await transcriber.transcribe_youtube_video(youtube_url, language)