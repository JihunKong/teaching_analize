"""
Diagnostic Report Generator
Professional medical diagnostic report style for TVAS analysis
Clean, data-rich, immediately comprehensible visualization
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import re

class DiagnosticReportGenerator:
    """Generate diagnostic professional analysis reports"""

    def __init__(self):
        self.design_system_css = "/static/design_system/index.css"

    def _fix_css_braces(self, html_content: str) -> str:
        """
        Fix double curly braces in CSS that prevent proper rendering.
        
        Python f-strings use {{ to produce { in output, but they double up
        to {{{{ in the template which becomes {{ in the final HTML.
        We need to convert {{ to { for valid CSS syntax.
        """
        def replace_in_style(match):
            style_content = match.group(1)
            # Replace {{ with { and }} with } only in CSS
            style_content = style_content.replace('{{', '{')
            style_content = style_content.replace('}}', '}')
            return f'<style>{style_content}</style>'
        
        # Process all <style> tags
        fixed_html = re.sub(
            r'<style>(.*?)</style>',
            replace_in_style,
            html_content,
            flags=re.DOTALL
        )
        
        return fixed_html

    def generate_hero_section(self, overall_score: float, percentile: int, profile_type: str) -> str:
        """Generate at-a-glance hero summary section"""

        # Determine status color based on score
        if overall_score >= 80:
            status_class = "score-card--excellent"
            status_text = "우수"
        elif overall_score >= 70:
            status_class = "score-card--good"
            status_text = "양호"
        elif overall_score >= 60:
            status_class = "score-card--adequate"
            status_text = "적정"
        else:
            status_class = "score-card--needs-improvement"
            status_text = "개선필요"

        return f'''
        
        <div class="hero-evaluation-container">
<div class="hero-summary">
            <div class="hero-summary__title">전체 교수 효과성 점수</div>
            <div class="hero-summary__score">
                {overall_score:.0f}<span class="hero-summary__score-max">/100</span>
            </div>
            <div class="hero-summary__status-bar">
                <div class="hero-summary__status-fill score-card__status-fill--{status_class.split('--')[1]}"
                     style="width: {overall_score}%;"></div>
            </div>
            <div class="hero-summary__percentile">
                상위 {100 - percentile}% ({status_text})
            </div>
            <div class="hero-summary__profile">
                <div class="hero-summary__profile-label">교수 유형</div>
                <div class="hero-summary__profile-type">{profile_type}</div>
            </div>
        </div>
        '''

    def generate_score_card(self, value: float, label: str, max_value: float = 100) -> str:
        """Generate individual metric score card"""

        percentage = (value / max_value) * 100 if max_value > 0 else 0

        # Determine status
        if percentage >= 80:
            status = "excellent"
        elif percentage >= 70:
            status = "good"
        elif percentage >= 60:
            status = "adequate"
        else:
            status = "needs-improvement"

        return f'''
        <div class="score-card score-card--{status}">
            <div class="score-card__label">{label}</div>
            <div class="score-card__value">{value:.1f}</div>
            <div class="score-card__status-bar">
                <div class="score-card__status-fill score-card__status-fill--{status}"
                     style="width: {percentage}%;"></div>
            </div>
        </div>
        '''

    def generate_insight_card(self, title: str, description: str, example: str = None, card_type: str = "strength") -> str:
        """Generate strength or improvement insight card"""

        icon = "✓" if card_type == "strength" else "⚠"

        example_html = ""
        if example:
            example_html = f'''
            <div class="insight-card__example">
                발화 예시: "{example}"
            </div>
            '''

        return f'''
        <div class="insight-card insight-card--{card_type}">
            <div class="insight-card__header">
                <div class="insight-card__icon insight-card__icon--{card_type}">{icon}</div>
                <h4 class="insight-card__title">{title}</h4>
            </div>
            <p class="insight-card__description">{description}</p>
            {example_html}
        </div>
        '''

    def generate_recommendation_table(self, recommendations: list) -> str:
        """Generate recommendations as a table instead of cards"""
        if not recommendations:
            return ""
        
        table_html = """
        <table class="recommendation-table">
            <thead>
                <tr>
                    <th class="recommendation-table__header recommendation-table__header--priority">우선순위</th>
                    <th class="recommendation-table__header recommendation-table__header--action">실천 과제</th>
                    <th class="recommendation-table__header recommendation-table__header--importance">중요도</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, action in enumerate(recommendations[:5], 1):
            priority = "high" if i <= 2 else "medium" if i <= 4 else "low"
            priority_label = "높음" if priority == "high" else "보통" if priority == "medium" else "낮음"
            priority_class = f"recommendation-badge--{{{{priority}}}}"
            
            table_html += f"""
                <tr class="recommendation-table__row">
                    <td class="recommendation-table__cell recommendation-table__cell--priority">
                        <span class="recommendation-table__number">{{{{i}}}}</span>
                    </td>
                    <td class="recommendation-table__cell recommendation-table__cell--action">
                        {{{{action}}}}
                    </td>
                    <td class="recommendation-table__cell recommendation-table__cell--importance">
                        <span class="recommendation-badge {{{{priority_class}}}}">
                            <span class="recommendation-badge__icon">●</span>
                            {{{{priority_label}}}}
                        </span>
                    </td>
                </tr>
            """
        
        table_html += """
            </tbody>
        </table>
        """
        
        return table_html

    def generate_recommendation_card(self, number: int, title: str, description: str, priority: str, why: str = None) -> str:
        """Generate actionable coaching recommendation card"""

        why_html = ""
        if why:
            why_html = f'''
            <div class="recommendation-card__why">
                <div class="recommendation-card__why-title">왜 중요한가?</div>
                <p>{why}</p>
            </div>
            '''

        return f'''
        <div class="recommendation-card">
            <div class="recommendation-card__header">
                <div class="recommendation-card__number">{number}</div>
                <h4 class="recommendation-card__title">{title}</h4>
                <span class="recommendation-badge recommendation-badge--{priority}">
                    <span class="recommendation-badge__icon">●</span>
                    {priority.upper()}
                </span>
            </div>
            <div class="recommendation-card__content">
                <p class="recommendation-card__description">{description}</p>
                {why_html}
            </div>
        </div>
        '''

    def generate_timeline(self, stage_distribution: Dict[str, float]) -> str:
        """Generate lesson progression timeline"""

        intro = stage_distribution.get('introduction', 0)
        dev = stage_distribution.get('development', 0)
        closing = stage_distribution.get('closing', 0)

        return f'''
        <div class="timeline">
            <div class="timeline__segment timeline__segment--introduction" style="width: {intro}%;">
                <span class="timeline__label">도입</span>
                <span class="timeline__percentage">{intro:.0f}%</span>
            </div>
            <div class="timeline__segment timeline__segment--development" style="width: {dev}%;">
                <span class="timeline__label">전개</span>
                <span class="timeline__percentage">{dev:.0f}%</span>
            </div>
            <div class="timeline__segment timeline__segment--closing" style="width: {closing}%;">
                <span class="timeline__label">정리</span>
                <span class="timeline__percentage">{closing:.0f}%</span>
            </div>
        </div>
        '''

    def generate_stat_grid(self, stats: List[Dict[str, Any]]) -> str:
        """Generate 3-column stat grid"""

        items_html = ""
        for stat in stats:
            items_html += f'''
            <div class="stat-item">
                <div class="stat-item__label">{stat['label']}</div>
                <div class="stat-item__value">{stat['value']}</div>
            </div>
            '''

        return f'''
        <div class="stat-grid">
            {items_html}
        </div>
        '''

    def _generate_core_metrics_cards(self, quantitative_metrics: Dict[str, Any]) -> str:
        """
        Generate core metrics score cards (top 3 most important metrics)

        Args:
            quantitative_metrics: Dict of metric results

        Returns:
            HTML string with 3 score cards
        """
        if not quantitative_metrics:
            # Fallback to hardcoded values if no metrics available
            return f'''
            {self.generate_score_card(85.0, "수업 단계 균형")}
            {self.generate_score_card(72.0, "맥락 다양성")}
            {self.generate_score_card(68.0, "인지 수준")}
            '''

        # Priority metrics to display (in order of importance)
        priority_metrics = [
            'dev_time_ratio',
            'context_diversity',
            'avg_cognitive_level',
            'question_ratio',
            'higher_order_ratio',
            'cognitive_progression'
        ]

        # Metric name translations (Korean)
        metric_translations = {
            'dev_time_ratio': '전개 단계 균형',
            'context_diversity': '맥락 다양성',
            'avg_cognitive_level': '평균 인지 수준',
            'question_ratio': '질문 비율',
            'higher_order_ratio': '고차원적 사고',
            'cognitive_progression': '인지 수준 진행',
            'intro_time_ratio': '도입 단계 비율',
            'closing_time_ratio': '정리 단계 비율',
            'feedback_ratio': '피드백 비율',
            'explanation_ratio': '설명 비율'
        }

        # Select top 3 metrics (prioritize priority list, then by score)
        available_metrics = []
        for metric_name in priority_metrics:
            if metric_name in quantitative_metrics:
                metric_data = quantitative_metrics[metric_name]
                available_metrics.append((metric_name, metric_data))

        # If less than 3, add more from remaining metrics
        if len(available_metrics) < 3:
            remaining = [
                (name, data) for name, data in quantitative_metrics.items()
                if name not in [m[0] for m in available_metrics]
            ]
            # Sort by score
            remaining.sort(key=lambda x: x[1].get('normalized_score', 0), reverse=True)
            available_metrics.extend(remaining[:3 - len(available_metrics)])

        # Generate cards
        cards_html = ""
        for metric_name, metric_data in available_metrics[:3]:
            label = metric_translations.get(metric_name, metric_name.replace('_', ' ').title())
            score = metric_data.get('normalized_score', 0)
            cards_html += self.generate_score_card(score, label)

        return cards_html

    def _derive_distribution_metrics(self, matrix_analysis: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Derive additional metrics from matrix_analysis distribution data

        Args:
            matrix_analysis: Analysis results containing statistics and distributions

        Returns:
            Dict of derived metrics with value, normalized_score, and status
        """
        derived_metrics = {}

        # Get statistics
        stats = matrix_analysis.get('statistics', {})

        # 1. Extract stage distribution
        stage_stats = stats.get('stage_stats', {})
        stage_dist = stage_stats.get('stage_distribution', {})

        intro_pct = stage_dist.get('introduction', 0.0)
        dev_pct = stage_dist.get('development', 0.0)
        closing_pct = stage_dist.get('closing', 0.0)

        # Calculate scores for stage metrics
        derived_metrics['intro_time_ratio'] = self._calculate_metric_score(
            intro_pct, optimal_range=(10, 20), unit='%'
        )
        derived_metrics['closing_time_ratio'] = self._calculate_metric_score(
            closing_pct, optimal_range=(10, 20), unit='%'
        )

        # 2. Extract context distribution
        context_stats = stats.get('context_stats', {})
        context_dist = context_stats.get('context_distribution', {})

        explanation_pct = context_dist.get('explanation', 0.0)
        question_pct = context_dist.get('question', 0.0)
        feedback_pct = context_dist.get('feedback', 0.0)

        # Calculate scores for context metrics
        derived_metrics['explanation_ratio'] = self._calculate_metric_score(
            explanation_pct, optimal_range=(30, 45), unit='%'
        )
        derived_metrics['question_ratio'] = self._calculate_metric_score(
            question_pct, optimal_range=(20, 35), unit='%'
        )
        derived_metrics['feedback_ratio'] = self._calculate_metric_score(
            feedback_pct, optimal_range=(15, 25), unit='%'
        )

        # 3. Extract level distribution
        level_stats = stats.get('level_stats', {})
        level_dist = level_stats.get('level_distribution', {})

        l1_pct = level_dist.get('L1', 0.0)
        l2_pct = level_dist.get('L2', 0.0)
        l3_pct = level_dist.get('L3', 0.0)

        # Calculate scores for cognitive level metrics
        derived_metrics['l1_ratio'] = self._calculate_metric_score(
            l1_pct, optimal_range=(25, 35), unit='%'
        )
        derived_metrics['l2_ratio'] = self._calculate_metric_score(
            l2_pct, optimal_range=(40, 55), unit='%'
        )
        derived_metrics['l3_ratio'] = self._calculate_metric_score(
            l3_pct, optimal_range=(15, 30), unit='%'
        )

        return derived_metrics

    def _calculate_metric_score(self, value: float, optimal_range: tuple, unit: str) -> Dict[str, Any]:
        """
        Calculate normalized score and status for a metric value

        Args:
            value: The metric value
            optimal_range: Tuple of (min, max) for optimal range
            unit: Unit of measurement (e.g., '%', '')

        Returns:
            Dict with value, normalized_score, and status
        """
        min_optimal, max_optimal = optimal_range

        # Determine status
        if min_optimal <= value <= max_optimal:
            status = 'optimal'
            # Score in optimal range: 80-100
            range_position = (value - min_optimal) / (max_optimal - min_optimal) if max_optimal > min_optimal else 0.5
            normalized_score = 80 + (20 * range_position)
        elif value < min_optimal:
            status = 'deficit'
            # Score below optimal: 0-80
            if min_optimal > 0:
                normalized_score = 80 * (value / min_optimal)
            else:
                normalized_score = 40
        else:  # value > max_optimal
            status = 'excess'
            # Score above optimal: 80-0 (decreases with excess)
            excess_ratio = (value - max_optimal) / max_optimal if max_optimal > 0 else 1
            normalized_score = max(0, 80 * (1 - excess_ratio))

        return {
            'value': value,
            'normalized_score': round(normalized_score, 1),
            'status': status
        }

    def generate_horizontal_metrics_bars_html(self, quantitative_metrics: Dict[str, Any]) -> str:
        """
        Generate InBody-style horizontal bar charts for all metrics
        Pure HTML+CSS implementation (no Chart.js)

        Args:
            quantitative_metrics: Dict of all metric results

        Returns:
            HTML string with horizontal bars
        """
        # Metric translations and optimal ranges
        metric_info = {
            'dev_time_ratio': {'name': '전개 단계 시간 비율', 'optimal': (50, 70), 'unit': '%'},
            'intro_time_ratio': {'name': '도입 단계 시간 비율', 'optimal': (10, 20), 'unit': '%'},
            'closing_time_ratio': {'name': '정리 단계 시간 비율', 'optimal': (10, 20), 'unit': '%'},
            'context_diversity': {'name': '맥락 다양성 (엔트로피)', 'optimal': (2.0, 2.5), 'unit': ''},
            'question_ratio': {'name': '질문 비율', 'optimal': (20, 35), 'unit': '%'},
            'feedback_ratio': {'name': '피드백 비율', 'optimal': (15, 25), 'unit': '%'},
            'explanation_ratio': {'name': '설명 비율', 'optimal': (30, 45), 'unit': '%'},
            'avg_cognitive_level': {'name': '평균 인지 수준', 'optimal': (1.8, 2.3), 'unit': ''},
            'higher_order_ratio': {'name': '고차원적 사고 비율', 'optimal': (40, 60), 'unit': '%'},
            'cognitive_progression': {'name': '인지 수준 진행', 'optimal': (0.15, 0.35), 'unit': ''},
            'l1_ratio': {'name': 'L1 (기억/이해) 비율', 'optimal': (20, 40), 'unit': '%'},
            'l2_ratio': {'name': 'L2 (적용/분석) 비율', 'optimal': (35, 50), 'unit': '%'},
            'l3_ratio': {'name': 'L3 (평가/창조) 비율', 'optimal': (15, 30), 'unit': '%'},
            'pattern_alignment': {'name': '패턴 정렬도', 'optimal': (70, 90), 'unit': ''},
            'teaching_flow_score': {'name': '수업 흐름 점수', 'optimal': (70, 90), 'unit': ''}
        }

        bars_html = '<div class="inbody-metrics-container">'

        for metric_key, metric_data in quantitative_metrics.items():
            if metric_key not in metric_info:
                continue

            info = metric_info[metric_key]
            value = metric_data.get('value', 0)
            score = metric_data.get('normalized_score', 0)
            optimal_min, optimal_max = info['optimal']

            # Determine status: deficit (below), optimal (in range), excess (above)
            if value < optimal_min:
                status = 'deficit'
                bar_color = 'var(--inbody-red)'
                # Calculate deviation as percentage of optimal minimum
                deviation = ((optimal_min - value) / optimal_min) * 100 if optimal_min > 0 else 0
                bar_width = max(5, min(50, deviation))  # 5-50% range
                bar_direction = 'left'
            elif value > optimal_max:
                status = 'excess'
                bar_color = 'var(--inbody-gray-dark)'
                # Calculate deviation as percentage of optimal maximum
                deviation = ((value - optimal_max) / optimal_max) * 100 if optimal_max > 0 else 0
                bar_width = max(5, min(50, deviation))  # 5-50% range
                bar_direction = 'right'
            else:
                status = 'optimal'
                bar_color = 'var(--inbody-black)'
                # Calculate position within optimal range (0.0 to 1.0)
                range_position = (value - optimal_min) / (optimal_max - optimal_min) if optimal_max > optimal_min else 0.5
                # Bar width varies based on distance from center: 8% at center, up to 20% at edges
                bar_width = 8 + (12 * abs(0.5 - range_position) * 2)
                bar_direction = 'center'

            # Format value display
            if info['unit'] == '%':
                value_display = f"{value:.1f}%"
                optimal_display = f"{optimal_min}~{optimal_max}%"
            else:
                value_display = f"{value:.2f}"
                optimal_display = f"{optimal_min:.1f}~{optimal_max:.1f}"

            # Generate bar HTML
            bars_html += f'''
            <div class="inbody-metric-row">
                <div class="inbody-metric-label">{info['name']}</div>
                <div class="inbody-metric-bar-container">
                    <div class="inbody-bar-track">
                        <div class="inbody-bar-centerline"></div>
                        <div class="inbody-bar {bar_direction}" style="width: {bar_width}%; background-color: {bar_color};"></div>
                    </div>
                </div>
                <div class="inbody-metric-value">{value_display}</div>
                <div class="inbody-metric-optimal">{optimal_display}</div>
                <div class="inbody-metric-status status-{status}">
                    {'부족' if status == 'deficit' else ('최적' if status == 'optimal' else '과다')}
                </div>
                <div class="inbody-metric-score">{score:.0f}</div>
            </div>
            '''

        bars_html += '</div>'
        return bars_html

    def generate_metrics_detail_table(self, quantitative_metrics: Dict[str, Any]) -> str:
        """
        Generate InBody-style detailed metrics table

        Args:
            quantitative_metrics: Dict of all metric results

        Returns:
            HTML string with metrics table
        """
        # Metric translations
        metric_info = {
            'dev_time_ratio': {'name': '전개 단계 시간 비율', 'optimal': (50, 70), 'unit': '%'},
            'intro_time_ratio': {'name': '도입 단계 시간 비율', 'optimal': (10, 20), 'unit': '%'},
            'closing_time_ratio': {'name': '정리 단계 시간 비율', 'optimal': (10, 20), 'unit': '%'},
            'context_diversity': {'name': '맥락 다양성', 'optimal': (2.0, 2.5), 'unit': ''},
            'question_ratio': {'name': '질문 비율', 'optimal': (20, 35), 'unit': '%'},
            'feedback_ratio': {'name': '피드백 비율', 'optimal': (15, 25), 'unit': '%'},
            'explanation_ratio': {'name': '설명 비율', 'optimal': (30, 45), 'unit': '%'},
            'avg_cognitive_level': {'name': '평균 인지 수준', 'optimal': (1.8, 2.3), 'unit': ''},
            'higher_order_ratio': {'name': '고차원적 사고', 'optimal': (40, 60), 'unit': '%'},
            'cognitive_progression': {'name': '인지 수준 진행', 'optimal': (0.15, 0.35), 'unit': ''},
            'l1_ratio': {'name': 'L1 비율', 'optimal': (20, 40), 'unit': '%'},
            'l2_ratio': {'name': 'L2 비율', 'optimal': (35, 50), 'unit': '%'},
            'l3_ratio': {'name': 'L3 비율', 'optimal': (15, 30), 'unit': '%'},
            'pattern_alignment': {'name': '패턴 정렬도', 'optimal': (70, 90), 'unit': ''},
            'teaching_flow_score': {'name': '수업 흐름', 'optimal': (70, 90), 'unit': ''}
        }

        table_html = '''
        <div class="inbody-table-container">
            <table class="inbody-metrics-table">
                <thead>
                    <tr>
                        <th>지표명</th>
                        <th>현재값</th>
                        <th>최적범위</th>
                        <th>상태</th>
                        <th>점수</th>
                    </tr>
                </thead>
                <tbody>
        '''

        for metric_key, metric_data in quantitative_metrics.items():
            if metric_key not in metric_info:
                continue

            info = metric_info[metric_key]
            value = metric_data.get('value', 0)
            score = metric_data.get('normalized_score', 0)
            optimal_min, optimal_max = info['optimal']

            # Determine status
            if value < optimal_min:
                status = '부족'
                status_class = 'deficit'
            elif value > optimal_max:
                status = '과다'
                status_class = 'excess'
            else:
                status = '최적'
                status_class = 'optimal'

            # Format values
            if info['unit'] == '%':
                value_display = f"{value:.1f}%"
                optimal_display = f"{optimal_min}~{optimal_max}%"
            else:
                value_display = f"{value:.2f}"
                optimal_display = f"{optimal_min:.1f}~{optimal_max:.1f}"

            table_html += f'''
                <tr>
                    <td class="metric-name">{info['name']}</td>
                    <td class="metric-value">{value_display}</td>
                    <td class="metric-optimal">{optimal_display}</td>
                    <td class="metric-status status-{status_class}">{status}</td>
                    <td class="metric-score">{score:.0f}</td>
                </tr>
            '''

        table_html += '''
                </tbody>
            </table>
        </div>
        '''

        return table_html

    def generate_strengths_improvements_tables(self, coaching_feedback: Dict[str, Any]) -> str:
        """
        Generate side-by-side tables for strengths and improvements
        InBody-style table format with 3 columns: # | 항목 | 상세

        Args:
            coaching_feedback: Coaching feedback data with strengths and improvements

        Returns:
            HTML string with 2-column grid containing two tables
        """
        # Extract strengths
        strengths = coaching_feedback.get('strengths', [])[:3]

        # Extract improvements (try multiple field names)
        improvements = (
            coaching_feedback.get('improvements', []) or
            coaching_feedback.get('areas_for_growth', []) or
            coaching_feedback.get('areas_for_improvement', [])
        )[:3]

        # Build strengths table
        strengths_rows = ""
        for i, strength in enumerate(strengths, 1):
            if isinstance(strength, dict):
                point = strength.get('point', '')
                detail = strength.get('example', '')
            else:
                point = strength
                detail = ""

            strengths_rows += f'''
                    <tr>
                        <td>{i}</td>
                        <td>{point}</td>
                        <td>{detail if detail else '-'}</td>
                    </tr>
'''

        # Build improvements table
        improvements_rows = ""
        for i, improvement in enumerate(improvements, 1):
            if isinstance(improvement, dict):
                point = improvement.get('point', '')
                detail = improvement.get('suggestion') or improvement.get('example', '')
            else:
                point = improvement
                detail = ""

            improvements_rows += f'''
                    <tr>
                        <td>{i}</td>
                        <td>{point}</td>
                        <td>{detail if detail else '-'}</td>
                    </tr>
'''

        html = f'''
        <div class="strengths-improvements-container">
            <div class="strength-improvement-table strength-improvement-table--strength">
                <div class="strength-improvement-table__header">
                    <h3 class="strength-improvement-table__title">✓ 강점</h3>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>항목</th>
                            <th>상세</th>
                        </tr>
                    </thead>
                    <tbody>
{strengths_rows}
                    </tbody>
                </table>
            </div>

            <div class="strength-improvement-table strength-improvement-table--improvement">
                <div class="strength-improvement-table__header">
                    <h3 class="strength-improvement-table__title">⚠ 개선 영역</h3>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>항목</th>
                            <th>상세</th>
                        </tr>
                    </thead>
                    <tbody>
{improvements_rows}
                    </tbody>
                </table>
            </div>
        </div>
'''

        return html

    # ============ Chart Generation Methods ============

    def _generate_chartjs_config(
        self,
        chart_type: str,
        labels: List[str],
        datasets: List[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> str:
        """
        Generate Chart.js configuration JSON

        Args:
            chart_type: 'radar', 'bar', 'line', 'doughnut', 'pie'
            labels: Chart labels
            datasets: List of dataset configurations
            options: Chart.js options

        Returns:
            JSON string configuration
        """
        import json

        default_options = {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            }
        }

        if options:
            default_options.update(options)

        config = {
            'type': chart_type,
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': default_options
        }

        return json.dumps(config, ensure_ascii=False)

    def generate_metrics_radar_chart(self, quantitative_metrics: Dict[str, Any]) -> str:
        """
        Generate radar chart for top 7-8 metrics

        Returns:
            HTML with canvas and Chart.js config
        """
        import json

        # Priority metrics for radar chart
        priority_metrics = [
            'dev_time_ratio',
            'context_diversity',
            'avg_cognitive_level',
            'question_ratio',
            'feedback_ratio',
            'higher_order_ratio',
            'cognitive_progression'
        ]

        metric_labels = {
            'dev_time_ratio': '전개 단계',
            'context_diversity': '맥락 다양성',
            'avg_cognitive_level': '인지 수준',
            'question_ratio': '질문 비율',
            'feedback_ratio': '피드백',
            'higher_order_ratio': '고차원 사고',
            'cognitive_progression': '인지 진행'
        }

        # Extract scores
        labels = []
        scores = []
        for metric in priority_metrics:
            if metric in quantitative_metrics:
                labels.append(metric_labels.get(metric, metric))
                scores.append(quantitative_metrics[metric].get('normalized_score', 0))

        # Create dataset
        dataset = {
            'label': '현재 점수',
            'data': scores,
            'backgroundColor': 'rgba(102, 126, 234, 0.2)',
            'borderColor': 'rgb(102, 126, 234)',
            'borderWidth': 2,
            'pointBackgroundColor': 'rgb(102, 126, 234)',
            'pointBorderColor': '#fff',
            'pointHoverBackgroundColor': '#fff',
            'pointHoverBorderColor': 'rgb(102, 126, 234)'
        }

        config = self._generate_chartjs_config(
            'radar',
            labels,
            [dataset],
            {
                'scales': {
                    'r': {
                        'beginAtZero': True,
                        'max': 100,
                        'ticks': {
                            'stepSize': 20
                        }
                    }
                }
            }
        )

        return f'''
        <div class="chart-container" style="height: 280px;">
            <canvas id="metricsRadarChart"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('metricsRadarChart').getContext('2d');
                new Chart(ctx, {config});
            }})();
        </script>
        '''

    def generate_detailed_metrics_bar_chart(self, quantitative_metrics: Dict[str, Any]) -> str:
        """
        Generate horizontal bar chart for all 15 metrics

        Returns:
            HTML with canvas and Chart.js config
        """
        import json

        # Get all metrics sorted by score
        metrics_list = []
        for name, data in quantitative_metrics.items():
            metrics_list.append({
                'name': name,
                'score': data.get('normalized_score', 0),
                'status': data.get('status', 'good')
            })

        metrics_list.sort(key=lambda x: x['score'], reverse=True)

        # Metric translations
        metric_translations = {
            'dev_time_ratio': '전개 단계 비율',
            'context_diversity': '맥락 다양성',
            'avg_cognitive_level': '평균 인지 수준',
            'question_ratio': '질문 비율',
            'higher_order_ratio': '고차원 사고 비율',
            'cognitive_progression': '인지 수준 진행',
            'intro_time_ratio': '도입 단계 비율',
            'closing_time_ratio': '정리 단계 비율',
            'feedback_ratio': '피드백 비율',
            'explanation_ratio': '설명 비율',
            'utterance_density': '발화 밀도',
            'extended_dialogue_ratio': '확장 대화 비율',
            'avg_wait_time': '평균 대기 시간',
            'irf_pattern_ratio': 'IRF 패턴 비율',
            'dev_question_depth': '전개 질문 깊이'
        }

        labels = [metric_translations.get(m['name'], m['name']) for m in metrics_list]
        scores = [m['score'] for m in metrics_list]

        # Color-code by status
        colors = []
        for m in metrics_list:
            if m['score'] >= 80:
                colors.append('rgba(16, 185, 129, 0.8)')  # success
            elif m['score'] >= 70:
                colors.append('rgba(59, 130, 246, 0.8)')  # info
            elif m['score'] >= 60:
                colors.append('rgba(245, 158, 11, 0.8)')  # warning
            else:
                colors.append('rgba(239, 68, 68, 0.8)')   # danger

        dataset = {
            'label': '점수',
            'data': scores,
            'backgroundColor': colors,
            'borderColor': colors,
            'borderWidth': 1
        }

        config = self._generate_chartjs_config(
            'bar',
            labels,
            [dataset],
            {
                'indexAxis': 'y',
                'scales': {
                    'x': {
                        'beginAtZero': True,
                        'max': 100
                    }
                },
                'plugins': {
                    'legend': {
                        'display': False
                    }
                }
            }
        )

        return f'''
        <div class="chart-container" style="height: 400px;">
            <canvas id="detailedMetricsBarChart"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('detailedMetricsBarChart').getContext('2d');
                new Chart(ctx, {config});
            }})();
        </script>
        '''

    def generate_stage_distribution_chart(self, matrix_analysis: Dict[str, Any]) -> str:
        """
        Generate pie/doughnut chart for stage distribution

        Returns:
            HTML with canvas and Chart.js config
        """
        import json

        # Extract stage distribution
        stats = matrix_analysis.get('statistics', {})
        stage_stats = stats.get('stage_stats', {})
        stage_dist = stage_stats.get('stage_distribution', {})

        labels = ['도입', '전개', '정리']
        data = [
            stage_dist.get('introduction', 0),
            stage_dist.get('development', 0),
            stage_dist.get('closing', 0)
        ]

        dataset = {
            'data': data,
            'backgroundColor': [
                'rgba(102, 126, 234, 0.8)',  # primary
                'rgba(118, 75, 162, 0.8)',   # secondary
                'rgba(59, 130, 246, 0.8)'    # info
            ],
            'borderColor': '#fff',
            'borderWidth': 2
        }

        config = self._generate_chartjs_config(
            'doughnut',
            labels,
            [dataset],
            {
                'plugins': {
                    'legend': {
                        'position': 'bottom'
                    }
                }
            }
        )

        return f'''
        <div class="chart-container" style="height: 220px;">
            <canvas id="stageDistChart"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('stageDistChart').getContext('2d');
                new Chart(ctx, {config});
            }})();
        </script>
        '''

    def generate_context_distribution_chart(self, matrix_analysis: Dict[str, Any]) -> str:
        """
        Generate bar chart for context distribution

        Returns:
            HTML with canvas and Chart.js config
        """
        import json

        # Extract context distribution
        stats = matrix_analysis.get('statistics', {})
        context_stats = stats.get('context_stats', {})
        context_dist = context_stats.get('context_distribution', {})

        labels = ['설명', '질문', '피드백', '촉진', '관리']
        data = [
            context_dist.get('explanation', 0),
            context_dist.get('question', 0),
            context_dist.get('feedback', 0),
            context_dist.get('facilitation', 0),
            context_dist.get('management', 0)
        ]

        dataset = {
            'label': '비율 (%)',
            'data': data,
            'backgroundColor': 'rgba(102, 126, 234, 0.8)',
            'borderColor': 'rgb(102, 126, 234)',
            'borderWidth': 1
        }

        config = self._generate_chartjs_config(
            'bar',
            labels,
            [dataset],
            {
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 100
                    }
                },
                'plugins': {
                    'legend': {
                        'display': False
                    }
                }
            }
        )

        return f'''
        <div class="chart-container" style="height: 220px;">
            <canvas id="contextDistChart"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('contextDistChart').getContext('2d');
                new Chart(ctx, {config});
            }})();
        </script>
        '''

    def generate_level_distribution_chart(self, matrix_analysis: Dict[str, Any]) -> str:
        """
        Generate stacked bar chart for cognitive level distribution

        Returns:
            HTML with canvas and Chart.js config
        """
        import json

        # Extract level distribution
        stats = matrix_analysis.get('statistics', {})
        level_stats = stats.get('level_stats', {})
        level_dist = level_stats.get('level_distribution', {})

        labels = ['인지 수준 분포']
        l1_data = [level_dist.get('L1', 0)]
        l2_data = [level_dist.get('L2', 0)]
        l3_data = [level_dist.get('L3', 0)]

        datasets = [
            {
                'label': 'L1 (기억/이해)',
                'data': l1_data,
                'backgroundColor': 'rgba(59, 130, 246, 0.8)'
            },
            {
                'label': 'L2 (적용/분석)',
                'data': l2_data,
                'backgroundColor': 'rgba(16, 185, 129, 0.8)'
            },
            {
                'label': 'L3 (평가/창조)',
                'data': l3_data,
                'backgroundColor': 'rgba(245, 158, 11, 0.8)'
            }
        ]

        config = self._generate_chartjs_config(
            'bar',
            labels,
            datasets,
            {
                'indexAxis': 'y',
                'scales': {
                    'x': {
                        'stacked': True,
                        'max': 100
                    },
                    'y': {
                        'stacked': True
                    }
                }
            }
        )

        return f'''
        <div class="chart-container" style="height: 120px;">
            <canvas id="levelDistChart"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('levelDistChart').getContext('2d');
                new Chart(ctx, {config});
            }})();
        </script>
        '''

    def generate_pattern_similarity_chart(self, pattern_matching: Dict[str, Any]) -> str:
        """
        Generate bar chart for pattern similarity scores

        Returns:
            HTML with canvas and Chart.js config
        """
        import json

        # Get all pattern similarities
        all_patterns = pattern_matching.get('all_pattern_similarities', [])

        # Handle both dict and list formats
        if isinstance(all_patterns, dict):
            # Convert dict to list of dicts and sort by similarity
            pattern_list = [
                {'pattern_name': name, 'similarity': score}
                for name, score in all_patterns.items()
            ]
            sorted_patterns = sorted(pattern_list, key=lambda x: x['similarity'], reverse=True)[:5]
            labels = [p['pattern_name'] for p in sorted_patterns]
            data = [p['similarity'] * 100 for p in sorted_patterns]
        elif not all_patterns:
            # Fallback to best match only
            best_match = pattern_matching.get('best_match', {})
            labels = [best_match.get('pattern_name', '균형잡힌 촉진자')]
            data = [best_match.get('similarity_score', 0.75) * 100]
        else:
            # Original list format
            sorted_patterns = sorted(all_patterns, key=lambda x: x['similarity'], reverse=True)[:5]
            labels = [p['pattern_name'] for p in sorted_patterns]
            data = [p['similarity'] * 100 for p in sorted_patterns]

        # Color first bar differently (best match)
        colors = ['rgba(102, 126, 234, 0.8)']  # primary for best match
        colors.extend(['rgba(156, 163, 175, 0.6)'] * (len(data) - 1))  # gray for others

        dataset = {
            'label': '유사도 (%)',
            'data': data,
            'backgroundColor': colors,
            'borderColor': colors,
            'borderWidth': 1
        }

        config = self._generate_chartjs_config(
            'bar',
            labels,
            [dataset],
            {
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'max': 100
                    }
                },
                'plugins': {
                    'legend': {
                        'display': False
                    }
                }
            }
        )

        return f'''
        <div class="chart-container" style="height: 220px;">
            <canvas id="patternSimilarityChart"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('patternSimilarityChart').getContext('2d');
                new Chart(ctx, {config});
            }})();
        </script>
        '''

    # ============ End Chart Generation Methods ============

    # ============ Data Extraction Helper Methods ============

    def _extract_stage_distribution(self, matrix_analysis: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract stage distribution percentages from matrix analysis

        Args:
            matrix_analysis: Matrix analysis result containing statistics

        Returns:
            Dict with stage percentages: {"introduction": 15.5, "development": 68.2, "closing": 16.3}
        """
        stats = matrix_analysis.get('statistics', {})
        stage_stats = stats.get('stage_stats', {})
        stage_dist = stage_stats.get('stage_distribution', {})

        # Return with default 0 values if not present
        return {
            'introduction': stage_dist.get('introduction', 0.0),
            'development': stage_dist.get('development', 0.0),
            'closing': stage_dist.get('closing', 0.0)
        }

    def _extract_context_distribution(self, matrix_analysis: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract context distribution percentages from matrix analysis

        Args:
            matrix_analysis: Matrix analysis result containing statistics

        Returns:
            Dict with context percentages: {"explanation": 35, "question": 25, ...}
        """
        stats = matrix_analysis.get('statistics', {})
        context_stats = stats.get('context_stats', {})
        context_dist = context_stats.get('context_distribution', {})

        return {
            'explanation': context_dist.get('explanation', 0.0),
            'question': context_dist.get('question', 0.0),
            'feedback': context_dist.get('feedback', 0.0),
            'facilitation': context_dist.get('facilitation', 0.0),
            'management': context_dist.get('management', 0.0)
        }

    def _extract_level_distribution(self, matrix_analysis: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract cognitive level distribution percentages from matrix analysis

        Args:
            matrix_analysis: Matrix analysis result containing statistics

        Returns:
            Dict with level percentages: {"L1": 40, "L2": 35, "L3": 25}
        """
        stats = matrix_analysis.get('statistics', {})
        level_stats = stats.get('level_stats', {})
        level_dist = level_stats.get('level_distribution', {})

        return {
            'L1': level_dist.get('L1', 0.0),
            'L2': level_dist.get('L2', 0.0),
            'L3': level_dist.get('L3', 0.0)
        }

    def _extract_top_metrics(
        self,
        quantitative_metrics: Dict[str, Any],
        count: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get top N metrics by priority/importance

        Priority order:
        1. dev_time_ratio (전개 단계 균형)
        2. context_diversity (맥락 다양성)
        3. avg_cognitive_level (평균 인지 수준)
        4. question_ratio (질문 비율)
        5. feedback_ratio (피드백 비율)
        6. higher_order_ratio (고차원 사고 비율)
        7. cognitive_progression (인지 수준 진행)

        Args:
            quantitative_metrics: Dict of metric results
            count: Number of top metrics to return (default: 7)

        Returns:
            List of metric dicts with name, score, status, korean_name
        """
        priority_order = [
            'dev_time_ratio',
            'context_diversity',
            'avg_cognitive_level',
            'question_ratio',
            'feedback_ratio',
            'higher_order_ratio',
            'cognitive_progression',
            'intro_time_ratio',
            'closing_time_ratio',
            'explanation_ratio',
            'utterance_density',
            'extended_dialogue_ratio',
            'avg_wait_time',
            'irf_pattern_ratio',
            'dev_question_depth'
        ]

        metric_translations = {
            'dev_time_ratio': '전개 단계 비율',
            'context_diversity': '맥락 다양성',
            'avg_cognitive_level': '평균 인지 수준',
            'question_ratio': '질문 비율',
            'feedback_ratio': '피드백 비율',
            'higher_order_ratio': '고차원 사고 비율',
            'cognitive_progression': '인지 수준 진행',
            'intro_time_ratio': '도입 단계 비율',
            'closing_time_ratio': '정리 단계 비율',
            'explanation_ratio': '설명 비율',
            'utterance_density': '발화 밀도',
            'extended_dialogue_ratio': '확장 대화 비율',
            'avg_wait_time': '평균 대기 시간',
            'irf_pattern_ratio': 'IRF 패턴 비율',
            'dev_question_depth': '전개 질문 깊이'
        }

        top_metrics = []
        for metric_name in priority_order[:count]:
            if metric_name in quantitative_metrics:
                metric_data = quantitative_metrics[metric_name]
                top_metrics.append({
                    'name': metric_name,
                    'korean_name': metric_translations.get(metric_name, metric_name),
                    'score': metric_data.get('normalized_score', 0),
                    'value': metric_data.get('value', 0),
                    'status': metric_data.get('status', 'good')
                })

        return top_metrics

    def _extract_all_metrics_sorted(
        self,
        quantitative_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get all 15 metrics sorted by category and score

        Categories:
        - Time Dimension: intro_time_ratio, dev_time_ratio, closing_time_ratio
        - Context Dimension: context_diversity, explanation_ratio, question_ratio, feedback_ratio
        - Cognitive Dimension: avg_cognitive_level, higher_order_ratio, cognitive_progression
        - Interaction Quality: utterance_density, extended_dialogue_ratio, avg_wait_time
        - Composite Patterns: irf_pattern_ratio, dev_question_depth

        Args:
            quantitative_metrics: Dict of metric results

        Returns:
            List of metric dicts sorted by score (descending)
        """
        metric_translations = {
            'dev_time_ratio': '전개 단계 비율',
            'context_diversity': '맥락 다양성',
            'avg_cognitive_level': '평균 인지 수준',
            'question_ratio': '질문 비율',
            'higher_order_ratio': '고차원 사고 비율',
            'cognitive_progression': '인지 수준 진행',
            'intro_time_ratio': '도입 단계 비율',
            'closing_time_ratio': '정리 단계 비율',
            'feedback_ratio': '피드백 비율',
            'explanation_ratio': '설명 비율',
            'utterance_density': '발화 밀도',
            'extended_dialogue_ratio': '확장 대화 비율',
            'avg_wait_time': '평균 대기 시간',
            'irf_pattern_ratio': 'IRF 패턴 비율',
            'dev_question_depth': '전개 질문 깊이'
        }

        metric_categories = {
            'intro_time_ratio': 'time',
            'dev_time_ratio': 'time',
            'closing_time_ratio': 'time',
            'context_diversity': 'context',
            'explanation_ratio': 'context',
            'question_ratio': 'context',
            'feedback_ratio': 'context',
            'avg_cognitive_level': 'cognitive',
            'higher_order_ratio': 'cognitive',
            'cognitive_progression': 'cognitive',
            'utterance_density': 'interaction',
            'extended_dialogue_ratio': 'interaction',
            'avg_wait_time': 'interaction',
            'irf_pattern_ratio': 'composite',
            'dev_question_depth': 'composite'
        }

        all_metrics = []
        for metric_name, metric_data in quantitative_metrics.items():
            all_metrics.append({
                'name': metric_name,
                'korean_name': metric_translations.get(metric_name, metric_name),
                'category': metric_categories.get(metric_name, 'other'),
                'score': metric_data.get('normalized_score', 0),
                'value': metric_data.get('value', 0),
                'status': metric_data.get('status', 'good')
            })

        # Sort by score descending
        all_metrics.sort(key=lambda x: x['score'], reverse=True)

        return all_metrics

    # ============ End Data Extraction Methods ============

    def calculate_overall_score(self, quantitative_metrics: Dict[str, Any]) -> float:
        """
        Calculate overall score from quantitative metrics

        Args:
            quantitative_metrics: Dict of metric results

        Returns:
            Overall score (0-100 average)
        """
        if not quantitative_metrics:
            return 75.0

        scores = []
        for metric_name, metric_data in quantitative_metrics.items():
            score = metric_data.get('normalized_score', 0)
            scores.append(score)

        if not scores:
            return 75.0

        return sum(scores) / len(scores)

    def calculate_percentile(self, overall_score: float) -> int:
        """
        Estimate percentile ranking based on overall score

        Args:
            overall_score: Overall score (0-100)

        Returns:
            Estimated percentile (0-100)
        """
        # Simplified percentile estimation
        # In production, this would compare against database of scores
        if overall_score >= 90:
            return 95  # Top 5%
        elif overall_score >= 80:
            return 75  # Top 25%
        elif overall_score >= 70:
            return 50  # Top 50%
        elif overall_score >= 60:
            return 30  # Top 70%
        else:
            return 10  # Bottom 90%

    def generate_html_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generate complete diagnostic HTML report

        Args:
            analysis_data: Full analysis result with coaching, metrics, patterns

        Returns:
            Complete HTML document string
        """

        framework = analysis_data.get('framework', 'cbil_comprehensive')
        timestamp = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        analysis_id = analysis_data.get('analysis_id', 'N/A')

        # Extract key data
        coaching_feedback = analysis_data.get('coaching_feedback', {})
        quantitative_metrics = analysis_data.get('quantitative_metrics', {})
        pattern_matching = analysis_data.get('pattern_matching', {})
        matrix_analysis = analysis_data.get('matrix_analysis', {})

        # Calculate overall score from actual metrics
        overall_score = self.calculate_overall_score(quantitative_metrics)
        percentile = self.calculate_percentile(overall_score)
        profile_type = pattern_matching.get('best_match', {}).get('pattern_name', '균형잡힌 촉진자')

        # Generate hero section
        hero_html = self.generate_hero_section(overall_score, percentile, profile_type)

        # Generate core metric score cards (use top 3 metrics by score)
        core_metrics_html = self._generate_core_metrics_cards(quantitative_metrics)

        # Generate strengths and improvements tables (instead of cards)
        strengths_improvements_tables_html = self.generate_strengths_improvements_tables(coaching_feedback)

        # Generate recommendations
        recommendations_html = ""
        
        # Get priority actions with fallback to improvements
        priority_actions = coaching_feedback.get('priority_actions', [])
        if not priority_actions:
            # Fallback: Use improvements data to generate priority actions
            improvements = coaching_feedback.get('improvements', []) or coaching_feedback.get('areas_for_improvement', [])
            priority_actions = []
            for improvement in improvements[:5]:
                if isinstance(improvement, dict):
                    action_text = improvement.get('point', '')
                    if improvement.get('example'):
                        action_text = f"{action_text}: {improvement.get('example')}"
                else:
                    action_text = improvement
                if action_text:
                    priority_actions.append(action_text)
        
        for i, action in enumerate(priority_actions[:5], 1):
            priority = "high" if i <= 2 else "medium" if i <= 4 else "low"
            recommendations_html += self.generate_recommendation_card(
                number=i,
                title=action,
                description="",  # Removed redundant text
                priority=priority
            )

        # Derive additional metrics from matrix_analysis distributions
        if matrix_analysis.get('statistics'):
            derived_metrics = self._derive_distribution_metrics(matrix_analysis)
            quantitative_metrics.update(derived_metrics)

        # Generate InBody components
        inbody_bars_html = self.generate_horizontal_metrics_bars_html(quantitative_metrics)
        inbody_table_html = self.generate_metrics_detail_table(quantitative_metrics)

        # Generate charts for new sections
        metrics_radar_chart = self.generate_metrics_radar_chart(quantitative_metrics)
        detailed_metrics_bar_chart = self.generate_detailed_metrics_bar_chart(quantitative_metrics)

        stage_distribution_chart = self.generate_stage_distribution_chart(matrix_analysis)
        context_distribution_chart = self.generate_context_distribution_chart(matrix_analysis)
        level_distribution_chart = self.generate_level_distribution_chart(matrix_analysis)

        pattern_similarity_chart = self.generate_pattern_similarity_chart(pattern_matching)

        # Extract distribution data for text display
        stage_dist = self._extract_stage_distribution(matrix_analysis)
        context_dist = self._extract_context_distribution(matrix_analysis)
        level_dist = self._extract_level_distribution(matrix_analysis)

        # Extract individual values for template
        stage_intro = stage_dist.get('introduction', 0)
        stage_dev = stage_dist.get('development', 0)
        stage_close = stage_dist.get('closing', 0)

        context_expl = context_dist.get('explanation', 0)
        context_ques = context_dist.get('question', 0)
        context_feed = context_dist.get('feedback', 0)

        level_l1 = level_dist.get('L1', 0)
        level_l2 = level_dist.get('L2', 0)
        level_l3 = level_dist.get('L3', 0)

        # Extract pattern matching info
        best_match = pattern_matching.get('best_match', {})
        best_pattern_name = best_match.get('pattern_name', '균형잡힌 촉진자')
        best_pattern_description = best_match.get('pattern_description', '전개 단계 중심, 다양한 맥락 활용')
        best_pattern_similarity = best_match.get('similarity_score', 0.75) * 100

        # Build complete HTML
        html = f'''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TVAS 교수 분석 보고서</title>
    <style>
        
        .report-header {{{{
            background: var(--white);
            border-bottom: 2px solid var(--primary-600);
            padding: 1.5rem 2rem;
            margin-bottom: var(--space-4-compact);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}}}

        .report-header__title {{{{
            font-size: 1.5rem;
            font-weight: var(--weight-bold);
            color: var(--primary-900);
            margin-bottom: var(--space-1);
        }}}}

        .report-header__meta {{{{
            font-size: var(--text-sm);
            color: var(--gray-600);
        }}}}

        .report-header__info {{{{
            text-align: center;
        }}}}

        .report-header__subtitle {{{{
            font-size: 0.9rem;
            color: var(--gray-700);
            font-weight: 500;
        }}}}

        .report-header__badge {{{{
            font-size: 0.75rem;
            color: var(--primary-600);
            font-weight: 600;
            margin-top: 0.25rem;
        }}}}

        
        :root {{{{
            --space-3-compact: 1rem;      
            --space-4-compact: 1.5rem;    
            --space-6-compact: 2rem;      
            --space-8-compact: 3rem;      
        }}}}

        
        :root {{{{
            --inbody-red: #8B0000;           
            --inbody-red-light: #CC0000;     
            --inbody-gray-dark: #666666;     
            --inbody-gray-medium: #999999;   
            --inbody-gray-light: #CCCCCC;    
            --inbody-bg: #F0F0F0;            
            --inbody-black: #000000;         
            --inbody-white: #FFFFFF;
            --inbody-primary: #667EEA;
            --inbody-primary-dark: #5A67D8;
            --inbody-border: #E5E7EB;
        }}}}

        /* ============ Complete Base CSS System ============ */
        :root {{{{
            /* Extended color palette */
            --white: #FFFFFF;
            --black: #000000;
            --primary-500: #667EEA;
            --primary-600: #5A67D8;
            --primary-700: #4C51BF;
            --primary-900: #2D3748;
            --gray-50: #F9FAFB;
            --gray-100: #F3F4F6;
            --gray-200: #E5E7EB;
            --gray-300: #D1D5DB;
            --gray-400: #9CA3AF;
            --gray-500: #6B7280;
            --gray-600: #4B5563;
            --gray-700: #374151;
            --gray-800: #1F2937;
            --gray-900: #111827;
            --green-500: #10B981;
            --green-600: #059669;
            --yellow-500: #F59E0B;
            --yellow-600: #D97706;
            --red-500: #EF4444;
            --red-600: #DC2626;
            
            /* Spacing scale */
            --space-1: 0.25rem;
            --space-2: 0.5rem;
            --space-3: 0.75rem;
            --space-4: 1rem;
            --space-5: 1.25rem;
            --space-6: 1.5rem;
            --space-8: 2rem;
            --space-10: 2.5rem;
            --space-12: 3rem;
            
            /* Typography */
            --text-xs: 0.75rem;
            --text-sm: 0.875rem;
            --text-base: 1rem;
            --text-lg: 1.125rem;
            --text-xl: 1.25rem;
            --text-2xl: 1.5rem;
            --weight-normal: 400;
            --weight-medium: 500;
            --weight-semibold: 600;
            --weight-bold: 700;
            
            /* Effects */
            --radius-sm: 0.25rem;
            --radius-md: 0.375rem;
            --radius-lg: 0.5rem;
            --radius-xl: 0.75rem;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }}}}

        /* ============ Utility Classes ============ */
        .flex {{ display: flex; }}
        .inline-flex {{ display: inline-flex; }}
        .justify-start {{ justify-content: flex-start; }}
        .justify-center {{ justify-content: center; }}
        .justify-between {{ justify-content: space-between; }}
        .justify-around {{ justify-content: space-around; }}
        .items-start {{ align-items: flex-start; }}
        .items-center {{ align-items: center; }}
        .items-end {{ align-items: flex-end; }}
        .flex-col {{ flex-direction: column; }}
        .flex-wrap {{ flex-wrap: wrap; }}
        .gap-2 {{ gap: var(--space-2); }}
        .gap-3 {{ gap: var(--space-3); }}
        .gap-4 {{ gap: var(--space-4); }}
        .gap-6 {{ gap: var(--space-6); }}
        
        .grid {{ display: grid; }}
        .grid-cols-1 {{ grid-template-columns: repeat(1, minmax(0, 1fr)); }}
        .grid-cols-2 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        .grid-cols-3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
        .grid-cols-4 {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
        
        .container {{ 
            max-width: 1200px; 
            margin-left: auto; 
            margin-right: auto; 
            padding-left: var(--space-4); 
            padding-right: var(--space-4); 
        }}
        
        /* Padding utilities */
        .p-2 {{ padding: var(--space-2); }}
        .p-3 {{ padding: var(--space-3); }}
        .p-4 {{ padding: var(--space-4); }}
        .p-6 {{ padding: var(--space-6); }}
        .px-4 {{ padding-left: var(--space-4); padding-right: var(--space-4); }}
        .py-2 {{ padding-top: var(--space-2); padding-bottom: var(--space-2); }}
        .py-4 {{ padding-top: var(--space-4); padding-bottom: var(--space-4); }}
        
        /* Margin utilities */
        .m-0 {{ margin: 0; }}
        .mt-2 {{ margin-top: var(--space-2); }}
        .mt-4 {{ margin-top: var(--space-4); }}
        .mb-2 {{ margin-bottom: var(--space-2); }}
        .mb-3 {{ margin-bottom: var(--space-3); }}
        .mb-4 {{ margin-bottom: var(--space-4); }}
        .mb-6 {{ margin-bottom: var(--space-6); }}
        
        /* Text utilities */
        .text-xs {{ font-size: var(--text-xs); }}
        .text-sm {{ font-size: var(--text-sm); }}
        .text-base {{ font-size: var(--text-base); }}
        .text-lg {{ font-size: var(--text-lg); }}
        .text-xl {{ font-size: var(--text-xl); }}
        .text-2xl {{ font-size: var(--text-2xl); }}
        .font-medium {{ font-weight: var(--weight-medium); }}
        .font-semibold {{ font-weight: var(--weight-semibold); }}
        .font-bold {{ font-weight: var(--weight-bold); }}
        .text-center {{ text-align: center; }}
        .text-primary-700 {{ color: var(--primary-700); }}
        .text-gray-600 {{ color: var(--gray-600); }}
        .text-gray-700 {{ color: var(--gray-700); }}
        .text-gray-900 {{ color: var(--gray-900); }}

        /* ============ Component Classes ============ */
        .card {{
            background: var(--white);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            padding: var(--space-6);
        }}

        .score-card__status-fill--excellent {{
            background: linear-gradient(135deg, var(--green-500) 0%, var(--green-600) 100%);
        }}

        .score-card__status-fill--good {{
            background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        }}

        .score-card__status-fill--fair {{
            background: linear-gradient(135deg, var(--yellow-500) 0%, var(--yellow-600) 100%);
        }}

        .score-card__status-fill--poor {{
            background: linear-gradient(135deg, var(--red-500) 0%, var(--red-600) 100%);
        }}

        .subsection-header {{
            display: flex;
            align-items: center;
            gap: var(--space-3);
            margin-bottom: var(--space-4);
            padding-bottom: var(--space-3);
            border-bottom: 2px solid var(--gray-200);
        }}

        .subsection-header__icon {{
            font-size: var(--text-xl);
        }}

        .subsection-header__title {{
            font-size: var(--text-lg);
            font-weight: var(--weight-semibold);
            color: var(--gray-900);
        }}

        .metric-stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--space-4);
            margin-top: var(--space-4);
        }}

        .metric-stat-pill {{
            display: flex;
            flex-direction: column;
            padding: var(--space-3);
            background: var(--gray-50);
            border-radius: var(--radius-md);
            border-left: 3px solid var(--gray-300);
        }}

        .metric-stat-pill--primary {{
            border-left-color: var(--primary-600);
            background: rgba(102, 126, 234, 0.05);
        }}

        .metric-stat-pill--success {{
            border-left-color: var(--green-500);
            background: rgba(16, 185, 129, 0.05);
        }}

        .metric-stat-pill--warning {{
            border-left-color: var(--yellow-500);
            background: rgba(245, 158, 11, 0.05);
        }}

        .metric-stat-pill__bar {{
            height: 4px;
            background: var(--gray-200);
            border-radius: 2px;
            overflow: hidden;
            margin-top: var(--space-2);
        }}

        .recommendation-card {{
            background: var(--white);
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            padding: var(--space-4);
            transition: all 0.2s;
        }}

        .recommendation-card:hover {{
            box-shadow: var(--shadow-md);
            border-color: var(--primary-500);
        }}

        .recommendation-card__header {{
            display: flex;
            align-items: center;
            gap: var(--space-3);
            margin-bottom: var(--space-3);
        }}

        .recommendation-card__number {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            background: var(--primary-500);
            color: var(--white);
            border-radius: 50%;
            font-weight: var(--weight-bold);
            font-size: var(--text-sm);
        }}

        .recommendation-card__title {{
            flex: 1;
            font-size: var(--text-base);
            font-weight: var(--weight-semibold);
            color: var(--gray-900);
        }}

        .recommendation-badge {{
            display: inline-flex;
            align-items: center;
            gap: var(--space-1);
            padding: 4px 12px;
            border-radius: var(--radius-md);
            font-size: var(--text-xs);
            font-weight: var(--weight-medium);
        }}

        .recommendation-badge--high {{
            background: rgba(239, 68, 68, 0.1);
            color: var(--red-600);
        }}

        .recommendation-badge--medium {{
            background: rgba(245, 158, 11, 0.1);
            color: var(--yellow-600);
        }}

        .recommendation-badge--low {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--green-600);
        }}

        .recommendation-badge__icon {{
            font-size: var(--text-sm);
        }}

        .summary-card__icon-wrapper {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            background: var(--primary-500);
            border-radius: var(--radius-lg);
            color: var(--white);
        }}

        .summary-card__icon {{
            font-size: var(--text-2xl);
        }}

        .summary-card__content {{
            flex: 1;
        }}

        .status-bar {{
            height: 8px;
            background: var(--gray-200);
            border-radius: var(--radius-md);
            overflow: hidden;
            margin-top: var(--space-2);
        }}

        .status-bar__fill {{
            height: 100%;
            border-radius: var(--radius-md);
            transition: width 0.3s ease;
        }}

        .report-footer__icon {{
            font-size: var(--text-base);
            color: var(--gray-600);
        }}

        .report-footer__text {{
            color: var(--gray-700);
        }}

        .report-footer__contact {{
            color: var(--gray-600);
            font-size: var(--text-sm);
        }}


        
        .two-column-layout {{{{
            display: grid;
            grid-template-columns: 60% 38%;
            gap: 2%;
            margin-top: var(--space-4-compact);
            align-items: start;
        }}}}

        .two-column-layout__left {{{{
            
        }}}}

        .two-column-layout__right {{{{
            
            
        }}}}

        .sidebar-section {{{{
            margin-bottom: var(--space-3-compact);
        }}}}

        .sidebar-card {{{{
            background: var(--white);
            border-radius: var(--radius-lg);
            padding: var(--space-3-compact);
            box-shadow: var(--shadow-md);
            margin-bottom: 12px;
        }}}}

        
        .chart-container {{{{
            position: relative;
            margin: 20px auto;
            max-width: 700px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}}}

        
        .section {{{{
            margin-bottom: var(--space-6-compact);
        }}}}

        .section-header {{{{
            margin-bottom: var(--space-3-compact);
        }}}}

        .section-title {{{{
            font-size: 1.125rem;  
        }}}}

        @media (max-width: 1200px) {{{{
            .two-column-layout {{{{
                grid-template-columns: 1fr;
                gap: var(--space-4);
            }}}}

            .two-column-layout__right {{{{
                position: static;
                max-height: none;
            }}}}
        }}}}

        @media (max-width: 768px) {{{{
            .chart-container {{{{
                max-width: 100%;
                margin: 20px auto;
                padding: 15px;
            }}}}
        }}}}

        
        .inbody-metrics-container {{{{
            background: var(--inbody-white);
            padding: 20px;
            border-radius: 8px;
            box-shadow: var(--shadow-md);
            margin: 20px 0;
        }}}}

        .inbody-metric-row {{{{
            display: grid;
            grid-template-columns: 2fr 3fr 1fr 1.5fr 1fr 0.8fr;
            gap: 10px;
            align-items: center;
            padding: 8px 0;
            border-bottom: 0.5px solid var(--inbody-gray-light);
            font-size: 11px;
        }}}}

        .inbody-metric-row:last-child {{{{
            border-bottom: none;
        }}}}

        .inbody-metric-label {{{{
            font-weight: 500;
            color: var(--inbody-black);
            font-size: 10px;
        }}}}

        .inbody-metric-bar-container {{{{
            position: relative;
            height: 24px;
        }}}}

        .inbody-bar-track {{{{
            position: relative;
            width: 100%;
            height: 100%;
            background: var(--inbody-bg);
            border-radius: 4px;
            overflow: hidden;
        }}}}

        .inbody-bar-centerline {{{{
            position: absolute;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 2px;
            background: var(--inbody-gray-medium);
            transform: translateX(-50%);
            z-index: 1;
        }}}}

        .inbody-bar {{{{
            position: absolute;
            height: 100%;
            transition: width 0.3s ease;
            z-index: 2;
        }}}}

        .inbody-bar.left {{{{
            right: 50%;
            border-radius: 4px 0 0 4px;
        }}}}

        .inbody-bar.right {{{{
            left: 50%;
            border-radius: 0 4px 4px 0;
        }}}}

        .inbody-bar.center {{{{
            left: 50%;
            transform: translateX(-50%);
            border-radius: 4px;
            
        }}}}

        .inbody-metric-value {{{{
            font-weight: 600;
            color: var(--inbody-black);
            text-align: right;
            font-size: 11px;
        }}}}

        .inbody-metric-optimal {{{{
            color: var(--inbody-gray-dark);
            font-size: 9px;
            text-align: center;
        }}}}

        .inbody-metric-status {{{{
            font-weight: 500;
            text-align: center;
            font-size: 10px;
        }}}}

        .inbody-metric-status.status-deficit {{{{
            color: var(--inbody-red);
        }}}}

        .inbody-metric-status.status-optimal {{{{
            color: var(--inbody-black);
        }}}}

        .inbody-metric-status.status-excess {{{{
            color: var(--inbody-gray-dark);
        }}}}

        .inbody-metric-score {{{{
            font-weight: 600;
            color: var(--inbody-black);
            text-align: right;
            font-size: 12px;
        }}}}

        
        .inbody-table-container {{{{
            background: var(--inbody-white);
            padding: 15px;
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
            margin: 20px 0;
            overflow-x: auto;
        }}}}

        .inbody-metrics-table {{{{
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
        }}}}

        .inbody-metrics-table thead {{{{
            background: var(--inbody-bg);
        }}}}

        .inbody-metrics-table th {{{{
            padding: 8px 6px;
            text-align: left;
            font-weight: 600;
            color: var(--inbody-black);
            border-bottom: 0.5px solid var(--inbody-gray-medium);
            font-size: 9px;
        }}}}

        .inbody-metrics-table td {{{{
            padding: 6px;
            border-bottom: 0.5px solid var(--inbody-gray-light);
            font-size: 9px;
        }}}}

        .inbody-metrics-table tbody tr:last-child td {{{{
            border-bottom: none;
        }}}}

        .inbody-metrics-table tbody tr:hover {{{{
            background: var(--inbody-bg);
        }}}}

        .inbody-metrics-table .metric-name {{{{
            font-weight: 500;
            color: var(--inbody-black);
        }}}}

        .inbody-metrics-table .metric-value {{{{
            font-weight: 600;
            text-align: right;
            color: var(--inbody-black);
        }}}}

        .inbody-metrics-table .metric-optimal {{{{
            text-align: center;
            color: var(--inbody-gray-dark);
            font-size: 8px;
        }}}}

        .inbody-metrics-table .metric-status {{{{
            text-align: center;
            font-weight: 500;
        }}}}

        .inbody-metrics-table .metric-status.status-deficit {{{{
            color: var(--inbody-red);
        }}}}

        .inbody-metrics-table .metric-status.status-optimal {{{{
            color: var(--inbody-black);
        }}}}

        .inbody-metrics-table .metric-status.status-excess {{{{
            color: var(--inbody-gray-dark);
        }}}}

        .inbody-metrics-table .metric-score {{{{
            text-align: right;
            font-weight: 600;
            color: var(--inbody-black);
            font-size: 10px;
        }}}}

        
        .three-column-layout {{
            display: grid;
            grid-template-columns: 48% 48%;
            gap: 4%;
            margin-top: var(--space-4-compact);
            align-items: start;
        }}

        .three-column-layout__left {{
            
        }}

        .three-column-layout__middle {{
            
        }}

        
        .three-column-layout .section {{
            margin-bottom: var(--space-3-compact);
        }}

        .three-column-layout .section-title {{
            font-size: 1rem;
        }}

        
        .hero-summary {{
            max-width: 48%;
            margin: var(--space-4-compact) 0;
            padding: var(--space-4-compact);
            background: linear-gradient(135deg, var(--inbody-primary) 0%, var(--inbody-primary-dark) 100%);
            border-radius: 12px;
            color: var(--inbody-white);
            box-shadow: var(--shadow-md);
        }}

        .hero-summary__title {{
            font-size: 0.875rem;
            font-weight: 500;
            opacity: 0.9;
            margin-bottom: 8px;
        }}

        .hero-summary__score {{
            font-size: 3rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 12px;
        }}

        .hero-summary__score-max {{
            font-size: 1.5rem;
            opacity: 0.7;
        }}

        .hero-summary__status-bar {{
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 8px;
        }}

        .hero-summary__status-fill {{
            height: 100%;
            background: var(--inbody-white);
            border-radius: 4px;
            transition: width 0.3s ease;
        }}

        .hero-summary__percentile {{
            font-size: 0.875rem;
            margin-bottom: 16px;
            opacity: 0.9;
        }}

        .hero-summary__profile {{
            padding-top: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .hero-summary__profile-label {{
            font-size: 0.75rem;
            opacity: 0.7;
            margin-bottom: 4px;
        }}

        .hero-summary__profile-type {{
            font-size: 1.25rem;
            font-weight: 600;
        }}
        .three-column-layout .section {{{{
            margin-bottom: var(--space-3-compact);
        }}}}

        .three-column-layout .section-title {{{{
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }}}}

        /* Recommendation Table Styles */
        .recommendation-table {{{{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: var(--space-3-compact);
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}}}

        .recommendation-table thead {{{{
            background: linear-gradient(135deg, var(--inbody-primary) 0%, var(--inbody-primary-dark) 100%);
        }}}}

        .recommendation-table th {{{{
            color: white;
            font-weight: 600;
            font-size: 0.875rem;
            padding: 12px 16px;
            text-align: left;
        }}}}

        .recommendation-table th:first-child {{{{
            width: 80px;
            text-align: center;
        }}}}

        .recommendation-table th:last-child {{{{
            width: 100px;
            text-align: center;
        }}}}

        .recommendation-table tr {{{{
            border-bottom: 1px solid var(--inbody-border);
            transition: background-color 0.2s ease;
        }}}}

        .recommendation-table tbody tr:last-child {{{{
            border-bottom: none;
        }}}}

        .recommendation-table tbody tr:hover {{{{
            background-color: var(--inbody-bg);
        }}}}

        .recommendation-table td {{{{
            padding: 16px;
            vertical-align: middle;
        }}}}

        .recommendation-table td:first-child {{{{
            text-align: center;
            font-weight: 600;
        }}}}

        .recommendation-table td:last-child {{{{
            text-align: center;
        }}}}

        .recommendation-table__number {{{{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: var(--inbody-primary);
            color: white;
            font-weight: 700;
            font-size: 1rem;
        }}}}

        /* Strength and Improvement Tables */
        .strength-table, .improvement-table {{{{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: var(--space-2-compact);
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
            font-size: 0.875rem;
        }}}}

        .strength-table thead, .improvement-table thead {{{{
            background: var(--inbody-bg);
        }}}}

        .strength-table th, .improvement-table th {{{{
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
            color: var(--inbody-gray-dark);
            border-bottom: 2px solid var(--inbody-border);
        }}}}

        .strength-table th:first-child, .improvement-table th:first-child {{{{
            width: 50px;
            text-align: center;
        }}}}

        .strength-table td, .improvement-table td {{{{
            padding: 12px;
            border-bottom: 1px solid var(--inbody-border);
            vertical-align: top;
        }}}}

        .strength-table td:first-child, .improvement-table td:first-child {{{{
            text-align: center;
            font-weight: 600;
            color: var(--inbody-primary);
        }}}}

        .strength-table tbody tr:last-child td, 
        .improvement-table tbody tr:last-child td {{{{
            border-bottom: none;
        }}}}

        .strength-table tbody tr:hover,
        .improvement-table tbody tr:hover {{{{
            background-color: var(--inbody-bg);
        }}}}

        .three-column-layout .chart-container {{{{
            height: 180px;
            padding: 10px;
            margin: 10px 0;
        }}}}

        
        .three-column-layout .inbody-metrics-container {{{{
            padding: 15px;
            margin: 15px 0;
        }}}}

        .three-column-layout .inbody-table-container {{{{
            padding: 10px;
            margin: 15px 0;
        }}}}

        @media (max-width: 1200px) {{{{
            .three-column-layout {{{{
                grid-template-columns: 1fr;
                gap: 20px;
            }}}}
        }}}}

        
        .print-button {{{{
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 14px 28px;
            background: var(--primary-600);
            color: white;
            border: none;
            border-radius: var(--radius-lg);
            font-size: var(--text-base);
            font-weight: var(--weight-semibold);
            cursor: pointer;
            box-shadow: var(--shadow-lg);
            transition: all 0.3s ease;
            z-index: 1000;
        }}}}

        .print-button:hover {{{{
            background: var(--primary-700);
            box-shadow: var(--shadow-xl);
            transform: translateY(-2px);
        }}}}

        .print-button:active {{{{
            transform: translateY(0);
        }}}}

        .print-button__icon {{{{
            margin-right: 8px;
        }}}}

        
        .strengths-improvements-container {{{{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}}}

        .strength-improvement-table {{{{
            background: var(--inbody-white);
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
            overflow: hidden;
        }}}}

        .strength-improvement-table__header {{{{
            background: var(--inbody-bg);
            padding: 12px 15px;
            border-bottom: 1px solid var(--inbody-gray-medium);
        }}}}

        .strength-improvement-table__title {{{{
            font-size: 1rem;
            font-weight: 600;
            color: var(--inbody-black);
            margin: 0;
        }}}}

        .strength-improvement-table--strength .strength-improvement-table__header {{{{
            border-left: 4px solid #10B981;
        }}}}

        .strength-improvement-table--improvement .strength-improvement-table__header {{{{
            border-left: 4px solid #F59E0B;
        }}}}

        .strength-improvement-table table {{{{
            width: 100%;
            border-collapse: collapse;
        }}}}

        .strength-improvement-table th {{{{
            background: var(--inbody-bg);
            padding: 8px 10px;
            text-align: left;
            font-weight: 600;
            color: var(--inbody-black);
            font-size: 9px;
            border-bottom: 0.5px solid var(--inbody-gray-medium);
        }}}}

        .strength-improvement-table td {{{{
            padding: 8px 10px;
            border-bottom: 0.5px solid var(--inbody-gray-light);
            font-size: 9px;
            color: var(--inbody-black);
            vertical-align: top;
        }}}}

        .strength-improvement-table tbody tr:last-child td {{{{
            border-bottom: none;
        }}}}

        .strength-improvement-table tbody tr:hover {{{{
            background: var(--inbody-bg);
        }}}}

        .strength-improvement-table td:first-child {{{{
            width: 40px;
            text-align: center;
            font-weight: 600;
            color: var(--inbody-black);
        }}}}

        .strength-improvement-table td:nth-child(2) {{{{
            font-weight: 500;
            width: 40%;
        }}}}

        .strength-improvement-table td:nth-child(3) {{{{
            color: var(--inbody-gray-dark);
            font-size: 8px;
            width: calc(60% - 40px);
        }}}}

        
        @media print {{{{
            * {{{{
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}}}

            body {{{{
                font-size: 10px;
                line-height: 1.4;
                background: white;
            }}}}

            .report-container {{{{
                max-width: 100%;
                padding: 15px;
            }}}}

            .section {{{{
                margin-bottom: 15px;
                page-break-inside: auto;
            }}}}

            .section-title {{{{
                font-size: 13px;
                margin-bottom: 10px;
                padding-bottom: 6px;
            }}}}

            .subsection-header {{{{
                font-size: 11px;
                margin-bottom: 8px;
            }}}}

            /* InBody Bars - Maintain good size and color */
            .inbody-metric-bar-container {{{{
                height: 20px;
                margin-bottom: 10px;
            }}}}

            .inbody-bar-track {{{{
                height: 20px;
            }}}}

            .inbody-metric-label {{{{
                font-size: 9px;
                margin-bottom: 4px;
            }}}}

            .inbody-metric-value {{{{
                font-size: 9px;
            }}}}

            /* Tables */
            table {{{{
                font-size: 9px;
                page-break-inside: auto;
            }}}}

            table th {{{{
                font-size: 9.5px;
                padding: 6px 8px;
            }}}}

            table td {{{{
                padding: 5px 8px;
            }}}}

            /* Metrics */
            .metric-row {{{{
                padding: 6px 8px;
                margin-bottom: 4px;
            }}}}

            .metric-label {{{{
                font-size: 9px;
            }}}}

            .metric-value {{{{
                font-size: 9px;
            }}}}

            /* Layout */
            .three-column-layout {{{{
                gap: 3%;
                page-break-inside: auto;
            }}}}

            .three-column-layout__left,
            .three-column-layout__middle {{{{
                page-break-inside: auto;
            }}}}

            /* Charts - maintain size */
            canvas {{{{
                max-width: 100%;
                height: auto;
                page-break-inside: avoid;
            }}}}

            /* Hero Summary */
            .hero-summary {{{{
                padding: 12px;
                page-break-after: auto;
            }}}}

            .hero-summary__score {{{{
                font-size: 2.5rem;
            }}}}

            .hero-summary__profile-type {{{{
                font-size: 1.1rem;
            }}}}

            /* Recommendations */
            .recommendation-table {{{{
                font-size: 9px;
            }}}}

            .recommendation-table th {{{{
                padding: 6px 8px;
            }}}}

            .recommendation-table td {{{{
                padding: 5px 8px;
            }}}}

            /* Strength/Improvement tables */
            .strength-table,
            .improvement-table {{{{
                font-size: 9px;
            }}}}

            /* Footer */
            .report-footer {{{{
                font-size: 8px;
                padding: 10px 0;
                margin-top: 20px;
            }}}}

            /* Hide non-essential elements */
            .no-print {{{{
                display: none;
            }}}}

            /* Ensure colors print */
            .inbody-bar {{{{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}}}

            .status-bar__fill {{{{
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }}}}
        }}}}

        .recommendation-table__header {{{{
            background: var(--inbody-primary) !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}}}

        .recommendation-table__row {{{{
            page-break-inside: avoid;
        }}}}
        
        .hero-evaluation-container {{{{
            grid-template-columns: 100%;
            gap: 6px;
            margin: 6px 0;
            page-break-inside: avoid;
        }}}}
            
            @page {{{{
                size: A4;
                margin: 8mm 10mm;
            }}}}

            
            .print-button {{{{
                display: none !important;
            }}}}

            
            .container {{{{
                max-width: 100%;
                padding: 0;
            }}}}

            
            .report-header {{{{
                padding: 6px 8px;
                margin-bottom: 8px;
                page-break-after: avoid;
                border-bottom: 1.5px solid var(--primary-700);
            }}}}

            .report-header__title {{{{
                font-size: 1rem;
                margin-bottom: 2px;
            }}}}

            .report-header__meta {{{{
                font-size: 0.65rem;
            }}}}

            
            .hero-summary {{{{
                padding: 8px;
                margin-bottom: 8px;
                
            }}}}

            .hero-summary__title {{{{
                font-size: 0.75rem;
            }}}}

            .hero-summary__score {{{{
                font-size: 1.8rem;
            }}}}

            
            .three-column-layout {{{{
                display: block !important;
            }}}}

            .three-column-layout__left,
            .three-column-layout__middle,
            .three-column-layout__right {{{{
                width: 100%;
                page-break-inside: avoid;
            }}}}

            
            .section {{{{
                margin-bottom: 6px;
                page-break-inside: avoid;
            }}}}

            .section-title {{{{
                font-size: 0.85rem;
                margin-bottom: 3px;
            }}}}

            .section-subtitle {{{{
                font-size: 0.65rem;
            }}}}

            
            .inbody-metrics-container {{{{
                padding: 6px;
                margin: 6px 0;
            }}}}

            .inbody-metric-row {{{{
                padding: 2px 0;
                font-size: 6.5px;
                grid-template-columns: 1.8fr 2.5fr 0.8fr 1.2fr 0.8fr 0.6fr;
                gap: 6px;
            }}}}

            .inbody-metric-label {{{{
                font-size: 6.5px;
            }}}}

            .inbody-metric-bar-container {{{{
                height: 14px;
            }}}}

            .inbody-metric-value,
            .inbody-metric-optimal,
            .inbody-metric-status,
            .inbody-metric-score {{{{
                font-size: 6.5px;
            }}}}

            
            .inbody-table-container {{{{
                padding: 4px;
                margin: 6px 0;
            }}}}

            .inbody-metrics-table {{{{
                font-size: 6px;
            }}}}

            .inbody-metrics-table th,
            .inbody-metrics-table td {{{{
                padding: 2px 3px;
                font-size: 6px;
            }}}}

            
            .chart-container {{{{
                height: 150px !important;
                max-height: 150px;
                overflow: hidden;
                padding: 6px;
                margin: 6px 0;
                page-break-inside: avoid;
            }}}}

            
            .chart-container canvas {{{{
                max-width: 100% !important;
                max-height: 138px !important;  
                object-fit: contain;
            }}}}

            
            .metric-stats-grid {{{{
                margin-top: 4px;
            }}}}

            .metric-stat-pill {{{{
                padding: 2px 4px;
                font-size: 6px;
            }}}}

            .metric-stat-pill__label,
            .metric-stat-pill__value {{{{
                font-size: 6px;
            }}}}

            
            .insight-card,
            .recommendation-card {{{{
                padding: 4px 6px;
                margin-bottom: 4px;
                page-break-inside: avoid;
            }}}}

            .insight-card__title,
            .recommendation-card__title {{{{
                font-size: 0.7rem;
                margin-bottom: 2px;
            }}}}

            .insight-card__description,
            .recommendation-card__description {{{{
                font-size: 0.65rem;
                line-height: 1.2;
            }}}}

            
            .grid,
            .grid-cols-2,
            .grid-cols-3 {{{{
                display: block !important;
                gap: 0 !important;
            }}}}

            .grid > *,
            .grid-cols-2 > *,
            .grid-cols-3 > * {{{{
                width: 100% !important;
                display: block !important;
                margin-bottom: 8px;
                page-break-inside: avoid;
            }}}}

            
            .grid > *:last-child,
            .grid-cols-2 > *:last-child,
            .grid-cols-3 > *:last-child {{{{
                margin-bottom: 0;
            }}}}

            
            .report-footer {{{{
                margin-top: 8px;
                font-size: 0.6rem;
                page-break-before: avoid;
            }}}}

            .report-footer__card {{{{
                padding: 4px;
            }}}}

            
            .summary-card {{{{
                padding: 6px;
                margin: 6px 0;
                page-break-inside: avoid;
            }}}}

            .summary-card__text {{{{
                font-size: 0.65rem;
                line-height: 1.3;
            }}}}

            
            .strengths-improvements-container {{{{
                gap: 10px;
                margin: 10px 0;
            }}}}

            .strength-improvement-table__header {{{{
                padding: 6px 8px;
            }}}}

            .strength-improvement-table__title {{{{
                font-size: 0.7rem;
            }}}}

            .strength-improvement-table th,
            .strength-improvement-table td {{{{
                padding: 4px 6px;
                font-size: 6px;
            }}}}

            .strength-improvement-table td:nth-child(3) {{{{
                font-size: 5.5px;
            }}}}

            
            body {{{{
                font-size: 7.5px;
                line-height: 1.25;
            }}}}
        }}}}
    </style>

    <!-- Chart.js Library -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="report-header">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="report-header__title">TVAS 교수 분석 보고서</h1>
                    <div class="report-header__meta">
                        분석 ID: {analysis_id} | 생성일: {timestamp}
                    </div>
                </div>
                <div class="report-header__info">
                    <div class="report-header__subtitle">교사 발화 분석 시스템</div>
                    <div class="report-header__badge">전문 진단 보고서</div>
                </div>
            </div>
        </header>

        <!-- Hero Summary -->
        {hero_html}

        <!-- Three-Column Layout -->
        <div class="three-column-layout">
            <!-- Left Column: InBody Bars and Table -->
            <div class="three-column-layout__left">

        <!-- InBody Horizontal Metrics Bars -->
        <section class="section">
            <div class="section-header">
                <h2 class="section-title">📊 전체 지표 현황</h2>
            </div>
            {inbody_bars_html}
        </section>

        <!-- InBody Metrics Detail Table -->
        <section class="section">
            <div class="section-header">
                <h2 class="section-title">📋 지표 상세</h2>
            </div>
            {inbody_table_html}
        </section>

        <!-- Strengths & Improvements Tables -->
        <section class="section">
            <div class="section-header">
                <h2 class="section-title">💡 강점 및 개선 영역</h2>
            </div>
            {strengths_improvements_tables_html}

            <!-- Pattern Analysis (moved from middle column) -->
            <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid var(--inbody-bg);">
                <div class="subsection-header" style="margin-bottom: 12px;">
                    <span class="subsection-header__icon">🎯</span>
                    <h3 class="subsection-header__title">교수 패턴 분석</h3>
                </div>
                <p style="color: var(--inbody-gray-dark); font-size: 9px; margin-bottom: 12px;">
                    이상적 교수 패턴과의 유사도 비교
                </p>
                <div class="grid grid-cols-2 gap-6">
                    <div>
                        <div class="subsection-header">
                            <span class="subsection-header__icon">🔍</span>
                            <h3 class="subsection-header__title">패턴 유사도 분석</h3>
                        </div>
                        {pattern_similarity_chart}
                    </div>
                    <div>
                        <div class="card p-6">
                            <h3 class="text-xl font-bold text-primary-700 mb-2">
                                가장 유사한 패턴: {best_pattern_name}
                            </h3>
                            <p class="text-gray-700 mb-3">
                                {best_pattern_description}
                            </p>
                            <div class="flex items-center gap-2">
                                <div class="status-bar" style="width: 100%; height: 12px; border-radius: 6px;">
                                    <div class="status-bar__fill" style="width: {best_pattern_similarity:.0f}%; background: var(--primary-500);"></div>
                                </div>
                                <span class="text-2xl font-mono font-bold text-primary-700">{best_pattern_similarity:.0f}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

            </div>
            <!-- End Left Column -->

            <!-- Middle Column: Distribution Charts -->
            <div class="three-column-layout__middle">

        <!-- Distribution Analysis -->
        <section class="section">
            <div class="section-header">
                <h2 class="section-title">수업 구조 분석</h2>
                <p class="section-subtitle">수업 단계, 교수 기능, 인지 수준 분포</p>
            </div>
            <div class="grid grid-cols-3 gap-6">
                <div>
                    <div class="subsection-header">
                        <span class="subsection-header__icon">⏱️</span>
                        <h3 class="subsection-header__title">수업 단계 분포</h3>
                    </div>
                    {stage_distribution_chart}
                    
                </div>
                <div>
                    <div class="subsection-header">
                        <span class="subsection-header__icon">🎯</span>
                        <h3 class="subsection-header__title">교수 기능 분포</h3>
                    </div>
                    {context_distribution_chart}
                    
                </div>
                <div>
                    <div class="subsection-header">
                        <span class="subsection-header__icon">🧠</span>
                        <h3 class="subsection-header__title">인지 수준 분포</h3>
                    </div>
                    {level_distribution_chart}
                    
                </div>
            </div>
        </section>

        <!-- Coaching Recommendations (moved from right column) -->
        <section class="section">
            <div class="section-header">
                <h2 class="section-title">🎯 우선순위 코칭 추천</h2>
                <p class="section-subtitle">개선을 위한 구체적인 실천 과제</p>
            </div>
            {recommendations_html}
        </section>
            </div>
            <!-- End Middle Column -->


        </div>
        <!-- End Three-Column Layout -->

        <!-- Overall Assessment -->
        <section class="section overall-evaluation" style="margin-top: 0; margin-bottom: 0;">
            <div class="section-header">
                <h2 class="section-title">종합 평가</h2>
            </div>
            <div class="summary-card">
                <div class="summary-card__icon-wrapper">
                    <div class="summary-card__icon">📋</div>
                </div>
                <div class="summary-card__content">
                    <p class="summary-card__text">
                        {coaching_feedback.get('overall_assessment', '분석 중...')}
                    </p>
                </div>
            </div>
        </section>
        </div>


        <!-- Footer -->
        <footer class="report-footer" style="margin-top: var(--space-8-compact); padding-top: var(--space-6-compact); border-top: 2px solid var(--gray-300);">
            <div class="report-footer__card">
                <div class="report-footer__icon">🎓</div>
                <p class="report-footer__text">
                    이 보고서는 TVAS (Teacher Voice Analysis System)에 의해 자동 생성되었습니다.
                </p>
                <p class="report-footer__contact">
                    질문이나 피드백: <a href="mailto:support@tvas.ai" class="report-footer__link">support@tvas.ai</a>
                </p>
                <div class="report-footer__timestamp">
                    생성 시각: {timestamp} | 분석 ID: {analysis_id}
                </div>
            </div>
        </footer>
    </div>

    <!-- Floating Print/PDF Download Button -->
    <button onclick="downloadPDF()" class="print-button">
        <span class="print-button__icon">📥</span>
        PDF 다운로드
    </button>

    <!-- Print/PDF Download Script -->
    <script>
        function downloadPDF() {{{{
            // Set document title for PDF filename
            const originalTitle = document.title;
            const timestamp = new Date().toISOString().slice(0, 10);
            document.title = `TVAS_교수분석보고서_${{{timestamp}}}`;

            // Trigger print dialog
            window.print();

            // Restore original title
            setTimeout(() => {{{{
                document.title = originalTitle;
            }}}}, 100);
        }}}}

        // Keyboard shortcut: Ctrl+P or Cmd+P
        document.addEventListener('keydown', (e) => {{{{
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {{{{
                e.preventDefault();
                downloadPDF();
            }}}}
        }}}});
    </script>
</body>
</html>
        '''

        # Fix CSS double braces
        html = self._fix_css_braces(html)
        
        return html


# Test/Demo function
if __name__ == "__main__":
    generator = DiagnosticReportGenerator()

    # Mock data for testing
    mock_data = {
        "analysis_id": "test_001",
        "framework": "cbil_comprehensive",
        "coaching_feedback": {
            "overall_assessment": "이 수업은 전반적으로 균형잡힌 교수 전략을 보여줍니다. 도입, 전개, 정리 단계가 적절히 배분되었으며, 학생 참여를 유도하는 질문이 효과적으로 사용되었습니다.",
            "strengths": [
                "높은 인지 수준의 질문을 통해 학생들의 고차원적 사고를 촉진함",
                "수업 단계 간 전환이 자연스럽고 논리적임",
                "다양한 교수 맥락(설명, 질문, 피드백)을 적절히 혼합 사용"
            ],
            "areas_for_improvement": [
                "학생 발화에 대한 피드백 빈도가 낮음",
                "정리 단계에서 학습 내용 정리 시간이 부족함",
                "개별 학생에 대한 맞춤형 질문이 제한적임"
            ],
            "priority_actions": [
                "학생 응답 후 즉각적이고 구체적인 피드백 제공하기",
                "정리 단계를 최소 5분 이상 확보하여 학습 내용 정리하기",
                "다양한 수준의 학생을 고려한 차별화된 질문 전략 수립하기",
                "학생 간 상호작용을 촉진하는 질문 기법 사용하기",
                "수업 중간에 형성평가를 통해 이해도 점검하기"
            ]
        },
        "quantitative_metrics": {},
        "pattern_matching": {
            "best_match": {
                "pattern_name": "균형잡힌 촉진자"
            }
        },
        "matrix_analysis": {}
    }

    html = generator.generate_html_report(mock_data)

    # Save to file for testing
    with open("test_diagnostic_report.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ diagnostic report generated: test_diagnostic_report.html")
    print(f"✓ Report length: {len(html)} characters")
