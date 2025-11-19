"""
Coaching Generator - Generates personalized teaching coaching feedback
Uses OpenAI GPT-4 to create actionable, evidence-based coaching
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import jsonschema

from services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


@dataclass
class CoachingFeedback:
    """Structured coaching feedback"""
    overall_assessment: str
    strengths: List[Dict[str, str]]  # Changed: Now accepts [{"point": "...", "detail": "..."}]
    areas_for_growth: List[Dict[str, str]]  # Changed: Now accepts [{"point": "...", "detail": "..."}]
    priority_actions: List[str]
    pedagogical_recommendations: Optional[Dict[str, str]] = None
    resources_and_strategies: Optional[List[str]] = None
    next_session_goals: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class CoachingGenerator:
    """Generates personalized coaching feedback for teachers"""

    # Metric name translations (technical → Korean)
    METRIC_TRANSLATIONS = {
        # Time distribution metrics
        'intro_time_ratio': '도입 시간 비율',
        'development_time_ratio': '전개 시간 비율',
        'closing_time_ratio': '정리 시간 비율',
        'stage_balance': '단계별 균형',

        # Context/function metrics
        'context_diversity': '맥락 다양성',
        'explanation_ratio': '설명 비율',
        'question_ratio': '질문 비율',
        'feedback_ratio': '피드백 비율',
        'facilitation_ratio': '촉진 비율',
        'management_ratio': '관리 비율',

        # Cognitive level metrics
        'avg_cognitive_level': '평균 인지 수준',
        'cognitive_diversity': '인지 다양성',
        'higher_order_ratio': '고차원적 사고 비율',
        'cognitive_progression': '인지적 진행도',
        'l1_ratio': 'L1 수준 비율',
        'l2_ratio': 'L2 수준 비율',
        'l3_ratio': 'L3 수준 비율',

        # Interaction metrics
        'utterance_density': '발화 밀도',
        'avg_utterance_length': '평균 발화 길이',
        'avg_wait_time': '평균 대기 시간',
        'interaction_rate': '상호작용 빈도',

        # Pattern matching
        'pattern_alignment': '패턴 일치도',
        'direct_instruction_match': '직접 교수법 일치도',
        'inquiry_based_match': '탐구 기반 일치도',
        'collaborative_match': '협력 학습 일치도',

        # CBIL metrics
        'cbil_alignment': 'CBIL 정렬도',
        'cbil_stage_coverage': 'CBIL 단계 포함률',

        # Quality metrics
        'question_quality': '질문 품질',
        'feedback_quality': '피드백 품질',
        'explanation_clarity': '설명 명확성'
    }

    # Metric units (for proper display)
    METRIC_UNITS = {
        'utterance_density': '회/분',
        'avg_utterance_length': '단어',
        'avg_wait_time': '초',
        'avg_cognitive_level': '점',
        'intro_time_ratio': '%',
        'development_time_ratio': '%',
        'closing_time_ratio': '%',
        'question_ratio': '%',
        'feedback_ratio': '%',
        'explanation_ratio': '%',
        'facilitation_ratio': '%',
        'management_ratio': '%',
        'higher_order_ratio': '%',
        'l1_ratio': '%',
        'l2_ratio': '%',
        'l3_ratio': '%',
        'pattern_alignment': '%',
        'direct_instruction_match': '%',
        'inquiry_based_match': '%',
        'collaborative_match': '%'
    }

    def __init__(
        self,
        system_prompt_file: Optional[str] = None,
        templates_file: Optional[str] = None,
        schema_file: Optional[str] = None,
        openai_service: Optional[OpenAIService] = None
    ):
        """
        Args:
            system_prompt_file: Path to coaching_system.txt
            templates_file: Path to coaching_templates.yaml
            schema_file: Path to coaching_output.json
            openai_service: OpenAIService instance (creates new if None)
        """
        # Set default paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(current_dir)

        if system_prompt_file is None:
            system_prompt_file = os.path.join(base_dir, 'prompts', 'coaching_system.txt')

        if templates_file is None:
            templates_file = os.path.join(base_dir, 'prompts', 'coaching_templates.yaml')

        if schema_file is None:
            schema_file = os.path.join(base_dir, 'schemas', 'coaching_output.json')

        self.system_prompt_file = system_prompt_file
        self.templates_file = templates_file
        self.schema_file = schema_file

        # Load resources
        self.system_prompt = self._load_system_prompt()
        self.templates = self._load_templates()
        self.schema = self._load_schema()

        # OpenAI service
        self.openai_service = openai_service or OpenAIService()

        logger.info("CoachingGenerator initialized successfully")

    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            with open(self.system_prompt_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            raise

    def _load_templates(self) -> Dict[str, Any]:
        """Load prompt templates from YAML"""
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data['templates']
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
            raise

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema for validation"""
        try:
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise

    def _build_coaching_prompt(
        self,
        matrix_data: Dict[str, Any],
        metrics_data: Dict[str, Any],
        pattern_match: Dict[str, Any],
        template_name: str = "comprehensive_coaching",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build coaching prompt from analysis data

        Args:
            matrix_data: 3D matrix analysis results
            metrics_data: Quantitative metrics results
            pattern_match: Pattern matching results
            template_name: Name of template to use
            context: Additional context (subject, grade_level, etc.)

        Returns:
            Formatted prompt string
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")

        template = self.templates[template_name]['prompt_template']
        context = context or {}

        # Extract statistics from matrix data
        stats = matrix_data.get('statistics', {})
        stage_stats = stats.get('stage_stats', {})
        context_stats = stats.get('context_stats', {})
        level_stats = stats.get('level_stats', {})

        # Calculate percentages
        stage_dist = stage_stats.get('stage_distribution', {})
        context_dist = context_stats.get('context_distribution', {})
        level_dist = level_stats.get('level_distribution', {})

        total_utterances = stats.get('total_utterances', 0)

        # Build key metrics summary with Korean translations
        key_metrics_list = []
        for metric_name, metric_result in metrics_data.items():
            # Get Korean translation or fallback to original name
            korean_name = self.METRIC_TRANSLATIONS.get(metric_name, metric_name)

            # Get unit if available
            unit = self.METRIC_UNITS.get(metric_name, '')

            # Format value with unit
            if unit == '%':
                value_str = f"{metric_result.value * 100:.1f}%"
            elif unit:
                value_str = f"{metric_result.value:.2f}{unit}"
            else:
                value_str = f"{metric_result.value:.2f}"

            # Format status in Korean
            status_korean = {
                'optimal': '최적',
                'good': '양호',
                'needs_improvement': '개선 필요',
                'critical': '주의 필요'
            }.get(metric_result.status, metric_result.status)

            key_metrics_list.append(
                f"  - {korean_name}: {value_str} "
                f"(점수: {metric_result.normalized_score:.1f}/100, "
                f"상태: {status_korean})"
            )
        key_metrics_str = "\n".join(key_metrics_list)

        # Format template
        formatted_prompt = template.format(
            # Stage distribution
            intro_time=stage_dist.get('introduction', 0),
            intro_count=stage_stats.get('counts_by_stage', {}).get('introduction', 0),
            dev_time=stage_dist.get('development', 0),
            dev_count=stage_stats.get('counts_by_stage', {}).get('development', 0),
            closing_time=stage_dist.get('closing', 0),
            closing_count=stage_stats.get('counts_by_stage', {}).get('closing', 0),

            # Context distribution
            explanation_pct=context_dist.get('explanation', 0),
            question_pct=context_dist.get('question', 0),
            feedback_pct=context_dist.get('feedback', 0),
            facilitation_pct=context_dist.get('facilitation', 0),
            management_pct=context_dist.get('management', 0),

            # Level distribution
            l1_pct=level_dist.get('L1', 0),
            l2_pct=level_dist.get('L2', 0),
            l3_pct=level_dist.get('L3', 0),
            avg_cognitive_level=level_stats.get('avg_cognitive_level', 0),

            # Pattern matching
            pattern_name=pattern_match.get('pattern_name', 'Unknown'),
            pattern_similarity=pattern_match.get('similarity_score', 0),
            match_quality=pattern_match.get('match_quality', 'Unknown'),
            pattern_description=pattern_match.get('pattern_description', ''),

            # Metrics
            key_metrics=key_metrics_str,

            # Context
            duration=context.get('duration', 'Unknown'),
            total_utterances=total_utterances,
            subject=context.get('subject', 'General'),
            grade_level=context.get('grade_level', 'Not specified')
        )

        return formatted_prompt

    def _validate_coaching_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate coaching output against JSON schema

        Args:
            data: Coaching feedback data

        Returns:
            True if valid, raises ValidationError if invalid
        """
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Coaching output validation failed: {e}")
            raise

    def _sanitize_coaching_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove English metric names from coaching output as safety measure

        Removes patterns like (utterance_density: 99.1/100) or (question_ratio: 0.25)
        from all text fields to ensure clean Korean-only output.

        Args:
            data: Coaching feedback data

        Returns:
            Sanitized coaching feedback data
        """
        import re

        # Pattern to match English metric names with optional scores
        # Matches: (metric_name: value) or (metric_name: value/100)
        metric_pattern = r'\s*\([a-z_]+(?:_[a-z]+)*:\s*[\d.]+(?:/100)?\)'

        def clean_text(text: str) -> str:
            """Remove metric patterns and clean up spacing"""
            if not text:
                return text
            # Remove metric patterns
            cleaned = re.sub(metric_pattern, '', text)
            # Clean up multiple spaces
            cleaned = re.sub(r'\s+', ' ', cleaned)
            return cleaned.strip()

        # Clean strengths
        if 'strengths' in data and isinstance(data['strengths'], list):
            for item in data['strengths']:
                if isinstance(item, dict):
                    if 'point' in item:
                        item['point'] = clean_text(item['point'])
                    if 'detail' in item:
                        item['detail'] = clean_text(item['detail'])

        # Clean areas_for_growth
        if 'areas_for_growth' in data and isinstance(data['areas_for_growth'], list):
            for item in data['areas_for_growth']:
                if isinstance(item, dict):
                    if 'point' in item:
                        item['point'] = clean_text(item['point'])
                    if 'detail' in item:
                        item['detail'] = clean_text(item['detail'])

        # Clean priority_actions (if they contain metric names)
        if 'priority_actions' in data and isinstance(data['priority_actions'], list):
            data['priority_actions'] = [clean_text(action) for action in data['priority_actions']]

        # Clean overall_assessment
        if 'overall_assessment' in data:
            data['overall_assessment'] = clean_text(data['overall_assessment'])

        logger.info("Coaching output sanitized - removed any English metric names")
        return data

    async def generate_coaching(
        self,
        matrix_data: Dict[str, Any],
        metrics_data: Dict[str, Any],
        pattern_match: Dict[str, Any],
        template_name: str = "comprehensive_coaching",
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> CoachingFeedback:
        """
        Generate personalized coaching feedback

        Args:
            matrix_data: 3D matrix analysis results
            metrics_data: Quantitative metrics results
            pattern_match: Pattern matching results
            template_name: Template to use
            context: Additional context
            max_retries: Maximum retry attempts

        Returns:
            CoachingFeedback object
        """
        logger.info(f"Generating coaching feedback using template: {template_name}")

        # Build prompt
        user_prompt = self._build_coaching_prompt(
            matrix_data=matrix_data,
            metrics_data=metrics_data,
            pattern_match=pattern_match,
            template_name=template_name,
            context=context
        )

        # Try multiple times with retry logic
        for attempt in range(max_retries):
            try:
                # Call OpenAI (GPT-5 default temperature=1.0)
                response_text = await self.openai_service.generate_text(
                    prompt=user_prompt,
                    system_prompt=self.system_prompt,
                    max_completion_tokens=2000  # ⚠️ GPT-5 parameter
                )

                # Parse JSON response
                # Try to extract JSON from markdown code blocks
                response_text = response_text.strip()
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    response_text = response_text[start:end].strip()
                elif '```' in response_text:
                    start = response_text.find('```') + 3
                    end = response_text.find('```', start)
                    response_text = response_text[start:end].strip()

                coaching_data = json.loads(response_text)

                # Validate against schema
                self._validate_coaching_output(coaching_data)

                # Sanitize output (remove English metric names as safety measure)
                coaching_data = self._sanitize_coaching_output(coaching_data)

                # Create CoachingFeedback object
                feedback = CoachingFeedback(
                    overall_assessment=coaching_data['overall_assessment'],
                    strengths=coaching_data['strengths'],
                    areas_for_growth=coaching_data['areas_for_growth'],
                    priority_actions=coaching_data['priority_actions'],
                    pedagogical_recommendations=coaching_data.get('pedagogical_recommendations'),
                    resources_and_strategies=coaching_data.get('resources_and_strategies'),
                    next_session_goals=coaching_data.get('next_session_goals'),
                    metadata={
                        'template_used': template_name,
                        'attempt': attempt + 1,
                        'total_utterances': matrix_data.get('statistics', {}).get('total_utterances', 0)
                    }
                )

                logger.info(f"Coaching feedback generated successfully on attempt {attempt + 1}")
                return feedback

            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("All retry attempts exhausted")
                    raise
                continue

            except Exception as e:
                logger.error(f"Unexpected error generating coaching: {e}")
                raise

        raise RuntimeError("Failed to generate valid coaching feedback")

    def to_dict(self, feedback: CoachingFeedback) -> Dict[str, Any]:
        """
        Convert CoachingFeedback to dictionary

        Args:
            feedback: CoachingFeedback object

        Returns:
            Dictionary representation
        """
        return {
            'overall_assessment': feedback.overall_assessment,
            'strengths': feedback.strengths,
            'areas_for_growth': feedback.areas_for_growth,
            'priority_actions': feedback.priority_actions,
            'pedagogical_recommendations': feedback.pedagogical_recommendations,
            'resources_and_strategies': feedback.resources_and_strategies,
            'next_session_goals': feedback.next_session_goals,
            'metadata': feedback.metadata
        }

    def to_markdown(self, feedback: CoachingFeedback) -> str:
        """
        Convert CoachingFeedback to markdown format

        Args:
            feedback: CoachingFeedback object

        Returns:
            Markdown formatted string
        """
        md = f"# Teaching Coaching Feedback\n\n"
        md += f"## Overall Assessment\n\n{feedback.overall_assessment}\n\n"

        md += f"## Strengths\n\n"
        for i, strength in enumerate(feedback.strengths, 1):
            if isinstance(strength, dict):
                md += f"{i}. **{strength['point']}**\n   {strength['detail']}\n"
            else:
                # Fallback for old string format
                md += f"{i}. {strength}\n"
        md += "\n"

        md += f"## Areas for Growth\n\n"
        for i, area in enumerate(feedback.areas_for_growth, 1):
            if isinstance(area, dict):
                md += f"{i}. **{area['point']}**\n   {area['detail']}\n"
            else:
                # Fallback for old string format
                md += f"{i}. {area}\n"
        md += "\n"

        md += f"## Priority Actions\n\n"
        for i, action in enumerate(feedback.priority_actions, 1):
            md += f"{i}. {action}\n"
        md += "\n"

        if feedback.pedagogical_recommendations:
            md += f"## Pedagogical Recommendations\n\n"
            for key, value in feedback.pedagogical_recommendations.items():
                title = key.replace('_', ' ').title()
                md += f"### {title}\n{value}\n\n"

        if feedback.resources_and_strategies:
            md += f"## Resources and Strategies\n\n"
            for i, resource in enumerate(feedback.resources_and_strategies, 1):
                md += f"{i}. {resource}\n"
            md += "\n"

        if feedback.next_session_goals:
            md += f"## Next Session Goals\n\n"
            for i, goal in enumerate(feedback.next_session_goals, 1):
                md += f"{i}. {goal}\n"
            md += "\n"

        return md

    async def generate_coaching_with_cbil(
        self,
        matrix_data: Dict[str, Any],
        metrics_data: Dict[str, Any],
        pattern_match: Dict[str, Any],
        cbil_scores: Dict[str, Any],
        cbil_alignment: float,
        template_name: str = "comprehensive_coaching",
        context: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> CoachingFeedback:
        """
        Generate coaching feedback with CBIL framework integration

        Args:
            matrix_data: 3D matrix analysis results
            metrics_data: Quantitative metrics results
            pattern_match: Pattern matching results
            cbil_scores: CBIL 7-stage scores dictionary
            cbil_alignment: CBIL-Module3 alignment score (0-1)
            template_name: Template to use
            context: Additional context
            max_retries: Maximum retry attempts

        Returns:
            CoachingFeedback object with CBIL insights
        """
        logger.info(f"Generating CBIL-integrated coaching using template: {template_name}")

        # Load CBIL coaching template
        cbil_template_file = os.path.join(
            os.path.dirname(self.templates_file),
            'cbil_coaching_templates.yaml'
        )

        try:
            with open(cbil_template_file, 'r', encoding='utf-8') as f:
                cbil_templates = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load CBIL templates: {e}, using standard template")
            return await self.generate_coaching(
                matrix_data, metrics_data, pattern_match,
                template_name, context, max_retries
            )

        # Build CBIL-enhanced prompt
        user_prompt = self._build_cbil_enhanced_prompt(
            matrix_data=matrix_data,
            metrics_data=metrics_data,
            pattern_match=pattern_match,
            cbil_scores=cbil_scores,
            cbil_alignment=cbil_alignment,
            cbil_templates=cbil_templates,
            context=context or {}
        )

        # Generate with retry logic
        for attempt in range(max_retries):
            try:
                response_text = await self.openai_service.generate_text(
                    prompt=user_prompt,
                    system_prompt=self.system_prompt,
                    max_completion_tokens=2500  # ⚠️ GPT-5 parameter - Longer for CBIL integration (default temp=1.0)
                )

                # Parse JSON
                response_text = response_text.strip()
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    response_text = response_text[start:end].strip()
                elif '```' in response_text:
                    start = response_text.find('```') + 3
                    end = response_text.find('```', start)
                    response_text = response_text[start:end].strip()

                coaching_data = json.loads(response_text)

                # Validate
                self._validate_coaching_output(coaching_data)

                # Sanitize output (remove English metric names as safety measure)
                coaching_data = self._sanitize_coaching_output(coaching_data)

                # Add CBIL-specific fields if present
                if 'cbil_insights' in coaching_data:
                    metadata = {
                        'template_used': template_name,
                        'attempt': attempt + 1,
                        'cbil_integrated': True,
                        'cbil_alignment': cbil_alignment
                    }
                else:
                    metadata = {
                        'template_used': template_name,
                        'attempt': attempt + 1
                    }

                feedback = CoachingFeedback(
                    overall_assessment=coaching_data['overall_assessment'],
                    strengths=coaching_data['strengths'],
                    areas_for_growth=coaching_data['areas_for_growth'],
                    priority_actions=coaching_data['priority_actions'],
                    pedagogical_recommendations=coaching_data.get('pedagogical_recommendations'),
                    resources_and_strategies=coaching_data.get('resources_and_strategies'),
                    next_session_goals=coaching_data.get('next_session_goals'),
                    metadata=metadata
                )

                logger.info(f"CBIL-integrated coaching generated successfully on attempt {attempt + 1}")
                return feedback

            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                logger.warning(f"CBIL coaching attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error("All CBIL coaching retry attempts exhausted")
                    raise
                continue

        raise RuntimeError("Failed to generate valid CBIL-integrated coaching")

    def _build_cbil_enhanced_prompt(
        self,
        matrix_data: Dict[str, Any],
        metrics_data: Dict[str, Any],
        pattern_match: Dict[str, Any],
        cbil_scores: Dict[str, Any],
        cbil_alignment: float,
        cbil_templates: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Build prompt with CBIL integration"""

        # Get CBIL template
        cbil_template = cbil_templates['templates']['cbil_comprehensive_coaching']['prompt_template']

        # Format CBIL scores summary
        cbil_scores_summary = ""
        for stage, score_data in cbil_scores.get('stage_scores', {}).items():
            cbil_scores_summary += f"  - {stage}: {score_data['score']}/3점 ({score_data['percentage']:.0f}%)\n"

        # Build CBIL-Matrix correlation summary
        cbil_matrix_correlation = "CBIL 단계와 3D 매트릭스 단계 간 매핑:\n"
        from core.cbil_integration import CBILIntegration
        integrator = CBILIntegration()

        for cbil_stage in integrator.CBIL_STAGES:
            matrix_stage = integrator.CBIL_TO_MATRIX_STAGE[cbil_stage]
            stage_data = cbil_scores.get('stage_scores', {}).get(cbil_stage, {})
            score = stage_data.get('score', 0)
            cbil_matrix_correlation += f"  - {cbil_stage} → {matrix_stage} (점수: {score}/3)\n"

        # Extract statistics
        stats = matrix_data.get('statistics', {})
        stage_stats = stats.get('stage_stats', {})
        context_stats = stats.get('context_stats', {})
        level_stats = stats.get('level_stats', {})

        stage_dist = stage_stats.get('stage_distribution', {})
        context_dist = context_stats.get('context_distribution', {})
        level_dist = level_stats.get('level_distribution', {})

        # Format template
        formatted_prompt = cbil_template.format(
            cbil_scores_summary=cbil_scores_summary,
            cbil_total_score=cbil_scores.get('total_score', 0),
            cbil_max_score=cbil_scores.get('max_total_score', 21),
            cbil_percentage=cbil_scores.get('overall_percentage', 0),

            intro_pct=stage_dist.get('introduction', 0),
            dev_pct=stage_dist.get('development', 0),
            closing_pct=stage_dist.get('closing', 0),

            explanation_pct=context_dist.get('explanation', 0),
            question_pct=context_dist.get('question', 0),
            feedback_pct=context_dist.get('feedback', 0),
            facilitation_pct=context_dist.get('facilitation', 0),
            management_pct=context_dist.get('management', 0),

            l1_pct=level_dist.get('L1', 0),
            l2_pct=level_dist.get('L2', 0),
            l3_pct=level_dist.get('L3', 0),

            pattern_name=pattern_match.get('pattern_name', 'Unknown'),
            pattern_similarity=pattern_match.get('similarity_score', 0),
            cbil_alignment=cbil_alignment,

            cbil_matrix_correlation=cbil_matrix_correlation
        )

        return formatted_prompt


# ============ Demo/Test Code ============

if __name__ == "__main__":
    import asyncio

    print("=" * 60)
    print("Coaching Generator Demo")
    print("=" * 60)

    # Mock data for demonstration
    mock_matrix_data = {
        "statistics": {
            "total_utterances": 100,
            "stage_stats": {
                "stage_distribution": {
                    "introduction": 15,
                    "development": 70,
                    "closing": 15
                },
                "counts_by_stage": {
                    "introduction": 15,
                    "development": 70,
                    "closing": 15
                }
            },
            "context_stats": {
                "context_distribution": {
                    "explanation": 35,
                    "question": 25,
                    "feedback": 20,
                    "facilitation": 15,
                    "management": 5
                }
            },
            "level_stats": {
                "level_distribution": {
                    "L1": 30,
                    "L2": 50,
                    "L3": 20
                },
                "avg_cognitive_level": 1.9
            }
        }
    }

    mock_metrics = {
        "question_ratio": type('obj', (object,), {
            'value': 0.25, 'normalized_score': 85.0, 'status': 'optimal'
        })(),
        "cognitive_diversity": type('obj', (object,), {
            'value': 0.70, 'normalized_score': 75.0, 'status': 'good'
        })()
    }

    mock_pattern_match = {
        "pattern_name": "Inquiry-Based Learning",
        "pattern_description": "Student-led exploration with high-order thinking",
        "similarity_score": 0.78,
        "match_quality": "good"
    }

    mock_context = {
        "subject": "Mathematics",
        "grade_level": "Grade 8",
        "duration": 45
    }

    async def demo():
        generator = CoachingGenerator()
        print("\nCoachingGenerator initialized successfully")
        print(f"System prompt loaded: {len(generator.system_prompt)} characters")
        print(f"Templates loaded: {list(generator.templates.keys())}")

        print("\n" + "-" * 60)
        print("Note: Skipping OpenAI call in demo mode")
        print("-" * 60)

        # In real usage:
        # feedback = await generator.generate_coaching(
        #     matrix_data=mock_matrix_data,
        #     metrics_data=mock_metrics,
        #     pattern_match=mock_pattern_match,
        #     context=mock_context
        # )
        # print("\nCoaching feedback generated:")
        # print(generator.to_markdown(feedback))

        print("\nDemo complete! CoachingGenerator is ready for use.")

    asyncio.run(demo())
