"""
Advanced PDF Report Generator with Chart Rendering
Generates professional PDF reports with embedded matplotlib charts
"""

import os
import io
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64

# PDF generation
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Chart rendering
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import numpy as np

logger = logging.getLogger(__name__)


class AdvancedPDFGenerator:
    """Generate PDF reports with rendered charts using matplotlib"""

    def __init__(self):
        """Initialize PDF generator with default settings"""
        self.font_config = FontConfiguration()
        self.dpi = 150  # High quality for PDF

        # Chart color schemes
        self.colors = {
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#4BC0C0',
            'warning': '#FFCE56',
            'danger': '#FF6384',
            'info': '#36A2EB'
        }

        # Set matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
        plt.rcParams['axes.unicode_minus'] = False

    def generate_pdf_with_charts(
        self,
        analysis_data: Dict[str, Any],
        include_cover: bool = True
    ) -> bytes:
        """
        Generate PDF report with rendered charts

        Args:
            analysis_data: Analysis result data
            include_cover: Include professional cover page

        Returns:
            PDF file as bytes
        """
        try:
            logger.info(f"Generating PDF report for {analysis_data.get('analysis_id', 'unknown')}")

            framework = analysis_data.get('framework', 'generic')

            # Generate charts based on framework
            chart_images = self._generate_chart_images(analysis_data, framework)

            # Generate HTML with embedded chart images
            html_content = self._generate_html_with_charts(
                analysis_data,
                chart_images,
                include_cover
            )

            # Convert to PDF
            pdf_bytes = self._html_to_pdf(html_content)

            logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise

    def _generate_chart_images(
        self,
        analysis_data: Dict[str, Any],
        framework: str
    ) -> Dict[str, str]:
        """
        Generate chart images as base64-encoded data URLs

        Args:
            analysis_data: Analysis result data
            framework: Framework type

        Returns:
            Dictionary of chart_name -> base64 data URL
        """
        chart_images = {}

        try:
            if framework == 'cbil':
                # CBIL radar chart
                cbil_chart = self._render_cbil_radar_chart(analysis_data)
                if cbil_chart:
                    chart_images['cbil_radar'] = cbil_chart

            elif framework == 'cbil_comprehensive':
                # CBIL comprehensive: radar + bar charts
                result_data = analysis_data.get('result', analysis_data)

                # CBIL radar chart
                cbil_chart = self._render_cbil_comprehensive_radar(result_data)
                if cbil_chart:
                    chart_images['cbil_radar'] = cbil_chart

                # Module 3 metrics bar chart
                metrics_chart = self._render_module3_metrics_bar(result_data)
                if metrics_chart:
                    chart_images['metrics_bar'] = metrics_chart

            elif framework == 'student_discussion':
                # Student discussion bar chart
                discussion_chart = self._render_discussion_chart(analysis_data)
                if discussion_chart:
                    chart_images['discussion_bar'] = discussion_chart

            else:
                # Generic bar chart
                generic_chart = self._render_generic_chart(analysis_data)
                if generic_chart:
                    chart_images['generic_bar'] = generic_chart

            logger.info(f"Generated {len(chart_images)} chart images")
            return chart_images

        except Exception as e:
            logger.error(f"Chart generation failed: {str(e)}")
            return {}

    def _render_cbil_radar_chart(self, analysis_data: Dict[str, Any]) -> Optional[str]:
        """Render CBIL 7-stage radar chart"""
        try:
            # Extract CBIL scores from analysis text
            from html_report_generator import HTMLReportGenerator
            generator = HTMLReportGenerator()
            chart_data = generator._extract_cbil_data(analysis_data.get('analysis', ''))

            if not chart_data or not chart_data.get('data'):
                return None

            labels = chart_data['labels']
            values = chart_data['data']

            # Create radar chart
            fig = Figure(figsize=(8, 6), dpi=self.dpi)
            ax = fig.add_subplot(111, projection='polar')

            # Number of variables
            num_vars = len(labels)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            values_plot = values + [values[0]]  # Close the plot
            angles += angles[:1]

            # Plot
            ax.plot(angles, values_plot, 'o-', linewidth=2, color=self.colors['primary'])
            ax.fill(angles, values_plot, alpha=0.25, color=self.colors['primary'])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, size=10)
            ax.set_ylim(0, 100)
            ax.set_yticks([25, 50, 75, 100])
            ax.set_yticklabels(['25', '50', '75', '100'], size=8)
            ax.grid(True)
            ax.set_title('CBIL 7단계 점수', size=14, weight='bold', pad=20)

            # Convert to base64
            return self._fig_to_base64(fig)

        except Exception as e:
            logger.error(f"CBIL radar chart rendering failed: {str(e)}")
            return None

    def _render_cbil_comprehensive_radar(self, result_data: Dict[str, Any]) -> Optional[str]:
        """Render CBIL comprehensive radar chart"""
        try:
            cbil_insights = result_data.get('coaching_feedback', {}).get('cbil_insights', {})
            cbil_scores = cbil_insights.get('cbil_scores', {})
            stage_scores = cbil_scores.get('stage_scores', {})

            if not stage_scores:
                return None

            # Prepare data
            stages = ["Engage", "Focus", "Investigate", "Organize", "Generalize", "Transfer", "Reflect"]
            values = []

            for stage in ["engage", "focus", "investigate", "organize", "generalize", "transfer", "reflect"]:
                stage_data = stage_scores.get(stage, {})
                score = stage_data.get('score', 0)
                # Normalize to 0-100
                normalized = (score / 3.0) * 100
                values.append(normalized)

            # Create radar chart
            fig = Figure(figsize=(8, 6), dpi=self.dpi)
            ax = fig.add_subplot(111, projection='polar')

            num_vars = len(stages)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            values_plot = values + [values[0]]
            angles += angles[:1]

            ax.plot(angles, values_plot, 'o-', linewidth=2, color=self.colors['primary'])
            ax.fill(angles, values_plot, alpha=0.25, color=self.colors['primary'])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(stages, size=10)
            ax.set_ylim(0, 100)
            ax.set_yticks([25, 50, 75, 100])
            ax.set_yticklabels(['25', '50', '75', '100'], size=8)
            ax.grid(True)
            ax.set_title('CBIL 7단계 점수', size=14, weight='bold', pad=20)

            return self._fig_to_base64(fig)

        except Exception as e:
            logger.error(f"CBIL comprehensive radar rendering failed: {str(e)}")
            return None

    def _render_module3_metrics_bar(self, result_data: Dict[str, Any]) -> Optional[str]:
        """Render Module 3 metrics bar chart"""
        try:
            metrics = result_data.get('quantitative_metrics', {})

            if not metrics:
                return None

            # Get top 10 metrics
            metric_items = list(metrics.items())[:10]
            labels = [name.replace('_', ' ').title() for name, _ in metric_items]
            values = [data.get('normalized_score', 0) for _, data in metric_items]

            # Create bar chart
            fig = Figure(figsize=(10, 6), dpi=self.dpi)
            ax = fig.add_subplot(111)

            y_pos = np.arange(len(labels))
            bars = ax.barh(y_pos, values, color=self.colors['success'])

            # Color code by value
            for i, (bar, value) in enumerate(zip(bars, values)):
                if value >= 80:
                    bar.set_color(self.colors['success'])
                elif value >= 60:
                    bar.set_color(self.colors['info'])
                else:
                    bar.set_color(self.colors['warning'])

            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels, size=9)
            ax.set_xlabel('점수 (0-100)', size=10)
            ax.set_xlim(0, 100)
            ax.set_title('Module 3 정량 지표 (Top 10)', size=14, weight='bold', pad=15)
            ax.grid(axis='x', alpha=0.3)

            # Add value labels
            for i, v in enumerate(values):
                ax.text(v + 2, i, f'{v:.1f}', va='center', size=8)

            fig.tight_layout()
            return self._fig_to_base64(fig)

        except Exception as e:
            logger.error(f"Module 3 metrics bar chart rendering failed: {str(e)}")
            return None

    def _render_discussion_chart(self, analysis_data: Dict[str, Any]) -> Optional[str]:
        """Render student discussion bar chart"""
        try:
            from html_report_generator import HTMLReportGenerator
            generator = HTMLReportGenerator()
            chart_data = generator._extract_discussion_data(analysis_data.get('analysis', ''))

            if not chart_data or not chart_data.get('data'):
                return None

            labels = chart_data['labels']
            values = chart_data['data']

            fig = Figure(figsize=(10, 6), dpi=self.dpi)
            ax = fig.add_subplot(111)

            x_pos = np.arange(len(labels))
            bars = ax.bar(x_pos, values, color=self.colors['info'])

            ax.set_xticks(x_pos)
            ax.set_xticklabels(labels, rotation=45, ha='right', size=9)
            ax.set_ylabel('빈도', size=10)
            ax.set_title('학생주도 질문과 대화 분석', size=14, weight='bold', pad=15)
            ax.grid(axis='y', alpha=0.3)

            fig.tight_layout()
            return self._fig_to_base64(fig)

        except Exception as e:
            logger.error(f"Discussion chart rendering failed: {str(e)}")
            return None

    def _render_generic_chart(self, analysis_data: Dict[str, Any]) -> Optional[str]:
        """Render generic bar chart"""
        try:
            from html_report_generator import HTMLReportGenerator
            generator = HTMLReportGenerator()
            framework = analysis_data.get('framework', 'generic')
            chart_data = generator._extract_generic_data(analysis_data.get('analysis', ''), framework)

            if not chart_data or not chart_data.get('data'):
                return None

            labels = chart_data['labels']
            values = chart_data['data']

            fig = Figure(figsize=(10, 6), dpi=self.dpi)
            ax = fig.add_subplot(111)

            x_pos = np.arange(len(labels))
            ax.bar(x_pos, values, color=self.colors['primary'])

            ax.set_xticks(x_pos)
            ax.set_xticklabels(labels, rotation=45, ha='right', size=9)
            ax.set_ylabel('값', size=10)
            ax.set_title(chart_data.get('title', '분석 결과'), size=14, weight='bold', pad=15)
            ax.grid(axis='y', alpha=0.3)

            fig.tight_layout()
            return self._fig_to_base64(fig)

        except Exception as e:
            logger.error(f"Generic chart rendering failed: {str(e)}")
            return None

    def _fig_to_base64(self, fig: Figure) -> str:
        """Convert matplotlib figure to base64 data URL"""
        try:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight', facecolor='white')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            logger.error(f"Figure to base64 conversion failed: {str(e)}")
            plt.close(fig)
            return ""

    def _generate_html_with_charts(
        self,
        analysis_data: Dict[str, Any],
        chart_images: Dict[str, str],
        include_cover: bool
    ) -> str:
        """Generate HTML content with embedded chart images"""

        framework = analysis_data.get('framework', 'generic')
        framework_names = {
            "cbil": "개념기반 탐구 수업(CBIL) 분석",
            "cbil_comprehensive": "CBIL + Module 3 종합 분석",
            "student_discussion": "학생주도 질문과 대화 및 토론 수업",
            "lesson_coaching": "수업 설계와 실행 코칭"
        }
        framework_name = framework_names.get(framework, framework)

        result_data = analysis_data.get('result', analysis_data)
        analysis_text = result_data.get('cbil_analysis_text', analysis_data.get('analysis', ''))
        timestamp = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        analysis_id = analysis_data.get('analysis_id', 'N/A')

        # Cover page HTML
        cover_html = ""
        if include_cover:
            cover_html = self._generate_cover_page_html(framework_name, timestamp, analysis_id)

        # Chart sections
        charts_html = ""
        if 'cbil_radar' in chart_images:
            charts_html += f'''
            <div class="chart-container">
                <img src="{chart_images['cbil_radar']}" alt="CBIL Radar Chart" style="max-width: 100%; height: auto;">
            </div>
            '''

        if 'metrics_bar' in chart_images:
            charts_html += f'''
            <div class="chart-container">
                <img src="{chart_images['metrics_bar']}" alt="Module 3 Metrics" style="max-width: 100%; height: auto;">
            </div>
            '''

        if 'discussion_bar' in chart_images:
            charts_html += f'''
            <div class="chart-container">
                <img src="{chart_images['discussion_bar']}" alt="Discussion Analysis" style="max-width: 100%; height: auto;">
            </div>
            '''

        if 'generic_bar' in chart_images:
            charts_html += f'''
            <div class="chart-container">
                <img src="{chart_images['generic_bar']}" alt="Analysis Chart" style="max-width: 100%; height: auto;">
            </div>
            '''

        # Analysis content
        analysis_html = f'<pre class="analysis-text">{analysis_text}</pre>'

        # Complete HTML
        html = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{framework_name} - AIBOA 분석 보고서</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-right {{
                content: "페이지 " counter(page) " / " counter(pages);
                font-size: 10px;
                color: #666;
            }}
        }}

        body {{
            font-family: 'Nanum Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }}

        .cover-page {{
            page-break-after: always;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}

        .cover-title {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 30px;
        }}

        .cover-subtitle {{
            font-size: 24px;
            color: #666;
            margin-bottom: 50px;
        }}

        .cover-meta {{
            font-size: 14px;
            color: #999;
        }}

        .report-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }}

        .report-title {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .report-meta {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .chart-container {{
            margin: 30px 0;
            page-break-inside: avoid;
            text-align: center;
        }}

        .analysis-text {{
            font-size: 11px;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
            padding: 20px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2C3E50;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 15px;
            border-left: 5px solid #667eea;
        }}
    </style>
</head>
<body>
    {cover_html}

    <div class="report-header">
        <div class="report-title">{framework_name}</div>
        <div class="report-meta">
            분석 ID: {analysis_id} | 생성 시간: {timestamp}
        </div>
    </div>

    <div class="section-title">📊 시각화 분석</div>
    {charts_html}

    <div class="section-title">📝 상세 분석 결과</div>
    {analysis_html}
</body>
</html>
'''

        return html

    def _generate_cover_page_html(
        self,
        framework_name: str,
        timestamp: str,
        analysis_id: str
    ) -> str:
        """Generate professional cover page HTML"""
        return f'''
    <div class="cover-page">
        <div class="cover-title">AIBOA 교육 분석 보고서</div>
        <div class="cover-subtitle">{framework_name}</div>
        <div class="cover-meta">
            <p>분석 ID: {analysis_id}</p>
            <p>생성 일시: {timestamp}</p>
            <p style="margin-top: 50px; font-size: 12px;">
                Powered by AIBOA - AI-Based Observatory for Analysis
            </p>
        </div>
    </div>
'''

    def _html_to_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint"""
        try:
            # Create PDF
            pdf = HTML(string=html_content).write_pdf(
                font_config=self.font_config
            )
            return pdf
        except Exception as e:
            logger.error(f"HTML to PDF conversion failed: {str(e)}")
            raise


# ============ Demo/Test Code ============

if __name__ == "__main__":
    print("=" * 60)
    print("Advanced PDF Generator Demo")
    print("=" * 60)
    print("\nThis module generates PDF reports with rendered charts.")
    print("Usage: Import and use in main.py endpoints")
    print("\nFeatures:")
    print("  ✓ Matplotlib chart rendering")
    print("  ✓ Professional cover pages")
    print("  ✓ Multi-framework support")
    print("  ✓ High-quality output (150 DPI)")
    print("\n" + "=" * 60)
