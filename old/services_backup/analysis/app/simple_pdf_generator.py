"""
Simple PDF Report Generator for CBIL Teaching Analysis
Uses only ReportLab for PDF generation without external chart dependencies
"""

import os
from datetime import datetime
from typing import Dict, List
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class SimpleCBILReportGenerator:
    """Generate professional PDF reports for CBIL analysis using only ReportLab"""
    
    def __init__(self):
        self.setup_styles()
        
    def setup_styles(self):
        """Setup ReportLab styles"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='Title',
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # CENTER
            textColor=HexColor('#2C3E50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading1',
            fontSize=18,
            spaceAfter=12,
            textColor=HexColor('#4ECDC4'),
            borderLeft=4,
            leftIndent=15
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2',
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor('#2C3E50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Summary',
            fontSize=12,
            spaceAfter=12,
            backgroundColor=HexColor('#E8F6F3'),
            borderPadding=10
        ))
        
    def create_cbil_table(self, cbil_scores: Dict[str, float]) -> Table:
        """Create a table showing CBIL scores"""
        level_names = [
            "단순 확인", "사실 회상", "개념 설명", 
            "분석적 사고", "종합적 이해", "평가적 판단", "창의적 적용"
        ]
        
        # Prepare table data
        data = [['CBIL 단계', '개수', '비율']]
        total = sum(cbil_scores.values()) or 1
        
        for i, level_name in enumerate(level_names, 1):
            count = cbil_scores.get(f"level_{i}", 0)
            percentage = (count / total) * 100
            data.append([
                level_name,
                f"{count}개",
                f"{percentage:.1f}%"
            ])
        
        # Create table
        table = Table(data, colWidths=[5*cm, 2*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4ECDC4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F9FA')])
        ]))
        
        return table
        
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
                "• 현재 수업이 단순 확인과 사실 회상 중심입니다. "
                "학습자의 분석적 사고를 촉진하는 질문을 더 많이 활용해보세요."
            )
            
        if high_level < 20:
            recommendations.append(
                "• 창의적 사고와 평가적 판단을 요구하는 활동을 늘려 "
                "학습자의 고차원적 사고력을 발달시켜보세요."
            )
            
        if percentages.get("level_4", 0) > 30:
            recommendations.append(
                "• 분석적 사고 활동이 활발합니다. "
                "이를 종합적 이해로 연결하는 브리지 질문을 추가해보세요."
            )
            
        # Add general recommendations
        if len(recommendations) < 3:
            recommendations.extend([
                "• 학습 목표에 따라 적절한 인지부하 수준을 계획적으로 배치하세요.",
                "• 학습자의 수준을 고려하여 점진적으로 인지부하를 높여가세요.",
                "• 다양한 인지부하 수준을 균형있게 활용하여 학습 효과를 극대화하세요."
            ])
            
        return recommendations[:5]  # Return top 5 recommendations
    
    def generate_summary(self, cbil_scores: Dict[str, float]) -> str:
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
    
    def generate_pdf_report(self, analysis_data: Dict, output_path: str = None) -> bytes:
        """Generate complete PDF report"""
        try:
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
            
            # Extract CBIL scores
            cbil_scores = analysis_data.get('cbil_scores', {})
            
            # Build story (content)
            story = []
            
            # Title
            story.append(Paragraph("🎓 AIBOA 교수 언어 분석 보고서", self.styles['Title']))
            story.append(Paragraph("AI 기반 교육 관찰 및 분석 플랫폼", self.styles['Normal']))
            story.append(Spacer(1, 0.5*cm))
            
            # Analysis info
            timestamp = datetime.now().strftime('%Y년 %m월 %d일')
            analysis_id = analysis_data.get('id', 'N/A')
            info_text = f"분석일: {timestamp} | 분석 ID: {analysis_id}"
            story.append(Paragraph(info_text, self.styles['Normal']))
            story.append(Spacer(1, 1*cm))
            
            # Summary section
            summary = self.generate_summary(cbil_scores)
            story.append(Paragraph("📊 분석 요약", self.styles['Heading1']))
            story.append(Paragraph(summary, self.styles['Summary']))
            story.append(Spacer(1, 0.5*cm))
            
            # Text info
            text_length = len(analysis_data.get('text', ''))
            story.append(Paragraph(f"분석된 텍스트 길이: {text_length}자", self.styles['Normal']))
            story.append(Spacer(1, 1*cm))
            
            # CBIL Analysis Results
            story.append(Paragraph("📈 CBIL 7단계 분석 결과", self.styles['Heading1']))
            story.append(Spacer(1, 0.5*cm))
            
            # CBIL table
            cbil_table = self.create_cbil_table(cbil_scores)
            story.append(cbil_table)
            story.append(Spacer(1, 1*cm))
            
            # Recommendations
            recommendations = self.generate_recommendations(cbil_scores)
            story.append(Paragraph("💡 개선 권장사항", self.styles['Heading1']))
            story.append(Spacer(1, 0.5*cm))
            
            for recommendation in recommendations:
                story.append(Paragraph(recommendation, self.styles['Normal']))
                story.append(Spacer(1, 0.3*cm))
            
            story.append(Spacer(1, 1*cm))
            
            # Footer
            footer_text = (
                "본 보고서는 AIBOA (AI-Based Observation and Analysis) 시스템에 의해 생성되었습니다.<br/>"
                "교육 컨설팅 문의: contact@aiboa.edu | www.aiboa.edu"
            )
            story.append(Paragraph(footer_text, self.styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                    
            return pdf_bytes
            
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            raise