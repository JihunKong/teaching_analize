#!/usr/bin/env python3
"""
Create a demo professional report to show the final result
"""

import sys
import os
sys.path.append('/Users/jihunkong/teaching_analize/services/analysis')

from app.html_report_generator import HTMLReportGenerator

def create_demo_report():
    # Sample analysis data
    analysis_data = {
        'id': 'demo-analysis-001',
        'text': '안녕하세요 여러분. 오늘은 과학 시간입니다. 물의 순환에 대해 배워보겠습니다. 누구 물의 순환이 무엇인지 알고 있나요? 네, 맞습니다. 물이 증발하고 구름이 되고 다시 비가 되는 과정이죠. 그럼 이제 더 자세히 살펴볼까요? 증발은 어떻게 일어날까요? 태양열 때문입니다. 왜 그럴까요? 태양이 물을 데우기 때문입니다. 그럼 이 과정을 비판적으로 생각해보세요. 다른 요인들도 있을까요? 여러분만의 창의적인 해결책을 제시해보세요.',
        'cbil_scores': {
            'level_1': 2,  # 단순 확인
            'level_2': 3,  # 사실 회상  
            'level_3': 4,  # 개념 설명
            'level_4': 3,  # 분석적 사고
            'level_5': 2,  # 종합적 이해
            'level_6': 1,  # 평가적 판단
            'level_7': 1   # 창의적 적용
        }
    }
    
    generator = HTMLReportGenerator()
    html_content = generator.generate_html_report(analysis_data)
    
    with open('AIBOA_Professional_Report_Demo.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Professional demo report created!")
    print("📁 File: AIBOA_Professional_Report_Demo.html")
    print("📄 Open in browser to see the professional layout")
    print("🖨️ Use browser's Print to PDF for final PDF version")
    
    # Print summary
    print(f"\n📊 Report includes:")
    print(f"   • Professional header with AIBOA branding")
    print(f"   • Executive summary")
    print(f"   • CBIL 7-level analysis with SVG charts")
    print(f"   • Pie chart for cognitive load distribution") 
    print(f"   • Specific improvement recommendations")
    print(f"   • Print-ready CSS styling")
    print(f"   • Korean language support")

if __name__ == "__main__":
    create_demo_report()