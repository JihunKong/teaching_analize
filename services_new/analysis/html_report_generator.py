"""
Enhanced HTML-based Professional Report Generator for All 13 Analysis Frameworks
Creates interactive HTML reports with Chart.js visualizations
"""

from datetime import datetime
from typing import Dict, List, Any
import json
import re

class HTMLReportGenerator:
    """Generate professional HTML reports for all analysis frameworks"""
    
    # Framework definitions matching the API structure
    FRAMEWORK_NAMES = {
        "cbil": "개념기반 탐구 수업(CBIL) 분석",
        "student_discussion": "학생주도 질문과 대화 및 토론 수업",
        "lesson_coaching": "수업 설계와 실행 코칭",
        "questioning": "교사의 질문 유형 분석",
        "feedback": "교사 피드백 분석",
        "participation": "학생 참여도 분석",
        "classroom_management": "학급 경영 분석",
        "learning_objectives": "학습 목표 달성도 분석",
        "assessment": "평가 방법 분석",
        "differentiation": "개별화 교육 분석",
        "technology_integration": "테크놀로지 활용 분석",
        "critical_thinking": "비판적 사고 촉진 분석",
        "collaborative_learning": "협력 학습 분석"
    }
    
    def extract_chart_data(self, analysis_text: str, framework: str) -> Dict[str, Any]:
        """Extract chart data from analysis text based on framework"""
        
        if framework == "cbil":
            return self._extract_cbil_data(analysis_text)
        elif framework == "student_discussion":
            return self._extract_discussion_data(analysis_text)
        elif framework == "lesson_coaching":
            return self._extract_coaching_data(analysis_text)
        else:
            return self._extract_generic_data(analysis_text, framework)
    
    def _extract_cbil_data(self, analysis_text: str) -> Dict[str, Any]:
        """Extract CBIL scoring data from analysis text"""
        # Look for scoring patterns like "점수: X점" or "→ 구간 X"
        score_patterns = [
            r'점수:\s*(\d+)점',
            r'→\s*구간\s*(\d+)',
            r'(\d+)점',
            r'구간\s*(\d+)'
        ]
        
        stages = ["Engage", "Focus", "Investigate", "Organize", "Generalize", "Transfer", "Reflect"]
        scores = {}
        
        # Split text by CBIL stages
        stage_sections = []
        current_section = ""
        lines = analysis_text.split('\n')
        
        for line in lines:
            # Check if line contains stage name
            stage_found = False
            for stage in stages:
                if stage.lower() in line.lower() or stage in line:
                    if current_section and stage_sections:
                        stage_sections.append(current_section.strip())
                    current_section = line + "\n"
                    stage_found = True
                    break
            
            if not stage_found and current_section:
                current_section += line + "\n"
        
        if current_section:
            stage_sections.append(current_section.strip())
        
        # Extract scores from sections
        for i, section in enumerate(stage_sections[:len(stages)]):
            stage_name = stages[i] if i < len(stages) else f"stage_{i+1}"
            
            score = 0
            for pattern in score_patterns:
                matches = re.findall(pattern, section, re.IGNORECASE)
                if matches:
                    try:
                        score = int(matches[-1])  # Take last found score
                        break
                    except ValueError:
                        continue
            
            scores[stage_name] = score
        
        return {
            "type": "radar",
            "title": "CBIL 7단계 실행 평가",
            "labels": stages,
            "data": [scores.get(stage, 0) for stage in stages],
            "max_value": 3
        }
    
    def _extract_discussion_data(self, analysis_text: str) -> Dict[str, Any]:
        """Extract student discussion analysis data"""
        # Look for frequency patterns like "X회", "구간 X"
        frequency_pattern = r'(\d+)회|구간\s*(\d+)'
        
        categories = ["사실적", "해석적", "평가적"]
        followup_types = ["명료화", "초점화", "정교화", "확장화", "입증화"]
        dialogue_types = ["추가하기", "참여하기", "반응하기", "유보하기", "수용하기", "반대하기", "변환하기"]
        
        # Extract data for each category
        question_data = self._extract_category_data(analysis_text, categories, "질문 유형")
        followup_data = self._extract_category_data(analysis_text, followup_types, "후속 질문")
        dialogue_data = self._extract_category_data(analysis_text, dialogue_types, "수업대화")
        
        return {
            "type": "multiple_bar",
            "title": "학생 주도 토론 분석",
            "datasets": [
                {"label": "질문 유형", "data": question_data, "backgroundColor": "#FF6384"},
                {"label": "후속 질문", "data": followup_data, "backgroundColor": "#36A2EB"},
                {"label": "수업대화", "data": dialogue_data, "backgroundColor": "#FFCE56"}
            ]
        }
    
    def _extract_coaching_data(self, analysis_text: str) -> Dict[str, Any]:
        """Extract lesson coaching analysis data"""
        coaching_areas = [
            "학습 목표의 명확성", "도입의 효과", "학습 내용의 적절성",
            "학습 방법의 다양성", "상호작용과 개별화", "학습 평가의 타당성",
            "피드백의 효과", "수업의 전개", "활동의 효과", "평가의 충실성"
        ]
        
        scores = []
        for area in coaching_areas:
            # Look for mentions of each area and extract associated scores
            area_score = self._find_score_near_text(analysis_text, area)
            scores.append(area_score)
        
        return {
            "type": "bar",
            "title": "수업 설계와 실행 코칭 분석",
            "labels": coaching_areas,
            "data": scores,
            "backgroundColor": "#4BC0C0"
        }
    
    def _extract_generic_data(self, analysis_text: str, framework: str) -> Dict[str, Any]:
        """Extract data for generic frameworks"""
        # Create a simple word frequency or score-based visualization
        lines = analysis_text.split('\n')
        scores = []
        labels = []
        
        for line in lines:
            if '점수' in line or '구간' in line or '회' in line:
                # Extract numerical values
                numbers = re.findall(r'\d+', line)
                if numbers:
                    score = int(numbers[0])
                    # Get the context (first few words) as label
                    words = line.split()[:3]
                    label = ' '.join(words).replace(':', '').strip()
                    
                    if label and score > 0:
                        labels.append(label)
                        scores.append(score)
        
        if not scores:
            # Fallback: create dummy data
            labels = ["분석 항목 1", "분석 항목 2", "분석 항목 3"]
            scores = [1, 2, 1]
        
        return {
            "type": "doughnut",
            "title": self.FRAMEWORK_NAMES.get(framework, f"{framework} 분석"),
            "labels": labels,
            "data": scores
        }
    
    def _extract_category_data(self, text: str, categories: List[str], section_name: str) -> List[int]:
        """Helper to extract numerical data for categories"""
        data = []
        
        for category in categories:
            score = self._find_score_near_text(text, category)
            data.append(score)
        
        return data
    
    def _find_score_near_text(self, text: str, search_text: str) -> int:
        """Find numerical score near specific text"""
        lines = text.split('\n')
        
        for line in lines:
            if search_text in line:
                # Look for score patterns in this line
                patterns = [r'(\d+)회', r'구간\s*(\d+)', r'점수:\s*(\d+)', r'(\d+)점']
                
                for pattern in patterns:
                    matches = re.findall(pattern, line)
                    if matches:
                        try:
                            return int(matches[0])
                        except (ValueError, IndexError):
                            continue
        
        return 0
    
    def generate_chart_js_config(self, chart_data: Dict[str, Any]) -> str:
        """Generate Chart.js configuration for different chart types"""
        
        if chart_data["type"] == "radar":
            config = {
                "type": "radar",
                "data": {
                    "labels": chart_data["labels"],
                    "datasets": [{
                        "label": chart_data["title"],
                        "data": chart_data["data"],
                        "backgroundColor": "rgba(54, 162, 235, 0.2)",
                        "borderColor": "rgba(54, 162, 235, 1)",
                        "pointBackgroundColor": "rgba(54, 162, 235, 1)",
                        "pointBorderColor": "#fff",
                        "pointHoverBackgroundColor": "#fff",
                        "pointHoverBorderColor": "rgba(54, 162, 235, 1)"
                    }]
                },
                "options": {
                    "responsive": True,
                    "scales": {
                        "r": {
                            "angleLines": {"display": False},
                            "suggestedMin": 0,
                            "suggestedMax": chart_data.get("max_value", 10)
                        }
                    },
                    "plugins": {
                        "legend": {"display": False},
                        "title": {
                            "display": True,
                            "text": chart_data["title"]
                        }
                    }
                }
            }
            
        elif chart_data["type"] == "multiple_bar":
            config = {
                "type": "bar",
                "data": {
                    "labels": chart_data["datasets"][0].get("labels", [f"항목 {i+1}" for i in range(len(chart_data["datasets"][0]["data"]))]),
                    "datasets": chart_data["datasets"]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": chart_data["title"]
                        }
                    },
                    "scales": {
                        "y": {"beginAtZero": True}
                    }
                }
            }
            
        elif chart_data["type"] == "doughnut":
            config = {
                "type": "doughnut",
                "data": {
                    "labels": chart_data["labels"],
                    "datasets": [{
                        "data": chart_data["data"],
                        "backgroundColor": [
                            "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", 
                            "#9966FF", "#FF9F40", "#FF6384", "#C9CBCF"
                        ]
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": chart_data["title"]
                        },
                        "legend": {"position": "bottom"}
                    }
                }
            }
            
        else:  # Default to bar chart
            config = {
                "type": "bar",
                "data": {
                    "labels": chart_data["labels"],
                    "datasets": [{
                        "data": chart_data["data"],
                        "backgroundColor": chart_data.get("backgroundColor", "#36A2EB")
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": chart_data["title"]
                        },
                        "legend": {"display": False}
                    },
                    "scales": {
                        "y": {"beginAtZero": True}
                    }
                }
            }
        
        return json.dumps(config, ensure_ascii=False)
    
    def generate_recommendations(self, analysis_text: str, framework: str) -> List[str]:
        """Generate framework-specific recommendations"""
        recommendations = []
        
        # Extract existing recommendations from analysis text
        lines = analysis_text.split('\n')
        current_rec = ""
        
        for line in lines:
            line = line.strip()
            
            # Look for recommendation markers
            if any(marker in line for marker in ['대안 제시', '권장사항', '개선', '제안', '추천', '권고']):
                if current_rec:
                    recommendations.append(current_rec.strip())
                current_rec = line
            elif line.startswith(('•', '-', '*', '1.', '2.', '3.')) or '할 수 있다' in line or '필요하다' in line:
                if current_rec:
                    current_rec += "\n" + line
                else:
                    recommendations.append(line)
        
        if current_rec and current_rec not in recommendations:
            recommendations.append(current_rec.strip())
        
        # Add generic recommendations if none found
        if not recommendations:
            framework_name = self.FRAMEWORK_NAMES.get(framework, framework)
            recommendations = [
                f"📋 {framework_name} 결과를 바탕으로 수업 개선 계획을 수립하세요.",
                f"🎯 분석된 내용을 동료 교사와 공유하여 피드백을 받아보세요.",
                f"💡 정기적인 분석을 통해 교수법 개선 효과를 측정하세요."
            ]
        
        return recommendations[:5]
    
    def generate_html_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generate complete HTML report with Chart.js"""
        
        framework = analysis_data.get('framework', 'generic')
        framework_name = self.FRAMEWORK_NAMES.get(framework, framework)
        analysis_text = analysis_data.get('analysis', '')
        timestamp = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        analysis_id = analysis_data.get('analysis_id', 'N/A')
        
        # Extract chart data
        chart_data = self.extract_chart_data(analysis_text, framework)
        chart_config = self.generate_chart_js_config(chart_data)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(analysis_text, framework)
        
        # Character and word counts
        char_count = len(analysis_text)
        word_count = len(analysis_text.split())
        
        html_content = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{framework_name} - AIBOA 분석 보고서</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .title {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 15px;
        }}
        
        .meta-info {{
            font-size: 14px;
            opacity: 0.8;
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
        }}
        
        .section {{
            background: white;
            margin: 25px 0;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            break-inside: avoid;
        }}
        
        h2 {{
            color: #2C3E50;
            border-left: 5px solid #667eea;
            padding-left: 20px;
            margin-bottom: 25px;
            font-size: 22px;
            display: flex;
            align-items: center;
        }}
        
        h2::before {{
            content: '📊';
            margin-right: 10px;
            font-size: 24px;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }}
        
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}
        
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .recommendation-item {{
            padding: 20px;
            margin: 15px 0;
            background: linear-gradient(90deg, #e3f2fd 0%, #f1f8e9 100%);
            border-radius: 12px;
            border-left: 5px solid #2196F3;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }}
        
        .recommendation-item:hover {{
            transform: translateY(-2px);
        }}
        
        .analysis-content {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            font-size: 15px;
            line-height: 1.8;
            white-space: pre-wrap;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            font-size: 14px;
        }}
        
        .toggle-button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 15px;
            transition: background 0.3s ease;
        }}
        
        .toggle-button:hover {{
            background: #5a67d8;
        }}
        
        .collapsible-content {{
            display: none;
        }}
        
        .collapsible-content.active {{
            display: block;
        }}
        
        @media print {{
            body {{ 
                margin: 0; 
                padding: 0;
                font-size: 12pt;
                background: white;
            }}
            .section {{ 
                page-break-inside: avoid; 
                box-shadow: none;
            }}
            .chart-container {{ page-break-inside: avoid; }}
            .toggle-button {{ display: none; }}
            .collapsible-content {{ display: block !important; }}
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ padding: 20px; }}
            .title {{ font-size: 24px; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">🎓 AIBOA 교육 분석 보고서</div>
        <div class="subtitle">{framework_name}</div>
        <div class="meta-info">
            분석일: {timestamp} | 분석 ID: {analysis_id}
        </div>
    </div>

    <div class="section">
        <h2>📈 분석 개요</h2>
        
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-number">{char_count:,}</div>
                <div class="stat-label">분석된 문자 수</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{word_count:,}</div>
                <div class="stat-label">분석된 단어 수</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{framework_name.count('단계') or framework_name.count('유형') or 1}</div>
                <div class="stat-label">분석 차원</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>📊 시각화 분석</h2>
        <div class="chart-container">
            <canvas id="analysisChart"></canvas>
        </div>
    </div>

    <div class="section">
        <h2>💡 개선 권장사항</h2>
        {''.join([f'<div class="recommendation-item">{rec}</div>' for rec in recommendations])}
    </div>

    <div class="section">
        <h2>📝 상세 분석 결과</h2>
        <button class="toggle-button" onclick="toggleAnalysis()">분석 내용 보기/숨기기</button>
        <div id="analysisContent" class="collapsible-content">
            <div class="analysis-content">{analysis_text}</div>
        </div>
    </div>

    <div class="footer">
        <p><strong>본 보고서는 AIBOA (AI-Based Observation and Analysis) 시스템에 의해 생성되었습니다.</strong></p>
        <p>교육 컨설팅 문의: contact@aiboa.edu | 📞 1588-0000</p>
    </div>

    <script>
        // Chart.js configuration
        const ctx = document.getElementById('analysisChart').getContext('2d');
        const chartConfig = {chart_config};
        
        new Chart(ctx, chartConfig);
        
        // Toggle functionality
        function toggleAnalysis() {{
            const content = document.getElementById('analysisContent');
            content.classList.toggle('active');
        }}
        
        // Print functionality
        function printReport() {{
            window.print();
        }}
        
        // Auto-expand analysis content if short
        document.addEventListener('DOMContentLoaded', function() {{
            const analysisText = `{analysis_text}`;
            if (analysisText.length < 500) {{
                document.getElementById('analysisContent').classList.add('active');
            }}
        }});
    </script>
</body>
</html>
        '''
        
        return html_content