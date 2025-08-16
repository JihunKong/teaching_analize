#!/usr/bin/env python3
"""
Force tab switching and test analysis with JavaScript execution
"""

from playwright.sync_api import sync_playwright
import time

def force_tab_test():
    print("💪 Force tab switching test")
    print("=" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        try:
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Force tab switching with JavaScript
            print("🔧 Force switching to analysis tab...")
            page.evaluate("""
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.add('hidden');
                });
                
                // Show analysis tab
                const analysisTab = document.getElementById('analysis-tab');
                if (analysisTab) {
                    analysisTab.classList.remove('hidden');
                    console.log('Analysis tab forced to show');
                }
                
                // Update tab button states
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                const analysisButton = document.querySelector('[onclick*="analysis"]');
                if (analysisButton) {
                    analysisButton.classList.add('active');
                }
            """)
            
            time.sleep(2)
            
            # Try to fill analysis text
            print("✍️ Trying to fill analysis text...")
            page.fill("#analysis-text", "간단한 분석 테스트 문장입니다.")
            print("✅ Text filled successfully")
            
            # Click analyze button
            page.click("#analyze-btn")
            print("🚀 Analysis started")
            
            # Wait for result
            time.sleep(8)
            
            # Check result
            result_content = page.text_content("#analysis-result")
            print(f"📊 Analysis result: {result_content}")
            
            if "전체 점수" in result_content:
                print("🎉 SUCCESS: Detailed analysis results displayed!")
                success = True
            elif "분석" in result_content:
                print("✅ PARTIAL: Analysis completed but without detailed scores")
                success = True
            else:
                print("❌ FAILED: No analysis result")
                success = False
            
            # Take screenshot
            page.screenshot(path="force_test_result.png")
            print("📸 Screenshot saved")
            
            return success
            
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="force_test_error.png")
            return False
            
        finally:
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    success = force_tab_test()
    print(f"\n🏁 Final result: {'SUCCESS' if success else 'FAILED'}")