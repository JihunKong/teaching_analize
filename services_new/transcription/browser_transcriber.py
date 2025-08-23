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
    
    async def click_transcript_button(self) -> bool:
        """
        Click the YouTube transcript button to open the transcript panel.
        This implements the method requested by the user: opening YouTube video page 
        and clicking the "스크립트" (Script/Transcript) button.
        """
        try:
            logger.info("Looking for YouTube transcript button (스크립트 button)")
            
            # Wait for page to load completely
            await asyncio.sleep(3)
            
            # Try different selectors for the transcript button
            # These are based on current YouTube DOM structure (2024-2025)
            transcript_button_selectors = [
                # Modern YouTube transcript buttons
                'button[aria-label*="transcript" i]',
                'button[aria-label*="Show transcript" i]',
                'button[aria-label*="스크립트" i]',
                'button[aria-label*="자막" i]',
                'button[title*="transcript" i]',
                'button[title*="Show transcript" i]',
                'button[title*="스크립트" i]',
                'button[title*="자막" i]',
                
                # Menu-based transcript access ("..." more button)
                '[aria-label*="더 보기" i]',
                '[aria-label*="More actions" i]',
                'button[aria-label="더보기"]',
                'button[aria-label="More actions"]',
                'yt-button-renderer[aria-label*="더 보기" i]',
                'yt-button-renderer[aria-label*="More actions" i]',
                
                # Direct transcript panel toggles
                '[data-testid="transcript-button"]',
                'ytd-transcript-renderer',
                '.ytd-engagement-panel-title-header-renderer button',
                
                # Alternative selectors
                'yt-button-view-model[aria-label*="transcript" i]',
                'yt-button-view-model[aria-label*="스크립트" i]',
            ]
            
            # First try direct transcript buttons
            for selector in transcript_button_selectors:
                try:
                    # Look for the button
                    button = await self.page.query_selector(selector)
                    if button:
                        # Check if button is visible and clickable
                        is_visible = await button.is_visible()
                        if is_visible:
                            logger.info(f"Found transcript button with selector: {selector}")
                            await button.click()
                            await asyncio.sleep(2)
                            
                            # If this was a "More" button, look for transcript option in menu
                            if "더 보기" in selector or "More actions" in selector:
                                await self._click_transcript_in_menu()
                            
                            return True
                        
                except Exception as e:
                    logger.debug(f"Failed to click button {selector}: {e}")
                    continue
            
            # If no direct button found, try clicking three-dot menu and looking for transcript
            logger.info("No direct transcript button found, trying menu approach")
            return await self._try_menu_approach()
            
        except Exception as e:
            logger.error(f"Error clicking transcript button: {e}")
            return False
    
    async def _click_transcript_in_menu(self) -> bool:
        """Click transcript option from opened menu"""
        try:
            # Wait for menu to open
            await asyncio.sleep(1)
            
            # Look for transcript menu items
            menu_selectors = [
                'yt-formatted-string:has-text("Show transcript")',
                'yt-formatted-string:has-text("스크립트")',
                'yt-formatted-string:has-text("자막")',
                '[role="menuitem"]:has-text("transcript")',
                '[role="menuitem"]:has-text("스크립트")',
                '[role="menuitem"]:has-text("자막")',
                'tp-yt-paper-item:has-text("transcript")',
                'tp-yt-paper-item:has-text("스크립트")',
            ]
            
            for selector in menu_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        logger.info(f"Found transcript menu item: {selector}")
                        await element.click()
                        await asyncio.sleep(2)
                        return True
                except Exception as e:
                    logger.debug(f"Failed to click menu item {selector}: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Error clicking transcript in menu: {e}")
            return False
    
    async def _try_menu_approach(self) -> bool:
        """Try to access transcript through three-dot menu"""
        try:
            # Look for three-dot menu buttons
            more_buttons = [
                '#top-level-buttons-computed #button[aria-label*="더 보기"]',
                '#top-level-buttons-computed #button[aria-label*="More actions"]',
                'ytd-menu-renderer yt-icon-button[aria-label*="더 보기"]',
                'ytd-menu-renderer yt-icon-button[aria-label*="More actions"]',
                'button[aria-label="더보기"]',
                'button[aria-label="More actions"]',
            ]
            
            for selector in more_buttons:
                try:
                    button = await self.page.query_selector(selector)
                    if button and await button.is_visible():
                        logger.info(f"Found more actions button: {selector}")
                        await button.click()
                        await asyncio.sleep(2)
                        
                        # Now look for transcript in the menu
                        if await self._click_transcript_in_menu():
                            return True
                        
                        # If not found, close menu and try next button
                        await self.page.keyboard.press('Escape')
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.debug(f"Failed to click more button {selector}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error in menu approach: {e}")
            return False
    
    async def extract_transcript_from_dom(self) -> Optional[List[Dict[str, Any]]]:
        """
        Extract transcript segments directly from YouTube DOM structure.
        This implements the user's requested method: clicking "스크립트" button and copying all transcript messages.
        """
        try:
            logger.info("Starting transcript extraction by clicking 스크립트 (Script) button")
            
            # Step 1: Click the transcript button to open the transcript panel
            if not await self.click_transcript_button():
                logger.error("Failed to click transcript button")
                return None
            
            # Step 2: Wait for transcript panel to load
            logger.info("Waiting for transcript panel to load...")
            await asyncio.sleep(3)
            
            # Step 3: Look for transcript segments in various possible DOM structures
            segment_selectors = [
                # Modern YouTube transcript segment selectors (2024-2025)
                '.segment.ytd-transcript-segment-renderer',
                'ytd-transcript-segment-renderer .segment',
                '.ytd-transcript-segment-list-renderer .segment',
                
                # Alternative segment selectors
                '.transcript-segment',
                '.cue-group',
                '[data-testid="transcript-segment"]',
                
                # Engagement panel transcript segments
                '.ytd-engagement-panel-section-list-renderer .segment',
                'ytd-transcript-body-renderer .segment',
                
                # Fallback selectors
                'ytd-transcript-renderer .segment',
            ]
            
            transcript_data = []
            
            for selector in segment_selectors:
                try:
                    # Wait for segments to appear
                    await self.page.wait_for_selector(selector, timeout=10000)
                    segments = await self.page.query_selector_all(selector)
                    
                    if segments:
                        logger.info(f"Found {len(segments)} transcript segments with selector: {selector}")
                        
                        for segment in segments:
                            try:
                                # Extract timestamp
                                timestamp_selectors = [
                                    '.segment-timestamp',
                                    '.timestamp', 
                                    '[class*="timestamp"]',
                                    '.time'
                                ]
                                
                                timestamp_text = ""
                                for ts_selector in timestamp_selectors:
                                    timestamp_element = await segment.query_selector(ts_selector)
                                    if timestamp_element:
                                        timestamp_text = await timestamp_element.inner_text()
                                        break
                                
                                # Extract text content
                                text_selectors = [
                                    'yt-formatted-string.segment-text',
                                    '.segment-text',
                                    '.text',
                                    '[class*="text"]'
                                ]
                                
                                segment_text = ""
                                for text_selector in text_selectors:
                                    text_element = await segment.query_selector(text_selector)
                                    if text_element:
                                        segment_text = await text_element.inner_text()
                                        break
                                
                                # If we couldn't find specific text element, try getting all text
                                if not segment_text:
                                    segment_text = await segment.inner_text()
                                    # Remove timestamp from text if it's included
                                    if timestamp_text and timestamp_text in segment_text:
                                        segment_text = segment_text.replace(timestamp_text, "").strip()
                                
                                # Add segment if we have content
                                if segment_text.strip():
                                    start_seconds = self.parse_timestamp(timestamp_text.strip()) if timestamp_text else None
                                    transcript_data.append({
                                        'text': segment_text.strip(),
                                        'start': start_seconds or 0,
                                        'duration': 3.0  # Default duration
                                    })
                                    logger.debug(f"Added segment: {timestamp_text} -> {segment_text[:50]}...")
                            
                            except Exception as e:
                                logger.debug(f"Error parsing segment: {e}")
                                continue
                        
                        break  # Successfully found segments, no need to try other selectors
                        
                except PlaywrightTimeoutError:
                    logger.debug(f"No segments found with selector: {selector}")
                    continue
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            if not transcript_data:
                logger.warning("No transcript segments found after clicking transcript button")
                # Try alternative extraction method
                return await self._extract_all_visible_text()
            
            logger.info(f"Successfully extracted {len(transcript_data)} transcript segments")
            return transcript_data
            
        except Exception as e:
            logger.error(f"Error extracting transcript from DOM: {e}")
            return None
    
    async def _extract_all_visible_text(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fallback method to extract all visible transcript text when specific selectors fail.
        This copies ALL transcript messages that appear as requested by the user.
        """
        try:
            logger.info("Trying fallback method to extract all visible transcript text")
            
            # Look for any element that might contain transcript content
            transcript_containers = [
                'ytd-transcript-body-renderer',
                'ytd-transcript-segment-list-renderer', 
                'ytd-transcript-renderer',
                '.ytd-engagement-panel-section-list-renderer',
                '[role="main"] [class*="transcript"]',
                '[class*="transcript-container"]',
                '[class*="caption"]'
            ]
            
            for container_selector in transcript_containers:
                try:
                    container = await self.page.query_selector(container_selector)
                    if container and await container.is_visible():
                        # Get all text content from the container
                        all_text = await container.inner_text()
                        
                        if all_text and len(all_text.strip()) > 50:  # Minimum length check
                            logger.info(f"Found transcript text using fallback method: {len(all_text)} characters")
                            
                            # Split into segments by time patterns or line breaks
                            segments = self._split_text_into_segments(all_text)
                            return segments
                            
                except Exception as e:
                    logger.debug(f"Error with container {container_selector}: {e}")
                    continue
            
            logger.error("Fallback text extraction also failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in fallback text extraction: {e}")
            return None
    
    def _split_text_into_segments(self, text: str) -> List[Dict[str, Any]]:
        """Split transcript text into segments"""
        try:
            segments = []
            lines = text.split('\n')
            current_time = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line contains timestamp
                time_match = re.search(r'(\d+:\d+)', line)
                if time_match:
                    timestamp = time_match.group(1)
                    parsed_time = self.parse_timestamp(timestamp)
                    if parsed_time is not None:
                        current_time = parsed_time
                    
                    # Remove timestamp from text
                    text_content = re.sub(r'\d+:\d+', '', line).strip()
                else:
                    text_content = line
                
                if text_content:
                    segments.append({
                        'text': text_content,
                        'start': current_time,
                        'duration': 3.0
                    })
                    current_time += 3  # Increment for next segment
            
            return segments if segments else [{'text': text, 'start': 0, 'duration': 3.0}]
            
        except Exception as e:
            logger.error(f"Error splitting text into segments: {e}")
            return [{'text': text, 'start': 0, 'duration': 3.0}]
    
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