"""
Evaluation Service - Orchestrates comprehensive teaching evaluation
Integrates 3D Matrix, Metrics, Pattern Matching, and Coaching Generation
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from core.matrix_builder import MatrixBuilder
from core.metrics_calculator import MetricsCalculator
from core.pattern_matcher import PatternMatcher
from core.coaching_generator import CoachingGenerator
from utils.semantic_cache import SemanticCache

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Comprehensive evaluation result"""
    evaluation_id: str
    evaluation_type: str
    created_at: str

    # Core analysis results
    matrix_analysis: Dict[str, Any]
    quantitative_metrics: Dict[str, Any]
    pattern_matching: Dict[str, Any]
    coaching_feedback: Dict[str, Any]

    # Metadata
    input_metadata: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None


class EvaluationService:
    """Comprehensive teaching evaluation orchestrator"""

    def __init__(
        self,
        matrix_builder: Optional[MatrixBuilder] = None,
        metrics_calculator: Optional[MetricsCalculator] = None,
        pattern_matcher: Optional[PatternMatcher] = None,
        coaching_generator: Optional[CoachingGenerator] = None,
        semantic_cache: Optional[SemanticCache] = None
    ):
        """
        Args:
            matrix_builder: MatrixBuilder instance
            metrics_calculator: MetricsCalculator instance
            pattern_matcher: PatternMatcher instance
            coaching_generator: CoachingGenerator instance
            semantic_cache: SemanticCache for consistency guarantee
        """
        self.semantic_cache = semantic_cache
        self.matrix_builder = matrix_builder or MatrixBuilder(semantic_cache=self.semantic_cache)
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        self.pattern_matcher = pattern_matcher or PatternMatcher()
        self.coaching_generator = coaching_generator or CoachingGenerator()

        logger.info(
            "EvaluationService initialized with all components (caching: %s)",
            "enabled" if semantic_cache else "disabled"
        )

    async def evaluate_teaching(
        self,
        utterances: List[Dict[str, Any]],
        evaluation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        include_raw_data: bool = False
    ) -> EvaluationResult:
        """
        Perform comprehensive teaching evaluation

        Workflow:
        1. Build 3D Matrix (Stage × Context × Level)
        2. Calculate Quantitative Metrics (15 metrics)
        3. Match Teaching Pattern (cosine similarity)
        4. Generate Coaching Feedback (OpenAI GPT-4)

        Args:
            utterances: List of teacher utterances
            evaluation_id: Optional custom evaluation ID
            context: Additional context (subject, grade_level, duration)
            include_raw_data: Include raw classification data

        Returns:
            EvaluationResult with all analysis components
        """
        start_time = datetime.now()
        evaluation_id = evaluation_id or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        context = context or {}

        logger.info(f"Starting evaluation {evaluation_id} with {len(utterances)} utterances")

        # Step 1: Build 3D Matrix
        logger.info("Step 1/4: Building 3D matrix...")
        matrix_result = await self.matrix_builder.build_3d_matrix(
            utterances=utterances,
            include_raw_data=include_raw_data
        )
        matrix_data = matrix_result.get('matrix', {})
        logger.info("3D matrix completed")

        # Step 2: Calculate Quantitative Metrics
        logger.info("Step 2/4: Calculating quantitative metrics...")
        all_metrics = self.metrics_calculator.calculate_all_metrics(
            matrix_data=matrix_data,
            utterances=utterances
        )

        # Convert metrics to serializable format
        metrics_dict = {
            name: {
                'value': metric.value,
                'normalized_score': metric.normalized_score,
                'optimal_range': metric.optimal_range,
                'status': metric.status,
                'description': metric.description
            }
            for name, metric in all_metrics.items()
        }
        logger.info(f"Calculated {len(all_metrics)} metrics")

        # Step 3: Match Teaching Pattern
        logger.info("Step 3/4: Matching teaching pattern...")
        pattern_match = self.pattern_matcher.match_pattern(matrix_data)

        # Get all pattern similarities for comparison
        all_pattern_similarities = self.pattern_matcher.get_all_pattern_similarities(matrix_data)

        pattern_dict = {
            'best_match': {
                'pattern_name': pattern_match.pattern_name,
                'pattern_description': pattern_match.pattern_description,
                'similarity_score': pattern_match.similarity_score,
                'match_quality': pattern_match.match_quality,
                'stage_similarities': pattern_match.stage_similarities,
                'characteristics': pattern_match.characteristics,
                'recommendations': pattern_match.recommendations
            },
            'all_pattern_similarities': all_pattern_similarities
        }
        logger.info(f"Best match: {pattern_match.pattern_name} ({pattern_match.similarity_score:.3f})")

        # Step 4: Generate Coaching Feedback
        logger.info("Step 4/4: Generating coaching feedback...")
        coaching_feedback = await self.coaching_generator.generate_coaching(
            matrix_data=matrix_result,
            metrics_data=all_metrics,
            pattern_match=pattern_dict['best_match'],
            context=context
        )

        coaching_dict = self.coaching_generator.to_dict(coaching_feedback)
        logger.info("Coaching feedback generated")

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Build final result
        result = EvaluationResult(
            evaluation_id=evaluation_id,
            evaluation_type="comprehensive_teaching_evaluation",
            created_at=datetime.now().isoformat(),
            matrix_analysis=matrix_result,
            quantitative_metrics=metrics_dict,
            pattern_matching=pattern_dict,
            coaching_feedback=coaching_dict,
            input_metadata={
                'total_utterances': len(utterances),
                'context': context
            },
            processing_time=processing_time
        )

        logger.info(f"Evaluation {evaluation_id} completed in {processing_time:.2f}s")
        return result

    def to_dict(self, result: EvaluationResult) -> Dict[str, Any]:
        """Convert EvaluationResult to dictionary"""
        return asdict(result)

    def to_json(self, result: EvaluationResult) -> str:
        """Convert EvaluationResult to JSON string"""
        import json
        return json.dumps(asdict(result), indent=2, ensure_ascii=False)

    def get_summary(self, result: EvaluationResult) -> Dict[str, Any]:
        """
        Get concise summary of evaluation

        Returns:
            Dictionary with key highlights
        """
        metrics = result.quantitative_metrics
        pattern = result.pattern_matching['best_match']
        coaching = result.coaching_feedback

        # Top performing metrics
        top_metrics = sorted(
            [(name, data['normalized_score']) for name, data in metrics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Low performing metrics
        low_metrics = sorted(
            [(name, data['normalized_score']) for name, data in metrics.items()],
            key=lambda x: x[1]
        )[:3]

        summary = {
            'evaluation_id': result.evaluation_id,
            'created_at': result.created_at,
            'total_utterances': result.input_metadata['total_utterances'],
            'processing_time': f"{result.processing_time:.2f}s",

            'pattern_match': {
                'name': pattern['pattern_name'],
                'similarity': f"{pattern['similarity_score']:.1%}",
                'quality': pattern['match_quality']
            },

            'top_performing_metrics': [
                {'name': name, 'score': f"{score:.1f}/100"}
                for name, score in top_metrics
            ],

            'areas_needing_attention': [
                {'name': name, 'score': f"{score:.1f}/100"}
                for name, score in low_metrics
            ],

            'key_strengths': coaching['strengths'][:3],
            'priority_actions': coaching['priority_actions'][:3],

            'overall_assessment': coaching['overall_assessment']
        }

        return summary

    async def evaluate_with_cbil(
        self,
        utterances: List[Dict[str, Any]],
        cbil_analysis_text: str,
        evaluation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        include_raw_data: bool = False
    ):
        """
        Perform comprehensive evaluation with CBIL integration

        Workflow:
        1. Parse CBIL analysis text
        2. Run standard Module 3 evaluation
        3. Integrate CBIL with Module 3 results
        4. Generate unified coaching

        Args:
            utterances: List of teacher utterances
            cbil_analysis_text: CBIL 7-stage analysis text from Solar API
            evaluation_id: Optional custom evaluation ID
            context: Additional context
            include_raw_data: Include raw classification data

        Returns:
            Enhanced EvaluationResult with CBIL integration
        """
        from core.cbil_integration import CBILIntegration

        start_time = datetime.now()
        evaluation_id = evaluation_id or f"cbil_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        context = context or {}

        logger.info(f"Starting CBIL-integrated evaluation {evaluation_id}")

        # Step 1: Parse CBIL analysis
        logger.info("Step 1/5: Parsing CBIL analysis...")
        cbil_integrator = CBILIntegration()
        cbil_result = cbil_integrator.parse_cbil_analysis(cbil_analysis_text)
        logger.info(f"CBIL total score: {cbil_result.total_score}/{cbil_result.max_total_score}")

        # Step 2-4: Standard Module 3 evaluation
        logger.info("Step 2-4/5: Running Module 3 evaluation...")
        base_result = await self.evaluate_teaching(
            utterances=utterances,
            evaluation_id=evaluation_id,
            context=context,
            include_raw_data=include_raw_data
        )

        # Step 5: Integrate CBIL with Module 3
        logger.info("Step 5/5: Integrating CBIL with Module 3...")

        # Map CBIL to matrix
        cbil_matrix_mapping = cbil_integrator.map_cbil_to_3d_matrix(
            cbil_result,
            base_result.matrix_analysis
        )

        # Calculate alignment
        cbil_alignment = cbil_integrator.calculate_cbil_alignment_score(
            cbil_result,
            base_result.pattern_matching['best_match']
        )

        # Generate CBIL-specific coaching
        cbil_coaching = cbil_integrator.generate_cbil_specific_coaching(
            cbil_result,
            cbil_matrix_mapping
        )

        # Enhance coaching feedback with CBIL insights
        enhanced_coaching = dict(base_result.coaching_feedback)
        if 'cbil_insights' not in enhanced_coaching:
            enhanced_coaching['cbil_insights'] = {}

        enhanced_coaching['cbil_insights'] = {
            'cbil_scores': cbil_integrator.to_dict(cbil_result),
            'cbil_matrix_mapping': cbil_matrix_mapping,
            'cbil_alignment_score': cbil_alignment,
            'cbil_specific_recommendations': cbil_coaching
        }

        # Update pattern matching with CBIL alignment
        enhanced_pattern_matching = dict(base_result.pattern_matching)
        enhanced_pattern_matching['cbil_alignment'] = cbil_alignment

        # Create enhanced result
        processing_time = (datetime.now() - start_time).total_seconds()

        enhanced_result = EvaluationResult(
            evaluation_id=evaluation_id,
            evaluation_type="cbil_comprehensive_evaluation",
            created_at=datetime.now().isoformat(),
            matrix_analysis=base_result.matrix_analysis,
            quantitative_metrics=base_result.quantitative_metrics,
            pattern_matching=enhanced_pattern_matching,
            coaching_feedback=enhanced_coaching,
            input_metadata={
                'total_utterances': len(utterances),
                'cbil_total_score': cbil_result.total_score,
                'cbil_max_score': cbil_result.max_total_score,
                'cbil_percentage': cbil_result.overall_percentage,
                'context': context
            },
            processing_time=processing_time
        )

        logger.info(f"CBIL-integrated evaluation {evaluation_id} completed in {processing_time:.2f}s")
        logger.info(f"CBIL-Module3 alignment: {cbil_alignment:.3f}")

        return enhanced_result


# ============ Demo/Test Code ============

if __name__ == "__main__":
    import asyncio

    print("=" * 60)
    print("Evaluation Service Demo")
    print("=" * 60)

    # Mock utterances
    mock_utterances = [
        {"id": "utt_001", "text": "Today we'll learn about the Pythagorean theorem", "timestamp": "00:00:30"},
        {"id": "utt_002", "text": "Can anyone tell me what a right triangle is?", "timestamp": "00:01:00"},
        {"id": "utt_003", "text": "Excellent! A right triangle has one 90-degree angle", "timestamp": "00:01:30"},
        {"id": "utt_004", "text": "Now, let's look at the relationship between the sides", "timestamp": "00:02:00"},
        {"id": "utt_005", "text": "The theorem states that a² + b² = c²", "timestamp": "00:03:00"},
    ]

    mock_context = {
        "subject": "Mathematics",
        "grade_level": "Grade 8",
        "duration": 45
    }

    async def demo():
        service = EvaluationService()
        print("\nEvaluationService initialized with all components:")
        print("  ✓ MatrixBuilder")
        print("  ✓ MetricsCalculator")
        print("  ✓ PatternMatcher")
        print("  ✓ CoachingGenerator")

        print("\n" + "-" * 60)
        print("Note: Skipping full evaluation in demo mode")
        print("(Full evaluation requires OpenAI API key)")
        print("-" * 60)

        # In real usage:
        # result = await service.evaluate_teaching(
        #     utterances=mock_utterances,
        #     context=mock_context
        # )
        # summary = service.get_summary(result)
        # print("\nEvaluation Summary:")
        # print(json.dumps(summary, indent=2, ensure_ascii=False))

        print("\nDemo complete! EvaluationService is ready for use.")
        print("\nWorkflow:")
        print("  1. Build 3D Matrix (Stage × Context × Level)")
        print("  2. Calculate 15 Quantitative Metrics")
        print("  3. Match Teaching Pattern (4 ideal patterns)")
        print("  4. Generate Coaching Feedback (OpenAI GPT-4)")

    asyncio.run(demo())

