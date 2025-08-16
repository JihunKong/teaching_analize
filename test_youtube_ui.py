#!/usr/bin/env python3
"""
Test YouTube transcription via UI
"""

from playwright.sync_api import sync_playwright
import time

def test_youtube_ui():
    print("🎬 Testing YouTube transcription UI")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"🖥️ Console: {msg.text}"))
        
        try:
            print("🌐 Loading AIBOA...")
            page.goto("http://3.38.107.23:3000", timeout=15000)
            
            page.wait_for_selector("h1", timeout=10000)
            print("✅ Page loaded")
            
            # Stay on transcription tab (default)
            print("🎙️ Testing transcription tab...")
            
            # Use a very short YouTube video for quick testing
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - short and popular
            print(f"📺 Testing with URL: {test_url}")
            
            # Fill YouTube URL
            page.fill("#youtube-url", test_url)
            
            # Select language
            page.select_option("#language", "en")
            
            # Take screenshot before
            page.screenshot(path="before_transcription.png")
            
            # Click transcribe button
            print("🚀 Starting transcription...")
            page.click("#transcribe-btn")
            
            # Wait for loading
            time.sleep(3)
            
            # Check button state
            button = page.query_selector("#transcribe-btn")
            if button:
                button_text = button.text_content()
                print(f"🔘 Button text: '{button_text}'")
            
            # Check result div
            result_div = page.query_selector("#transcription-result")
            if result_div:
                result_content = result_div.text_content()
                print(f"📋 Transcription result: '{result_content[:200]}...'")
            
            # Wait for transcription to complete (give it more time)
            print("⏳ Waiting for transcription to complete...")
            for i in range(12):  # Wait up to 60 seconds
                time.sleep(5)
                result_div = page.query_selector("#transcription-result")
                if result_div:
                    content = result_div.text_content()
                    if "전사 완료" in content or "transcript" in content.lower():
                        print("🎉 Transcription completed!")
                        print(f"📄 Final result: {content[:300]}...")
                        break
                    elif "실패" in content or "error" in content.lower():
                        print("❌ Transcription failed")
                        print(f"Error: {content}")
                        break
                print(f"⏳ Still waiting... ({i+1}/12)")
            
            # Final screenshot
            page.screenshot(path="after_transcription.png")
            print("📸 Final screenshot saved")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    test_youtube_ui()