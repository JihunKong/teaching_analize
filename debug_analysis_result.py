#!/usr/bin/env python3
"""
Debug analysis result display issues
"""

from playwright.sync_api import sync_playwright
import time

def debug_analysis():
    print("🔍 Debugging analysis result display")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Log all console messages
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        page.on("requestfailed", lambda req: print(f"Request failed: {req.url}"))
        page.on("response", lambda resp: print(f"Response: {resp.status} {resp.url}"))
        
        try:
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Switch to analysis tab properly
            page.evaluate("switchTab('analysis')")
            time.sleep(2)
            
            # Fill text  
            page.fill("#analysis-text", "테스트 분석 문장")
            print("✍️ Text entered")
            
            # Check if result div exists
            result_div_exists = page.query_selector("#analysis-result") is not None
            print(f"📋 Result div exists: {result_div_exists}")
            
            # Click analyze button
            page.click("#analyze-btn") 
            print("🚀 Analysis started")
            
            # Monitor for 15 seconds
            for i in range(15):
                time.sleep(1)
                
                # Check button state
                button_text = page.text_content("#analyze-btn")
                
                # Check result div content
                result_content = ""
                result_div = page.query_selector("#analysis-result")
                if result_div:
                    result_content = result_div.text_content()
                    is_hidden = "hidden" in (result_div.get_attribute("class") or "")
                    print(f"[{i+1}s] Button: '{button_text}' | Result hidden: {is_hidden} | Content: '{result_content[:50]}...'")
                else:
                    print(f"[{i+1}s] Button: '{button_text}' | No result div found")
                
                # Stop if we see results
                if result_content and len(result_content) > 20:
                    print("✅ Result appeared!")
                    break
            
            # Final screenshot and summary
            page.screenshot(path="debug_analysis.png")
            
            final_result = page.text_content("#analysis-result") or "No result"
            print(f"\n📊 Final result: {final_result}")
            
            # Test direct API call from browser
            print("\n🧪 Testing direct API call...")
            page.evaluate("""
                console.log('=== TESTING API DIRECTLY ===');
                fetch('/api/analyze/text', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': 'analysis-api-key-prod-2025'
                    },
                    body: JSON.stringify({text: '테스트', framework: 'cbil'})
                })
                .then(response => {
                    console.log('API Response status:', response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('API Response data:', JSON.stringify(data, null, 2));
                    
                    // Manually display result
                    const resultDiv = document.getElementById('analysis-result');
                    if (resultDiv) {
                        resultDiv.innerHTML = '<h4>직접 API 호출 결과</h4><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                        resultDiv.classList.remove('hidden');
                    }
                })
                .catch(error => {
                    console.error('API Error:', error);
                });
            """)
            
            time.sleep(5)  # Wait for API test
            
            # Final result check
            final_content = page.text_content("#analysis-result") or "No content"
            print(f"📋 After API test: {final_content[:200]}...")
            
            page.screenshot(path="after_api_test.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    debug_analysis()