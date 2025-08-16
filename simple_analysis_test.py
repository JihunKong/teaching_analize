#!/usr/bin/env python3
"""
Simple direct test of analysis functionality
"""

from playwright.sync_api import sync_playwright
import time

def simple_test():
    print("🔬 Simple analysis test")
    print("=" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Enable all console messages
        page.on("console", lambda msg: print(f"Console [{msg.type}]: {msg.text}"))
        
        try:
            # Go to page
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Wait a bit for JavaScript to initialize
            time.sleep(2)
            
            # Try to find the analysis tab and click it
            analysis_tab = page.wait_for_selector("text=분석", timeout=5000)
            analysis_tab.click()
            print("📊 Analysis tab clicked")
            
            time.sleep(2)
            
            # Try to find and fill the textarea
            textarea = page.wait_for_selector("#analysis-text", timeout=5000)
            if textarea:
                print("✅ Textarea found")
                
                # Clear and fill
                textarea.fill("")
                textarea.fill("간단한 테스트 문장입니다.")
                print("✍️ Text entered")
                
                # Find and click button
                button = page.wait_for_selector("#analyze-btn", timeout=5000)
                if button:
                    button.click()
                    print("🚀 Analysis button clicked")
                    
                    # Wait for result
                    time.sleep(8)
                    
                    # Check result
                    result = page.query_selector("#analysis-result")
                    if result:
                        content = result.text_content()
                        print(f"📊 Result: {content[:500]}...")
                        
                        if "전체 점수" in content:
                            print("🎉 SUCCESS: Detailed results shown!")
                        else:
                            print("⚠️ Basic result only")
                    
                    # Screenshot
                    page.screenshot(path="simple_test.png")
                    print("📸 Screenshot saved")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="error_screenshot.png")
            
        finally:
            time.sleep(5)  # Keep browser open to observe
            browser.close()

if __name__ == "__main__":
    simple_test()