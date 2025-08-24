#!/usr/bin/env python3
"""
Selenium YouTube Script Scraper
YouTube의 스크립트 보기 기능을 Selenium으로 크롤링
"""

import time
import logging
import re
from typing import Optional, List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class SeleniumYouTubeScraper:
    """Selenium을 사용한 YouTube 스크립트 크롤링"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.wait = None
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.quit_driver()
    
    def start_driver(self):
        """Chrome WebDriver 시작"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless=new')
            
            # 안정성 및 성능 최적화 옵션들
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            
            # 성능 최적화 옵션들
            chrome_options.add_argument('--disable-images')  # 이미지 로딩 비활성화
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-ipc-flooding-protection')
            
            # 메모리 사용량 최적화
            chrome_options.add_argument('--memory-pressure-off')
            chrome_options.add_argument('--max_old_space_size=2048')
            
            # 브라우저 감지 방지
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User-Agent 설정
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            
            # 창 크기 설정 (스크립트 패널을 위해) - 빠른 로딩을 위해 작게 설정
            chrome_options.add_argument('--window-size=1366,768')  # 1920x1080에서 더 작게
            
            # Docker 환경에서는 시스템 chromium-driver 사용
            import os
            if os.path.exists('/usr/bin/chromedriver'):
                # Docker 환경 (Debian/Ubuntu)
                service = Service('/usr/bin/chromedriver')
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            elif os.path.exists('/usr/local/bin/chromedriver'):
                # 로컬 환경
                service = Service('/usr/local/bin/chromedriver')
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # WebDriver Manager를 사용하여 자동으로 ChromeDriver 설치/관리
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)
            
            # webdriver 감지 방지 스크립트
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome driver started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Chrome driver: {e}")
            raise
    
    def quit_driver(self):
        """WebDriver 종료"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Chrome driver closed")
        except Exception as e:
            logger.error(f"❌ Error closing driver: {e}")
    
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
        
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def wait_for_ads_to_finish(self) -> bool:
        """광고 종료 대기 및 스킵 - 최적화된 버전"""
        try:
            logger.info("⏳ Quick ad check...")
            
            # 광고 스킵 버튼 대기 (최대 5초로 단축)
            skip_selectors = [
                ".ytp-ad-skip-button",
                ".ytp-skip-ad-button", 
                "button.ytp-ad-skip-button-modern"
            ]
            
            for _ in range(5):  # 5초로 단축
                for selector in skip_selectors:
                    try:
                        skip_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if skip_button.is_displayed() and skip_button.is_enabled():
                            skip_button.click()
                            logger.info("✅ Skipped ad")
                            return True
                    except:
                        continue
                
                # 광고가 없는지 빠른 확인
                try:
                    ad_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ytp-ad-player-overlay, .ytp-ad-module")
                    if not ad_elements:
                        logger.info("✅ No ads detected")
                        return True
                except:
                    pass
                
                time.sleep(0.5)  # 1초에서 0.5초로 단축
            
            logger.info("⏰ Ad check complete - proceeding")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Ad handling error: {e}")
            return True

    def wait_for_video_ready(self) -> bool:
        """비디오 준비 상태 대기 - 최적화된 버전"""
        try:
            logger.info("🎬 Quick video ready check...")
            
            # 비디오 플레이어 대기 (단축된 타임아웃)
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            except TimeoutException:
                logger.warning("⚠️ Video element not found quickly")
            
            # 플레이어 컨트롤 대기 (첫 번째 발견되는 것만)
            control_selectors = [
                ".ytp-chrome-controls",
                ".ytp-right-controls", 
                "#menu"
            ]
            
            for selector in control_selectors:
                try:
                    WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"✅ Found controls: {selector}")
                    break
                except TimeoutException:
                    continue
            
            # 안정화 시간 대폭 단축
            time.sleep(1)  # 3초에서 1초로 단축
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error waiting for video: {e}")
            return False

    def load_youtube_page(self, video_id: str) -> bool:
        """YouTube 페이지 로드 - 광고 처리 포함"""
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            self.driver.get(youtube_url)
            logger.info(f"✅ Loaded YouTube page: {youtube_url}")
            
            # 기본 페이지 로드 대기
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            logger.info("✅ Video player found")
            
            # 광고 처리
            if not self.wait_for_ads_to_finish():
                logger.warning("⚠️ Ad handling may have failed")
            
            # 비디오 준비 상태 대기
            if not self.wait_for_video_ready():
                logger.warning("⚠️ Video ready check failed")
            
            return True
            
        except TimeoutException:
            logger.error("❌ Timeout waiting for video player")
            return False
        except Exception as e:
            logger.error(f"❌ Error loading YouTube page: {e}")
            return False
    
    def debug_menu_contents(self):
        """메뉴 내용 디버깅"""
        try:
            logger.info("🔍 Debugging menu contents...")
            
            # 모든 메뉴 항목 찾기
            menu_items = self.driver.find_elements(By.CSS_SELECTOR, "[role='menuitem'], ytd-menu-service-item-renderer, button")
            logger.info(f"📋 Found {len(menu_items)} potential menu items")
            
            for i, item in enumerate(menu_items[:10]):  # 첫 10개만 로깅
                try:
                    text = item.text.strip()
                    aria_label = item.get_attribute('aria-label') or ''
                    class_name = item.get_attribute('class') or ''
                    
                    if text or aria_label:  # 빈 요소 제외
                        logger.info(f"🔸 Menu item {i}: text='{text}', aria-label='{aria_label}', class='{class_name[:50]}...'")
                except Exception as e:
                    logger.debug(f"Error examining menu item {i}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error debugging menu: {e}")
    
    def find_transcript_button(self):
        """다양한 방법으로 스크립트 버튼 찾기"""
        # CSS 셀렉터들
        css_selectors = [
            "button[aria-label*='transcript' i]",
            "button[aria-label*='자막']",
            "[role='menuitem'][aria-label*='transcript' i]",
            "ytd-menu-service-item-renderer:has(yt-formatted-string)",
            "button:has(yt-formatted-string)",
            "[aria-label*='Show transcript']",
            "[aria-label*='Transcript']"
        ]
        
        # XPath 셀렉터들  
        xpath_selectors = [
            "//button[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'transcript')]",
            "//button[contains(@aria-label, '자막')]",
            "//div[@role='menu']//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'transcript')]",
            "//*[@role='menuitem']//yt-formatted-string[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'transcript')]",
            "//yt-formatted-string[contains(text(), '스크립트')]",
            "//yt-formatted-string[contains(text(), 'Show transcript')]",
            "//yt-formatted-string[contains(text(), 'Transcript')]",
            "//*[contains(text(), '스크립트 보기')]",
            "//*[contains(text(), 'Show transcript')]"
        ]
        
        # CSS 셀렉터 시도
        for selector in css_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed() and element.is_enabled():
                    logger.info(f"✅ Found transcript button with CSS selector: {selector}")
                    return element
            except NoSuchElementException:
                continue
        
        # XPath 셀렉터 시도
        for selector in xpath_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed() and element.is_enabled():
                    logger.info(f"✅ Found transcript button with XPath selector: {selector}")
                    return element
            except NoSuchElementException:
                continue
        
        return None
    
    def find_transcript_by_text(self):
        """텍스트 내용으로 스크립트 버튼 찾기"""
        possible_texts = [
            'transcript', 'Transcript', 'TRANSCRIPT',
            '스크립트', '자막', '대본',
            'Show transcript', 'Open transcript',
            'Transcript 보기', '자막 보기'
        ]
        
        # 모든 클릭 가능한 요소에서 텍스트 검색
        clickable_elements = self.driver.find_elements(By.CSS_SELECTOR, "button, [role='menuitem'], a, ytd-menu-service-item-renderer")
        
        for element in clickable_elements:
            try:
                element_text = element.text.strip().lower()
                aria_label = (element.get_attribute('aria-label') or '').lower()
                
                for text in possible_texts:
                    if text.lower() in element_text or text.lower() in aria_label:
                        if element.is_displayed() and element.is_enabled():
                            logger.info(f"✅ Found transcript by text: '{element.text}' / '{element.get_attribute('aria-label')}'")
                            return element
            except Exception as e:
                continue
        
        return None
    
    def wait_for_transcript_panel(self, timeout=15):
        """스크립트 패널 로드 대기 - 사용자 제공 정보 기반"""
        panel_selectors = [
            # 사용자가 확인한 정확한 셀렉터
            "ytd-transcript-search-panel-renderer",
            "ytd-transcript-search-panel-renderer.style-scope.ytd-transcript-renderer",
            
            # 기존 셀렉터들
            "ytd-transcript-renderer",
            "ytd-engagement-panel-section-list-renderer[target-id='engagement-panel-transcript']",
            "[aria-label*='transcript']",
            ".ytd-transcript-renderer",
            "#transcript"
        ]
        
        for selector in panel_selectors:
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                logger.info(f"✅ Transcript panel opened with selector: {selector}")
                return True
            except TimeoutException:
                continue
        
        logger.error("❌ Transcript panel did not load")
        return False

    def find_more_actions_button(self) -> any:
        """더보기 버튼 찾기 - 사용자 제공 정보 기반 개선"""
        more_button_selectors = [
            # 사용자가 확인한 정확한 셀렉터
            "tp-yt-paper-button#expand",
            "tp-yt-paper-button[id='expand']",
            "#expand.button.style-scope.ytd-text-inline-expander",
            "tp-yt-paper-button.button.style-scope.ytd-text-inline-expander",
            
            # 더보기 텍스트로 찾기
            "tp-yt-paper-button:contains('더보기')",
            "tp-yt-paper-button:contains('...더보기')",
            "button:contains('더보기')",
            "button:contains('...더보기')",
            
            # 기존 더보기 버튼 패턴들
            "button[aria-label*='더보기']",
            "button[aria-label*='More actions']", 
            "button[aria-label*='Show more']",
            "#menu button",
            "ytd-menu-renderer button",
            
            # 새로운 YouTube UI 패턴
            "button.yt-spec-button-shape-next[aria-label*='More']",
            "yt-button-shape button[aria-label*='More']",
            "#top-level-buttons #menu button",
            ".ytd-menu-renderer button",
            
            # 비디오 플레이어 내부 버튼들
            ".ytp-right-controls button",
            "button[title*='More']",
            "button[title*='더보기']"
        ]
        
        for selector in more_button_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # 버튼의 위치가 화면 내에 있는지 확인
                        location = element.location
                        if location['x'] >= 0 and location['y'] >= 0:
                            # 텍스트 내용도 확인
                            button_text = element.text.strip().lower()
                            if '더보기' in button_text or 'more' in button_text or selector.startswith('tp-yt-paper-button'):
                                logger.info(f"✅ Found more button with selector: {selector}, text: '{element.text}'")
                                return element
                            elif not button_text:  # 텍스트가 없는 경우도 시도
                                logger.info(f"✅ Found more button with selector: {selector} (no text)")
                                return element
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # 텍스트 기반으로 추가 검색
        try:
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in all_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.strip()
                        if '더보기' in button_text or '...더보기' in button_text:
                            logger.info(f"✅ Found more button by text: '{button_text}'")
                            return button
                except:
                    continue
        except Exception as e:
            logger.debug(f"Text-based search failed: {e}")
        
        # tp-yt-paper-button 요소들 전체 검색
        try:
            paper_buttons = self.driver.find_elements(By.TAG_NAME, "tp-yt-paper-button")
            for button in paper_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.strip()
                        button_id = button.get_attribute('id') or ''
                        if '더보기' in button_text or 'expand' in button_id.lower():
                            logger.info(f"✅ Found tp-yt-paper-button: id='{button_id}', text='{button_text}'")
                            return button
                except:
                    continue
        except Exception as e:
            logger.debug(f"tp-yt-paper-button search failed: {e}")
        
        return None

    def ensure_menu_is_open(self) -> bool:
        """메뉴가 열려있는지 확인하고 열기"""
        try:
            # 메뉴가 이미 열려있는지 확인
            menu_indicators = [
                "ytd-menu-popup-renderer",
                ".ytp-popup.ytp-contextmenu",
                "ytd-menu-service-item-renderer",
                "[role='menu']"
            ]
            
            for indicator in menu_indicators:
                try:
                    menu_element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    if menu_element.is_displayed():
                        logger.info(f"✅ Menu already open: {indicator}")
                        return True
                except:
                    continue
            
            logger.info("📋 Menu not open, attempting to open...")
            return False
            
        except Exception as e:
            logger.debug(f"Menu check error: {e}")
            return False

    def open_transcript_panel(self) -> bool:
        """스크립트 패널 열기 - TRANSCRIPT 전용 (자막 CC 아님)"""
        try:
            logger.info("🔍 Looking for YouTube TRANSCRIPT button (not CC/captions)...")
            
            # 1단계: 직접 스크립트 버튼 찾기
            transcript_button = self.find_transcript_button()
            if transcript_button:
                try:
                    transcript_button.click()
                    logger.info("✅ Clicked direct transcript button")
                    return self.wait_for_transcript_panel()
                except:
                    logger.info("⚠️ Direct transcript button click failed, trying menu approach")
            
            # 2단계: 메뉴 접근 방식
            # 메뉴가 이미 열려있는지 확인
            if self.ensure_menu_is_open():
                logger.info("📋 Menu already open, proceeding to find transcript")
            else:
                # 더보기 버튼 찾기 및 클릭
                more_button = self.find_more_actions_button()
                
                if not more_button:
                    # 화면을 스크롤해서 버튼을 찾아보기
                    logger.info("🔄 Scrolling to find more button...")
                    self.driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(0.5)  # 2초에서 0.5초로 단축
                    more_button = self.find_more_actions_button()
                
                if not more_button:
                    logger.error("❌ Could not find more actions button")
                    return False
                
                # 더보기 버튼으로 스크롤 - 최적화
                self.driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                time.sleep(0.3)  # 1초에서 0.3초로 단축
                
                # 더보기 버튼 클릭 (여러 방법 시도)
                try:
                    more_button.click()
                    logger.info("✅ Clicked more actions button (normal click)")
                except:
                    try:
                        self.driver.execute_script("arguments[0].click();", more_button)
                        logger.info("✅ Clicked more actions button (JS click)")
                    except Exception as e:
                        logger.error(f"❌ Failed to click more button: {e}")
                        return False
                
                # 메뉴 로드 동적 대기 - 최적화됨
                logger.info("⏳ Waiting for menu to load dynamically...")
                try:
                    # 메뉴 항목이 실제로 로드될 때까지 대기 (최대 3초)
                    WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 
                            "[role='menuitem'], ytd-menu-service-item-renderer, button"))
                    )
                    logger.info("✅ Menu loaded dynamically")
                except TimeoutException:
                    logger.warning("⚠️ Menu load timeout - proceeding anyway")
                    time.sleep(1)  # 최소한의 대기
            
            # 3단계: 메뉴 내에서 스크립트 찾기
            self.debug_menu_contents()
            
            # 스크립트 버튼 찾기 - TRANSCRIPT ONLY
            transcript_button = self.find_transcript_button()
            
            if not transcript_button:
                # 텍스트 기반 fallback 검색
                logger.info("🔄 Trying text-based transcript search (not captions)...")
                transcript_button = self.find_transcript_by_text()
            
            if not transcript_button:
                logger.error("❌ Could not find YouTube TRANSCRIPT button (auto-generated transcripts should always be available)")
                return False
            
            # 4단계: 스크립트 버튼 클릭
            try:
                transcript_button.click()
                logger.info("✅ Clicked transcript button (normal click)")
            except:
                self.driver.execute_script("arguments[0].click();", transcript_button)
                logger.info("✅ Clicked transcript button (JS click)")
            
            # 5단계: 스크립트 패널 로드 대기
            return self.wait_for_transcript_panel()
                
        except Exception as e:
            logger.error(f"❌ Error opening YouTube transcript panel: {e}")
            logger.info("NOTE: Looking for TRANSCRIPT (auto-generated), not captions/subtitles")
            return False
    
    def scroll_transcript_panel_to_load_all(self) -> bool:
        """스크립트 패널을 끝까지 스크롤하여 모든 세그먼트 로드 - 개선된 버전"""
        try:
            logger.info("📜 Loading all transcript segments by scrolling...")
            
            # 다양한 패널 컨테이너 셀렉터 시도
            container_selectors = [
                "ytd-transcript-renderer",
                ".ytd-transcript-renderer",
                "#contents.ytd-transcript-renderer",
                "[aria-label*='transcript'] [role='region']"
            ]
            
            transcript_container = None
            for selector in container_selectors:
                try:
                    transcript_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"✅ Found transcript container: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not transcript_container:
                logger.warning("⚠️ Could not find transcript container for scrolling")
                return True  # 스크롤 없이 계속 진행
            
            # 세그먼트 셀렉터들
            segment_selectors = [
                "ytd-transcript-segment-renderer",
                ".ytd-transcript-segment-renderer",
                "[class*='transcript-segment']"
            ]
            
            last_count = 0
            retry_count = 0
            max_retries = 5
            scroll_attempts = 0
            max_scroll_attempts = 20
            
            while retry_count < max_retries and scroll_attempts < max_scroll_attempts:
                # 현재 세그먼트 수 확인
                current_count = 0
                for selector in segment_selectors:
                    segments = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if segments:
                        current_count = len(segments)
                        break
                
                # 다양한 스크롤 방법 시도
                scroll_methods = [
                    # 1. 컨테이너 내부 스크롤
                    """
                    var container = arguments[0];
                    container.scrollTop = container.scrollHeight;
                    """,
                    # 2. 페이지 전체 스크롤 (패널이 고정되지 않은 경우)
                    "window.scrollTo(0, document.body.scrollHeight);",
                    # 3. 키보드 이벤트로 스크롤
                    """
                    var container = arguments[0];
                    container.focus();
                    var event = new KeyboardEvent('keydown', { key: 'End' });
                    container.dispatchEvent(event);
                    """
                ]
                
                for method in scroll_methods:
                    try:
                        if "arguments[0]" in method:
                            self.driver.execute_script(method, transcript_container)
                        else:
                            self.driver.execute_script(method)
                        time.sleep(0.3)  # 스크롤 간 대기 시간 단축
                    except:
                        continue
                
                # 새 콘텐츠 로드 대기 - 최적화
                time.sleep(1)  # 3초에서 1초로 단축
                scroll_attempts += 1
                
                # 새로운 세그먼트 수 확인
                new_count = 0
                for selector in segment_selectors:
                    segments = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if segments:
                        new_count = len(segments)
                        break
                
                logger.info(f"📊 Scroll {scroll_attempts}: Segments {current_count} → {new_count}")
                
                # 더 이상 새로운 세그먼트가 로드되지 않으면 완료
                if new_count == current_count:
                    retry_count += 1
                    logger.info(f"🔄 No new segments, retry {retry_count}/{max_retries}")
                else:
                    retry_count = 0  # 새 콘텐츠가 로드되면 재시도 카운터 리셋
                    last_count = new_count
                
                # 50분 영상 기준으로 대략 300-500개 세그먼트 예상
                if new_count > 500:
                    logger.info("📈 Sufficient segments loaded, stopping scroll")
                    break
                
                # 최소한 몇 개의 세그먼트가 있으면 계속 진행
                if new_count > 10 and retry_count >= max_retries:
                    logger.info(f"📝 Found {new_count} segments, proceeding...")
                    break
            
            # 최종 세그먼트 수 확인
            final_count = 0
            for selector in segment_selectors:
                segments = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if segments:
                    final_count = len(segments)
                    break
            
            logger.info(f"✅ Final segments loaded: {final_count}")
            return final_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error scrolling transcript panel: {e}")
            return True  # 스크롤 실패해도 세그먼트 추출 시도
    
    def extract_transcript_segments(self) -> List[Dict]:
        """스크립트 세그먼트들 추출 (전체 로드 후) - 개선된 버전"""
        try:
            logger.info("🔍 Looking for transcript segments...")
            
            # 다양한 세그먼트 셀렉터 시도 - 사용자 정보 기반 개선
            segment_selectors = [
                # 스크린샷에서 확인된 패널 하위의 세그먼트들
                "ytd-transcript-search-panel-renderer ytd-transcript-segment-renderer",
                "ytd-transcript-search-panel-renderer [class*='segment']",
                "ytd-transcript-search-panel-renderer [class*='transcript']",
                
                # 기존 셀렉터들
                "ytd-transcript-segment-renderer",
                ".ytd-transcript-segment-renderer", 
                "[class*='transcript-segment']",
                ".segment-text",
                "[role='button'][class*='transcript']"
            ]
            
            segments = []
            for selector in segment_selectors:
                try:
                    # 더 짧은 대기 시간으로 시도
                    WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    segments = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if segments:
                        logger.info(f"✅ Found {len(segments)} segments with selector: {selector}")
                        break
                except TimeoutException:
                    logger.debug(f"Selector {selector} not found")
                    continue
            
            # 세그먼트가 없으면 패널 내용 디버깅
            if not segments:
                logger.warning("⚠️ No transcript segments found, debugging panel content...")
                self.debug_transcript_panel()
                
                # 대체 방법: 모든 클릭 가능한 요소에서 텍스트 추출
                transcript_text = self.extract_transcript_text_fallback()
                if transcript_text:
                    return [{'timestamp': None, 'text': transcript_text}]
                
                return []
            
            # 전체 스크립트 로드
            if not self.scroll_transcript_panel_to_load_all():
                logger.warning("⚠️ Failed to load all transcript segments")
            
            transcript_data = []
            logger.info(f"🔍 Processing {len(segments)} segments...")
            
            for i, segment in enumerate(segments):
                try:
                    # 진행률 표시 (매 50개마다)
                    if i % 50 == 0:
                        logger.info(f"📝 Processing segment {i+1}/{len(segments)}")
                    
                    # 타임스탬프 추출 - 다양한 방법
                    timestamp = None
                    timestamp_selectors = [
                        ".ytd-transcript-segment-renderer",
                        "[data-start-ms]",
                        ".timestamp",
                        "[class*='time']"
                    ]
                    
                    for ts_selector in timestamp_selectors:
                        try:
                            timestamp_element = segment.find_element(By.CSS_SELECTOR, ts_selector)
                            
                            # data-start-ms 속성에서 추출
                            start_ms = timestamp_element.get_attribute("data-start-ms")
                            if start_ms:
                                timestamp = int(start_ms) // 1000
                                break
                            
                            # aria-label에서 추출
                            aria_label = timestamp_element.get_attribute("aria-label")
                            if aria_label:
                                # "X분 Y초에서..." 형식에서 시간 추출
                                time_patterns = [
                                    r'(\d+)분\s*(\d+)초',
                                    r'(\d+):(\d+)',
                                    r'(\d+)m\s*(\d+)s'
                                ]
                                for pattern in time_patterns:
                                    time_match = re.search(pattern, aria_label)
                                    if time_match:
                                        minutes, seconds = int(time_match.group(1)), int(time_match.group(2))
                                        timestamp = minutes * 60 + seconds
                                        break
                                if timestamp:
                                    break
                        except NoSuchElementException:
                            continue
                    
                    # 텍스트 추출 - 다양한 방법
                    text = None
                    text_selectors = [
                        "yt-formatted-string",
                        ".segment-text",
                        "[class*='text']",
                        "span",
                        "div"
                    ]
                    
                    for text_selector in text_selectors:
                        try:
                            text_element = segment.find_element(By.CSS_SELECTOR, text_selector)
                            text = text_element.text.strip()
                            if text and len(text) > 5:  # 의미있는 텍스트만
                                break
                        except NoSuchElementException:
                            continue
                    
                    # 직접 텍스트 추출 fallback
                    if not text:
                        text = segment.text.strip()
                    
                    if text and len(text) > 2:
                        transcript_data.append({
                            'timestamp': timestamp,
                            'text': text
                        })
                        
                except Exception as e:
                    logger.debug(f"Error processing segment {i}: {e}")
                    continue
            
            logger.info(f"✅ Extracted {len(transcript_data)} transcript segments")
            return transcript_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting transcript segments: {e}")
            # 마지막 fallback 시도
            transcript_text = self.extract_transcript_text_fallback()
            if transcript_text:
                return [{'timestamp': None, 'text': transcript_text}]
            return []
    
    def debug_transcript_panel(self):
        """스크립트 패널 내용 디버깅"""
        try:
            logger.info("🔍 Debugging transcript panel contents...")
            
            # 패널 내의 모든 요소 찾기
            panel_elements = self.driver.find_elements(By.CSS_SELECTOR, "ytd-transcript-renderer *")
            logger.info(f"📋 Found {len(panel_elements)} elements in transcript panel")
            
            # 텍스트가 있는 요소들만 로깅
            text_elements = []
            for element in panel_elements[:20]:  # 첫 20개만 검사
                try:
                    text = element.text.strip()
                    tag_name = element.tag_name
                    class_name = element.get_attribute('class') or ''
                    
                    if text and len(text) > 3:
                        text_elements.append({
                            'tag': tag_name,
                            'class': class_name[:50],
                            'text': text[:100]
                        })
                except:
                    continue
            
            logger.info(f"📝 Found {len(text_elements)} text elements:")
            for i, elem in enumerate(text_elements[:10]):
                logger.info(f"  {i+1}. <{elem['tag']} class='{elem['class']}...'>{elem['text']}...</>")
                
        except Exception as e:
            logger.error(f"❌ Error debugging transcript panel: {e}")
    
    def extract_transcript_text_fallback(self) -> Optional[str]:
        """대체 방법으로 전체 스크립트 텍스트 추출"""
        try:
            logger.info("🔄 Trying fallback text extraction...")
            
            # 스크립트 패널에서 모든 텍스트 추출 - 사용자 정보 기반
            panel_selectors = [
                # 사용자가 확인한 정확한 패널
                "ytd-transcript-search-panel-renderer",
                "ytd-transcript-search-panel-renderer.style-scope.ytd-transcript-renderer",
                
                # 기존 셀렉터들
                "ytd-transcript-renderer",
                "[aria-label*='transcript']",
                ".ytd-transcript-renderer"
            ]
            
            for selector in panel_selectors:
                try:
                    panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                    full_text = panel.text.strip()
                    
                    if full_text and len(full_text) > 50:
                        # 불필요한 UI 텍스트 제거
                        lines = full_text.split('\n')
                        cleaned_lines = []
                        
                        for line in lines:
                            line = line.strip()
                            # 시간 정보나 의미있는 텍스트만 유지
                            if (line and 
                                len(line) > 3 and 
                                not line.lower() in ['transcript', 'show transcript', '스크립트', '자막'] and
                                not line.startswith('0:') and  # 시간 정보 제외 (별도로 처리)
                                not re.match(r'^\d+:\d+$', line)):
                                cleaned_lines.append(line)
                        
                        if cleaned_lines:
                            result = ' '.join(cleaned_lines)
                            logger.info(f"✅ Fallback extraction successful: {len(result)} characters")
                            return result
                        
                except NoSuchElementException:
                    continue
            
            logger.warning("⚠️ Fallback text extraction failed")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error in fallback text extraction: {e}")
            return None
    
    def scrape_youtube_transcript(self, video_url: str) -> Optional[str]:
        """YouTube 스크립트 크롤링 메인 메서드"""
        video_id = self.extract_video_id(video_url)
        if not video_id:
            logger.error(f"❌ Could not extract video ID from: {video_url}")
            return None
        
        logger.info(f"🎬 Scraping transcript for video: {video_id}")
        
        try:
            # 1. YouTube 페이지 로드
            if not self.load_youtube_page(video_id):
                return None
            
            # 2. 스크립트 패널 열기
            if not self.open_transcript_panel():
                return None
            
            # 3. 스크립트 세그먼트 추출
            segments = self.extract_transcript_segments()
            
            if not segments:
                logger.error("❌ Failed to extract transcript segments")
                return None
            
            # 4. 텍스트 조합
            full_text = ' '.join([seg['text'] for seg in segments if seg['text']])
            
            logger.info(f"✅ Successfully scraped transcript: {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            return None


# 편의 함수
def scrape_youtube_transcript(video_url: str, headless: bool = True) -> Optional[str]:
    """YouTube 스크립트 크롤링 편의 함수"""
    with SeleniumYouTubeScraper(headless=headless) as scraper:
        return scraper.scrape_youtube_transcript(video_url)


# 테스트 코드
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 수업 비디오 테스트
    video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
    
    print(f"🎬 Testing Selenium scraper for: {video_url}")
    
    try:
        transcript = scrape_youtube_transcript(video_url, headless=False)
        
        if transcript:
            print(f"✅ Success! Extracted {len(transcript)} characters")
            print(f"📝 Preview: {transcript[:300]}...")
            
            # 파일로 저장
            with open('selenium_transcript.txt', 'w', encoding='utf-8') as f:
                f.write(transcript)
            print("💾 Saved to selenium_transcript.txt")
            
        else:
            print("❌ Failed to scrape transcript")
            
    except Exception as e:
        print(f"❌ Error: {e}")