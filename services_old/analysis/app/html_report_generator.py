"""
HTML-based Professional Report Generator for CBIL Teaching Analysis
Creates print-ready HTML reports that can be converted to PDF by browser
"""

from datetime import datetime
from typing import Dict, List


class HTMLReportGenerator:
    """Generate professional HTML reports for CBIL analysis"""
    
    def create_chart_svg(self, cbil_scores: Dict[str, float]) -> str:
        """Create SVG bar chart for CBIL scores"""
        level_names = [
            "단순 확인", "사실 회상", "개념 설명", 
            "분석적 사고", "종합적 이해", "평가적 판단", "창의적 적용"
        ]
        
        # Get max value for scaling
        max_val = max(cbil_scores.values()) if cbil_scores.values() else 1
        scale = 300 / max_val if max_val > 0 else 1
        
        # Colors for each bar
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                 '#FFEAA7', '#DDA0DD', '#98D8C8']
        
        svg_content = '<svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">'
        
        # Draw bars
        bar_width = 70
        bar_gap = 10
        start_x = 30
        
        for i, level_name in enumerate(level_names):
            score = cbil_scores.get(f"level_{i+1}", 0)
            bar_height = score * scale
            x = start_x + i * (bar_width + bar_gap)
            y = 350 - bar_height
            
            # Bar
            svg_content += f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{colors[i]}" opacity="0.8"/>'
            
            # Value label
            svg_content += f'<text x="{x + bar_width/2}" y="{y - 5}" text-anchor="middle" font-size="12" font-weight="bold">{score}</text>'
            
            # Level label (rotated)
            svg_content += f'<text x="{x + bar_width/2}" y="375" text-anchor="middle" font-size="10" transform="rotate(-45, {x + bar_width/2}, 375)">{level_name}</text>'
        
        # Y-axis
        svg_content += '<line x1="25" y1="50" x2="25" y2="350" stroke="black" stroke-width="2"/>'
        
        # X-axis
        svg_content += '<line x1="25" y1="350" x2="580" y2="350" stroke="black" stroke-width="2"/>'
        
        # Title
        svg_content += '<text x="300" y="25" text-anchor="middle" font-size="16" font-weight="bold">CBIL 7단계 분석 결과</text>'
        
        svg_content += '</svg>'
        return svg_content
    
    def create_pie_chart_svg(self, cbil_scores: Dict[str, float]) -> str:
        """Create SVG pie chart for CBIL distribution"""
        import math
        
        # Filter non-zero scores
        non_zero_scores = {k: v for k, v in cbil_scores.items() if v > 0}
        if not non_zero_scores:
            return '<p>표시할 데이터가 없습니다.</p>'
        
        level_names = {
            "level_1": "단순 확인", "level_2": "사실 회상", "level_3": "개념 설명",
            "level_4": "분석적 사고", "level_5": "종합적 이해", 
            "level_6": "평가적 판단", "level_7": "창의적 적용"
        }
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                 '#FFEAA7', '#DDA0DD', '#98D8C8']
        
        total = sum(non_zero_scores.values())
        cx, cy, r = 150, 150, 100
        
        svg_content = '<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">'
        svg_content += '<text x="200" y="25" text-anchor="middle" font-size="16" font-weight="bold">CBIL 인지부하 분포</text>'
        
        # Draw pie slices
        current_angle = 0
        color_idx = 0
        
        for key, value in non_zero_scores.items():
            percentage = value / total
            angle = percentage * 360
            
            # Calculate slice path
            start_angle = math.radians(current_angle)
            end_angle = math.radians(current_angle + angle)
            
            x1 = cx + r * math.cos(start_angle)
            y1 = cy + r * math.sin(start_angle)
            x2 = cx + r * math.cos(end_angle)
            y2 = cy + r * math.sin(end_angle)
            
            large_arc = 1 if angle > 180 else 0
            
            path = f'M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z'
            svg_content += f'<path d="{path}" fill="{colors[color_idx % len(colors)]}" opacity="0.8"/>'
            
            # Add percentage label
            label_angle = math.radians(current_angle + angle/2)
            label_x = cx + (r * 0.7) * math.cos(label_angle)
            label_y = cy + (r * 0.7) * math.sin(label_angle)
            svg_content += f'<text x="{label_x}" y="{label_y}" text-anchor="middle" font-size="12" font-weight="bold">{percentage*100:.1f}%</text>'
            
            current_angle += angle
            color_idx += 1
        
        # Legend
        legend_y = 50
        for i, (key, value) in enumerate(non_zero_scores.items()):
            legend_name = level_names.get(key, key)
            svg_content += f'<rect x="320" y="{legend_y + i*20}" width="15" height="15" fill="{colors[i % len(colors)]}"/>'
            svg_content += f'<text x="340" y="{legend_y + i*20 + 12}" font-size="12">{legend_name}</text>'
        
        svg_content += '</svg>'
        return svg_content
    
    def generate_recommendations(self, cbil_scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        total_items = sum(cbil_scores.values())
        
        if total_items == 0:
            return ["분석할 데이터가 충분하지 않습니다."]
        
        percentages = {k: (v/total_items)*100 for k, v in cbil_scores.items()}
        low_level = sum(percentages.get(f"level_{i}", 0) for i in [1, 2, 3])
        high_level = sum(percentages.get(f"level_{i}", 0) for i in [5, 6, 7])
        
        if low_level > 60:
            recommendations.append(
                "🔍 현재 수업이 단순 확인과 사실 회상 중심입니다. "
                "학습자의 분석적 사고를 촉진하는 질문을 더 많이 활용해보세요."
            )
            
        if high_level < 20:
            recommendations.append(
                "📈 창의적 사고와 평가적 판단을 요구하는 활동을 늘려 "
                "학습자의 고차원적 사고력을 발달시켜보세요."
            )
            
        if percentages.get("level_4", 0) > 30:
            recommendations.append(
                "✨ 분석적 사고 활동이 활발합니다. "
                "이를 종합적 이해로 연결하는 브리지 질문을 추가해보세요."
            )
            
        if len(recommendations) < 3:
            recommendations.extend([
                "🎯 학습 목표에 따라 적절한 인지부하 수준을 계획적으로 배치하세요.",
                "💡 학습자의 수준을 고려하여 점진적으로 인지부하를 높여가세요.",
                "🔄 다양한 인지부하 수준을 균형있게 활용하여 학습 효과를 극대화하세요."
            ])
            
        return recommendations[:5]
    
    def generate_summary(self, cbil_scores: Dict[str, float]) -> str:
        """Generate executive summary"""
        total = sum(cbil_scores.values())
        if total == 0:
            return "분석할 데이터가 없습니다."
            
        max_level = max(cbil_scores.items(), key=lambda x: x[1])
        level_names = {
            "level_1": "단순 확인", "level_2": "사실 회상", "level_3": "개념 설명",
            "level_4": "분석적 사고", "level_5": "종합적 이해", 
            "level_6": "평가적 판단", "level_7": "창의적 적용"
        }
        
        dominant_level = level_names.get(max_level[0], "알 수 없음")
        percentage = (max_level[1] / total) * 100
        
        return f"수업에서 '{dominant_level}' 수준이 {percentage:.1f}%로 가장 높게 나타났습니다. 총 {total}개의 교수 언어가 분석되었습니다."
    
    def generate_html_report(self, analysis_data: Dict) -> str:
        """Generate complete HTML report"""
        cbil_scores = analysis_data.get('cbil_scores', {})
        timestamp = datetime.now().strftime('%Y년 %m월 %d일')
        analysis_id = analysis_data.get('id', 'N/A')
        text_length = len(analysis_data.get('text', ''))
        
        summary = self.generate_summary(cbil_scores)
        recommendations = self.generate_recommendations(cbil_scores)
        bar_chart = self.create_chart_svg(cbil_scores)
        pie_chart = self.create_pie_chart_svg(cbil_scores)
        
        html_content = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIBOA 교수 언어 분석 보고서</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Nanum Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #4ECDC4;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .title {{
            font-size: 28px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            font-size: 16px;
            color: #7F8C8D;
            margin-bottom: 15px;
        }}
        
        .meta-info {{
            font-size: 14px;
            color: #666;
        }}
        
        .section {{
            margin: 30px 0;
            padding: 20px;
            border-radius: 8px;
            break-inside: avoid;
        }}
        
        .summary {{ background-color: #E8F6F3; }}
        .analysis {{ background-color: #FDF2E9; }}
        .recommendations {{ background-color: #E8F4FD; }}
        
        h2 {{
            color: #2C3E50;
            border-left: 4px solid #4ECDC4;
            padding-left: 15px;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        
        .summary-text {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        
        .chart-container {{
            text-align: center;
            margin: 20px 0;
            break-inside: avoid;
        }}
        
        .recommendation-item {{
            padding: 15px;
            margin: 15px 0;
            background-color: white;
            border-radius: 8px;
            border-left: 4px solid #4ECDC4;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-box {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #4ECDC4;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }}
        
        @media print {{
            body {{ 
                margin: 0; 
                padding: 0;
                font-size: 12pt;
            }}
            .section {{ page-break-inside: avoid; }}
            .chart-container {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🎓 AIBOA 교수 언어 분석 보고서</div>
        <div class="subtitle">AI 기반 교육 관찰 및 분석 플랫폼</div>
        <div class="meta-info">
            분석일: {timestamp} | 분석 ID: {analysis_id}
        </div>
    </div>

    <div class="section summary">
        <h2>📊 분석 요약</h2>
        <div class="summary-text">{summary}</div>
        
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-number">{text_length}</div>
                <div class="stat-label">분석된 텍스트 길이 (자)</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{sum(cbil_scores.values())}</div>
                <div class="stat-label">총 교수 언어 개수</div>
            </div>
        </div>
    </div>

    <div class="section analysis">
        <h2>📈 CBIL 7단계 분석 결과</h2>
        
        <div class="chart-container">
            <h3>단계별 상세 분석</h3>
            {bar_chart}
        </div>
        
        <div class="chart-container">
            <h3>인지부하 분포</h3>
            {pie_chart}
        </div>
    </div>

    <div class="section recommendations">
        <h2>💡 개선 권장사항</h2>
        {''.join([f'<div class="recommendation-item">{rec}</div>' for rec in recommendations])}
    </div>

    <div class="footer">
        <p>본 보고서는 AIBOA (AI-Based Observation and Analysis) 시스템에 의해 생성되었습니다.</p>
        <p>교육 컨설팅 문의: contact@aiboa.edu | www.aiboa.edu</p>
    </div>
</body>
</html>
        '''
        
        return html_content