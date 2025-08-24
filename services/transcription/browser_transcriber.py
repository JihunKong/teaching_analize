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
                '--disable-features=VizDisplayCompositor',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-ipc-flooding-protection'
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
        """Wait for YouTube page and video to load enough for transcript access"""
        try:
            # Wait for basic YouTube page structure to load
            page_selectors = [
                '#movie_player',  # Main video container
                'video',          # Video element
                'ytd-watch-flexy', # Watch page container
                '#primary'        # Primary content area
            ]
            
            # Try to find at least one key element that indicates the page loaded
            for selector in page_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=15000)
                    logger.info(f"Found page element: {selector}")
                    break
                except PlaywrightTimeoutError:
                    continue
            else:
                logger.warning("Could not find main page elements, but continuing...")
            
            # Wait for page to stabilize
            await asyncio.sleep(5)
            
            # Check if we can access the page content and detect UI language
            try:
                page_title = await self.page.title()
                html_lang = await self.page.get_attribute('html', 'lang') or 'unknown'
                
                if 'YouTube' in page_title or len(page_title) > 5:
                    logger.info(f"YouTube page loaded with title: {page_title} (language: {html_lang})")
                    
                    # Log Korean UI detection for debugging
                    if html_lang.startswith('ko') or any(korean_char in page_title for korean_char in ['유튜브', '영상', '비디오']):
                        logger.info("Korean YouTube UI detected - using enhanced Korean selectors")
                    
                    return True
            except Exception as e:
                logger.debug(f"Could not get page title or language: {e}")
            
            # Even if video isn't fully loaded, we can try to access transcript
            logger.info("Proceeding with transcript extraction even if video isn't fully loaded")
            return True
            
        except Exception as e:
            logger.error(f"Error waiting for page load: {e}")
            return False
    

    async def click_transcript_button(self) -> bool:
        """
        Click the YouTube transcript button to open the transcript panel.
        Enhanced with comprehensive debugging and scrolling to ensure transcript controls are visible.
        """
        try:
            logger.info("Looking for YouTube transcript button (스크립트 button)")
            
            # Wait for page to load completely
            await asyncio.sleep(5)
            
            # Aggressive scrolling to find transcript controls
            logger.info("Aggressive scrolling to find transcript controls")
            
            # Scroll to different sections of the page
            scroll_positions = [
                "window.scrollTo(0, 400)",  # Below video player  
                "window.scrollTo(0, 800)",  # Into description area
                "window.scrollTo(0, 1200)", # Further down
                "window.scrollTo(0, document.body.scrollHeight / 2)" # Middle of page
            ]
            
            for i, scroll_cmd in enumerate(scroll_positions):
                logger.info(f"Scrolling to position {i+1}/4: {scroll_cmd}")
                await self.page.evaluate(scroll_cmd)
                await asyncio.sleep(2)
                
                # After each scroll, look for "Show more" buttons to expand sections
                await self._expand_description_sections()
                
                # Check if any transcript buttons became visible
                transcript_visible = await self._quick_transcript_check()
                if transcript_visible:
                    logger.info(f"Transcript controls became visible after scroll position {i+1}")
                    break
            
            # Take screenshot for debugging
            try:
                await self.page.screenshot(path="/tmp/youtube_before_transcript_search.png", full_page=True)
                logger.info("Screenshot saved: /tmp/youtube_before_transcript_search.png")
            except Exception as e:
                logger.debug(f"Could not take screenshot: {e}")
            
            # Detect Korean UI and log for debugging
            is_korean_ui = await self._detect_korean_ui()
            logger.info(f"Korean UI detected: {is_korean_ui}")
            
            # Enhanced debugging - log ALL visible buttons
            await self._debug_all_visible_elements()
            
            # Enhanced transcript button detection with comprehensive Korean support
            transcript_button_selectors = self._get_transcript_only_selectors(is_korean_ui)
            
            # Log all available buttons for debugging
            await self._debug_available_buttons()
                
            
            # Try transcript button selectors with enhanced debugging
            for i, selector in enumerate(transcript_button_selectors):
                try:
                    logger.info(f"Trying selector {i+1}/{len(transcript_button_selectors)}: {selector}")
                    
                    # Look for the button
                    button = await self.page.query_selector(selector)
                    if button:
                        # Check if button is visible and clickable
                        is_visible = await button.is_visible()
                        is_enabled = await button.is_enabled()
                        button_text = await button.inner_text() if is_visible else "N/A"
                        aria_label = await button.get_attribute('aria-label') if is_visible else "N/A"
                        
                        logger.info(f"Found button - visible: {is_visible}, enabled: {is_enabled}, text: '{button_text}', aria-label: '{aria_label}'")
                        
                        if is_visible and is_enabled:
                            logger.info(f"✅ Clicking transcript button with selector: {selector}")
                            
                            # Take screenshot before clicking
                            try:
                                await self.page.screenshot(path=f"/tmp/before_click_{i}.png")
                            except:
                                pass
                            
                            await button.click()
                            await asyncio.sleep(3)  # Wait longer for panel to open
                            
                            # Take screenshot after clicking
                            try:
                                await self.page.screenshot(path=f"/tmp/after_click_{i}.png")
                            except:
                                pass
                            
                            # Check if transcript panel opened
                            panel_opened = await self._verify_transcript_panel_opened()
                            if panel_opened:
                                logger.info("✅ Transcript panel opened successfully")
                                return True
                            else:
                                logger.warning("❌ Transcript panel did not open, trying next selector")
                                # If this was a "More" button, look for transcript option in menu
                                if any(term in selector.lower() for term in ["더 보기", "더보기", "more actions"]):
                                    if await self._click_transcript_in_menu():
                                        return True
                        else:
                            logger.debug(f"Button not clickable - visible: {is_visible}, enabled: {is_enabled}")
                        
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            # If no direct button found, try clicking three-dot menu and looking for transcript
            logger.info("No direct transcript button found, trying menu approach")
            return await self._try_menu_approach()
            
        except Exception as e:
            logger.error(f"Error clicking transcript button: {e}")
            return False
    
    async def _click_transcript_in_menu(self) -> bool:
        """Enhanced function to click transcript option from opened menu"""
        try:
            logger.info("Looking for transcript option in opened menu...")
            
            # Wait for menu to fully open
            await asyncio.sleep(2)
            
            # Enhanced menu item selectors for transcript options
            transcript_menu_selectors = [
                # Korean transcript menu items
                'tp-yt-paper-item:has-text("스크립트")',
                'tp-yt-paper-item:has-text("스크립트 표시")',
                'tp-yt-paper-item:has-text("자막")',
                'tp-yt-paper-item:has-text("자막 표시")',
                'ytd-menu-service-item-renderer:has-text("스크립트")',
                'ytd-menu-service-item-renderer:has-text("자막")',
                
                # English transcript menu items
                'tp-yt-paper-item:has-text("Transcript")',
                'tp-yt-paper-item:has-text("Show transcript")', 
                'ytd-menu-service-item-renderer:has-text("Transcript")',
                'ytd-menu-service-item-renderer:has-text("Show transcript")',
                
                # General menu item selectors with Korean text
                '[role="menuitem"]:has-text("스크립트")',
                '[role="menuitem"]:has-text("자막")',
                '[role="menuitem"]:has-text("Transcript")',
                'yt-formatted-string:has-text("스크립트")',
                'yt-formatted-string:has-text("자막")',
                'yt-formatted-string:has-text("Transcript")',
                
                # Look for buttons within the menu
                'yt-dropdown-menu button:has-text("스크립트")',
                'yt-dropdown-menu button:has-text("자막")',
                'yt-dropdown-menu button:has-text("Transcript")',
                
                # Aria-label based selectors for menu items
                '[role="menuitem"][aria-label*="스크립트" i]',
                '[role="menuitem"][aria-label*="자막" i]',
                '[role="menuitem"][aria-label*="transcript" i]',
                
                # More generic selectors
                '*[role="menuitem"]',
                'tp-yt-paper-item',
                'ytd-menu-service-item-renderer'
            ]
            
            # Debug: Log all visible menu items
            try:
                all_menu_items = await self.page.query_selector_all('[role="menuitem"], tp-yt-paper-item, ytd-menu-service-item-renderer')
                logger.info(f"Found {len(all_menu_items)} total menu items")
                
                for i, item in enumerate(all_menu_items[:10]):  # Log first 10 for debugging
                    try:
                        is_visible = await item.is_visible()
                        if is_visible:
                            text = await item.inner_text()
                            aria_label = await item.get_attribute('aria-label') or ''
                            logger.info(f"Menu item {i}: text='{text}', aria-label='{aria_label}'")
                    except:
                        pass
            except Exception as e:
                logger.debug(f"Error debugging menu items: {e}")
                
            # Try each transcript menu selector
            menu_selectors = [
                # Korean menu items
                'yt-formatted-string:has-text("스크립트")',
                'yt-formatted-string:has-text("자막")',
                'yt-formatted-string:has-text("대본")',
                'yt-formatted-string:has-text("스크립트 표시")',
                'yt-formatted-string:has-text("자막 표시")',
                '[role="menuitem"]:has-text("스크립트")',
                '[role="menuitem"]:has-text("자막")',
                '[role="menuitem"]:has-text("대본")',
                '[role="menuitem"]:has-text("스크립트 표시")',
                '[role="menuitem"]:has-text("자막 표시")',
                'tp-yt-paper-item:has-text("스크립트")',
                'tp-yt-paper-item:has-text("자막")',
                'tp-yt-paper-item:has-text("대본")',
                
                # English menu items
                'yt-formatted-string:has-text("Show transcript")',
                'yt-formatted-string:has-text("Transcript")',
                '[role="menuitem"]:has-text("transcript")',
                '[role="menuitem"]:has-text("Show transcript")',
                'tp-yt-paper-item:has-text("transcript")',
                'tp-yt-paper-item:has-text("Show transcript")',
                
                # Case-insensitive patterns for Korean text
                'yt-formatted-string[aria-label*="스크립트" i]',
                'yt-formatted-string[aria-label*="자막" i]',
                'yt-formatted-string[aria-label*="대본" i]',
                '[role="menuitem"][aria-label*="스크립트" i]',
                '[role="menuitem"][aria-label*="자막" i]',
                '[role="menuitem"][aria-label*="대본" i]',
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
        """Enhanced menu approach - look for visible menu buttons and transcript options"""
        try:
            logger.info("Trying enhanced menu approach for transcript access")
            
            # Enhanced menu button selectors - prioritizing visible ones
            menu_selectors = [
                # Primary selectors for visible menu buttons
                'button[aria-label*="더 보기" i]:visible',
                'button[aria-label*="더보기" i]:visible', 
                'button[aria-label*="More actions" i]:visible',
                'yt-button-renderer[aria-label*="더 보기" i]',
                'yt-button-renderer[aria-label*="More actions" i]',
                
                # Look in description area where menu is typically located
                '#description button[aria-label*="더 보기" i]',
                '#description button[aria-label*="More actions" i]',
                '.ytd-video-secondary-info-renderer button[aria-label*="더 보기" i]',
                '.ytd-video-secondary-info-renderer button[aria-label*="More actions" i]',
                
                # Look in engagement panel area
                'ytd-engagement-panel-section-list-renderer button',
                '.ytd-engagement-panel-section-list-renderer [role="button"]',
                
                # Fallback selectors
                'button[aria-label="더보기"]',
                'button[aria-label="더 보기"]', 
                'button[aria-label="More actions"]'
            ]
            
            # Try each menu selector
            for i, selector in enumerate(menu_selectors):
                try:
                    logger.info(f"Trying menu selector {i+1}/{len(menu_selectors)}: {selector}")
                    
                    elements = await self.page.query_selector_all(selector)
                    logger.info(f"Found {len(elements)} elements with selector {selector}")
                    
                    for j, element in enumerate(elements):
                        try:
                            is_visible = await element.is_visible()
                            is_enabled = await element.is_enabled()
                            
                            if is_visible and is_enabled:
                                button_text = await element.inner_text()
                                aria_label = await element.get_attribute('aria-label') or ''
                                
                                logger.info(f"Found visible menu button {j}: text='{button_text}', aria-label='{aria_label}'")
                                
                                # Click the menu button
                                await element.click()
                                logger.info(f"Clicked menu button, waiting for menu to open...")
                                await asyncio.sleep(3)  # Wait longer for menu to fully open
                                
                                # Take screenshot after menu click
                                try:
                                    await self.page.screenshot(path=f"/tmp/after_menu_click_{i}_{j}.png")
                                    logger.info(f"Screenshot saved: /tmp/after_menu_click_{i}_{j}.png")
                                except:
                                    pass
                                
                                # Try to find transcript option in the opened menu
                                if await self._click_transcript_in_menu():
                                    return True
                                
                                # If not found, close menu and continue
                                logger.info("Transcript not found in menu, closing and trying next...")
                                await self.page.keyboard.press('Escape')
                                await asyncio.sleep(1)
                                
                        except Exception as e:
                            logger.debug(f"Error with element {j}: {e}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            logger.warning("No working menu buttons found for transcript access")
            return False
            
        except Exception as e:
            logger.error(f"Error in enhanced menu approach: {e}")
            return False
    
    async def extract_transcript_from_dom(self) -> Optional[List[Dict[str, Any]]]:
        """
        Extract transcript segments directly from YouTube DOM structure.
        This implements the user's requested method: clicking "스크립트" button and copying all transcript messages.
        """
        try:
            logger.info("Starting transcript extraction by clicking 스크립트 (Script) button")
            
            # Step 1: Click transcript button directly (no CC button approach)
            transcript_opened = False
            
            # Direct transcript button approach only
            if await self.click_transcript_button():
                transcript_opened = True
                logger.info("Successfully opened transcript via direct button approach")
            
            if not transcript_opened:
                logger.error("Failed to open transcript panel with any method")
                return None
            
            # Step 2: Wait for transcript panel to load
            logger.info("Waiting for transcript panel to load...")
            await asyncio.sleep(3)
            
            # Step 3: Look for transcript segments using EXACT DOM structure from user
            segment_selectors = [
                # PRIMARY: Exact selectors from user's provided DOM structure
                '.segment.style-scope.ytd-transcript-segment-renderer',
                'div.segment.style-scope.ytd-transcript-segment-renderer',
                'div.segment.style-scope.ytd-transcript-segment-renderer[role="button"]',
                'div.segment.style-scope.ytd-transcript-segment-renderer[tabindex="0"]',
                
                # Alternative patterns with exact class combinations
                '.segment.ytd-transcript-segment-renderer',
                'ytd-transcript-segment-renderer .segment',
                'ytd-transcript-segment-renderer div.segment',
                '[role="button"].segment.style-scope.ytd-transcript-segment-renderer',
                
                # Korean UI specific patterns
                'ytd-transcript-segment-renderer[class*="segment"]',
                '.ytd-transcript-segment-renderer .segment',
                '[class*="transcript-segment"] .segment',
                
                # Fallback selectors for any transcript content
                'ytd-transcript-body-renderer .segment',
                'ytd-transcript-renderer .segment',
                'ytd-transcript-body-renderer div',
                'ytd-transcript-renderer div',
                
                # Generic transcript item selectors
                '.transcript-item',
                '.caption-item', 
                '[data-segment-id]',
                '[data-transcript-segment]'
            ]
            
            transcript_data = []
            
            for selector in segment_selectors:
                try:
                    # Wait for segments to appear
                    await self.page.wait_for_selector(selector, timeout=10000)
                    segments = await self.page.query_selector_all(selector)
                    
                    if segments:
                        logger.info(f"Found {len(segments)} transcript segments with selector: {selector}")
                        
                        for i, segment in enumerate(segments):
                            try:
                                # Log segment structure for debugging
                                if i < 3:  # Log first 3 segments for debugging
                                    segment_html = await segment.innerHTML()
                                    logger.info(f"DEBUG: Segment {i} HTML structure: {segment_html[:200]}...")
                                
                                # Extract timestamp using EXACT DOM structure from user
                                timestamp_selectors = [
                                    '.segment-timestamp.style-scope.ytd-transcript-segment-renderer',
                                    'div.segment-timestamp.style-scope.ytd-transcript-segment-renderer',
                                    '.segment-start-offset .segment-timestamp.style-scope.ytd-transcript-segment-renderer',
                                    '.segment-start-offset .segment-timestamp',
                                    '.segment-timestamp',
                                    '[class*="timestamp"]',
                                ]
                                
                                timestamp_text = ""
                                used_ts_selector = ""
                                for ts_selector in timestamp_selectors:
                                    timestamp_element = await segment.query_selector(ts_selector)
                                    if timestamp_element:
                                        timestamp_text = await timestamp_element.inner_text()
                                        used_ts_selector = ts_selector
                                        break
                                
                                # Extract text content using EXACT DOM structure from user
                                text_selectors = [
                                    'yt-formatted-string.segment-text.style-scope.ytd-transcript-segment-renderer',
                                    'yt-formatted-string.segment-text',
                                    '.segment-text.style-scope.ytd-transcript-segment-renderer',
                                    '.segment-text',
                                    'yt-formatted-string',
                                    '[class*="segment-text"]'
                                ]
                                
                                segment_text = ""
                                used_text_selector = ""
                                for text_selector in text_selectors:
                                    text_element = await segment.query_selector(text_selector)
                                    if text_element:
                                        segment_text = await text_element.inner_text()
                                        used_text_selector = text_selector
                                        break
                                
                                # If we couldn't find specific text element, try getting all text
                                if not segment_text:
                                    segment_text = await segment.inner_text()
                                    used_text_selector = "fallback:inner_text"
                                    # Remove timestamp from text if it's included
                                    if timestamp_text and timestamp_text in segment_text:
                                        segment_text = segment_text.replace(timestamp_text, "").strip()
                                
                                # Log successful extraction for debugging
                                if i < 3:  # Log first 3 segments for debugging
                                    logger.info(f"DEBUG: Segment {i} - timestamp: '{timestamp_text}' (selector: {used_ts_selector}) - text: '{segment_text[:100]}...' (selector: {used_text_selector})")
                                
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
                                logger.debug(f"Error parsing segment {i}: {e}")
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
    
    async def check_captions_availability(self) -> Dict[str, Any]:
        """Check if the video has transcripts available (auto-generated transcripts)"""
        try:
            transcript_info = {
                'has_transcripts': True,  # YouTube ALWAYS has auto-generated transcripts
                'transcript_types': ['auto-generated'],
                'transcript_available': True  # Always true for YouTube
            }
            
            # Check for CC button in video player
            cc_buttons = await self.page.query_selector_all('button[aria-label*="자막"], button[aria-label*="Captions"], button[aria-label*="CC"], .ytp-subtitles-button')
            
            for button in cc_buttons:
                if await button.is_visible():
                    aria_label = await button.get_attribute('aria-label') or ''
                    title = await button.get_attribute('title') or ''
                    
                    if '사용 불가' not in aria_label and 'unavailable' not in aria_label.lower():
                        caption_info['has_captions'] = True
                        caption_info['caption_types'].append(aria_label or title)
            
            # Check for transcript button availability
            transcript_selectors = [
                'button[aria-label*="스크립트"]',
                'button[aria-label*="transcript"]',
                'button:has-text("스크립트")',
                'button:has-text("Transcript")'
            ]
            
            for selector in transcript_selectors:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    caption_info['transcript_available'] = True
                    break
            
            logger.info(f"Transcript availability: {transcript_info}")
            return transcript_info
            
        except Exception as e:
            logger.error(f"Error checking caption availability: {e}")
            return {'has_transcripts': True, 'transcript_types': ['auto-generated'], 'transcript_available': True}  # Always true for YouTube

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
            
            # Navigate to YouTube video with longer timeout for production
            await self.page.goto(youtube_url, wait_until='domcontentloaded', timeout=60000)
            
            # Additional wait for JavaScript to load
            await asyncio.sleep(2)
            
            # Wait for video to load
            if not await self.wait_for_video_load():
                return {
                    "success": False,
                    "error": "Failed to load video in browser",
                    "video_id": video_id
                }
            
            # Get video metadata and transcript availability
            metadata = await self.get_video_metadata()
            transcript_info = await self.check_captions_availability()
            
            # NOTE: YouTube auto-generates transcripts for ALL videos - no early exit needed
            logger.info(f"Transcript detection results: {transcript_info}")
            logger.info("Proceeding with transcript extraction (YouTube auto-generates transcripts for all videos)")
            
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
                "processing_time": processing_time,
                "transcript_info": transcript_info
            }
    
    async def _detect_korean_ui(self) -> bool:
        """Detect if YouTube is using Korean UI"""
        try:
            # Check HTML lang attribute
            html_lang = await self.page.get_attribute('html', 'lang') or ''
            if html_lang.startswith('ko'):
                return True
            
            # Check page title for Korean characters
            page_title = await self.page.title()
            korean_chars = any('\uac00' <= char <= '\ud7a3' for char in page_title)
            
            # Check for Korean text in common UI elements
            korean_indicators = [
                'button:has-text("구독")',  # Subscribe button
                'button:has-text("좋아요")',  # Like button  
                'button:has-text("댓글")',   # Comments
                '[aria-label*="조회수"]',    # View count
            ]
            
            for indicator in korean_indicators:
                element = await self.page.query_selector(indicator)
                if element:
                    return True
            
            return korean_chars
            
        except Exception as e:
            logger.debug(f"Error detecting Korean UI: {e}")
            return False
    
    def _get_transcript_only_selectors(self, is_korean_ui: bool) -> List[str]:
        """Get transcript-only button selectors (NO captions/CC buttons) - FIXED to be more specific"""
        
        # SPECIFIC transcript-only selectors - removed overly broad ones that catch random buttons
        base_selectors = [
            # HIGH-PRIORITY: Specific aria-label based selectors
            'button[aria-label*="transcript" i]:not([aria-label*="탐색"])',
            'button[aria-label*="Show transcript" i]',
            'button[aria-label*="스크립트" i]:not([aria-label*="탐색"]):not([aria-label*="건너뛰기"])',
            'button[aria-label*="스크립트 표시" i]',
            'button[aria-label="스크립트 표시"]',
            'button[aria-label="Show transcript"]',
            
            # SPECIFIC YouTube component selectors for transcript
            'yt-button-renderer[aria-label*="transcript" i]',
            'yt-button-renderer[aria-label*="스크립트" i]',
            'yt-button-view-model[aria-label*="transcript" i]',
            'yt-button-view-model[aria-label*="스크립트" i]',
            
            # CONTEXT-SPECIFIC selectors in video controls area
            '#top-level-buttons-computed button[aria-label*="transcript" i]',
            '#top-level-buttons-computed button[aria-label*="스크립트" i]',
            '.ytd-video-primary-info-renderer button[aria-label*="transcript" i]',
            '.ytd-video-primary-info-renderer button[aria-label*="스크립트" i]',
            
            # Menu approach for transcript access  
            'button[aria-label*="더 보기" i]:not([aria-label*="탐색"])',
            'button[aria-label*="더보기" i]:not([aria-label*="탐색"])',
            'button[aria-label="더보기"]',
            'button[aria-label="더 보기"]',
            'button[aria-label*="More actions" i]',
            'button[aria-label="More actions"]',
            
            # YouTube-specific menu containers
            'yt-button-renderer[aria-label*="더 보기" i]',
            'yt-button-renderer[aria-label*="More actions" i]',
            
            # ONLY look for touch feedback elements WITH transcript context
            '*:has(.yt-spec-touch-feedback-shape__fill)[aria-label*="transcript" i]:not([aria-label*="탐색"])',
            '*:has(.yt-spec-touch-feedback-shape__fill)[aria-label*="스크립트" i]:not([aria-label*="탐색"]):not([aria-label*="건너뛰기"])',
            '*:has(.yt-spec-touch-feedback-shape__fill)[aria-label*="더 보기" i]:not([aria-label*="탐색"])',
            
            # Title-based selectors as backup
            'button[title*="transcript" i]',
            'button[title*="Show transcript" i]',
            'button[title*="스크립트" i]',
            'button[title*="스크립트 표시" i]',
            
            # CSS class-based selectors
            'button[class*="transcript" i]',
            'button[class*="caption" i]',
            '[class*="transcript-button" i]',
            '[class*="caption-button" i]',
            
            # Data attribute selectors
            '[data-testid="transcript-button"]',
            '[data-transcript-button]',
            
            # Panel and container selectors
            'ytd-transcript-renderer button',
            'ytd-engagement-panel-title-header-renderer button',
            '.ytd-engagement-panel-section-list-renderer button',
        ]
        
        if is_korean_ui:
            # Prioritize Korean selectors for Korean UI
            korean_priority = [s for s in base_selectors if any(k in s for k in ['스크립트', '자막', '대본', '더'])]
            english_selectors = [s for s in base_selectors if s not in korean_priority]
            return korean_priority + english_selectors
        else:
            return base_selectors
    
    async def _debug_all_visible_elements(self):
        """Enhanced debugging to log ALL visible interactive elements with full details"""
        try:
            logger.info("🔍 ENHANCED DEBUGGING: All visible interactive elements on page")
            
            # Find ALL interactive elements 
            all_elements = await self.page.query_selector_all(
                'button, [role="button"], a, [role="menuitem"], tp-yt-paper-item, '
                'ytd-menu-service-item-renderer, yt-button-renderer, yt-button-view-model, '
                '*:has(.yt-spec-touch-feedback-shape__fill), [onclick], [tabindex]'
            )
            logger.info(f"Found {len(all_elements)} total interactive elements")
            
            visible_count = 0
            for i, element in enumerate(all_elements[:50]):  # Check first 50 elements
                try:
                    is_visible = await element.is_visible()
                    if is_visible:
                        visible_count += 1
                        is_enabled = await element.is_enabled()
                        text = (await element.inner_text()).strip()[:100]  # Limit text length
                        aria_label = await element.get_attribute('aria-label') or ''
                        title = await element.get_attribute('title') or ''
                        class_name = await element.get_attribute('class') or ''
                        tag_name = await element.evaluate('el => el.tagName')
                        id_attr = await element.get_attribute('id') or ''
                        role = await element.get_attribute('role') or ''
                        
                        # Check if element contains transcript-related keywords
                        transcript_related = any(keyword in (text + aria_label + title + class_name).lower() 
                                               for keyword in ['스크립트', '자막', '대본', 'transcript', 'caption', '더보기', 'more'])
                        
                        log_level = "🎯 TRANSCRIPT-RELATED" if transcript_related else "📍 VISIBLE"
                        logger.info(
                            f"{log_level} Element #{visible_count}: "
                            f"tag={tag_name}, visible={is_visible}, enabled={is_enabled}, "
                            f"text='{text}', aria-label='{aria_label}', title='{title}', "
                            f"class='{class_name[:50]}...', id='{id_attr}', role='{role}'"
                        )
                        
                except Exception as e:
                    logger.debug(f"Error debugging element {i}: {e}")
                    continue
            
            logger.info(f"Total visible interactive elements: {visible_count}")
            
        except Exception as e:
            logger.error(f"Error in enhanced debugging: {e}")

    async def _expand_description_sections(self):
        """Expand collapsible sections that might contain transcript controls"""
        try:
            # Look for "Show more" buttons in description area
            expand_selectors = [
                # Korean "Show more" buttons
                'button:has-text("더 보기")',
                'button:has-text("더보기")', 
                '[role="button"]:has-text("더 보기")',
                '[role="button"]:has-text("더보기")',
                'yt-formatted-string:has-text("더 보기")',
                'yt-formatted-string:has-text("더보기")',
                
                # English "Show more" buttons  
                'button:has-text("Show more")',
                '[role="button"]:has-text("Show more")',
                'yt-formatted-string:has-text("Show more")',
                
                # By aria-label
                'button[aria-label*="더 보기" i]',
                'button[aria-label*="더보기" i]',
                'button[aria-label*="Show more" i]',
                
                # Description expansion buttons
                '.ytd-video-secondary-info-renderer button',
                '.ytd-expander button',
                'ytd-expander button'
            ]
            
            for selector in expand_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for element in elements:
                        is_visible = await element.is_visible()
                        if is_visible:
                            button_text = await element.inner_text()
                            if button_text and len(button_text.strip()) < 50:  # Avoid clicking large text blocks
                                logger.info(f"Expanding section with button: '{button_text}'")
                                await element.click()
                                await asyncio.sleep(1)
                except Exception as e:
                    logger.debug(f"Error expanding with selector {selector}: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Error in _expand_description_sections: {e}")

    async def _quick_transcript_check(self) -> bool:
        """Quick check if any transcript controls became visible"""
        try:
            # Quick selectors for common transcript buttons
            quick_selectors = [
                'button[aria-label*="스크립트" i]',
                'button[aria-label*="transcript" i]',
                'button:has-text("스크립트")',
                'button:has-text("Transcript")',
                '[role="button"]:has-text("스크립트")',
                '[role="button"]:has-text("Transcript")'
            ]
            
            for selector in quick_selectors:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    return True
            return False
            
        except Exception as e:
            logger.debug(f"Error in quick transcript check: {e}")
            return False

    async def _debug_available_buttons(self):
        """Debug helper to log all available buttons on the page with enhanced detection"""
        try:
            logger.info("🔍 Debugging available buttons on page...")
            
            # Find all buttons including those with .yt-spec-touch-feedback-shape__fill
            all_buttons = await self.page.query_selector_all('button, [role="button"], yt-button-renderer, *:has(.yt-spec-touch-feedback-shape__fill)')
            logger.info(f"Found {len(all_buttons)} total interactive elements on page")
            
            button_info = []
            for i, button in enumerate(all_buttons[:30]):  # Increased to 30 for better debugging
                try:
                    is_visible = await button.is_visible()
                    if is_visible:
                        text = await button.inner_text()
                        aria_label = await button.get_attribute('aria-label') or ''
                        title = await button.get_attribute('title') or ''
                        class_name = await button.get_attribute('class') or ''
                        tag_name = await button.evaluate('el => el.tagName')
                        
                        # Check for .yt-spec-touch-feedback-shape__fill
                        has_touch_feedback = await button.query_selector('.yt-spec-touch-feedback-shape__fill') is not None
                        
                        if any(term in (text + aria_label + title + class_name).lower() for term in 
                              ['transcript', 'script', '스크립트', '자막', '대본', 'caption']) or has_touch_feedback:
                            button_info.append({
                                'index': i,
                                'tag': tag_name.lower(),
                                'text': text.strip()[:50] if text else '',
                                'aria_label': aria_label[:100] if aria_label else '',
                                'title': title[:100] if title else '',
                                'class': class_name[:100] if class_name else '',
                                'has_touch_feedback': has_touch_feedback
                            })
                            
                except Exception as e:
                    logger.debug(f"Error inspecting button {i}: {e}")
                    continue
            
            if button_info:
                logger.info("🎯 Found potentially relevant interactive elements:")
                for info in button_info:
                    logger.info(f"  Element {info['index']} ({info['tag']}): text='{info['text']}' aria-label='{info['aria_label']}' title='{info['title']}' class='{info['class']}' touch_feedback={info['has_touch_feedback']}")
            else:
                logger.warning("❌ No transcript-related elements found in first 30 elements")
                
            # Also check DOM structure specifically for transcript segments
            segment_elements = await self.page.query_selector_all('.segment.style-scope.ytd-transcript-segment-renderer')
            if segment_elements:
                logger.info(f"✅ Found {len(segment_elements)} transcript segments already visible")
            else:
                logger.info("❌ No transcript segments currently visible")
                
        except Exception as e:
            logger.error(f"Error debugging buttons: {e}")
    
    async def _verify_transcript_panel_opened(self) -> bool:
        """Verify that the transcript panel has opened"""
        try:
            # Wait a bit for panel to load
            await asyncio.sleep(2)
            
            # Look for transcript panel indicators
            panel_selectors = [
                'ytd-transcript-renderer',
                'ytd-transcript-body-renderer', 
                'ytd-transcript-segment-list-renderer',
                '.ytd-engagement-panel-section-list-renderer ytd-transcript-renderer',
                '[class*="transcript"]',
                '.segment.style-scope.ytd-transcript-segment-renderer'
            ]
            
            for selector in panel_selectors:
                element = await self.page.query_selector(selector)
                if element and await element.is_visible():
                    logger.info(f"✅ Transcript panel detected with selector: {selector}")
                    return True
            
            # Also check if we can see transcript segments using EXACT user-provided selectors
            try:
                await self.page.wait_for_selector('.segment.style-scope.ytd-transcript-segment-renderer', timeout=3000)
                logger.info("✅ Transcript segments visible (exact DOM match)")
                return True
            except:
                # Try alternative segment detection
                try:
                    await self.page.wait_for_selector('div.segment.style-scope.ytd-transcript-segment-renderer[role="button"]', timeout=2000)
                    logger.info("✅ Transcript segments visible (alternative pattern)")
                    return True
                except:
                    pass
            
            logger.warning("❌ No transcript panel detected after clicking button")
            return False
            
        except Exception as e:
            logger.error(f"Error verifying transcript panel: {e}")
            return False

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