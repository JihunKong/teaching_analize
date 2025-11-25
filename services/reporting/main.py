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
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Premium Vibrant Palette */
            --color-primary: #6366f1; /* Indigo 500 */
            --color-primary-dark: #4338ca; /* Indigo 700 */
            --color-secondary: #10b981; /* Emerald 500 */
            --color-accent: #8b5cf6; /* Violet 500 */
            --color-background: #f8fafc;
            --color-surface: rgba(255, 255, 255, 0.85);
            --color-surface-dark: rgba(255, 255, 255, 0.95);
            --color-text-primary: #1e293b;
            --color-text-secondary: #64748b;
            
            /* Glassmorphism Effects */
            --glass-border: 1px solid rgba(255, 255, 255, 0.6);
            --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            --glass-blur: blur(16px);
            
            /* Spacing & Radius */
            --radius-lg: 1rem;
            --radius-xl: 1.5rem;
            --radius-2xl: 2rem;
            
            /* InBody Colors */
            --inbody-black: #1e293b;
            --inbody-gray: #94a3b8;
            --inbody-gray-light: #e2e8f0;
            --inbody-gray-dark: #475569;
            --inbody-red: #ef4444;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: var(--color-text-primary);
            background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 50%, #d1fae5 100%);
            min-height: 100vh;
            padding: 2rem;
            background-attachment: fixed;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            position: relative;
        }
        
        /* Main Frame Container */
        .report-frame {
            background: rgba(255, 255, 255, 0.4);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border-radius: var(--radius-2xl);
            border: var(--glass-border);
            box-shadow: var(--glass-shadow);
            padding: 3rem;
            margin-bottom: 2rem;
        }
        
        /* Glass Card */
        .glass-card {
            background: var(--color-surface);
            border-radius: var(--radius-xl);
            border: 1px solid rgba(255, 255, 255, 0.8);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            padding: 2rem;
            margin-bottom: 2rem;
            transition: transform 0.2s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        }

        .header {
            text-align: center;
            margin-bottom: 4rem;
            position: relative;
        }
        
        .header h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
            line-height: 1.1;
        }
        
        .header .subtitle {
            color: var(--color-text-secondary);
            font-size: 1.25rem;
            font-weight: 500;
            opacity: 0.9;
        }
        
        .section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--color-text-primary);
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid rgba(99, 102, 241, 0.1);
        }
        
        .section-title::before {
            content: '';
            display: block;
            width: 8px;
            height: 32px;
            background: linear-gradient(to bottom, var(--color-primary), var(--color-accent));
            border-radius: 4px;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .stat-card {
            background: var(--color-surface-dark);
            border-radius: var(--radius-lg);
            padding: 2rem;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        
        .stat-number {
            font-family: 'Outfit', sans-serif;
            font-size: 2.75rem;
            font-weight: 800;
            color: var(--color-primary);
            margin-bottom: 0.5rem;
            line-height: 1;
        }
        
        .stat-label {
            color: var(--color-text-secondary);
            font-size: 1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Analysis Content */
        .analysis-content {
            font-size: 1.1rem;
            line-height: 1.8;
            color: var(--color-text-primary);
        }

        /* InBody Style Metrics */
        .inbody-metrics-container {
            font-family: 'Inter', sans-serif;
            padding: 1.5rem;
            background: white;
            border-radius: var(--radius-lg);
        }

        .inbody-metric-row {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--inbody-gray-light);
        }

        .inbody-metric-label {
            width: 200px;
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--inbody-black);
        }

        .inbody-metric-bar-container {
            flex: 1;
            margin: 0 1.5rem;
            position: relative;
            height: 28px;
            display: flex;
            align-items: center;
        }

        .inbody-bar-track {
            width: 100%;
            height: 8px;
            background-color: var(--inbody-gray-light);
            border-radius: 4px;
            position: relative;
        }

        .inbody-bar-centerline {
            position: absolute;
            left: 50%;
            top: -6px;
            bottom: -6px;
            width: 2px;
            background-color: var(--inbody-gray);
            z-index: 1;
        }

        .inbody-bar {
            height: 100%;
            border-radius: 4px;
            position: absolute;
            top: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .inbody-bar.left { right: 50%; transform-origin: right; background: linear-gradient(to left, var(--inbody-red), #fca5a5); }
        .inbody-bar.right { left: 50%; transform-origin: left; background: linear-gradient(to right, var(--inbody-gray-dark), #94a3b8); }
        .inbody-bar.center { left: 50%; transform: translateX(-50%); background: linear-gradient(to right, var(--color-primary), var(--color-accent)); }

        .inbody-metric-value {
            width: 70px;
            text-align: right;
            font-weight: 700;
            color: var(--color-text-primary);
            font-size: 1.1rem;
        }

        .inbody-metric-optimal {
            width: 110px;
            text-align: center;
            font-size: 0.85rem;
            color: var(--inbody-gray-dark);
            background: #f1f5f9;
            padding: 2px 8px;
            border-radius: 4px;
            margin: 0 0.5rem;
        }

        .inbody-metric-status {
            width: 70px;
            text-align: center;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 6px;
        }

        .status-optimal { color: #047857; background: #d1fae5; }
        .status-deficit { color: #b91c1c; background: #fee2e2; }
        .status-excess { color: #334155; background: #e2e8f0; }

        .inbody-metric-score {
            width: 60px;
            text-align: right;
            font-weight: 800;
            color: var(--color-primary);
            font-size: 1.1rem;
        }

        /* Buttons */
        .export-buttons {
            margin-top: 4rem;
            text-align: center;
            display: flex;
            justify-content: center;
            gap: 1.5rem;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            padding: 1rem 2rem;
            background: white;
            color: var(--color-text-primary);
            text-decoration: none;
            border-radius: 0.75rem;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(0,0,0,0.05);
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
            color: white;
            border: none;
        }

        .btn-primary:hover {
            box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4);
        }

        .footer {
            text-align: center;
            padding: 3rem;
            color: var(--color-text-secondary);
            font-size: 0.9rem;
            margin-top: 2rem;
            opacity: 0.8;
        }

        /* Print Styles for Landscape PDF */
        @media print {
            @page {
                size: landscape;
                margin: 10mm;
            }
            
            body {
                background: white;
                padding: 0;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }
            
            .container {
                max-width: 100%;
                width: 100%;
            }
            
            .report-frame {
                background: none;
                border: none;
                box-shadow: none;
                padding: 0;
            }
            
            .glass-card {
                box-shadow: none;
                border: 1px solid #e2e8f0;
                break-inside: avoid;
                margin-bottom: 1.5rem;
                padding: 1.5rem;
                background: white;
            }
            
            .export-buttons, .footer {
                display: none;
            }

            .header {
                padding: 1rem;
                margin-bottom: 2rem;
                border-bottom: 3px solid var(--color-primary);
            }

            .header h1 {
                font-size: 2.5rem;
                background: none;
                -webkit-text-fill-color: var(--color-primary);
                color: var(--color-primary);
            }
            
            /* Ensure charts print well */
            canvas {
                max-width: 100% !important;
                max-height: 400px !important;
            }

            /* Force background colors */
            .status-optimal { background-color: #d1fae5 !important; color: #047857 !important; }
            .status-deficit { background-color: #fee2e2 !important; color: #b91c1c !important; }
            .status-excess { background-color: #e2e8f0 !important; color: #334155 !important; }
            
            .inbody-bar-track { background-color: #e2e8f0 !important; }
            .inbody-bar-centerline { background-color: #94a3b8 !important; }
            
            .inbody-bar.center { background-color: #6366f1 !important; }
            .inbody-bar.left { background-color: #ef4444 !important; }
            .inbody-bar.right { background-color: #475569 !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="report-frame">
            <!-- Header -->
            <div class="header">
                <h1>{{ title or "AIBOA 교육 분석 보고서" }}</h1>
                <div class="subtitle">AI 기반 수업 정밀 진단 리포트</div>
                <div class="subtitle" style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.7;">생성일: {{ timestamp }}</div>
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
            <div class="glass-card section">
                <h2 class="section-title">🎯 종합 분석 결과</h2>
                <div class="analysis-content">{{ analysis }}</div>
            </div>
            
            <!-- Metadata -->
            {% if metadata %}
            <div class="glass-card section">
                <h2 class="section-title">📊 메타데이터</h2>
                <div class="metadata-grid">
                    {% for key, value in metadata.items() %}
                    <div class="metadata-item" style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid rgba(0,0,0,0.05);">
                        <span class="metadata-label" style="font-weight: 600; color: var(--color-text-secondary);">{{ key }}</span>
                        <span class="metadata-value" style="font-weight: 500; color: var(--color-text-primary);">{{ value }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        </div>
        
        <!-- Export Options -->
        <div class="export-buttons">
            <a href="#" class="btn" onclick="window.print()">
                <span style="margin-right: 8px;">📄</span> 인쇄하기
            </a>
            <a href="#" class="btn btn-primary" onclick="downloadPDF()">
                <span style="margin-right: 8px;">📥</span> PDF 다운로드
            </a>
        </div>
    </div>
    
    <div class="footer">
        <p>AIBOA - AI 기반 교육 분석 플랫폼 | All Rights Reserved</p>
    </div>
    
    <script>
        function downloadPDF() {
            // Trigger print dialog which allows saving as PDF
            window.print();
        }
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