#!/usr/bin/env python3
"""
Test the fixed analysis display
"""

from playwright.sync_api import sync_playwright
import time

def test_fixed_analysis():
    print("🔧 Testing fixed analysis display")
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
            
            # Switch to analysis tab
            print("📊 Switching to analysis tab...")
            page.click("text=📊 분석")
            time.sleep(2)
            
            # Enter more complex educational text for better analysis
            test_text = "학생들에게 오늘 배운 수학 공식을 설명해보라고 했습니다. 그리고 이 공식이 실생활에서 어떻게 활용될 수 있는지 창의적으로 생각해보라고 했어요. 마지막으로 다른 공식과 비교하여 어떤 것이 더 유용한지 평가해달라고 했습니다."
            print(f"✍️ Entering text: {test_text[:100]}...")
            page.fill("#analysis-text", test_text)
            
            # Click analyze
            print("🚀 Starting analysis...")
            page.click("#analyze-btn")
            
            # Wait for result
            print("⏳ Waiting for analysis result...")
            time.sleep(5)
            
            # Check result content
            result_div = page.query_selector("#analysis-result")
            if result_div:
                result_content = result_div.text_content()
                print(f"📊 Result content: {result_content}")
                
                # Check for specific analysis data
                if "전체 점수" in result_content and "레벨" in result_content:
                    print("🎉 SUCCESS: Detailed analysis results are displayed!")
                    
                    # Take screenshot of success
                    page.screenshot(path="successful_analysis.png")
                    print("📸 Success screenshot saved")
                    
                    return True
                else:
                    print("⚠️ Analysis completed but detailed results not showing")
                    print(f"Content: {result_content}")
            
            # Take screenshot anyway
            page.screenshot(path="analysis_test_result.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            time.sleep(3)
            browser.close()
            
    return False

if __name__ == "__main__":
    success = test_fixed_analysis()
    print(f"\n🏁 Test result: {'SUCCESS' if success else 'NEEDS MORE WORK'}")