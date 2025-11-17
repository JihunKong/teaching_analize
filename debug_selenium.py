#!/usr/bin/env python3
"""
Debug script to test Selenium YouTube scraping and capture screenshots
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def test_youtube_scraping(url):
    """Test YouTube scraping with screenshots"""

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"Loading YouTube page: {url}")
        driver.get(url)
        time.sleep(5)

        # Take initial screenshot
        driver.save_screenshot('/tmp/youtube_initial.png')
        print("Screenshot saved: /tmp/youtube_initial.png")

        # Wait for video
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
        )
        print("Video element found")

        # Try to find expand button
        expand_selectors = [
            "tp-yt-paper-button#expand.button.style-scope.ytd-text-inline-expander",
            "tp-yt-paper-button#expand",
            "button#expand",
            "#expand",
            "ytd-text-inline-expander",
        ]

        for selector in expand_selectors:
            try:
                print(f"\nTrying selector: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Found {len(elements)} elements")
                for i, elem in enumerate(elements[:5]):
                    print(f"  Element {i}: visible={elem.is_displayed()}, enabled={elem.is_enabled()}")
                    try:
                        print(f"    Text: {elem.text[:50]}")
                    except:
                        pass
            except Exception as e:
                print(f"  Error: {e}")

        # Get page source snippet
        page_source = driver.page_source
        print(f"\nPage source length: {len(page_source)}")

        # Search for expand button in source
        if "expand" in page_source.lower():
            print("'expand' found in page source")
            # Find context around expand
            idx = page_source.lower().find("expand")
            print(f"Context: {page_source[max(0,idx-100):idx+100]}")

        # Try to click expand button
        print("\n=== CLICKING EXPAND BUTTON ===")
        expand_button_selector = "tp-yt-paper-button#expand.button.style-scope.ytd-text-inline-expander"
        expand_buttons = driver.find_elements(By.CSS_SELECTOR, expand_button_selector)
        for i, btn in enumerate(expand_buttons):
            if btn.is_displayed() and btn.is_enabled():
                print(f"Clicking visible expand button {i}")
                btn.click()
                time.sleep(3)
                break

        driver.save_screenshot('/tmp/youtube_after_expand.png')
        print("Screenshot saved: /tmp/youtube_after_expand.png")

        # Now search for transcript button
        print("\n=== SEARCHING FOR TRANSCRIPT BUTTON ===")
        transcript_xpaths = [
            "//span[contains(text(), '스크립트 보기')]",
            "//span[contains(text(), 'Show transcript')]",
            "//yt-formatted-string[contains(text(), '스크립트 보기')]",
            "//yt-formatted-string[contains(text(), 'Show transcript')]",
            "//*[contains(text(), 'transcript')]",
            "//*[contains(text(), '스크립트')]"
        ]

        for xpath in transcript_xpaths:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    print(f"\nXPath: {xpath}")
                    print(f"Found {len(elements)} elements")
                    for i, elem in enumerate(elements[:3]):
                        print(f"  Element {i}: visible={elem.is_displayed()}, enabled={elem.is_enabled()}")
                        try:
                            print(f"    Text: {elem.text[:100]}")
                        except:
                            pass
            except Exception as e:
                print(f"  Error with {xpath}: {e}")

        driver.save_screenshot('/tmp/youtube_final.png')
        print("\nFinal screenshot saved: /tmp/youtube_final.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    test_youtube_scraping("https://www.youtube.com/watch?v=gdZLi9oWNZg")
