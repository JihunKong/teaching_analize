#!/usr/bin/env python3
"""
ReportLab 기반 교육 컨설팅용 전문 PDF 보고서 생성기
- CBIL 7단계 분석 시각화
- 교육 전문가용 개선 권장사항
- A4 인쇄 품질 전문 디자인
"""

import io
import os
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class EducationReportGenerator:
    def __init__(self):
        self.setup_fonts()
        self.setup_matplotlib()
        
        # CBIL 7단계 정의
        self.cbil_levels = {
            1: {"name": "단순 확인", "color": colors.Color(0.91, 0.96, 0.99), "description": "기본적인 사실 확인"},
            2: {"name": "사실 회상", "color": colors.Color(0.82, 0.91, 0.87), "description": "학습 내용 기억"},
            3: {"name": "개념 설명", "color": colors.Color(1.0, 0.95, 0.8), "description": "개념 이해 및 설명"},
            4: {"name": "분석적 사고", "color": colors.Color(1.0, 0.91, 0.61), "description": "요소 분석 및 관계 파악"},
            5: {"name": "종합적 이해", "color": colors.Color(1.0, 0.67, 0.57), "description": "통합적 사고"},
            6: {"name": "평가적 판단", "color": colors.Color(1.0, 0.8, 0.82), "description": "비판적 평가"},
            7: {"name": "창의적 적용", "color": colors.Color(0.82, 0.77, 0.91), "description": "창의적 문제 해결"}
        }
        
        # 스타일 설정
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_fonts(self):
        """한글 폰트 설정"""
        try:
            # 시스템 한글 폰트 찾기
            font_paths = [
                '/System/Library/Fonts/AppleSDGothicNeo.ttc',
                '/Users/jihunkong/Library/Fonts/NanumGothic.ttf',
                '/opt/homebrew/share/fonts/NanumGothic.ttf'
            ]
            
            self.korean_font_name = 'Korean'
            font_registered = False
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont(self.korean_font_name, font_path))
                        font_registered = True
                        break
                    except:
                        continue
            
            if not font_registered:
                print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
                self.korean_font_name = 'Helvetica'
                
        except Exception as e:
            print(f"폰트 설정 실패: {e}")
            self.korean_font_name = 'Helvetica'
    
    def setup_matplotlib(self):
        """Matplotlib 설정"""
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.unicode_minus'] = False
        try:
            plt.rcParams['font.family'] = ['AppleGothic', 'DejaVu Sans']
        except:
            plt.rcParams['font.family'] = ['DejaVu Sans']
    
    def setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 제목 스타일
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.korean_font_name,
            fontSize=24,
            textColor=colors.Color(0.4, 0.49, 0.92),
            alignment=1,  # 중앙 정렬
            spaceAfter=30
        )
        
        # 섹션 제목 스타일
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontName=self.korean_font_name,
            fontSize=16,
            textColor=colors.Color(0.4, 0.49, 0.92),
            borderWidth=2,
            borderColor=colors.Color(0.4, 0.49, 0.92),
            borderPadding=5,
            leftIndent=10,
            spaceAfter=20
        )
        
        # 본문 스타일
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontName=self.korean_font_name,
            fontSize=11,
            leading=16,
            spaceAfter=12
        )
        
        # 권장사항 스타일
        self.recommendation_style = ParagraphStyle(
            'CustomRecommendation',
            parent=self.styles['Normal'],
            fontName=self.korean_font_name,
            fontSize=10,
            leading=14,
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=8
        )
    
    def create_cbil_chart_matplotlib(self, cbil_scores: Dict[str, float]) -> str:
        """Matplotlib을 사용한 CBIL 차트 생성"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 막대 그래프
        levels = list(range(1, 8))
        scores = [cbil_scores.get(str(level), 0.0) for level in levels]
        colors_hex = ['#E8F4FD', '#D1E7DD', '#FFF3CD', '#FFE69C', '#FFAB91', '#FFCDD2', '#D1C4E9']
        
        bars = ax1.bar(levels, scores, color=colors_hex, edgecolor='black', linewidth=0.5)
        
        # 값 표시
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{score:.1%}', ha='center', va='bottom', fontsize=9)
        
        ax1.set_title('CBIL 7단계 분석 결과', fontsize=14, fontweight='bold')
        ax1.set_xlabel('CBIL 레벨', fontsize=12)
        ax1.set_ylabel('비율 (%)', fontsize=12)
        ax1.set_xticks(levels)
        ax1.grid(axis='y', alpha=0.3)
        
        # 파이 차트
        low_levels = sum(cbil_scores.get(str(i), 0.0) for i in range(1, 3))
        mid_levels = sum(cbil_scores.get(str(i), 0.0) for i in range(3, 5))
        high_levels = sum(cbil_scores.get(str(i), 0.0) for i in range(5, 8))
        
        sizes = [low_levels, mid_levels, high_levels]
        labels = ['낮은 수준\n(Level 1-2)', '중간 수준\n(Level 3-4)', '높은 수준\n(Level 5-7)']
        colors_pie = ['#FFE0E0', '#FFF8DC', '#E8F5E8']
        
        # 0이 아닌 값만 필터링
        filtered_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors_pie) if size > 0]
        if filtered_data:
            sizes, labels, colors_pie = zip(*filtered_data)
            ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
        
        ax2.set_title('CBIL 수준별 분포', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 임시 파일로 저장
        chart_path = '/tmp/cbil_chart.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
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
        if cbil_scores:
            max_level = max(cbil_scores.items(), key=lambda x: x[1])
            if float(max_level[1]) > 0.5:
                recommendations.append(f"🔄 Level {max_level[0]}에 집중되어 있습니다. 다양한 사고 수준의 균형을 맞춰주세요.")
        
        return recommendations[:5]  # 최대 5개 권장사항
    
    def generate_pdf_report(self, analysis_data: Dict[str, Any], video_title: str = "분석 비디오") -> bytes:
        """PDF 보고서 생성"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        
        story = []
        
        # 제목
        title = Paragraph("🎓 AIBOA 교육 분석 보고서", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.5*cm))
        
        subtitle = Paragraph("CBIL(Cognitive Burden of Instructional Language) 7단계 분석", self.body_style)
        story.append(subtitle)
        story.append(Spacer(1, 1*cm))
        
        # 메타데이터 테이블
        metadata_data = [
            ["분석 일시", datetime.now().strftime("%Y년 %m월 %d일 %H:%M")],
            ["비디오 제목", video_title],
            ["분석 문장 수", f"{len(analysis_data.get('sentences', []))}개"],
            ["분석 방법", "AI 기반 CBIL 7단계 분류"]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[4*cm, 10*cm])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.9)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 1*cm))
        
        # 종합 결과
        overall_score = analysis_data.get('overall_score', 0.0)
        story.append(Paragraph("📊 종합 분석 결과", self.section_style))
        
        score_text = f"<para align=center><font size=36 color='#4169E1'><b>{overall_score:.1f}/7.0</b></font><br/><font size=14>전체 CBIL 평균 점수</font></para>"
        story.append(Paragraph(score_text, self.body_style))
        story.append(Spacer(1, 1*cm))
        
        # 차트 생성 및 삽입
        cbil_scores = analysis_data.get('cbil_scores', {})
        chart_path = self.create_cbil_chart_matplotlib(cbil_scores)
        
        story.append(Paragraph("📈 CBIL 7단계 상세 분석", self.section_style))
        
        # 차트 이미지 삽입
        if os.path.exists(chart_path):
            chart_img = Image(chart_path, width=15*cm, height=6*cm)
            story.append(chart_img)
            story.append(Spacer(1, 1*cm))
        
        # 레벨별 상세 정보 테이블
        level_data = [["레벨", "명칭", "비율", "설명"]]
        for level in range(1, 8):
            level_str = str(level)
            score = cbil_scores.get(level_str, 0.0)
            level_data.append([
                f"Level {level}",
                self.cbil_levels[level]['name'],
                f"{score:.1%}",
                self.cbil_levels[level]['description']
            ])
        
        level_table = Table(level_data, colWidths=[2*cm, 3*cm, 2*cm, 7*cm])
        level_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.4, 0.49, 0.92)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(level_table)
        story.append(Spacer(1, 1*cm))
        
        # 권장사항
        story.append(Paragraph("💡 교육 개선 권장사항", self.section_style))
        
        recommendations = self.generate_recommendations(cbil_scores, overall_score)
        
        for i, rec in enumerate(recommendations, 1):
            rec_text = f"{i}. {rec}"
            story.append(Paragraph(rec_text, self.recommendation_style))
        
        story.append(Spacer(1, 2*cm))
        
        # 푸터
        footer_text = f"본 보고서는 AIBOA 시스템에 의해 자동 생성되었습니다 | 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer = Paragraph(footer_text, self.body_style)
        story.append(footer)
        
        # PDF 빌드
        doc.build(story)
        
        # 임시 차트 파일 삭제
        if os.path.exists(chart_path):
            os.remove(chart_path)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def save_pdf_report(self, analysis_data: Dict[str, Any], output_path: str, video_title: str = "분석 비디오"):
        """PDF 보고서 파일로 저장"""
        pdf_bytes = self.generate_pdf_report(analysis_data, video_title)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return output_path

# 테스트 함수
def test_pdf_generation():
    generator = EducationReportGenerator()
    
    # 샘플 CBIL 분석 데이터 (더 현실적인 교육용 데이터)
    sample_data = {
        'cbil_scores': {
            '1': 0.12,  # 단순 확인
            '2': 0.18,  # 사실 회상  
            '3': 0.28,  # 개념 설명
            '4': 0.22,  # 분석적 사고
            '5': 0.12,  # 종합적 이해
            '6': 0.06,  # 평가적 판단
            '7': 0.02   # 창의적 적용
        },
        'overall_score': 3.2,
        'sentences': ['교육 문장 예시'] * 25  # 25개 문장 분석
    }
    
    pdf_path = "/tmp/aiboa_education_report.pdf"
    generator.save_pdf_report(sample_data, pdf_path, "수학 개념 설명 수업 - CBIL 분석")
    print(f"✅ 교육 컨설팅용 PDF 보고서 생성 완료: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    test_pdf_generation()