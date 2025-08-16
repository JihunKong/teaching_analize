#!/usr/bin/env python3
"""
Debug the UI issues with more detailed logging
"""

from playwright.sync_api import sync_playwright
import time

def debug_ui_test():
    print("🔍 Debug test for AIBOA UI issues")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"🖥️ Console: {msg.text}"))
        page.on("requestfailed", lambda req: print(f"❌ Request failed: {req.url} - {req.failure}"))
        
        try:
            print("🌐 Loading AIBOA...")
            page.goto("http://3.38.107.23:3000", timeout=15000)
            
            # Wait for page to fully load
            page.wait_for_selector("h1", timeout=10000)
            print("✅ Page loaded")
            
            # Switch to analysis tab
            print("📊 Switching to analysis tab...")
            page.click("text=📊 분석")
            time.sleep(2)
            
            # Fill analysis text
            test_text = "선생님이 학생들에게 질문했습니다."
            print(f"✍️ Entering text: {test_text}")
            page.fill("#analysis-text", test_text)
            
            # Take screenshot before clicking
            page.screenshot(path="before_analysis.png")
            print("📸 Screenshot taken before analysis")
            
            # Click analyze button
            print("🚀 Clicking analyze button...")
            page.click("#analyze-btn")
            
            # Wait a moment and check what happens
            time.sleep(3)
            
            # Check if loading appeared
            loading_elements = page.query_selector_all(".loading")
            print(f"⏳ Loading elements found: {len(loading_elements)}")
            
            # Check button state
            button = page.query_selector("#analyze-btn")
            if button:
                button_text = button.text_content()
                is_disabled = button.is_disabled()
                print(f"🔘 Button text: '{button_text}', Disabled: {is_disabled}")
            
            # Check result div content
            result_div = page.query_selector("#analysis-result")
            if result_div:
                result_content = result_div.text_content()
                is_hidden = "hidden" in (result_div.get_attribute("class") or "")
                print(f"📋 Result div content: '{result_content[:100]}...'")
                print(f"👁️ Result div hidden: {is_hidden}")
            
            # Wait longer for any network activity
            print("⏳ Waiting for network activity...")
            time.sleep(10)
            
            # Check again
            result_div = page.query_selector("#analysis-result")
            if result_div:
                final_content = result_div.text_content()
                print(f"🏁 Final result: '{final_content[:200]}...'")
            
            # Take final screenshot
            page.screenshot(path="after_analysis.png")
            print("📸 Final screenshot taken")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            # Keep browser open for 5 seconds to observe
            print("👀 Keeping browser open for observation...")
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    debug_ui_test()