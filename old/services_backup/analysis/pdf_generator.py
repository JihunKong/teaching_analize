#!/usr/bin/env python3
"""
교육 컨설팅용 전문 PDF 보고서 생성기
- CBIL 7단계 분석 시각화
- 교육 전문가용 개선 권장사항
- A4 인쇄 품질 전문 디자인
"""

import os
import io
import base64
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
import numpy as np
from jinja2 import Template
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class EducationReportGenerator:
    def __init__(self):
        self.setup_korean_fonts()
        self.setup_matplotlib()
        
        # CBIL 7단계 정의
        self.cbil_levels = {
            1: {"name": "단순 확인", "color": "#E8F4FD", "description": "기본적인 사실 확인"},
            2: {"name": "사실 회상", "color": "#D1E7DD", "description": "학습 내용 기억"},
            3: {"name": "개념 설명", "color": "#FFF3CD", "description": "개념 이해 및 설명"},
            4: {"name": "분석적 사고", "color": "#FFE69C", "description": "요소 분석 및 관계 파악"},
            5: {"name": "종합적 이해", "color": "#FFAB91", "description": "통합적 사고"},
            6: {"name": "평가적 판단", "color": "#FFCDD2", "description": "비판적 평가"},
            7: {"name": "창의적 적용", "color": "#D1C4E9", "description": "창의적 문제 해결"}
        }
    
    def setup_korean_fonts(self):
        """한글 폰트 설정"""
        try:
            # macOS/Windows 공통 한글 폰트 찾기
            available_fonts = fm.findSystemFonts()
            korean_fonts = [
                'AppleSDGothicNeo-Regular',
                'Malgun Gothic',
                'NanumGothic',
                'DejaVu Sans'
            ]
            
            self.korean_font = None
            for font_name in korean_fonts:
                try:
                    if any(font_name in path for path in available_fonts):
                        self.korean_font = font_name
                        break
                except:
                    continue
            
            if not self.korean_font:
                self.korean_font = 'DejaVu Sans'  # fallback
                
        except Exception as e:
            print(f"폰트 설정 실패: {e}")
            self.korean_font = 'DejaVu Sans'
    
    def setup_matplotlib(self):
        """Matplotlib 설정"""
        rcParams['font.family'] = 'sans-serif'
        rcParams['font.sans-serif'] = [self.korean_font, 'DejaVu Sans']
        rcParams['axes.unicode_minus'] = False
        plt.style.use('seaborn-v0_8-whitegrid')
    
    def create_cbil_bar_chart(self, cbil_scores: Dict[str, float]) -> str:
        """CBIL 7단계 막대 그래프 생성"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        levels = list(range(1, 8))
        scores = [cbil_scores.get(str(level), 0.0) for level in levels]
        colors = [self.cbil_levels[level]["color"] for level in levels]
        level_names = [f"Level {level}\n{self.cbil_levels[level]['name']}" for level in levels]
        
        bars = ax.bar(level_names, scores, color=colors, edgecolor='#333333', linewidth=1)
        
        # 값 표시
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{score:.1%}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_title('CBIL 7단계 분석 결과', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('비율 (%)', fontsize=12)
        ax.set_ylim(0, max(scores) * 1.2 if scores else 1)
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Base64 인코딩
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def create_cbil_pie_chart(self, cbil_scores: Dict[str, float]) -> str:
        """CBIL 분포 파이 차트 생성"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # 낮음/중간/높음 그룹화
        low_levels = sum(cbil_scores.get(str(i), 0.0) for i in range(1, 3))
        mid_levels = sum(cbil_scores.get(str(i), 0.0) for i in range(3, 5))
        high_levels = sum(cbil_scores.get(str(i), 0.0) for i in range(5, 8))
        
        sizes = [low_levels, mid_levels, high_levels]
        labels = ['낮은 수준\n(Level 1-2)', '중간 수준\n(Level 3-4)', '높은 수준\n(Level 5-7)']
        colors = ['#FFE0E0', '#FFF8DC', '#E8F5E8']
        
        # 비어있는 값 제거
        filtered_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
        if filtered_data:
            sizes, labels, colors = zip(*filtered_data)
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 11})
        
        ax.set_title('CBIL 수준별 분포', fontsize=16, fontweight='bold', pad=20)
        
        # Base64 인코딩
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def generate_recommendations(self, cbil_scores: Dict[str, float], overall_score: float) -> List[str]:
        """교육 개선 권장사항 생성"""
        recommendations = []
        
        # 전체 점수 기반 권장사항
        if overall_score < 2.5:
            recommendations.append("📈 기초 단계: 학습자의 기본 이해도를 높이는 활동을 늘려주세요.")
        elif overall_score < 4.0:
            recommendations.append("🎯 발전 단계: 분석적 사고를 촉진하는 질문을 추가해주세요.")
        else:
            recommendations.append("⭐ 우수 단계: 창의적 적용 기회를 더 많이 제공해주세요.")
        
        # 개별 레벨 분석
        high_levels = [5, 6, 7]
        high_level_total = sum(cbil_scores.get(str(level), 0.0) for level in high_levels)
        
        if high_level_total < 0.2:
            recommendations.append("🧠 고차원적 사고(Level 5-7)를 유도하는 질문을 늘려주세요.")
        
        if cbil_scores.get('7', 0.0) < 0.1:
            recommendations.append("💡 창의적 문제 해결 기회를 제공하여 Level 7 활동을 증진시켜주세요.")
        
        if cbil_scores.get('1', 0.0) > 0.4:
            recommendations.append("⚖️ 단순 확인 질문(Level 1)을 줄이고 더 도전적인 질문으로 발전시켜주세요.")
        
        # 균형 분석
        max_level = max(cbil_scores.items(), key=lambda x: x[1]) if cbil_scores else ('1', 0)
        if float(max_level[1]) > 0.5:
            recommendations.append(f"🔄 Level {max_level[0]}에 집중되어 있습니다. 다양한 사고 수준의 균형을 맞춰주세요.")
        
        return recommendations[:5]  # 최대 5개 권장사항
    
    def create_html_template(self) -> str:
        """HTML 템플릿 생성"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIBOA 교육 분석 보고서</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "AIBOA 교육 분석 보고서";
                font-family: "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-family: "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: "Apple SD Gothic Neo", "Malgun Gothic", "NanumGothic", sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
        }
        
        .header h1 {
            margin: 0;
            font-size: 24pt;
            font-weight: bold;
        }
        
        .header .subtitle {
            font-size: 14pt;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        .metadata {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            border-left: 4px solid #667eea;
        }
        
        .metadata table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .metadata td {
            padding: 0.5rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .metadata td:first-child {
            font-weight: bold;
            width: 30%;
            color: #495057;
        }
        
        .section {
            margin-bottom: 2rem;
            page-break-inside: avoid;
        }
        
        .section h2 {
            color: #667eea;
            font-size: 18pt;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #667eea;
        }
        
        .score-highlight {
            text-align: center;
            background: #e8f4fd;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 2px solid #667eea;
        }
        
        .score-highlight .score {
            font-size: 36pt;
            font-weight: bold;
            color: #667eea;
            margin: 0;
        }
        
        .score-highlight .description {
            font-size: 14pt;
            color: #495057;
            margin-top: 0.5rem;
        }
        
        .chart-container {
            text-align: center;
            margin: 2rem 0;
            page-break-inside: avoid;
        }
        
        .chart-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            background: white;
        }
        
        .recommendations {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .recommendations h3 {
            color: #856404;
            margin-top: 0;
            font-size: 16pt;
        }
        
        .recommendations ul {
            margin: 0;
            padding-left: 1.5rem;
        }
        
        .recommendations li {
            margin-bottom: 0.8rem;
            line-height: 1.7;
        }
        
        .footer {
            margin-top: 3rem;
            text-align: center;
            font-size: 10pt;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
            padding-top: 1rem;
        }
        
        .level-detail {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .level-card {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        
        .level-card .level-number {
            font-size: 24pt;
            font-weight: bold;
            color: #667eea;
        }
        
        .level-card .level-name {
            font-size: 14pt;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .level-card .level-score {
            font-size: 18pt;
            color: #28a745;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎓 AIBOA 교육 분석 보고서</h1>
        <div class="subtitle">CBIL(Cognitive Burden of Instructional Language) 7단계 분석</div>
    </div>
    
    <div class="metadata">
        <table>
            <tr>
                <td>분석 일시</td>
                <td>{{ analysis_date }}</td>
            </tr>
            <tr>
                <td>비디오 제목</td>
                <td>{{ video_title }}</td>
            </tr>
            <tr>
                <td>분석 문장 수</td>
                <td>{{ sentence_count }}개</td>
            </tr>
            <tr>
                <td>분석 방법</td>
                <td>AI 기반 CBIL 7단계 분류</td>
            </tr>
        </table>
    </div>
    
    <div class="section">
        <h2>📊 종합 분석 결과</h2>
        <div class="score-highlight">
            <div class="score">{{ overall_score }}/7.0</div>
            <div class="description">전체 CBIL 평균 점수</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📈 CBIL 7단계 상세 분석</h2>
        <div class="chart-container">
            <img src="{{ bar_chart }}" alt="CBIL 7단계 막대 그래프">
        </div>
        
        <div class="level-detail">
            {% for level, data in level_details.items() %}
            <div class="level-card">
                <div class="level-number">{{ level }}</div>
                <div class="level-name">{{ data.name }}</div>
                <div class="level-score">{{ "%.1f"|format(data.score * 100) }}%</div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <div class="section">
        <h2>🥧 수준별 분포</h2>
        <div class="chart-container">
            <img src="{{ pie_chart }}" alt="CBIL 수준별 분포 파이 차트">
        </div>
    </div>
    
    <div class="section">
        <h2>💡 교육 개선 권장사항</h2>
        <div class="recommendations">
            <h3>🎯 맞춤형 개선 방안</h3>
            <ul>
                {% for recommendation in recommendations %}
                <li>{{ recommendation }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    
    <div class="footer">
        <p>본 보고서는 AIBOA 시스템에 의해 자동 생성되었습니다 | 생성 시간: {{ generation_time }}</p>
        <p>교육 컨설팅 및 문의: aiboa@example.com</p>
    </div>
</body>
</html>
        """
    
    def generate_pdf_report(self, analysis_data: Dict[str, Any], video_title: str = "분석 비디오") -> bytes:
        """PDF 보고서 생성"""
        try:
            # 데이터 추출
            cbil_scores = analysis_data.get('cbil_scores', {})
            overall_score = analysis_data.get('overall_score', 0.0)
            
            # 차트 생성
            bar_chart = self.create_cbil_bar_chart(cbil_scores)
            pie_chart = self.create_cbil_pie_chart(cbil_scores)
            
            # 권장사항 생성
            recommendations = self.generate_recommendations(cbil_scores, overall_score)
            
            # 레벨 상세 정보
            level_details = {}
            for level in range(1, 8):
                level_str = str(level)
                score = cbil_scores.get(level_str, 0.0)
                level_details[level] = {
                    'name': self.cbil_levels[level]['name'],
                    'score': score,
                    'description': self.cbil_levels[level]['description']
                }
            
            # HTML 템플릿 렌더링
            template = Template(self.create_html_template())
            html_content = template.render(
                analysis_date=datetime.now().strftime("%Y년 %m월 %d일 %H:%M"),
                video_title=video_title,
                sentence_count=len(analysis_data.get('sentences', [])),
                overall_score=f"{overall_score:.1f}",
                bar_chart=bar_chart,
                pie_chart=pie_chart,
                level_details=level_details,
                recommendations=recommendations,
                generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # PDF 생성
            font_config = FontConfiguration()
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(font_config=font_config)
            
            return pdf_bytes
            
        except Exception as e:
            print(f"PDF 생성 실패: {e}")
            raise
    
    def save_pdf_report(self, analysis_data: Dict[str, Any], output_path: str, video_title: str = "분석 비디오"):
        """PDF 보고서 파일로 저장"""
        pdf_bytes = self.generate_pdf_report(analysis_data, video_title)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return output_path

# 테스트 데이터로 샘플 PDF 생성
def test_pdf_generation():
    generator = EducationReportGenerator()
    
    # 샘플 CBIL 분석 데이터
    sample_data = {
        'cbil_scores': {
            '1': 0.15,
            '2': 0.25, 
            '3': 0.30,
            '4': 0.20,
            '5': 0.08,
            '6': 0.02,
            '7': 0.00
        },
        'overall_score': 2.87,
        'sentences': ['문장1', '문장2', '문장3'] * 10
    }
    
    pdf_path = "/tmp/aiboa_sample_report.pdf"
    generator.save_pdf_report(sample_data, pdf_path, "샘플 교육 영상 분석")
    print(f"✅ 샘플 PDF 생성 완료: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    test_pdf_generation()