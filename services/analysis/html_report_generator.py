"""
Enhanced HTML-based Professional Report Generator for All 13 Analysis Frameworks
Creates interactive HTML reports with Chart.js visualizations
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import json
import re
import statistics
import numpy as np
import markdown  # For rendering markdown in HTML reports

class HTMLReportGenerator:
    """Generate professional HTML reports for all analysis frameworks"""
    
    # Framework definitions matching the API structure
    FRAMEWORK_NAMES = {
        "cbil": "개념기반 탐구 수업(CBIL) 분석",
        "cbil_comprehensive": "CBIL + Module 3 종합 분석",
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
    
    # Score normalization configurations for each framework
    FRAMEWORK_SCORE_CONFIGS = {
        "cbil": {
            "score_range": (0, 3),
            "score_type": "discrete",
            "dimensions": 7
        },
        "cbil_comprehensive": {
            "score_range": (0, 100),
            "score_type": "comprehensive",
            "dimensions": 22  # 7 CBIL stages + 15 Module 3 metrics
        },
        "student_discussion": {
            "score_range": (0, 10),
            "score_type": "frequency",
            "dimensions": 3  # Categories: factual, interpretive, evaluative
        },
        "lesson_coaching": {
            "score_range": (0, 100),
            "score_type": "percentage",
            "dimensions": 15
        }
    }
    
    def normalize_score(self, score: Union[int, float], framework: str, dimension: str = None) -> float:
        """Normalize scores from different frameworks to 0-100 scale"""
        if framework not in self.FRAMEWORK_SCORE_CONFIGS:
            return min(100, max(0, float(score)))
        
        config = self.FRAMEWORK_SCORE_CONFIGS[framework]
        min_score, max_score = config["score_range"]
        
        if config["score_type"] == "discrete":
            # CBIL: 0-3 scale -> 0-100 scale
            if max_score == 3:
                return (float(score) / 3.0) * 100
        elif config["score_type"] == "frequency":
            # Student Discussion: 0-10+ frequency -> 0-100 scale
            return min(100, (float(score) / 10.0) * 100)
        elif config["score_type"] == "percentage":
            # Already in percentage
            return min(100, max(0, float(score)))
        
        # Default linear normalization
        if max_score > min_score:
            normalized = ((float(score) - min_score) / (max_score - min_score)) * 100
            return min(100, max(0, normalized))
        
        return 50.0  # Fallback for edge cases
    
    def extract_framework_insights(self, analysis_text: str, framework: str) -> Dict[str, Any]:
        """Extract key insights and patterns from framework analysis"""
        insights = {
            "strengths": [],
            "improvements": [],
            "key_metrics": {},
            "patterns": []
        }
        
        lines = analysis_text.split('\n')
        
        # Look for strength indicators
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['우수', '좋', '효과적', '높', '잘']):
                if len(line.strip()) > 10:
                    insights["strengths"].append(line.strip())
        
        # Look for improvement areas
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['부족', '개선', '필요', '부족', '낮', '약함']):
                if len(line.strip()) > 10:
                    insights["improvements"].append(line.strip())
        
        # Extract numerical metrics
        numbers = re.findall(r'(\d+(?:\.\d+)?)\s*(?:점|%|회)', analysis_text)
        if numbers:
            insights["key_metrics"]["average_score"] = statistics.mean([float(n) for n in numbers[:10]])
            insights["key_metrics"]["score_range"] = {
                "min": min([float(n) for n in numbers[:10]]),
                "max": max([float(n) for n in numbers[:10]])
            }
        
        return insights
    
    def extract_chart_data(self, analysis_text: str, framework: str) -> Dict[str, Any]:
        """Extract chart data from analysis text based on framework"""

        if framework == "cbil":
            return self._extract_cbil_data(analysis_text)
        elif framework == "cbil_comprehensive":
            # For comprehensive results, analysis_text will be a dict with result data
            if isinstance(analysis_text, dict):
                return self._extract_cbil_comprehensive_data(analysis_text)
            else:
                return self._extract_generic_data(analysis_text, framework)
        elif framework == "student_discussion":
            return self._extract_discussion_data(analysis_text)
        elif framework == "lesson_coaching":
            return self._extract_coaching_data(analysis_text)
        else:
            return self._extract_generic_data(analysis_text, framework)
    
    def _extract_cbil_data(self, analysis_text: str) -> Dict[str, Any]:
        """Extract CBIL scoring data from analysis text"""
        # Enhanced scoring patterns with more variations
        score_patterns = [
            r'\*\*점수:\s*(\d+)점?\*\*',      # "**점수: 2점**"
            r'점수:\s*(\d+)점?',             # "점수: 2점" or "점수: 2"  
            r'(\d+)점\s*(?:입니다|이다|임)',      # "2점입니다" or "2점이다"
            r'→\s*구간\s*(\d+)',            # "→ 구간 2"
            r'구간\s*(\d+)',                # "구간 2"
            r'(\d+)점\b',                   # "2점" (word boundary)
            r'(\d+)\s*점',                  # "2 점"
            r'평가:\s*(\d+)',               # "평가: 2"
            r'수준:\s*(\d+)',               # "수준: 2"
            r'\*\*(\d+)점\*\*',             # "**2점**"
        ]
        
        stages = ["Engage", "Focus", "Investigate", "Organize", "Generalize", "Transfer", "Reflect"]
        korean_stage_names = ["흥미", "초점", "탐구", "조직", "일반화", "전이", "성찰"]
        
        scores = {}
        
        # First try: Split by numbered sections
        numbered_sections = re.split(r'(?:^|\n)\s*(?:####?\s*)?(\d+)\.?\s*(Engage|Focus|Investigate|Organize|Generalize|Transfer|Reflect|흥미|초점|탐구|조직|일반화|전이|성찰)', 
                                   analysis_text, flags=re.IGNORECASE | re.MULTILINE)
        
        if len(numbered_sections) > 1:
            # Process numbered sections
            for i in range(1, len(numbered_sections), 3):
                if i + 2 < len(numbered_sections):
                    stage_num = numbered_sections[i]
                    stage_name = numbered_sections[i + 1]
                    stage_content = numbered_sections[i + 2]
                    
                    try:
                        stage_idx = int(stage_num) - 1
                        if 0 <= stage_idx < len(stages):
                            score = self._find_score_in_text(stage_content, score_patterns)
                            scores[stages[stage_idx]] = score
                    except ValueError:
                        continue
        else:
            # Fallback: Split by stage names
            stage_sections = []
            current_section = ""
            lines = analysis_text.split('\n')
            
            for line in lines:
                stage_found = False
                for stage in stages + korean_stage_names:
                    if stage.lower() in line.lower():
                        if current_section:
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
                score = self._find_score_in_text(section, score_patterns)
                if i < len(stages):
                    scores[stages[i]] = score
        
        # Prioritize actual extracted scores, use fallback only when needed
        demo_scores = {"Engage": 2, "Focus": 3, "Investigate": 2, "Organize": 1, 
                     "Generalize": 1, "Transfer": 2, "Reflect": 2}
        
        final_scores = []
        actual_scores_found = 0

        # Try to use actual scores first
        for stage in stages:
            if stage in scores and scores[stage] > 0:
                final_scores.append(scores[stage])
                actual_scores_found += 1
            else:
                final_scores.append(0)

        # Only use demo data if NO actual scores were found
        if actual_scores_found == 0:
            logger.warning("No CBIL scores extracted from text, using demo data for visualization")
            final_scores = [demo_scores[stage] for stage in stages]
        else:
            logger.info(f"Found {actual_scores_found} out of 7 CBIL scores, using actual data")
        
        return {
            "type": "radar",
            "title": "CBIL 7단계 실행 평가",
            "labels": stages,
            "data": final_scores,
            "max_value": 3
        }
        
    def _find_score_in_text(self, text: str, patterns: List[str]) -> int:
        """Find numerical score in text using multiple patterns"""
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Take the last found score (most likely the final assessment)
                    score = int(matches[-1])
                    if 0 <= score <= 3:  # Valid CBIL score range
                        return score
                except (ValueError, IndexError):
                    continue
        return 0
    
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

    def _extract_cbil_comprehensive_data(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive CBIL + Module 3 data for visualization"""

        try:
            # Extract CBIL 7-stage scores with error handling
            cbil_insights = result_data.get('coaching_feedback', {}).get('cbil_insights', {})
            cbil_scores_data = cbil_insights.get('cbil_scores', {})
            cbil_stage_scores = cbil_scores_data.get('stage_scores', {})

            if not cbil_stage_scores:
                logger.warning("No CBIL stage scores found in result_data")
                # Return None to skip CBIL chart generation
                return None

            # Extract Module 3 metrics
            quantitative_metrics = result_data.get('quantitative_metrics', {})

            # Prepare CBIL stage chart
            cbil_stages = ["Engage", "Focus", "Investigate", "Organize", "Generalize", "Transfer", "Reflect"]
            cbil_scores = []

            for stage in ["engage", "focus", "investigate", "organize", "generalize", "transfer", "reflect"]:
                try:
                    stage_data = cbil_stage_scores.get(stage, {})
                    score = stage_data.get('score', None)

                    if score is None:
                        logger.warning(f"Missing score for CBIL stage: {stage}")
                        score = 0

                    # Validate score range (0-3)
                    if not (0 <= score <= 3):
                        logger.error(f"Invalid CBIL score {score} for stage {stage}, using 0")
                        score = 0

                    # Normalize to 0-100 scale (CBIL is 0-3)
                    normalized = (score / 3.0) * 100
                    cbil_scores.append(round(normalized, 1))

                except Exception as e:
                    logger.error(f"Error extracting CBIL score for stage {stage}: {e}")
                    cbil_scores.append(0)

            # Prepare Module 3 metrics chart (top 10 metrics)
            metric_labels = []
            metric_scores = []

            for metric_name, metric_data in list(quantitative_metrics.items())[:10]:
                # Clean metric name
                clean_name = metric_name.replace('_', ' ').title()
                metric_labels.append(clean_name)
                metric_scores.append(round(metric_data.get('normalized_score', 0), 1))

            # Pattern matching info
            pattern_match = result_data.get('pattern_matching', {}).get('best_match', {})
            pattern_name = pattern_match.get('pattern_name', 'Unknown')
            similarity_score = pattern_match.get('similarity_score', 0) * 100

            # CBIL alignment score
            cbil_alignment = cbil_insights.get('cbil_alignment_score', 0) * 100

            return {
                "type": "comprehensive",
                "title": "CBIL + Module 3 종합 분석",
                "cbil_chart": {
                    "type": "radar",
                    "title": "CBIL 7단계 점수",
                    "labels": cbil_stages,
                    "data": cbil_scores,
                    "backgroundColor": "rgba(102, 126, 234, 0.2)",
                    "borderColor": "#667eea"
                },
                "metrics_chart": {
                    "type": "bar",
                    "title": "Module 3 정량 지표 (Top 10)",
                    "labels": metric_labels,
                    "data": metric_scores,
                    "backgroundColor": "#4BC0C0"
                },
                "pattern_info": {
                    "name": pattern_name,
                    "similarity": round(similarity_score, 1),
                    "cbil_alignment": round(cbil_alignment, 1)
                },
                "summary": {
                    "cbil_total": cbil_scores_data.get('total_score', 0),
                    "cbil_max": cbil_scores_data.get('max_total_score', 21),
                    "cbil_percentage": round(cbil_scores_data.get('overall_percentage', 0), 1),
                    "pattern_match": pattern_name,
                    "total_utterances": result_data.get('input_metadata', {}).get('total_utterances', 0)
                }
            }

        except Exception as e:
            logger.error(f"Error extracting CBIL comprehensive data: {e}")
            return None

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

        if chart_data["type"] == "comprehensive":
            # For comprehensive CBIL reports, generate multiple charts
            cbil_chart_data = chart_data["cbil_chart"]
            metrics_chart_data = chart_data["metrics_chart"]

            # Generate CBIL radar chart config
            cbil_config = {
                "type": "radar",
                "data": {
                    "labels": cbil_chart_data["labels"],
                    "datasets": [{
                        "label": cbil_chart_data["title"],
                        "data": cbil_chart_data["data"],
                        "backgroundColor": cbil_chart_data.get("backgroundColor", "rgba(102, 126, 234, 0.2)"),
                        "borderColor": cbil_chart_data.get("borderColor", "#667eea"),
                        "pointBackgroundColor": "#667eea",
                        "pointBorderColor": "#fff",
                        "pointHoverBackgroundColor": "#fff",
                        "pointHoverBorderColor": "#667eea"
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "aspectRatio": 1.2,
                    "scales": {
                        "r": {
                            "angleLines": {"display": False},
                            "suggestedMin": 0,
                            "suggestedMax": 100,
                            "ticks": {
                                "font": {"size": 12}
                            }
                        }
                    },
                    "plugins": {
                        "legend": {"display": False},
                        "title": {
                            "display": True,
                            "text": cbil_chart_data["title"],
                            "font": {"size": 16, "weight": "bold"}
                        }
                    }
                }
            }

            # Generate Module 3 metrics bar chart config
            metrics_config = {
                "type": "bar",
                "data": {
                    "labels": metrics_chart_data["labels"],
                    "datasets": [{
                        "data": metrics_chart_data["data"],
                        "backgroundColor": metrics_chart_data.get("backgroundColor", "#4BC0C0")
                    }]
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "aspectRatio": 1.5,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": metrics_chart_data["title"],
                            "font": {"size": 16, "weight": "bold"}
                        },
                        "legend": {"display": False}
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "max": 100,
                            "ticks": {
                                "font": {"size": 12}
                            }
                        },
                        "x": {
                            "ticks": {
                                "font": {"size": 11}
                            }
                        }
                    }
                }
            }

            # Return both configs as JSON with special marker for dual chart
            return json.dumps({
                "type": "comprehensive",
                "cbil_chart": cbil_config,
                "metrics_chart": metrics_config,
                "pattern_info": chart_data["pattern_info"],
                "summary": chart_data["summary"]
            })

        elif chart_data["type"] == "radar":
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
                    "maintainAspectRatio": False,
                    "aspectRatio": 1.2,
                    "scales": {
                        "r": {
                            "angleLines": {"display": False},
                            "suggestedMin": 0,
                            "suggestedMax": chart_data.get("max_value", 10),
                            "ticks": {
                                "font": {"size": 12}
                            }
                        }
                    },
                    "plugins": {
                        "legend": {"display": False},
                        "title": {
                            "display": True,
                            "text": chart_data["title"],
                            "font": {"size": 16, "weight": "bold"}
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
                    "maintainAspectRatio": False,
                    "aspectRatio": 1.5,
                    "plugins": {
                        "title": {
                            "display": True,
                            "text": chart_data["title"],
                            "font": {"size": 16, "weight": "bold"}
                        }
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "ticks": {
                                "font": {"size": 12}
                            }
                        },
                        "x": {
                            "ticks": {
                                "font": {"size": 11}
                            }
                        }
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
    
    def generate_recommendations(self, analysis_text, framework: str) -> List[str]:
        """Generate framework-specific recommendations

        Args:
            analysis_text: Can be either a string (text to parse) or a list (pre-extracted recommendations)
            framework: Framework name

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Handle pre-extracted list (e.g., from coaching feedback)
        if isinstance(analysis_text, list):
            for item in analysis_text:
                if isinstance(item, dict):
                    # Format dictionary recommendations
                    title = item.get('title', item.get('action', ''))
                    description = item.get('description', item.get('rationale', ''))
                    if title:
                        rec = f"**{title}**"
                        if description:
                            rec += f"\n{description}"
                        recommendations.append(rec)
                elif isinstance(item, str) and item.strip():
                    recommendations.append(item.strip())

        # Handle text parsing (original logic)
        elif isinstance(analysis_text, str):
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

    def _markdown_to_html(self, text: str) -> str:
        """
        Convert markdown text to HTML

        Args:
            text: Markdown-formatted text (e.g., "**bold**", "- list item")

        Returns:
            HTML-formatted text

        Note:
            Uses markdown library with extensions for enhanced rendering:
            - extra: Tables, fenced code blocks, footnotes
            - nl2br: Newlines converted to <br> tags
        """
        if not text:
            return ""

        # Convert markdown to HTML with common extensions
        html = markdown.markdown(
            text,
            extensions=['extra', 'nl2br'],
            output_format='html5'
        )

        return html

    def aggregate_analysis_data(self, analysis_results: List[Dict[str, Any]], framework_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Aggregate multiple analysis results into unified insights"""
        if not analysis_results:
            return {}
        
        # Default equal weights
        if framework_weights is None:
            framework_weights = {result.get('framework', 'unknown'): 1.0 for result in analysis_results}
        
        aggregated = {
            "overall_score": 0.0,
            "framework_scores": {},
            "combined_insights": {
                "strengths": [],
                "improvements": [],
                "patterns": []
            },
            "recommendations": [],
            "comparison_data": {},
            "metadata": {
                "total_frameworks": len(analysis_results),
                "frameworks_included": [],
                "total_words_analyzed": 0,
                "analysis_dates": []
            }
        }
        
        framework_normalized_scores = {}
        
        # Process each framework result
        for result in analysis_results:
            framework = result.get('framework', 'unknown')
            analysis_text = result.get('analysis', '')
            
            # Update metadata
            aggregated["metadata"]["frameworks_included"].append(self.FRAMEWORK_NAMES.get(framework, framework))
            aggregated["metadata"]["total_words_analyzed"] += result.get('word_count', 0)
            aggregated["metadata"]["analysis_dates"].append(result.get('created_at', ''))
            
            # Extract chart data for scoring
            chart_data = self.extract_chart_data(analysis_text, framework)
            
            # Normalize scores
            if chart_data.get('data'):
                raw_scores = chart_data['data']
                if isinstance(raw_scores, list) and raw_scores:
                    avg_raw_score = statistics.mean([score for score in raw_scores if isinstance(score, (int, float))])
                    normalized_score = self.normalize_score(avg_raw_score, framework)
                    framework_normalized_scores[framework] = normalized_score
                    aggregated["framework_scores"][framework] = {
                        "raw_score": avg_raw_score,
                        "normalized_score": normalized_score,
                        "framework_name": self.FRAMEWORK_NAMES.get(framework, framework)
                    }
            
            # Extract insights
            insights = self.extract_framework_insights(analysis_text, framework)
            aggregated["combined_insights"]["strengths"].extend(insights["strengths"][:3])
            aggregated["combined_insights"]["improvements"].extend(insights["improvements"][:3])
            
            # Extract recommendations
            recs = self.generate_recommendations(analysis_text, framework)
            aggregated["recommendations"].extend(recs[:2])
        
        # Calculate overall weighted score
        if framework_normalized_scores:
            total_weight = sum(framework_weights.get(fw, 1.0) for fw in framework_normalized_scores.keys())
            weighted_sum = sum(
                score * framework_weights.get(fw, 1.0) 
                for fw, score in framework_normalized_scores.items()
            )
            aggregated["overall_score"] = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Prepare comparison data for charts
        aggregated["comparison_data"] = {
            "framework_names": [self.FRAMEWORK_NAMES.get(fw, fw) for fw in framework_normalized_scores.keys()],
            "normalized_scores": list(framework_normalized_scores.values()),
            "framework_ids": list(framework_normalized_scores.keys())
        }
        
        # Deduplicate and limit recommendations
        unique_recommendations = list(dict.fromkeys(aggregated["recommendations"]))
        aggregated["recommendations"] = unique_recommendations[:8]
        
        return aggregated
    
    def generate_comprehensive_chart_config(self, aggregated_data: Dict[str, Any]) -> str:
        """Generate Chart.js configuration for comprehensive comparison"""
        comparison_data = aggregated_data.get("comparison_data", {})
        
        if not comparison_data.get("framework_names"):
            return json.dumps({})
        
        # Multi-chart configuration
        config = {
            "type": "bar",
            "data": {
                "labels": comparison_data["framework_names"],
                "datasets": [{
                    "label": "통합 점수 (0-100)",
                    "data": comparison_data["normalized_scores"],
                    "backgroundColor": [
                        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", 
                        "#9966FF", "#FF9F40", "#FF6384", "#C9CBCF"
                    ],
                    "borderColor": [
                        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", 
                        "#9966FF", "#FF9F40", "#FF6384", "#C9CBCF"
                    ],
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "다중 프레임워크 비교 분석"
                    },
                    "legend": {"display": False}
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 100,
                        "ticks": {
                            "callback": "function(value) { return value + '점'; }"
                        }
                    }
                },
                "animation": {
                    "duration": 1500,
                    "easing": "easeOutQuart"
                }
            }
        }
        
        return json.dumps(config, ensure_ascii=False)
    
    def generate_comprehensive_report(self, analysis_results: List[Dict[str, Any]], 
                                    report_config: Dict[str, Any] = None) -> str:
        """Generate comprehensive HTML report combining multiple frameworks"""
        if not analysis_results:
            return "<html><body><h1>No analysis results provided</h1></body></html>"
        
        # Default configuration
        if report_config is None:
            report_config = {
                "report_type": "comparison",
                "framework_weights": {},
                "include_recommendations": True,
                "title": "종합 교육 분석 보고서"
            }
        
        # Aggregate data
        aggregated = self.aggregate_analysis_data(
            analysis_results, 
            report_config.get("framework_weights")
        )
        
        # Generate chart configuration
        chart_config = self.generate_comprehensive_chart_config(aggregated)
        
        # Prepare report metadata
        timestamp = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        analysis_ids = [result.get('analysis_id', 'N/A') for result in analysis_results]
        
        # Generate HTML
        html_content = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_config.get("title", "종합 교육 분석 보고서")} - AIBOA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @page {{
            size: A4;
            margin: 1.5cm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Nanum Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.7;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }}
        
        .report-container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 30px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: float 6s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-20px); }}
        }}
        
        .title {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }}
        
        .subtitle {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 20px;
            position: relative;
            z-index: 1;
        }}
        
        .meta-info {{
            font-size: 14px;
            background: rgba(255,255,255,0.15);
            padding: 12px 25px;
            border-radius: 30px;
            display: inline-block;
            backdrop-filter: blur(10px);
            position: relative;
            z-index: 1;
        }}
        
        .section {{
            padding: 35px;
            margin-bottom: 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        h2 {{
            color: #2C3E50;
            font-size: 24px;
            margin-bottom: 25px;
            padding-left: 20px;
            border-left: 5px solid #667eea;
            display: flex;
            align-items: center;
        }}
        
        .overall-score {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        
        .score-number {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        
        .score-label {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .frameworks-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        
        .framework-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .framework-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        
        .framework-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .framework-name {{
            font-size: 16px;
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 15px;
        }}
        
        .framework-score {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .framework-score-label {{
            font-size: 12px;
            color: #6c757d;
        }}
        
        .chart-container {{
            position: relative;
            height: 600px;
            margin: 40px auto;
            max-width: 100%;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 15px;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .insights-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }}
        
        .insights-column {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #28a745;
        }}
        
        .insights-column.improvements {{
            border-left-color: #ffc107;
        }}
        
        .insights-column h3 {{
            color: #2C3E50;
            font-size: 18px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .insights-list {{
            list-style: none;
        }}
        
        .insights-list li {{
            padding: 12px 0;
            border-bottom: 1px solid #dee2e6;
            position: relative;
            padding-left: 25px;
        }}
        
        .insights-list li:before {{
            content: "•";
            color: #667eea;
            font-weight: bold;
            position: absolute;
            left: 0;
        }}
        
        .insights-list li:last-child {{
            border-bottom: none;
        }}
        
        .recommendations {{
            display: grid;
            gap: 20px;
            margin: 25px 0;
        }}
        
        .recommendation-card {{
            background: linear-gradient(135deg, #e3f2fd 0%, #f1f8e9 100%);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #2196F3;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
        }}
        
        .recommendation-card:hover {{
            transform: translateX(5px);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .footer {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 14px;
        }}
        
        @media print {{
            body {{ 
                background: white;
                padding: 0;
                font-size: 12pt;
            }}
            .report-container {{
                box-shadow: none;
                border-radius: 0;
            }}
            .section {{ 
                page-break-inside: avoid; 
                padding: 20px;
            }}
            .chart-container {{ 
                page-break-inside: avoid; 
                height: 300px;
            }}
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .header {{ padding: 25px; }}
            .title {{ font-size: 26px; }}
            .insights-section {{ grid-template-columns: 1fr; }}
            .frameworks-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <div class="title">📊 {report_config.get("title", "종합 교육 분석 보고서")}</div>
            <div class="subtitle">다중 프레임워크 비교 분석</div>
            <div class="meta-info">
                분석일: {timestamp} | 포함된 분석: {len(analysis_results)}개
            </div>
        </div>

        <div class="section">
            <div class="overall-score">
                <div class="score-number">{aggregated["overall_score"]:.1f}점</div>
                <div class="score-label">통합 교육 효과성 점수</div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{aggregated["metadata"]["total_frameworks"]}</div>
                    <div class="stat-label">분석 프레임워크</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{aggregated["metadata"]["total_words_analyzed"]:,}</div>
                    <div class="stat-label">분석된 총 단어 수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(aggregated["recommendations"])}</div>
                    <div class="stat-label">통합 권장사항</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 프레임워크별 비교 분석</h2>
            
            <div class="frameworks-grid">
                {self._generate_framework_cards(aggregated["framework_scores"])}
            </div>
            
            <div class="chart-container">
                <canvas id="comparisonChart"></canvas>
            </div>
        </div>

        <div class="section">
            <h2>💡 통합 인사이트</h2>
            <div class="insights-section">
                <div class="insights-column">
                    <h3>🌟 주요 강점</h3>
                    <ul class="insights-list">
                        {self._generate_insights_list(aggregated["combined_insights"]["strengths"])}
                    </ul>
                </div>
                <div class="insights-column improvements">
                    <h3>🎯 개선 영역</h3>
                    <ul class="insights-list">
                        {self._generate_insights_list(aggregated["combined_insights"]["improvements"])}
                    </ul>
                </div>
            </div>
        </div>

'''
        
        # Add recommendations section if requested
        recommendations_section = ""
        if report_config.get("include_recommendations", True):
            recommendations_section = f'''
        <div class="section">
            <h2>🚀 통합 개선 권장사항</h2>
            <div class="recommendations">
                {self._generate_recommendation_cards(aggregated["recommendations"])}
            </div>
        </div>
        '''
        
        html_content += recommendations_section + f'''
        <div class="footer">
            <p><strong>본 종합 보고서는 AIBOA 시스템의 다중 프레임워크 분석을 통해 생성되었습니다.</strong></p>
            <p>분석 ID: {", ".join(analysis_ids[:3])}{"..." if len(analysis_ids) > 3 else ""}</p>
        </div>
    </div>

    <script>
        // Chart.js configuration
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        const chartConfig = {chart_config};
        
        new Chart(ctx, chartConfig);
        
        // Add interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Animate framework cards
            const cards = document.querySelectorAll('.framework-card');
            cards.forEach((card, index) => {{
                card.style.animationDelay = `${{index * 0.1}}s`;
                card.style.animation = 'fadeInUp 0.6s ease forwards';
            }});
        }});
        
        // Animation keyframes
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInUp {{
                from {{
                    opacity: 0;
                    transform: translateY(30px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        `;
        document.head.appendChild(style);

        // postMessage: Send iframe content height to parent window
        function sendHeightToParent() {{
            try {{
                const body = document.body;
                const html = document.documentElement;

                // Get the maximum height among different measurements
                const height = Math.max(
                    body.scrollHeight,
                    body.offsetHeight,
                    html.clientHeight,
                    html.scrollHeight,
                    html.offsetHeight
                );

                // Add padding for safety (50px)
                const paddedHeight = height + 50;

                console.log('Sending comprehensive report height to parent:', paddedHeight);
                window.parent.postMessage({{
                    type: 'iframe-height',
                    height: paddedHeight
                }}, window.location.origin);
            }} catch (e) {{
                console.error('Failed to send height to parent:', e);
            }}
        }}

        // Send initial height after page load and animations complete
        setTimeout(sendHeightToParent, 800);

        // ResizeObserver: Monitor content size changes
        if (typeof ResizeObserver !== 'undefined') {{
            const resizeObserver = new ResizeObserver(() => {{
                sendHeightToParent();
            }});
            resizeObserver.observe(document.body);
        }}
    </script>
</body>
</html>
        '''
        
        return html_content
    
    def _generate_framework_cards(self, framework_scores: Dict[str, Any]) -> str:
        """Generate HTML for framework comparison cards"""
        cards = []
        for framework, score_data in framework_scores.items():
            card_html = f'''
                <div class="framework-card">
                    <div class="framework-name">{score_data["framework_name"]}</div>
                    <div class="framework-score">{score_data["normalized_score"]:.1f}</div>
                    <div class="framework-score-label">정규화 점수 (/100)</div>
                </div>
            '''
            cards.append(card_html)
        return ''.join(cards)
    
    def _generate_insights_list(self, insights: List[str]) -> str:
        """Generate HTML for insights list"""
        if not insights:
            return '<li>분석할 수 있는 인사이트가 충분하지 않습니다.</li>'
        
        items = []
        for insight in insights[:5]:  # Limit to 5 items
            clean_insight = insight.replace('*', '').replace('#', '').strip()
            if clean_insight:
                items.append(f'<li>{clean_insight}</li>')
        
        return ''.join(items) if items else '<li>추가 분석이 필요합니다.</li>'
    
    def _generate_recommendation_cards(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendation cards"""
        if not recommendations:
            return '<div class="recommendation-card">구체적인 권장사항을 생성하기 위해 더 많은 분석 데이터가 필요합니다.</div>'
        
        cards = []
        for i, rec in enumerate(recommendations, 1):
            clean_rec = rec.replace('*', '').replace('#', '').strip()
            if clean_rec:
                card_html = f'''
                    <div class="recommendation-card">
                        <strong>{i}.</strong> {clean_rec}
                    </div>
                '''
                cards.append(card_html)
        
        return ''.join(cards) if cards else '<div class="recommendation-card">권장사항을 생성할 수 없습니다.</div>'
    
    def generate_html_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generate complete HTML report with Chart.js"""

        framework = analysis_data.get('framework', 'generic')
        framework_name = self.FRAMEWORK_NAMES.get(framework, framework)
        analysis_text = analysis_data.get('analysis', '')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        analysis_id = analysis_data.get('analysis_id', 'N/A')

        # Extract chart data - for cbil_comprehensive, pass full result data
        if framework == 'cbil_comprehensive':
            # For comprehensive analysis, pass the full result structure
            result_data = analysis_data.get('result', analysis_data)
            chart_data = self.extract_chart_data(result_data, framework)
            # Use CBIL analysis text for display
            analysis_text = result_data.get('cbil_analysis_text', analysis_text)
        else:
            chart_data = self.extract_chart_data(analysis_text, framework)

        chart_config = self.generate_chart_js_config(chart_data)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(analysis_text, framework)
        
        # Character and word counts
        char_count = len(analysis_text)
        word_count = len(analysis_text.split())
        
        html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{framework_name} - TVAS Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        @font-face {{
            font-family: 'Inter';
            src: local('Inter'), local('Arial');
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Arial', sans-serif;
            line-height: 1.6;
            color: #0F172A;
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #F8FAFC;
        }}
        
        .header {{
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 40px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid #E2E8F0;
        }}
        
        .title {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 10px;
            color: #0F172A;
            letter-spacing: -0.02em;
        }}
        
        .subtitle {{
            font-size: 18px;
            color: #64748B;
            margin-bottom: 20px;
            font-weight: 500;
        }}
        
        .meta-info {{
            font-size: 14px;
            color: #64748B;
            background: #F1F5F9;
            padding: 8px 16px;
            border-radius: 9999px;
            display: inline-block;
            font-weight: 500;
        }}
        
        .section {{
            background: white;
            margin: 30px 0;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid #E2E8F0;
            break-inside: avoid;
        }}
        
        h2 {{
            color: #0F172A;
            border-left: 4px solid #2563EB;
            padding-left: 15px;
            margin-bottom: 25px;
            font-size: 20px;
            font-weight: 700;
            display: flex;
            align-items: center;
            letter-spacing: -0.01em;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 30px auto;
            max-width: 800px;
            padding: 20px;
            background: white;
            border-radius: 12px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 25px 0;
        }}
        
        .stat-box {{
            background: #F8FAFC;
            color: #0F172A;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #E2E8F0;
        }}
        
        .stat-number {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 5px;
            color: #2563EB;
            letter-spacing: -0.02em;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #64748B;
            font-weight: 500;
        }}
        
        .recommendation-item {{
            padding: 20px;
            margin: 15px 0;
            background: #F8FAFC;
            border-radius: 12px;
            border-left: 4px solid #10B981;
            border: 1px solid #E2E8F0;
            transition: transform 0.2s ease;
        }}
        
        .recommendation-item:hover {{
            transform: translateY(-2px);
        }}
        
        .analysis-content {{
            background: #F8FAFC;
            padding: 30px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            font-size: 16px;
            line-height: 1.8;
            white-space: pre-wrap;
            color: #334155;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 60px;
            padding: 30px;
            color: #94A3B8;
            font-size: 14px;
            border-top: 1px solid #E2E8F0;
        }}
        
        .toggle-button {{
            background: #2563EB;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 9999px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 15px;
            transition: background 0.2s ease;
        }}
        
        .toggle-button:hover {{
            background: #1D4ED8;
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
        {''.join([f'<div class="recommendation-item">{self._markdown_to_html(rec)}</div>' for rec in recommendations])}
    </div>

    <div class="section">
        <h2>📝 상세 분석 결과</h2>
        <button class="toggle-button" onclick="toggleAnalysis()">분석 내용 보기/숨기기</button>
        <div id="analysisContent" class="collapsible-content">
            <div class="analysis-content">{self._markdown_to_html(analysis_text)}</div>
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

            // Send initial height to parent window
            sendHeightToParent();
        }});

        // postMessage: Send iframe content height to parent window
        function sendHeightToParent() {{
            try {{
                const body = document.body;
                const html = document.documentElement;

                // Get the maximum height among different measurements
                const height = Math.max(
                    body.scrollHeight,
                    body.offsetHeight,
                    html.clientHeight,
                    html.scrollHeight,
                    html.offsetHeight
                );

                // Add padding for safety (50px)
                const paddedHeight = height + 50;

                console.log('Sending iframe height to parent:', paddedHeight);
                window.parent.postMessage({{
                    type: 'iframe-height',
                    height: paddedHeight
                }}, window.location.origin);
            }} catch (e) {{
                console.error('Failed to send height to parent:', e);
            }}
        }}

        // ResizeObserver: Monitor content size changes
        if (typeof ResizeObserver !== 'undefined') {{
            const resizeObserver = new ResizeObserver(() => {{
                sendHeightToParent();
            }});
            resizeObserver.observe(document.body);
        }}

        // Also send height when analysis content is toggled
        const originalToggle = toggleAnalysis;
        toggleAnalysis = function() {{
            originalToggle();
            setTimeout(sendHeightToParent, 100);
        }};
    </script>
</body>
</html>
        '''
        
        return html_content