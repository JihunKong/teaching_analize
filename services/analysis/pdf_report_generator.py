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
from diagnostic_report_generator import DiagnosticReportGenerator

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Generate PDF reports from HTML analysis reports"""
    
    def __init__(self):
        if not WEASYPRINT_AVAILABLE:
            logger.warning("WeasyPrint not available. PDF generation will be disabled.")

        # Initialize both HTML generators for different frameworks
        self.html_generator = HTMLReportGenerator()
        self.diagnostic_generator = DiagnosticReportGenerator()

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
            # Detect framework and use appropriate HTML generator
            framework = analysis_data.get('framework', '')

            if framework == 'cbil_comprehensive':
                # Use DiagnosticReportGenerator for comprehensive analysis
                logger.info(f"Using DiagnosticReportGenerator for framework: {framework}")
                html_content = self.diagnostic_generator.generate_html_report(analysis_data, for_pdf=True)
            else:
                # Use standard HTMLReportGenerator for other frameworks
                logger.info(f"Using HTMLReportGenerator for framework: {framework}")
                html_content = self.html_generator.generate_html_report(analysis_data)

            # Debug logging
            logger.info(f"HTML content type: {type(html_content)}")
            logger.info(f"HTML content length: {len(html_content) if isinstance(html_content, str) else 'N/A'}")

            # Create PDF-optimized CSS
            pdf_css = self._get_pdf_css()

            # Generate PDF
            try:
                logger.info("Creating HTML document from string...")
                html_doc = HTML(string=html_content)
                logger.info("HTML document created successfully")

                logger.info("Creating CSS document...")
                css_doc = CSS(string=pdf_css, font_config=self.font_config)
                logger.info("CSS document created successfully")

                logger.info("Writing PDF...")
                pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc], font_config=self.font_config)
                logger.info(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")

                return pdf_bytes
            except Exception as inner_e:
                logger.error(f"Error during PDF generation step: {type(inner_e).__name__}: {str(inner_e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to generate PDF report: {str(e)}")
    
    def _get_pdf_css(self) -> str:
        """Get PDF-optimized CSS styles"""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @bottom-right {
                content: "Page " counter(page) " / " counter(pages);
                font-size: 9pt;
                color: #94A3B8;
                font-family: 'Inter', sans-serif;
            }
            @bottom-left {
                content: "TVAS - Teacher Voice Analysis System";
                font-size: 9pt;
                color: #94A3B8;
                font-family: 'Inter', sans-serif;
            }
        }
        
        @font-face {
            font-family: 'Inter';
            src: local('Inter'), local('Arial');
        }
        
        /* Reset margins for print */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #0F172A;
            background: white !important;
        }
        
        /* Header styles */
        .header {
            text-align: center;
            border-bottom: 2px solid #F1F5F9;
            padding-bottom: 20px;
            margin-bottom: 40px;
            background: white !important;
            color: #0F172A !important;
            page-break-after: avoid;
        }
        
        .title {
            font-size: 24pt;
            font-weight: 700;
            color: #0F172A !important;
            margin-bottom: 10px;
            letter-spacing: -0.02em;
        }
        
        .subtitle {
            font-size: 14pt;
            color: #64748B !important;
            margin-bottom: 15px;
            font-weight: 500;
        }
        
        .meta-info {
            font-size: 10pt;
            color: #64748B !important;
            background: #F8FAFC !important;
            padding: 8px 16px;
            border-radius: 9999px;
            display: inline-block;
            border: 1px solid #E2E8F0;
        }
        
        /* Section styles */
        .section {
            background: white !important;
            margin: 30px 0;
            padding: 0;
            page-break-inside: avoid;
        }
        
        h2 {
            color: #0F172A !important;
            border-left: 4px solid #2563EB;
            padding-left: 15px;
            margin-bottom: 20px;
            font-size: 16pt;
            font-weight: 700;
            page-break-after: avoid;
        }
        
        /* Chart container - ensure it prints properly */
        .chart-container {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            background: white !important;
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
            gap: 15px;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        .stat-box {
            flex: 1;
            background: #F8FAFC !important;
            color: #0F172A !important;
            border: 1px solid #E2E8F0;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 24pt;
            font-weight: 800;
            color: #2563EB !important;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 10pt;
            color: #64748B !important;
            font-weight: 500;
        }
        
        /* Recommendations */
        .recommendation-item {
            padding: 20px;
            margin: 15px 0;
            background: #F8FAFC !important;
            border-radius: 8px;
            border-left: 4px solid #10B981; /* Emerald */
            border: 1px solid #E2E8F0;
            page-break-inside: avoid;
        }
        
        /* Analysis content */
        .analysis-content {
            background: white !important;
            padding: 10px 0;
            font-size: 11pt;
            line-height: 1.7;
            white-space: pre-wrap;
            page-break-inside: avoid;
            color: #334155;
            text-align: justify;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            background: white !important;
            color: #94A3B8 !important;
            border-top: 1px solid #F1F5F9;
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
            margin-bottom: 1em;
        }
        
        /* Chart placeholder for PDF */
        canvas {
            display: none;
        }
        
        .chart-container::after {
            content: "📊 Charts are available in the interactive web report.";
            display: block;
            text-align: center;
            font-style: italic;
            color: #64748B;
            padding: 40px;
            background: #F8FAFC;
            border: 2px dashed #E2E8F0;
            border-radius: 8px;
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