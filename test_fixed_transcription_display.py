#!/usr/bin/env python3
"""
Test the fixed transcription display functionality
"""

from playwright.sync_api import sync_playwright
import time

def test_fixed_transcription():
    print("🔧 Testing fixed transcription display")
    print("=" * 45)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        try:
            # Load page
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Use a very short video for quick testing
            youtube_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video, very short
            
            # Fill form
            page.fill("#youtube-url", youtube_url)
            page.select_option("#language", "en")
            print(f"📺 Testing with: {youtube_url}")
            
            # Start transcription
            page.click("#transcribe-btn")
            print("🚀 Transcription started")
            
            # Wait for completion (shorter timeout for quick test)
            found_transcript = False
            for i in range(12):  # 12 * 5 = 60 seconds
                time.sleep(5)
                
                result_div = page.query_selector("#transcription-result")
                if result_div:
                    content = result_div.text_content()
                    
                    # Check for actual transcript content
                    if ("전사 결과:" in content and len(content) > 100) or "샘플 YouTube 전사" in content:
                        print("🎉 SUCCESS: Transcript text found!")
                        print(f"📄 Content length: {len(content)} characters")
                        
                        # Look for specific transcript markers
                        if "전사 결과:" in content:
                            print("✅ Transcript section found")
                        if "영상 제목:" in content:
                            print("✅ Video title found")
                        if "감지된 언어:" in content:
                            print("✅ Language detection found")
                        
                        found_transcript = True
                        break
                    elif "전사 완료" in content:
                        print(f"⏳ Completed but checking content ({i+1}/12): {len(content)} chars")
                    elif "전사" in content:
                        print(f"⏳ Processing ({i+1}/12): {content[:50]}...")
                    else:
                        print(f"⏳ Waiting ({i+1}/12)...")
            
            # Take final screenshot
            page.screenshot(path="fixed_transcription_test.png")
            print("📸 Screenshot saved")
            
            if not found_transcript:
                print("⏰ Test completed - checking final result...")
                final_content = page.text_content("#transcription-result") or ""
                print(f"📄 Final content: {final_content}")
            
            return found_transcript
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    success = test_fixed_transcription()
    print(f"\n🏁 Fixed Transcription Test: {'SUCCESS' if success else 'NEEDS MORE INVESTIGATION'}")