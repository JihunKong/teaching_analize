#!/usr/bin/env python3
"""
Test the clean UI with proper API routing (no exposed ports)
"""

from playwright.sync_api import sync_playwright
import time

def test_clean_ui():
    print("🧪 Testing clean UI with proper API routing")
    print("=" * 55)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Monitor network requests
        def log_request(request):
            print(f"📤 Request: {request.method} {request.url}")
        
        def log_response(response):
            print(f"📥 Response: {response.status} {response.url}")
            
        page.on("request", log_request)
        page.on("response", log_response)
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        try:
            print("🌐 Loading AIBOA...")
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Test tab switching
            print("\n📊 Testing tab switching...")
            page.click("text=📊 분석")
            time.sleep(1)
            
            # Check if analysis tab is visible
            analysis_tab = page.query_selector("#analysis-tab")
            is_hidden = "hidden" in (analysis_tab.get_attribute("class") or "")
            print(f"📋 Analysis tab hidden: {is_hidden}")
            
            if not is_hidden:
                print("✅ Tab switching works!")
                
                # Test analysis
                print("\n🧪 Testing analysis...")
                page.fill("#analysis-text", "선생님이 학생들에게 수학 문제를 설명했습니다. 그리고 왜 그렇게 풀어야 하는지 이유를 물어보았습니다.")
                
                page.click("#analyze-btn")
                print("🚀 Analysis started")
                
                # Wait for result
                for i in range(10):
                    time.sleep(1)
                    result_div = page.query_selector("#analysis-result")
                    if result_div:
                        content = result_div.text_content()
                        if content and "전체 점수" in content:
                            print("🎉 SUCCESS: Detailed analysis result displayed!")
                            break
                        elif content and "분석" in content and len(content) > 50:
                            print("✅ SUCCESS: Analysis completed!")
                            break
                    print(f"⏳ Waiting... ({i+1}/10)")
                
                # Final result check
                final_result = page.text_content("#analysis-result") or ""
                print(f"📊 Final result: {final_result[:100]}...")
                
                # Take screenshot
                page.screenshot(path="clean_ui_test.png")
                print("📸 Screenshot saved")
                
                return len(final_result) > 20
            else:
                print("❌ Tab switching failed")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    success = test_clean_ui()
    print(f"\n🏁 Clean UI Test: {'SUCCESS' if success else 'FAILED'}")