#!/usr/bin/env python3
"""
Playwright test for AIBOA UI functionality
Tests the actual web interface at http://3.38.107.23:3000
"""

from playwright.sync_api import sync_playwright
import time

def test_aiboa_ui():
    print("🎭 Starting Playwright test for AIBOA UI")
    print("=" * 50)
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)  # headless=False to see what's happening
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("🌐 Navigating to AIBOA UI...")
            page.goto("http://3.38.107.23:3000", timeout=10000)
            
            print("⏳ Waiting for page to load...")
            page.wait_for_selector("h1", timeout=10000)
            
            # Check if the main elements are present
            title = page.text_content("h1")
            print(f"📄 Page title: {title}")
            
            # Check for tabs
            tabs = page.query_selector_all(".tab")
            print(f"🗂️ Found {len(tabs)} tabs")
            
            # Test Analysis tab (safer than YouTube which requires longer processing)
            print("\n📊 Testing Analysis Tab...")
            page.click("text=📊 분석")
            time.sleep(1)
            
            # Fill in analysis text
            analysis_text = "학생들에게 오늘 배운 내용을 설명해보세요. 이것이 왜 중요한지도 말해주세요."
            page.fill("#analysis-text", analysis_text)
            print(f"✍️ Entered text: {analysis_text[:50]}...")
            
            # Click analyze button
            print("🚀 Clicking analyze button...")
            page.click("#analyze-btn")
            
            # Wait for loading to appear
            loading_element = page.wait_for_selector(".loading", timeout=5000)
            print("⏳ Loading indicator appeared")
            
            # Wait for result (with generous timeout)
            print("⏳ Waiting for analysis result...")
            try:
                # Wait for either success result or error
                page.wait_for_selector("#analysis-result", timeout=15000)
                
                # Check the result content
                result = page.text_content("#analysis-result")
                print("✅ Analysis completed!")
                print(f"📊 Result preview: {result[:200]}...")
                
                # Check if it contains expected analysis data
                if "CBIL 분석 결과" in result or "analysis_id" in result:
                    print("🎉 SUCCESS: CBIL analysis working correctly!")
                    return True
                else:
                    print(f"⚠️ Unexpected result format: {result}")
                    return False
                    
            except Exception as e:
                print(f"❌ Analysis timeout or error: {e}")
                
                # Check if there's an error message
                error_content = page.text_content("#analysis-result")
                print(f"Error content: {error_content}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
            
        finally:
            print("\n📸 Taking screenshot...")
            page.screenshot(path="aiboa_test_screenshot.png")
            print("💾 Screenshot saved as aiboa_test_screenshot.png")
            
            browser.close()
            
    return False

if __name__ == "__main__":
    success = test_aiboa_ui()
    print(f"\n🏁 Test result: {'SUCCESS' if success else 'FAILED'}")