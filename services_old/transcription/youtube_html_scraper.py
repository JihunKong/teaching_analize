"""
YouTube HTML Scraper for "스크립트 보기" transcripts
실제 YouTube DOM에서 transcript 버튼을 누른 후 나타나는 텍스트를 스크래핑
"""
import re
import time
import logging
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class YouTubeHTMLScraper:
    """YouTube HTML 스크래핑을 통한 실제 전사 추출"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Selenium WebDriver 설정 (봇 차단 우회 설정 포함)"""
        if self.driver:
            return
            
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
            
        # 봇 차단 우회 설정
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 실제 사용자 브라우저처럼 보이도록 설정
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--lang=ko-KR')
        chrome_options.add_argument('--accept-language=ko-KR,ko,en-US,en')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # 봇 감지 방지 스크립트
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome WebDriver 초기화 완료")
            
        except Exception as e:
            logger.error(f"WebDriver 설정 실패: {e}")
            raise
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """YouTube URL에서 비디오 ID 추출"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def parse_timestamp(self, timestamp_str: str) -> float:
        """타임스탬프 문자열을 초 단위로 변환 (예: "0:07" -> 7.0)"""
        try:
            parts = timestamp_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            else:
                return 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def scrape_transcript_from_html(self, youtube_url: str, language: str = 'ko') -> Optional[Dict]:
        """
        실제 YouTube 페이지에서 "스크립트 보기" 버튼을 클릭하여 전사 추출
        
        Args:
            youtube_url: YouTube 비디오 URL
            language: 언어 코드
            
        Returns:
            전사 데이터 또는 None
        """
        video_id = self.extract_video_id(youtube_url)
        if not video_id:
            logger.error(f"비디오 ID 추출 실패: {youtube_url}")
            return None
        
        try:
            self.setup_driver()
            
            # YouTube 페이지 로드
            logger.info(f"YouTube 페이지 로딩: {youtube_url}")
            self.driver.get(youtube_url)
            
            # 페이지 로딩 대기
            time.sleep(3)
            
            # 동의 버튼이 있다면 클릭
            try:
                consent_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '모두 수락') or contains(text(), 'Accept all')]"))
                )
                consent_button.click()
                time.sleep(2)
                logger.info("쿠키 동의 완료")
            except TimeoutException:
                logger.info("쿠키 동의 버튼 없음 또는 이미 동의됨")
            
            # 비디오가 로드될 때까지 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
            )
            
            # 더보기 메뉴 버튼 찾기 (점 3개 버튼)
            more_menu_selectors = [
                "button[aria-label*='더보기']",
                "button[aria-label*='More actions']", 
                "yt-icon-button#button.ytd-menu-renderer",
                ".ytd-video-primary-info-renderer .ytd-menu-renderer yt-icon-button"
            ]
            
            more_button = None
            for selector in more_menu_selectors:
                try:
                    more_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except TimeoutException:
                    continue
                    
            if not more_button:
                logger.error("더보기 메뉴 버튼을 찾을 수 없습니다")
                return None
                
            # 더보기 메뉴 클릭
            logger.info("더보기 메뉴 클릭")
            more_button.click()
            time.sleep(2)
            
            # "스크립트 보기" 또는 "Show transcript" 메뉴 항목 찾기
            transcript_selectors = [
                "//span[contains(text(), '스크립트 보기')]",
                "//span[contains(text(), 'Show transcript')]",
                "//yt-formatted-string[contains(text(), '스크립트 보기')]",
                "//yt-formatted-string[contains(text(), 'Show transcript')]"
            ]
            
            transcript_button = None
            for selector in transcript_selectors:
                try:
                    transcript_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not transcript_button:
                logger.error("스크립트 보기 버튼을 찾을 수 없습니다")
                return None
                
            # 스크립트 보기 클릭
            logger.info("스크립트 보기 버튼 클릭")
            transcript_button.click()
            time.sleep(3)
            
            # 전사 패널이 나타날 때까지 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ytd-transcript-segment-renderer"))
            )
            
            # 전사 세그먼트들 추출
            segments = []
            segment_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ytd-transcript-segment-renderer")
            
            logger.info(f"찾은 전사 세그먼트 수: {len(segment_elements)}")
            
            for element in segment_elements:
                try:
                    # 타임스탬프 추출
                    timestamp_element = element.find_element(By.CSS_SELECTOR, ".segment-timestamp")
                    timestamp_str = timestamp_element.text.strip()
                    start_time = self.parse_timestamp(timestamp_str)
                    
                    # 텍스트 추출
                    text_element = element.find_element(By.CSS_SELECTOR, ".segment-text")
                    text = text_element.text.strip()
                    
                    if text:  # 빈 텍스트가 아닌 경우만 추가
                        segments.append({
                            "start": start_time,
                            "duration": 5.0,  # 기본 지속시간 (YouTube에서 정확한 duration은 제공하지 않음)
                            "text": text
                        })
                        
                except (NoSuchElementException, AttributeError) as e:
                    logger.warning(f"세그먼트 파싱 실패: {e}")
                    continue
            
            if not segments:
                logger.warning("추출된 전사 세그먼트가 없습니다")
                return None
            
            # 전체 텍스트 생성
            full_text = " ".join([segment["text"] for segment in segments])
            
            # 비디오 제목 추출
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, "h1.ytd-watch-metadata yt-formatted-string")
                title = title_element.text.strip()
            except NoSuchElementException:
                title = f"YouTube Video {video_id}"
            
            result = {
                "text": full_text,
                "segments": segments,
                "language": "한국어" if language == 'ko' else "English",
                "language_code": language,
                "is_generated": True,  # YouTube 자동 생성 자막으로 가정
                "is_translatable": True,
                "video_id": video_id,
                "title": title,
                "extraction_method": "html_scraping"
            }
            
            logger.info(f"HTML 스크래핑 성공: {len(segments)}개 세그먼트, 전체 텍스트 길이: {len(full_text)}")
            return result
            
        except Exception as e:
            logger.error(f"HTML 스크래핑 실패: {e}")
            return None
            
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def __del__(self):
        """소멸자에서 WebDriver 정리"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass


def get_youtube_transcript_html_scraping(url: str, language: str = "ko") -> Optional[Dict]:
    """
    HTML 스크래핑을 통한 YouTube 전사 추출 (main entry point)
    
    Args:
        url: YouTube 비디오 URL
        language: 언어 코드
        
    Returns:
        전사 데이터 또는 None
    """
    scraper = YouTubeHTMLScraper(headless=True)
    return scraper.scrape_transcript_from_html(url, language)


if __name__ == "__main__":
    # 테스트 코드
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = get_youtube_transcript_html_scraping(test_url, "ko")
    
    if result:
        print(f"✅ 스크래핑 성공!")
        print(f"제목: {result['title']}")
        print(f"전체 텍스트: {result['text'][:200]}...")
        print(f"세그먼트 수: {len(result['segments'])}")
    else:
        print("❌ 스크래핑 실패")