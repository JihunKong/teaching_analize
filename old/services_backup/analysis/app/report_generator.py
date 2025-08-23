"""
PDF Report Generator for CBIL Teaching Analysis
Generates professional PDF reports for educational consulting
"""

import os
import base64
from datetime import datetime
from typing import Dict, List, Optional
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import font_manager
import numpy as np
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from PIL import Image


class CBILReportGenerator:
    """Generate professional PDF reports for CBIL analysis results"""
    
    def __init__(self):
        self.setup_korean_fonts()
        self.setup_templates()
        
    def setup_korean_fonts(self):
        """Configure Korean font support for matplotlib"""
        try:
            # Try to find Korean fonts on system
            korean_fonts = [
                'NanumGothic', 'Malgun Gothic', 'AppleGothic', 
                'Noto Sans CJK KR', 'Nanum Gothic'
            ]
            
            self.korean_font = None
            for font_name in korean_fonts:
                try:
                    font_path = font_manager.findfont(font_name)
                    if font_path:
                        self.korean_font = font_name
                        plt.rcParams['font.family'] = font_name
                        break
                except:
                    continue
                    
            if not self.korean_font:
                print("⚠️ Warning: Korean font not found, using default font")
                self.korean_font = 'DejaVu Sans'
                
        except Exception as e:
            print(f"⚠️ Font setup error: {e}")
            self.korean_font = 'DejaVu Sans'
            
    def setup_templates(self):
        """Setup Jinja2 templates for HTML generation"""
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(template_dir, exist_ok=True)
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
    def create_cbil_chart(self, cbil_scores: Dict[str, float]) -> str:
        """Create CBIL 7-level analysis bar chart"""
        try:
            # CBIL levels in Korean
            levels = [
                "단순 확인", "사실 회상", "개념 설명", 
                "분석적 사고", "종합적 이해", "평가적 판단", "창의적 적용"
            ]
            
            # Extract scores in order
            scores = [cbil_scores.get(f"level_{i+1}", 0) for i in range(7)]
            
            # Create figure with Korean font
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Color scheme for professional look
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                     '#FFEAA7', '#DDA0DD', '#98D8C8']
            
            bars = ax.bar(levels, scores, color=colors, alpha=0.8, edgecolor='white', linewidth=2)
            
            # Styling
            ax.set_ylabel('빈도 (개)', fontsize=14, weight='bold')
            ax.set_title('CBIL 7단계 인지부하 분석 결과', fontsize=16, weight='bold', pad=20)
            ax.set_ylim(0, max(scores) * 1.2 if scores else 10)
            
            # Add value labels on bars
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax.annotate(f'{score}개',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=11, weight='bold')
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Convert to base64 for HTML embedding
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error creating CBIL chart: {e}")
            return ""
    
    def create_distribution_pie_chart(self, cbil_scores: Dict[str, float]) -> str:
        """Create pie chart for CBIL distribution"""
        try:
            # Filter out zero scores
            non_zero_scores = {k: v for k, v in cbil_scores.items() if v > 0}
            
            if not non_zero_scores:
                return ""
                
            level_names = {
                "level_1": "단순 확인", "level_2": "사실 회상", "level_3": "개념 설명",
                "level_4": "분석적 사고", "level_5": "종합적 이해", 
                "level_6": "평가적 판단", "level_7": "창의적 적용"
            }
            
            labels = [level_names.get(k, k) for k in non_zero_scores.keys()]
            sizes = list(non_zero_scores.values())
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Professional colors
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                     '#FFEAA7', '#DDA0DD', '#98D8C8'][:len(labels)]
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                             autopct='%1.1f%%', startangle=90,
                                             textprops={'fontsize': 11})
            
            ax.set_title('CBIL 인지부하 분포', fontsize=16, weight='bold', pad=20)
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
            return ""
    
    def generate_recommendations(self, cbil_scores: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on CBIL analysis"""
        recommendations = []
        
        # Calculate total and percentages
        total_items = sum(cbil_scores.values())
        if total_items == 0:
            return ["분석할 데이터가 충분하지 않습니다."]
        
        # Calculate percentages for each level
        percentages = {k: (v/total_items)*100 for k, v in cbil_scores.items()}
        
        # Low-level cognitive load (levels 1-3)
        low_level = sum(percentages.get(f"level_{i}", 0) for i in [1, 2, 3])
        
        # High-level cognitive load (levels 5-7) 
        high_level = sum(percentages.get(f"level_{i}", 0) for i in [5, 6, 7])
        
        # Generate specific recommendations
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
            
        # Add general recommendations
        if len(recommendations) < 3:
            recommendations.extend([
                "🎯 학습 목표에 따라 적절한 인지부하 수준을 계획적으로 배치하세요.",
                "💡 학습자의 수준을 고려하여 점진적으로 인지부하를 높여가세요.",
                "🔄 다양한 인지부하 수준을 균형있게 활용하여 학습 효과를 극대화하세요."
            ])
            
        return recommendations[:5]  # Return top 5 recommendations
    
    def generate_pdf_report(self, analysis_data: Dict, output_path: str = None) -> bytes:
        """Generate complete PDF report"""
        try:
            # Extract CBIL scores
            cbil_scores = analysis_data.get('cbil_scores', {})
            
            # Create visualizations
            bar_chart = self.create_cbil_chart(cbil_scores)
            pie_chart = self.create_distribution_pie_chart(cbil_scores)
            recommendations = self.generate_recommendations(cbil_scores)
            
            # Prepare template data
            template_data = {
                'timestamp': datetime.now().strftime('%Y년 %m월 %d일'),
                'analysis_id': analysis_data.get('id', 'N/A'),
                'text_length': len(analysis_data.get('text', '')),
                'cbil_scores': cbil_scores,
                'total_items': sum(cbil_scores.values()),
                'bar_chart': bar_chart,
                'pie_chart': pie_chart,
                'recommendations': recommendations,
                'summary': self._generate_summary(cbil_scores)
            }
            
            # Create HTML from template
            html_content = self._render_html_template(template_data)
            
            # Convert to PDF
            pdf_bytes = self._html_to_pdf(html_content)
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                    
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            raise
    
    def _generate_summary(self, cbil_scores: Dict[str, float]) -> str:
        """Generate executive summary"""
        total = sum(cbil_scores.values())
        if total == 0:
            return "분석할 데이터가 없습니다."
            
        # Find dominant level
        max_level = max(cbil_scores.items(), key=lambda x: x[1])
        level_names = {
            "level_1": "단순 확인", "level_2": "사실 회상", "level_3": "개념 설명",
            "level_4": "분석적 사고", "level_5": "종합적 이해", 
            "level_6": "평가적 판단", "level_7": "창의적 적용"
        }
        
        dominant_level = level_names.get(max_level[0], "알 수 없음")
        percentage = (max_level[1] / total) * 100
        
        return f"수업에서 '{dominant_level}' 수준이 {percentage:.1f}%로 가장 높게 나타났습니다. 총 {total}개의 교수 언어가 분석되었습니다."
    
    def _render_html_template(self, data: Dict) -> str:
        """Render HTML template with data"""
        # Create template if it doesn't exist
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'report_template.html')
        
        if not os.path.exists(template_path):
            self._create_default_template()
            
        template = self.env.get_template('report_template.html')
        return template.render(**data)
    
    def _create_default_template(self):
        """Create default HTML template"""
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(template_dir, exist_ok=True)
        
        template_content = '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>AIBOA 교수 언어 분석 보고서</title>
    <style>
        @page { margin: 2cm; }
        body { 
            font-family: 'Nanum Gothic', sans-serif; 
            line-height: 1.6; 
            color: #333;
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #4ECDC4;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .title { 
            font-size: 24px; 
            font-weight: bold; 
            color: #2C3E50;
            margin-bottom: 10px;
        }
        .subtitle { 
            font-size: 16px; 
            color: #7F8C8D; 
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            border-radius: 8px;
        }
        .summary { background-color: #E8F6F3; }
        .analysis { background-color: #FDF2E9; }
        .recommendations { background-color: #E8F4FD; }
        h2 { 
            color: #2C3E50; 
            border-left: 4px solid #4ECDC4; 
            padding-left: 15px;
        }
        .chart-container { 
            text-align: center; 
            margin: 20px 0; 
        }
        .chart { 
            max-width: 100%; 
            height: auto; 
        }
        .recommendation-item {
            padding: 10px;
            margin: 10px 0;
            background-color: white;
            border-radius: 5px;
            border-left: 4px solid #4ECDC4;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🎓 AIBOA 교수 언어 분석 보고서</div>
        <div class="subtitle">AI 기반 교육 관찰 및 분석 플랫폼</div>
        <div style="margin-top: 15px; font-size: 14px;">
            분석일: {{ timestamp }} | 분석 ID: {{ analysis_id }}
        </div>
    </div>

    <div class="section summary">
        <h2>📊 분석 요약</h2>
        <p><strong>{{ summary }}</strong></p>
        <p>분석된 텍스트 길이: {{ text_length }}자</p>
    </div>

    <div class="section analysis">
        <h2>📈 CBIL 7단계 분석 결과</h2>
        
        {% if bar_chart %}
        <div class="chart-container">
            <h3>단계별 상세 분석</h3>
            <img src="{{ bar_chart }}" alt="CBIL 막대 그래프" class="chart">
        </div>
        {% endif %}
        
        {% if pie_chart %}
        <div class="chart-container">
            <h3>인지부하 분포</h3>
            <img src="{{ pie_chart }}" alt="CBIL 파이 차트" class="chart">
        </div>
        {% endif %}
    </div>

    <div class="section recommendations">
        <h2>💡 개선 권장사항</h2>
        {% for recommendation in recommendations %}
        <div class="recommendation-item">
            {{ recommendation }}
        </div>
        {% endfor %}
    </div>

    <div class="footer">
        <p>본 보고서는 AIBOA (AI-Based Observation and Analysis) 시스템에 의해 생성되었습니다.</p>
        <p>교육 컨설팅 문의: contact@aiboa.edu | www.aiboa.edu</p>
    </div>
</body>
</html>
        '''
        
        template_path = os.path.join(template_dir, 'report_template.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content.strip())
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        try:
            # Create CSS for better PDF styling
            css_content = """
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-size: 12pt;
            }
            """
            
            css = CSS(string=css_content)
            pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[css])
            return pdf_bytes
            
        except Exception as e:
            print(f"Error converting HTML to PDF: {e}")
            raise