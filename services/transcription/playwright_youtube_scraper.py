#!/usr/bin/env python3
"""
Playwright YouTube Script Scraper
YouTube의 스크립트 보기 기능을 브라우저 자동화로 크롤링
"""

import asyncio
import logging
import re
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Page, Browser
import json

logger = logging.getLogger(__name__)

class PlaywrightYouTubeScraper:
    """Playwright를 사용한 YouTube 스크립트 크롤링"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.close_browser()
    
    async def start_browser(self):
        """브라우저 시작"""
        try:
            self.playwright = await async_playwright().start()
            
            # Chrome 브라우저 시작 (더 안정적)
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                ]
            )
            
            # 새 페이지 생성
            self.page = await self.browser.new_page()
            
            # 브라우저 감지 방지
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            logger.info("✅ Browser started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            raise
    
    async def close_browser(self):
        """브라우저 종료"""
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("✅ Browser closed")
        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """YouTube URL에서 비디오 ID 추출"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # 이미 video ID인 경우
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    async def wait_for_content_load(self, timeout: int = 30000):
        """페이지 콘텐츠 로드 대기"""
        try:
            # 비디오 플레이어가 로드될 때까지 대기
            await self.page.wait_for_selector('video', timeout=timeout)
            
            # 추가 대기 (JavaScript 로딩)
            await asyncio.sleep(3)
            
            logger.info("✅ Page content loaded")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Content load timeout: {e}")
            return False
    
    async def open_transcript_panel(self) -> bool:
        """스크립트 패널 열기"""
        try:
            # 방법 1: 더보기 버튼 클릭
            more_button_selectors = [
                'button[aria-label*="더보기"]',
                'button[aria-label*="More"]',
                'button[aria-label*="Show more"]',
                'ytd-menu-renderer button',
                '#menu button'
            ]
            
            for selector in more_button_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    logger.info(f"✅ Clicked more button: {selector}")
                    break
                except:
                    continue
            
            # 스크립트 메뉴 항목 클릭
            transcript_selectors = [
                'text="스크립트 보기"',
                'text="Show transcript"',
                'text="Transcript"',
                'yt-formatted-string:has-text("스크립트")',
                'yt-formatted-string:has-text("Transcript")'
            ]
            
            await asyncio.sleep(1)  # 메뉴 로드 대기
            
            for selector in transcript_selectors:
                try:
                    await self.page.click(selector, timeout=5000)
                    logger.info(f"✅ Clicked transcript menu: {selector}")
                    
                    # 스크립트 패널이 열릴 때까지 대기
                    await self.page.wait_for_selector('ytd-transcript-renderer', timeout=10000)
                    logger.info("✅ Transcript panel opened")
                    return True
                    
                except Exception as e:
                    logger.debug(f"Failed to click {selector}: {e}")
                    continue
            
            logger.warning("⚠️ Could not open transcript panel")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error opening transcript panel: {e}")
            return False
    
    async def extract_transcript_content(self) -> Optional[str]:
        """스크립트 내용 추출"""
        try:
            # 스크립트 항목들 대기
            await self.page.wait_for_selector('ytd-transcript-segment-renderer', timeout=10000)
            
            # 모든 스크립트 세그먼트 가져오기
            segments = await self.page.query_selector_all('ytd-transcript-segment-renderer')
            
            if not segments:
                logger.warning("⚠️ No transcript segments found")
                return None
            
            transcript_texts = []
            
            for segment in segments:
                try:
                    # 텍스트 추출
                    text_element = await segment.query_selector('yt-formatted-string')
                    if text_element:
                        text = await text_element.inner_text()
                        if text and text.strip():
                            transcript_texts.append(text.strip())
                except Exception as e:
                    logger.debug(f"Error extracting segment text: {e}")
                    continue
            
            if transcript_texts:
                full_transcript = ' '.join(transcript_texts)
                logger.info(f"✅ Extracted {len(transcript_texts)} segments, {len(full_transcript)} characters")
                return full_transcript
            else:
                logger.warning("⚠️ No transcript text found")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error extracting transcript content: {e}")
            return None
    
    async def get_transcript_with_timestamps(self) -> Optional[List[Dict]]:
        """타임스탬프와 함께 스크립트 추출"""
        try:
            await self.page.wait_for_selector('ytd-transcript-segment-renderer', timeout=10000)
            segments = await self.page.query_selector_all('ytd-transcript-segment-renderer')
            
            transcript_data = []
            
            for segment in segments:
                try:
                    # 타임스탬프 추출
                    timestamp_element = await segment.query_selector('.ytd-transcript-segment-renderer[role="button"]')
                    timestamp = None
                    if timestamp_element:
                        timestamp_text = await timestamp_element.get_attribute('aria-label')
                        if timestamp_text:
                            # "X분 Y초" 형식에서 시간 추출
                            time_match = re.search(r'(\d+)분\s*(\d+)초', timestamp_text)
                            if time_match:
                                minutes, seconds = int(time_match.group(1)), int(time_match.group(2))
                                timestamp = minutes * 60 + seconds
                    
                    # 텍스트 추출
                    text_element = await segment.query_selector('yt-formatted-string')
                    text = None
                    if text_element:
                        text = await text_element.inner_text()
                    
                    if text and text.strip():
                        transcript_data.append({
                            'timestamp': timestamp,
                            'text': text.strip()
                        })
                        
                except Exception as e:
                    logger.debug(f"Error processing segment: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(transcript_data)} segments with timestamps")
            return transcript_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting transcript with timestamps: {e}")
            return None
    
    async def scrape_youtube_transcript(self, video_url: str) -> Optional[str]:
        """YouTube 스크립트 크롤링 메인 메서드"""
        video_id = self.extract_video_id(video_url)
        if not video_id:
            logger.error(f"❌ Could not extract video ID from: {video_url}")
            return None
        
        logger.info(f"🎬 Scraping transcript for video: {video_id}")
        
        try:
            # YouTube 페이지 방문
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            await self.page.goto(youtube_url, wait_until='domcontentloaded', timeout=30000)
            logger.info(f"✅ Loaded YouTube page: {youtube_url}")
            
            # 콘텐츠 로드 대기
            if not await self.wait_for_content_load():
                logger.warning("⚠️ Content loading may be incomplete")
            
            # 스크립트 패널 열기
            if not await self.open_transcript_panel():
                logger.error("❌ Failed to open transcript panel")
                return None
            
            # 스크립트 내용 추출
            transcript = await self.extract_transcript_content()
            
            if transcript:
                logger.info(f"✅ Successfully scraped transcript: {len(transcript)} characters")
                return transcript
            else:
                logger.error("❌ Failed to extract transcript content")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            return None


# 편의 함수
async def scrape_youtube_transcript(video_url: str, headless: bool = True) -> Optional[str]:
    """YouTube 스크립트 크롤링 편의 함수"""
    async with PlaywrightYouTubeScraper(headless=headless) as scraper:
        return await scraper.scrape_youtube_transcript(video_url)


# 테스트 코드
if __name__ == "__main__":
    async def test_scraper():
        # 수업 비디오 테스트
        video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
        
        print(f"🎬 Testing Playwright scraper for: {video_url}")
        
        try:
            transcript = await scrape_youtube_transcript(video_url, headless=False)
            
            if transcript:
                print(f"✅ Success! Extracted {len(transcript)} characters")
                print(f"📝 Preview: {transcript[:300]}...")
                
                # 파일로 저장
                with open('scraped_transcript.txt', 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print("💾 Saved to scraped_transcript.txt")
                
            else:
                print("❌ Failed to scrape transcript")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # 테스트 실행
    asyncio.run(test_scraper())