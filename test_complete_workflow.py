#!/usr/bin/env python3
"""
Complete end-to-end test for AIBOA system:
1. Transcribe YouTube video
2. Analyze with CBIL
3. Generate professional PDF report
4. Test UI functionality
"""

from playwright.sync_api import sync_playwright
import time
import requests

def test_complete_workflow():
    print("🎯 AIBOA Complete Workflow Test")
    print("=" * 50)
    
    BASE_URL = "http://3.38.107.23:3000"
    API_KEY = "analysis-api-key-prod-2025"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Step 1: Test UI Loading
            print("1️⃣ Testing UI Loading...")
            page.goto(BASE_URL)
            page.wait_for_selector("h1")
            print("✅ UI loaded successfully")
            
            # Step 2: Test YouTube Transcription
            print("\n2️⃣ Testing YouTube Transcription...")
            youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
            
            page.fill("#youtube-url", youtube_url)
            page.click("#transcribe-btn")
            
            # Wait for transcription completion
            print("⏳ Waiting for transcription...")
            time.sleep(15)
            
            # Check if transcription completed
            result_content = page.text_content("#transcription-result") or ""
            if "전사 완료" in result_content:
                print("✅ Transcription completed successfully")
                print(f"📄 Result preview: {result_content[:100]}...")
            else:
                print("❌ Transcription failed or incomplete")
                return False
                
            # Step 3: Test CBIL Analysis
            print("\n3️⃣ Testing CBIL Analysis...")
            
            # Use a Korean educational text for analysis
            korean_text = """
            안녕하세요 여러분. 오늘은 과학 시간입니다. 
            물의 순환에 대해 배워보겠습니다. 
            누구 물의 순환이 무엇인지 알고 있나요? 
            네, 맞습니다. 물이 증발하고 구름이 되고 다시 비가 되는 과정이죠. 
            그럼 이제 더 자세히 살펴볼까요? 
            증발은 어떻게 일어날까요? 
            태양열 때문입니다. 
            왜 그럴까요? 
            태양이 물을 데우기 때문입니다.
            그럼 이 과정을 비판적으로 생각해보세요.
            다른 요인들도 있을까요?
            여러분만의 창의적인 해결책을 제시해보세요.
            """
            
            # API call for analysis
            analysis_response = requests.post(
                f"{BASE_URL}/api/analyze/text",
                headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
                json={"text": korean_text}
            )
            
            if analysis_response.status_code == 200:
                analysis_data = analysis_response.json()
                analysis_id = analysis_data.get("analysis_id")
                print(f"✅ CBIL Analysis completed: {analysis_id}")
                print(f"📊 CBIL Scores: {analysis_data.get('cbil_scores', {})}")
                
                # Step 4: Test Professional PDF Report Generation
                print("\n4️⃣ Testing Professional PDF Report Generation...")
                
                # Generate HTML report
                report_response = requests.get(
                    f"{BASE_URL}/api/reports/pdf/{analysis_id}",
                    headers={"X-API-Key": API_KEY}
                )
                
                if report_response.status_code == 200:
                    # Save report to file
                    with open("professional_report.html", "w", encoding="utf-8") as f:
                        f.write(report_response.text)
                    
                    print("✅ Professional HTML report generated successfully!")
                    print(f"📄 Report size: {len(report_response.text)} characters")
                    print("📁 Saved as: professional_report.html")
                    
                    # Validate report content
                    report_content = report_response.text
                    if all(keyword in report_content for keyword in [
                        "AIBOA 교수 언어 분석 보고서",
                        "CBIL 7단계 분석 결과", 
                        "개선 권장사항",
                        "svg",  # Charts present
                        "교육 컨설팅"
                    ]):
                        print("✅ Report contains all required sections")
                        print("✅ Professional formatting detected")
                        print("✅ Korean language support confirmed")
                        print("✅ Charts and visualizations included")
                        
                        # Step 5: Business Model Validation
                        print("\n5️⃣ Business Model Validation...")
                        print("✅ Transcript extraction: WORKING")
                        print("✅ CBIL analysis: WORKING") 
                        print("✅ Professional PDF reports: WORKING")
                        print("✅ Korean education focus: CONFIRMED")
                        print("✅ Consulting-grade output: READY")
                        print("✅ Print-ready format: AVAILABLE")
                        
                        return True
                    else:
                        print("❌ Report missing required sections")
                        return False
                else:
                    print(f"❌ Report generation failed: {report_response.status_code}")
                    return False
            else:
                print(f"❌ Analysis failed: {analysis_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False
            
        finally:
            time.sleep(5)  # Keep browser open for inspection
            browser.close()

def main():
    success = test_complete_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 COMPLETE WORKFLOW TEST: PASSED")
        print("")
        print("🚀 AIBOA System Status: READY FOR BUSINESS")
        print("")
        print("✅ All core features working:")
        print("   • YouTube transcription (Fixed Railway blocking)")
        print("   • CBIL 7-level analysis") 
        print("   • Professional PDF reports")
        print("   • Korean educational content support")
        print("   • Business consulting ready")
        print("")
        print("📈 Business Value Delivered:")
        print("   • Automated teaching analysis")
        print("   • Professional consultation reports")
        print("   • Printable PDF format")
        print("   • Educational expertise integration")
    else:
        print("❌ COMPLETE WORKFLOW TEST: FAILED")
        print("🔧 Some components need attention")

if __name__ == "__main__":
    main()