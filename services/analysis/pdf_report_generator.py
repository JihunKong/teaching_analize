"""
PDF Report Generator using weasyprint
Converts HTML reports to PDF for download
"""

import os
import tempfile
import logging
from typing import Dict, Any
from datetime import datetime

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from html_report_generator import HTMLReportGenerator

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Generate PDF reports from HTML analysis reports"""
    
    def __init__(self):
        if not WEASYPRINT_AVAILABLE:
            logger.warning("WeasyPrint not available. PDF generation will be disabled.")
        
        self.html_generator = HTMLReportGenerator()
        
        # Configure fonts if weasyprint is available
        if WEASYPRINT_AVAILABLE:
            self.font_config = FontConfiguration()
    
    def generate_pdf_report(self, analysis_data: Dict[str, Any]) -> bytes:
        """
        Generate PDF report from analysis data
        
        Args:
            analysis_data: Analysis result data
            
        Returns:
            PDF content as bytes
            
        Raises:
            RuntimeError: If WeasyPrint is not available
            Exception: If PDF generation fails
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("WeasyPrint is not installed. Install with: pip install weasyprint")
        
        try:
            # Generate HTML content
            html_content = self.html_generator.generate_html_report(analysis_data)
            
            # Create PDF-optimized CSS
            pdf_css = self._get_pdf_css()
            
            # Generate PDF
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=pdf_css, font_config=self.font_config)
            
            pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc], font_config=self.font_config)
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            raise Exception(f"Failed to generate PDF report: {str(e)}")
    
    def _get_pdf_css(self) -> str:
        """Get PDF-optimized CSS styles"""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "AIBOA 교육 분석 보고서";
                font-size: 12pt;
                color: #666;
            }
            @bottom-right {
                content: "페이지 " counter(page) " / " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        /* Reset margins for print */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Nanum Gothic', 'Malgun Gothic', sans-serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #333;
            background: white !important;
        }
        
        /* Header styles */
        .header {
            text-align: center;
            border-bottom: 3px solid #4ECDC4;
            padding-bottom: 20px;
            margin-bottom: 30px;
            background: white !important;
            color: #333 !important;
            page-break-after: avoid;
        }
        
        .title {
            font-size: 24pt;
            font-weight: bold;
            color: #2C3E50 !important;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 14pt;
            color: #7F8C8D !important;
            margin-bottom: 15px;
        }
        
        .meta-info {
            font-size: 12pt;
            color: #666 !important;
            background: #f8f9fa !important;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
        }
        
        /* Section styles */
        .section {
            background: white !important;
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            page-break-inside: avoid;
        }
        
        h2 {
            color: #2C3E50 !important;
            border-left: 4px solid #4ECDC4;
            padding-left: 15px;
            margin-bottom: 20px;
            font-size: 16pt;
            page-break-after: avoid;
        }
        
        /* Chart container - ensure it prints properly */
        .chart-container {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background: #f8f9fa !important;
            page-break-inside: avoid;
            height: auto !important;
            min-height: 200px;
        }
        
        /* Hide interactive elements in PDF */
        .toggle-button {
            display: none !important;
        }
        
        /* Always show content in PDF */
        .collapsible-content {
            display: block !important;
        }
        
        /* Stats grid */
        .stats-grid {
            display: flex;
            justify-content: space-around;
            gap: 10px;
            margin: 15px 0;
            page-break-inside: avoid;
        }
        
        .stat-box {
            flex: 1;
            background: #f8f9fa !important;
            color: #333 !important;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 18pt;
            font-weight: bold;
            color: #4ECDC4 !important;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 10pt;
            color: #666 !important;
        }
        
        /* Recommendations */
        .recommendation-item {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa !important;
            border-radius: 5px;
            border-left: 4px solid #2196F3;
            border: 1px solid #e9ecef;
            page-break-inside: avoid;
        }
        
        /* Analysis content */
        .analysis-content {
            background: #f8f9fa !important;
            padding: 20px;
            border-radius: 5px;
            border: 1px solid #e9ecef;
            font-size: 10pt;
            line-height: 1.6;
            white-space: pre-wrap;
            page-break-inside: avoid;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa !important;
            color: #666 !important;
            border-top: 1px solid #ddd;
            border-radius: 5px;
            font-size: 10pt;
        }
        
        /* Force page breaks where needed */
        .page-break {
            page-break-before: always;
        }
        
        /* Avoid breaks inside important elements */
        h2, h3 {
            page-break-after: avoid;
        }
        
        /* Ensure proper spacing */
        p {
            margin-bottom: 10px;
        }
        
        /* Chart placeholder for PDF */
        canvas {
            display: none;
        }
        
        .chart-container::after {
            content: "📊 차트는 HTML 버전에서 확인하실 수 있습니다.";
            display: block;
            text-align: center;
            font-style: italic;
            color: #666;
            padding: 40px;
            background: white;
            border: 2px dashed #ddd;
            border-radius: 5px;
        }
        """
    
    def save_pdf_to_file(self, analysis_data: Dict[str, Any], file_path: str) -> str:
        """
        Save PDF report to file
        
        Args:
            analysis_data: Analysis result data
            file_path: Path to save PDF file
            
        Returns:
            Path to saved PDF file
        """
        try:
            pdf_bytes = self.generate_pdf_report(analysis_data)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write PDF to file
            with open(file_path, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"PDF report saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to save PDF to file: {str(e)}")
            raise
    
    def generate_pdf_filename(self, analysis_data: Dict[str, Any]) -> str:
        """Generate appropriate filename for PDF"""
        
        analysis_id = analysis_data.get('analysis_id', 'unknown')
        framework = analysis_data.get('framework', 'analysis')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Clean framework name for filename
        framework_clean = framework.replace(' ', '_').replace('(', '').replace(')', '')
        
        return f"AIBOA_{framework_clean}_{analysis_id[:8]}_{timestamp}.pdf"

# Convenience function for direct usage
def generate_pdf_report_bytes(analysis_data: Dict[str, Any]) -> bytes:
    """
    Convenience function to generate PDF report as bytes
    
    Args:
        analysis_data: Analysis result data
        
    Returns:
        PDF content as bytes
    """
    generator = PDFReportGenerator()
    return generator.generate_pdf_report(analysis_data)

def is_pdf_generation_available() -> bool:
    """Check if PDF generation is available"""
    return WEASYPRINT_AVAILABLE