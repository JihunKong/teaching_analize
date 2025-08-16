#!/usr/bin/env python3
"""
Final comprehensive analysis test with result area debugging
"""

from playwright.sync_api import sync_playwright
import time

def final_test():
    print("🎯 Final comprehensive analysis test")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.on("console", lambda msg: print(f"[{msg.type}] {msg.text}"))
        
        try:
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Force tab switching
            page.evaluate("""
                document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));
                document.getElementById('analysis-tab').classList.remove('hidden');
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelector('[onclick*="analysis"]').classList.add('active');
            """)
            time.sleep(1)
            
            # Fill text
            page.fill("#analysis-text", "선생님이 학생들에게 수학 문제를 풀어보라고 했습니다. 그 다음에 왜 그렇게 풀었는지 설명해달라고 했어요.")
            print("✍️ Text entered")
            
            # Ensure result div is visible before clicking
            page.evaluate("""
                const resultDiv = document.getElementById('analysis-result');
                if (resultDiv) {
                    resultDiv.classList.remove('hidden');
                    resultDiv.style.display = 'block';
                    console.log('Result div made visible');
                }
            """)
            
            # Click analyze
            page.click("#analyze-btn")
            print("🚀 Analysis button clicked")
            
            # Wait and check result periodically
            for i in range(10):
                time.sleep(2)
                
                result_content = page.evaluate("""
                    const resultDiv = document.getElementById('analysis-result');
                    return resultDiv ? resultDiv.textContent : 'No result div';
                """)
                
                print(f"⏳ Check {i+1}: {result_content[:100]}...")
                
                if result_content and ("전체 점수" in result_content or "CBIL" in result_content):
                    print("🎉 SUCCESS: Analysis result found!")
                    break
                elif result_content and "분석" in result_content and len(result_content) > 20:
                    print("✅ Analysis completed (basic result)")
                    break
            
            # Final check and screenshot
            final_result = page.text_content("#analysis-result")
            print(f"📊 Final result: {final_result}")
            
            page.screenshot(path="final_analysis_test.png")
            
            # Also check the network tab for API calls
            page.evaluate("""
                console.log('=== CHECKING API RESPONSE ===');
                fetch('/api/analyze/text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': 'analysis-api-key-prod-2025'
                    },
                    body: JSON.stringify({
                        text: '테스트 문장입니다',
                        framework: 'cbil'
                    })
                }).then(r => r.json()).then(data => {
                    console.log('API Response:', JSON.stringify(data, null, 2));
                }).catch(e => {
                    console.error('API Error:', e);
                });
            """)
            
            time.sleep(3)  # Wait for API test result
            
            if final_result and len(final_result) > 10:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
        finally:
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    success = final_test()
    print(f"\n🏁 Final result: {'SUCCESS' if success else 'NEEDS DEBUGGING'}")