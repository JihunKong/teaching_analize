#!/usr/bin/env python3
"""
Simple debug of transcript display
"""

from playwright.sync_api import sync_playwright
import time

def simple_debug():
    print("🔧 Simple transcript debug")
    print("=" * 30)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        try:
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            
            # Manually call the display function with known data
            page.evaluate("""
                // Test with the known API response format
                const testData = {
                    "job_id": "test-job",
                    "status": "completed", 
                    "result": {
                        "text": "[샘플 YouTube 전사] URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "language": "en",
                        "duration": "00:10:00",
                        "segments": [
                            {"start": 0.0, "end": 5.0, "text": "YouTube 비디오 전사 시작"},
                            {"start": 5.0, "end": 10.0, "text": "내용이 여기에 표시됩니다."}
                        ]
                    }
                };
                
                console.log('Testing with known data format');
                displayTranscriptionResult(testData);
            """)
            
            time.sleep(3)
            
            # Check result
            result_content = page.text_content("#transcription-result") or ""
            print(f"Result: {result_content}")
            
            if "샘플 YouTube 전사" in result_content:
                print("✅ SUCCESS: Function is working with correct data format!")
            else:
                print("❌ Function still not working")
            
            page.screenshot(path="simple_debug.png")
            
        except Exception as e:
            print(f"Error: {e}")
            
        finally:
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    simple_debug()