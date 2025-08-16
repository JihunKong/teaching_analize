#!/usr/bin/env python3
"""
Test YouTube transcription through the fixed proxy
"""

from playwright.sync_api import sync_playwright
import time

def test_youtube_transcription():
    print("🎬 Testing YouTube transcription via fixed proxy")
    print("=" * 55)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Monitor all network activity
        page.on("request", lambda req: print(f"📤 {req.method} {req.url}"))
        page.on("response", lambda resp: print(f"📥 {resp.status} {resp.url}"))
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        try:
            # Load page
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Use Rick Roll as it's short and always available
            youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            
            # Fill form
            page.fill("#youtube-url", youtube_url)
            page.select_option("#language", "en")
            print(f"📺 Testing with: {youtube_url}")
            
            # Start transcription
            page.click("#transcribe-btn")
            print("🚀 Transcription started")
            
            # Monitor for 2 minutes
            found_result = False
            for i in range(24):  # 24 * 5 = 120 seconds
                time.sleep(5)
                
                result_div = page.query_selector("#transcription-result")
                if result_div:
                    content = result_div.text_content()
                    
                    if "전사 완료" in content:
                        print("🎉 SUCCESS: Transcription completed!")
                        print(f"📄 Result: {content[:200]}...")
                        found_result = True
                        break
                    elif "실패" in content or "오류" in content:
                        print(f"❌ FAILED: {content}")
                        break
                    elif content and len(content) > 30:
                        print(f"⏳ Status ({i+1}/24): {content[:100]}...")
                    else:
                        print(f"⏳ Waiting ({i+1}/24)...")
                
            if not found_result:
                print("⏰ Timeout after 2 minutes")
            
            # Final screenshot
            page.screenshot(path="youtube_test_result.png")
            print("📸 Screenshot saved")
            
            return found_result
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    success = test_youtube_transcription()
    print(f"\n🏁 YouTube Transcription Test: {'SUCCESS' if success else 'FAILED/TIMEOUT'}")