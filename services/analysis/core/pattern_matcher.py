"""
Pattern Matcher - Compares actual teaching patterns with ideal patterns
Uses cosine similarity to match against 4 ideal teaching patterns
"""

import os
import yaml
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PatternMatch:
    """Pattern matching result"""
    pattern_name: str
    pattern_description: str
    similarity_score: float  # 0-1, cosine similarity
    match_quality: str  # "excellent", "good", "partial", "poor"
    stage_similarities: Dict[str, float]
    characteristics: List[str]
    recommendations: List[str]


@dataclass
class PatternVector:
    """75-dimensional pattern vector (3 stages x 5 contexts x 5 levels)"""
    vector: np.ndarray  # shape: (75,)
    metadata: Dict[str, Any]


class PatternMatcher:
    """Teaching pattern matching system"""

    # Dimension configuration
    STAGES = ['introduction', 'development', 'closing']
    CONTEXTS = ['explanation', 'question', 'feedback', 'facilitation', 'management']
    LEVELS = ['L1', 'L2', 'L3']

    def __init__(self, patterns_file: Optional[str] = None):
        """
        Args:
            patterns_file: Path to ideal_patterns.yaml
        """
        if patterns_file is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            patterns_file = os.path.join(
                os.path.dirname(current_dir),
                'patterns',
                'ideal_patterns.yaml'
            )

        self.patterns_file = patterns_file
        self.ideal_patterns = self._load_patterns()
        self.ideal_vectors = self._build_ideal_vectors()
        logger.info(f"Loaded {len(self.ideal_patterns)} ideal patterns")

    def _load_patterns(self) -> Dict[str, Any]:
        """Load ideal patterns from YAML file"""
        try:
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data['patterns']
        except Exception as e:
            logger.error(f"Failed to load patterns: {e}")
            raise

    def _build_ideal_vectors(self) -> Dict[str, PatternVector]:
        """Build 75-dimensional vectors from pattern definitions"""
        vectors = {}
        for pattern_id, pattern_data in self.ideal_patterns.items():
            vector = self._pattern_to_vector(pattern_data)
            vectors[pattern_id] = PatternVector(
                vector=vector,
                metadata={
                    'name': pattern_data['name'],
                    'description': pattern_data['description'],
                    'characteristics': pattern_data['characteristics']
                }
            )
        return vectors

    def _pattern_to_vector(self, pattern_data: Dict[str, Any]) -> np.ndarray:
        """
        Convert pattern definition to 75-dimensional vector

        Vector structure:
        - 3 stages × 5 contexts × 5 levels = 75 dimensions (Note: using 5 levels for flexibility)
        - Actually uses 3 levels (L1, L2, L3), other 2 dimensions are zero

        Args:
            pattern_data: Pattern definition from YAML

        Returns:
            Normalized 75-dimensional vector
        """
        vector = np.zeros(75)

        stage_dist = pattern_data['stage_distribution']
        context_by_stage = pattern_data['context_by_stage']
        level_dist = pattern_data['level_distribution']

        idx = 0
        for stage in self.STAGES:
            stage_weight = stage_dist[stage]

            for context in self.CONTEXTS:
                context_weight = context_by_stage[stage][context]

                for level in self.LEVELS:
                    level_weight = level_dist[level]

                    # Combined probability: stage * context * level
                    vector[idx] = stage_weight * context_weight * level_weight
                    idx += 1

        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    def _matrix_to_vector(self, matrix_data: Dict[str, Any]) -> np.ndarray:
        """
        Convert 3D matrix data to 75-dimensional vector

        Args:
            matrix_data: 3D matrix result from MatrixBuilder

        Returns:
            Normalized 75-dimensional vector
        """
        vector = np.zeros(75)

        counts = matrix_data.get('counts', {})
        total_count = sum(
            sum(
                sum(levels.values())
                for levels in contexts.values()
            )
            for contexts in counts.values()
        )

        if total_count == 0:
            return vector

        idx = 0
        for stage in self.STAGES:
            stage_counts = counts.get(stage, {})

            for context in self.CONTEXTS:
                context_counts = stage_counts.get(context, {})

                for level in self.LEVELS:
                    count = context_counts.get(level, 0)
                    vector[idx] = count / total_count
                    idx += 1

        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors

        Returns:
            Similarity score (0-1), where 1 is identical
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

    def _calculate_stage_similarities(
        self,
        actual_vector: np.ndarray,
        ideal_vector: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate similarity for each stage separately

        Returns:
            Dict with similarity scores for each stage
        """
        stage_similarities = {}

        for stage_idx, stage in enumerate(self.STAGES):
            start_idx = stage_idx * len(self.CONTEXTS) * len(self.LEVELS)
            end_idx = start_idx + len(self.CONTEXTS) * len(self.LEVELS)

            actual_stage = actual_vector[start_idx:end_idx]
            ideal_stage = ideal_vector[start_idx:end_idx]

            similarity = self._cosine_similarity(actual_stage, ideal_stage)
            stage_similarities[stage] = similarity

        return stage_similarities

    def match_pattern(self, matrix_data: Dict[str, Any]) -> PatternMatch:
        """
        Find best matching ideal pattern for given teaching data

        Args:
            matrix_data: 3D matrix result from MatrixBuilder

        Returns:
            PatternMatch with best matching pattern
        """
        # Convert actual data to vector
        actual_vector = self._matrix_to_vector(matrix_data)

        # Calculate similarity with each ideal pattern
        best_match = None
        best_similarity = -1

        for pattern_id, pattern_vector in self.ideal_vectors.items():
            similarity = self._cosine_similarity(actual_vector, pattern_vector.vector)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = (pattern_id, pattern_vector)

        if best_match is None:
            raise ValueError("No patterns available for matching")

        pattern_id, pattern_vector = best_match

        # Calculate stage-wise similarities
        stage_similarities = self._calculate_stage_similarities(
            actual_vector,
            pattern_vector.vector
        )

        # Determine match quality
        if best_similarity >= 0.8:
            match_quality = "excellent"
        elif best_similarity >= 0.7:
            match_quality = "good"
        elif best_similarity >= 0.5:
            match_quality = "partial"
        else:
            match_quality = "poor"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            pattern_id,
            best_similarity,
            stage_similarities,
            matrix_data
        )

        return PatternMatch(
            pattern_name=pattern_vector.metadata['name'],
            pattern_description=pattern_vector.metadata['description'],
            similarity_score=best_similarity,
            match_quality=match_quality,
            stage_similarities=stage_similarities,
            characteristics=pattern_vector.metadata['characteristics'],
            recommendations=recommendations
        )

    def _generate_recommendations(
        self,
        matched_pattern_id: str,
        similarity_score: float,
        stage_similarities: Dict[str, float],
        matrix_data: Dict[str, Any]
    ) -> List[str]:
        """Generate improvement recommendations based on pattern matching"""
        recommendations = []

        # Overall similarity recommendations
        if similarity_score < 0.7:
            recommendations.append(
                "Consider reviewing your teaching strategy - the current pattern "
                "does not strongly align with any ideal pattern."
            )

        # Stage-specific recommendations
        weak_stages = [
            stage for stage, sim in stage_similarities.items()
            if sim < 0.6
        ]

        for stage in weak_stages:
            if stage == 'introduction':
                recommendations.append(
                    "Strengthen the Introduction stage: clearly state learning objectives "
                    "and activate prior knowledge."
                )
            elif stage == 'development':
                recommendations.append(
                    "Improve the Development stage: provide more structured learning activities "
                    "aligned with your teaching pattern."
                )
            elif stage == 'closing':
                recommendations.append(
                    "Enhance the Closing stage: include comprehensive summaries and "
                    "assess student understanding."
                )

        # Pattern-specific recommendations
        if matched_pattern_id == 'inquiry_based' and similarity_score < 0.7:
            recommendations.append(
                "For inquiry-based learning: increase higher-order questions (L2, L3) "
                "and provide more opportunities for student exploration."
            )
        elif matched_pattern_id == 'concept_understanding' and similarity_score < 0.7:
            recommendations.append(
                "For concept understanding: balance explanations with immediate checks "
                "for understanding and provide clear examples."
            )
        elif matched_pattern_id == 'discussion_centered' and similarity_score < 0.7:
            recommendations.append(
                "For discussion-centered learning: increase facilitation activities "
                "and encourage more peer-to-peer interaction."
            )
        elif matched_pattern_id == 'skill_training' and similarity_score < 0.7:
            recommendations.append(
                "For skill training: provide more structured practice opportunities "
                "and clear procedural guidance."
            )

        if not recommendations:
            recommendations.append(
                "Your teaching pattern is well-aligned! Continue maintaining "
                "this effective approach."
            )

        return recommendations

    def get_all_pattern_similarities(
        self,
        matrix_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate similarity scores for all ideal patterns

        Args:
            matrix_data: 3D matrix result from MatrixBuilder

        Returns:
            Dict mapping pattern names to similarity scores
        """
        actual_vector = self._matrix_to_vector(matrix_data)

        similarities = {}
        for pattern_id, pattern_vector in self.ideal_vectors.items():
            similarity = self._cosine_similarity(actual_vector, pattern_vector.vector)
            pattern_name = pattern_vector.metadata['name']
            similarities[pattern_name] = similarity

        return similarities


# ============ Test/Demo Code ============

if __name__ == "__main__":
    # Demo: Pattern matching
    import json

    print("=" * 60)
    print("Pattern Matcher Demo")
    print("=" * 60)

    # Initialize matcher
    matcher = PatternMatcher()
    print(f"\nLoaded {len(matcher.ideal_patterns)} ideal patterns:")
    for pattern_id, data in matcher.ideal_patterns.items():
        print(f"  - {pattern_id}: {data['name']}")

    # Example matrix data (from Module 2 output)
    example_matrix = {
        "counts": {
            "introduction": {
                "explanation": {"L1": 3, "L2": 2, "L3": 0},
                "question": {"L1": 2, "L2": 1, "L3": 0},
                "feedback": {"L1": 1, "L2": 0, "L3": 0},
                "facilitation": {"L1": 1, "L2": 0, "L3": 0},
                "management": {"L1": 1, "L2": 0, "L3": 0}
            },
            "development": {
                "explanation": {"L1": 10, "L2": 15, "L3": 5},
                "question": {"L1": 5, "L2": 12, "L3": 8},
                "feedback": {"L1": 3, "L2": 8, "L3": 4},
                "facilitation": {"L1": 2, "L2": 4, "L3": 2},
                "management": {"L1": 2, "L2": 1, "L3": 0}
            },
            "closing": {
                "explanation": {"L1": 2, "L2": 1, "L3": 0},
                "question": {"L1": 2, "L2": 2, "L3": 1},
                "feedback": {"L1": 2, "L2": 3, "L3": 1},
                "facilitation": {"L1": 1, "L2": 1, "L3": 0},
                "management": {"L1": 1, "L2": 0, "L3": 0}
            }
        }
    }

    # Match pattern
    print("\n" + "-" * 60)
    print("Matching pattern...")
    result = matcher.match_pattern(example_matrix)

    print(f"\nBest Match: {result.pattern_name}")
    print(f"Description: {result.pattern_description}")
    print(f"Similarity Score: {result.similarity_score:.3f}")
    print(f"Match Quality: {result.match_quality}")

    print("\nStage Similarities:")
    for stage, sim in result.stage_similarities.items():
        print(f"  {stage:15s}: {sim:.3f}")

    print("\nCharacteristics:")
    for char in result.characteristics:
        print(f"  - {char}")

    print("\nRecommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")

    # Show all pattern similarities
    print("\n" + "-" * 60)
    print("All Pattern Similarities:")
    all_sims = matcher.get_all_pattern_similarities(example_matrix)
    for pattern_name, sim in sorted(all_sims.items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern_name:30s}: {sim:.3f}")

    print("\n" + "=" * 60)
    print("Pattern Matcher Demo Complete!")
    print("=" * 60)
