#!/usr/bin/env python3
"""
AIBOA Reporting Service
HTML report generation with beautiful templates
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from jinja2 import Environment, DictLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AIBOA Reporting Service",
    description="Beautiful HTML report generation",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportRequest(BaseModel):
    analysis_result: Dict[str, Any]
    template: str = "comprehensive"
    title: Optional[str] = None

# HTML Templates
HTML_TEMPLATES = {
    "comprehensive": """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title or "AIBOA 교육 분석 보고서" }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.1rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-size: 1rem;
        }
        
        .section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #2c3e50;
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }
        
        .analysis-content {
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            white-space: pre-wrap;
            font-size: 1.1rem;
            line-height: 1.8;
        }
        
        .chart-container {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .metadata {
            background: #e8f4fd;
            border: 1px solid #bee5eb;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        
        .metadata h3 {
            color: #0c5460;
            margin-bottom: 15px;
        }
        
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .metadata-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #bee5eb;
        }
        
        .metadata-label {
            font-weight: bold;
            color: #0c5460;
        }
        
        .metadata-value {
            color: #495057;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: white;
            font-size: 0.9rem;
        }
        
        .export-buttons {
            margin: 20px 0;
            text-align: center;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 25px;
            margin: 0 10px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: transform 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>{{ title or "AIBOA 교육 분석 보고서" }}</h1>
            <div class="subtitle">AI 기반 수업 분석 시스템</div>
            <div class="subtitle">생성일: {{ timestamp }}</div>
        </div>
        
        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ character_count | default('N/A') }}</div>
                <div class="stat-label">분석 문자 수</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ word_count | default('N/A') }}</div>
                <div class="stat-label">단어 수</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ framework_name | default('CBIL') }}</div>
                <div class="stat-label">분석 프레임워크</div>
            </div>
        </div>
        
        <!-- Analysis Results -->
        <div class="section">
            <h2>🎯 분석 결과</h2>
            <div class="analysis-content">{{ analysis }}</div>
        </div>
        
        <!-- Metadata -->
        {% if metadata %}
        <div class="section">
            <h2>📊 메타데이터</h2>
            <div class="metadata">
                <div class="metadata-grid">
                    {% for key, value in metadata.items() %}
                    <div class="metadata-item">
                        <span class="metadata-label">{{ key }}:</span>
                        <span class="metadata-value">{{ value }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endif %}
        
        <!-- Export Options -->
        <div class="export-buttons">
            <a href="#" class="btn" onclick="window.print()">📄 인쇄하기</a>
            <a href="#" class="btn" onclick="downloadPDF()">📥 PDF 다운로드</a>
        </div>
    </div>
    
    <div class="footer">
        <p>AIBOA - AI 기반 교육 분석 플랫폼 | 생성 시각: {{ timestamp }}</p>
    </div>
    
    <script>
        function downloadPDF() {
            // This would typically integrate with a PDF generation service
            alert('PDF 다운로드 기능은 곧 구현될 예정입니다.');
        }
        
        // Add any interactive charts here if needed
        window.onload = function() {
            // Chart initialization would go here
            console.log('Report loaded successfully');
        };
    </script>
</body>
</html>
    """,
    
    "summary": """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title or "AIBOA 요약 보고서" }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        
        .report {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2rem;
        }
        
        .summary {
            background: #e3f2fd;
            border-left: 5px solid #2196f3;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .analysis {
            white-space: pre-wrap;
            font-size: 1.1rem;
            line-height: 1.8;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="report">
        <h1>{{ title or "AIBOA 요약 보고서" }}</h1>
        
        <div class="summary">
            <strong>프레임워크:</strong> {{ framework_name }}<br>
            <strong>생성일:</strong> {{ timestamp }}<br>
            <strong>분석 문자 수:</strong> {{ character_count }}
        </div>
        
        <div class="analysis">{{ analysis }}</div>
        
        <div class="footer">
            <p>AIBOA - AI 기반 교육 분석 플랫폼</p>
        </div>
    </div>
</body>
</html>
    """
}

# Initialize Jinja2 environment
jinja_env = Environment(loader=DictLoader(HTML_TEMPLATES))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "reporting", 
        "timestamp": datetime.now().isoformat(),
        "available_templates": list(HTML_TEMPLATES.keys())
    }

@app.get("/api/templates")
async def list_templates():
    """List available report templates"""
    templates = []
    for key in HTML_TEMPLATES.keys():
        templates.append({
            "id": key,
            "name": key.title(),
            "description": f"{key.title()} report template"
        })
    return {"templates": templates}

@app.post("/api/generate/html", response_class=HTMLResponse)
async def generate_html_report(request: ReportRequest):
    """Generate HTML report from analysis result"""
    try:
        # Extract data from analysis result
        analysis_data = request.analysis_result
        
        # Prepare template data
        template_data = {
            "title": request.title,
            "timestamp": datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"),
            "framework": analysis_data.get("framework", "unknown"),
            "framework_name": analysis_data.get("framework_name", "Unknown Framework"),
            "analysis": analysis_data.get("analysis", "No analysis content available"),
            "character_count": analysis_data.get("character_count", 0),
            "word_count": analysis_data.get("word_count", 0),
            "metadata": analysis_data.get("metadata", {})
        }
        
        # Get template
        template = jinja_env.get_template(request.template)
        
        # Generate HTML
        html_content = template.render(**template_data)
        
        logger.info(f"Generated {request.template} report for framework {analysis_data.get('framework')}")
        
        return html_content
        
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.post("/api/generate/json")
async def generate_json_report(request: ReportRequest):
    """Generate JSON report data"""
    try:
        analysis_data = request.analysis_result
        
        report_data = {
            "report_id": str(uuid.uuid4()),
            "title": request.title or "AIBOA Analysis Report",
            "generated_at": datetime.now().isoformat(),
            "framework": analysis_data.get("framework", "unknown"),
            "framework_name": analysis_data.get("framework_name", "Unknown Framework"),
            "analysis": analysis_data.get("analysis", ""),
            "statistics": {
                "character_count": analysis_data.get("character_count", 0),
                "word_count": analysis_data.get("word_count", 0)
            },
            "metadata": analysis_data.get("metadata", {}),
            "template": request.template
        }
        
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating JSON report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get service statistics"""
    return {
        "service": "reporting",
        "available_templates": len(HTML_TEMPLATES),
        "template_names": list(HTML_TEMPLATES.keys()),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)