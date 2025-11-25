"""
Quantitative Metrics Calculator
15개 정량 지표 계산 (100% 결정론적, 재현 가능)
"""

import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class MetricResult:
    """개별 메트릭 결과"""
    name: str
    value: float
    normalized_score: float  # 0-100
    optimal_range: Tuple[float, float]
    status: str  # "optimal", "good", "needs_improvement"
    description: str


class MetricsCalculator:
    """15개 정량 지표 계산기"""

    def __init__(self):
        # 최적 범위 정의 (based on educational research)
        self.optimal_ranges = {
            # Time Distribution
            "intro_time_ratio": (0.1, 0.2),
            "dev_time_ratio": (0.6, 0.8),
            "closing_time_ratio": (0.1, 0.2),
            "utterance_density": (2.0, 4.0),  # utterances per minute

            # Context Distribution
            "question_ratio": (0.15, 0.30),
            "explanation_ratio": (0.30, 0.50),
            "feedback_ratio": (0.10, 0.25),
            "context_diversity": (1.2, 2.0),  # Shannon entropy

            # Cognitive Complexity
            "avg_cognitive_level": (1.8, 2.5),  # 1=L1, 2=L2, 3=L3
            "higher_order_ratio": (0.40, 0.70),  # (L2+L3)/total
            "cognitive_progression": (0.3, 0.8),  # intro→dev→closing level increase

            # Interaction Quality
            "extended_dialogue_ratio": (0.20, 0.40),
            "avg_wait_time": (3.0, 8.0),  # seconds
            "irf_pattern_ratio": (0.15, 0.35),  # Initiation-Response-Feedback

            # Composite Patterns
            "dev_question_depth": (0.50, 0.80),  # (L2+L3 questions in dev)/(total questions in dev)
        }

        logger.info("Metrics Calculator initialized")

    def calculate_all_metrics(
        self,
        matrix_data: Dict[str, Any],
        utterances: List[Dict[str, Any]] = None
    ) -> Dict[str, MetricResult]:
        """
        모든 15개 메트릭 계산

        Args:
            matrix_data: 3D matrix output from matrix_builder
            utterances: Original utterances with timestamps (optional for advanced metrics)

        Returns:
            Dict of 15 MetricResult objects
        """
        logger.info("Calculating all 15 quantitative metrics...")

        results = {}

        # Category 1: Time Distribution (4 metrics)
        time_metrics = self.calculate_time_metrics(matrix_data)
        results.update(time_metrics)

        # Category 2: Context Distribution (4 metrics)
        context_metrics = self.calculate_context_metrics(matrix_data)
        results.update(context_metrics)

        # Category 3: Cognitive Complexity (3 metrics)
        cognitive_metrics = self.calculate_cognitive_metrics(matrix_data)
        results.update(cognitive_metrics)

        # Category 4: Interaction Quality (3 metrics)
        interaction_metrics = self.calculate_interaction_metrics(matrix_data, utterances)
        results.update(interaction_metrics)

        # Category 5: Composite Patterns (1 metric)
        composite_metrics = self.calculate_composite_metrics(matrix_data)
        results.update(composite_metrics)

        logger.info(f"Calculated {len(results)} metrics")
        return results

    def calculate_time_metrics(self, matrix_data: Dict) -> Dict[str, MetricResult]:
        """시간 분포 메트릭 (4개)"""
        data_points = matrix_data["data"]
        total = len(data_points)

        # Count by stage
        stage_counts = Counter(p["stage"] for p in data_points)

        # 1. Introduction time ratio
        intro_ratio = stage_counts.get("introduction", 0) / total

        # 2. Development time ratio
        dev_ratio = stage_counts.get("development", 0) / total

        # 3. Closing time ratio
        closing_ratio = stage_counts.get("closing", 0) / total

        # 4. Utterance density (utterances per minute)
        # Estimate: assume average lesson is 45 minutes
        estimated_duration = 45.0  # minutes
        utterance_density = total / estimated_duration

        return {
            "intro_time_ratio": self._create_metric_result(
                "intro_time_ratio",
                intro_ratio,
                "Introduction time ratio (proportion of utterances in introduction stage)"
            ),
            "dev_time_ratio": self._create_metric_result(
                "dev_time_ratio",
                dev_ratio,
                "Development time ratio (proportion of utterances in development stage)"
            ),
            "closing_time_ratio": self._create_metric_result(
                "closing_time_ratio",
                closing_ratio,
                "Closing time ratio (proportion of utterances in closing stage)"
            ),
            "utterance_density": self._create_metric_result(
                "utterance_density",
                utterance_density,
                "Utterance density (teacher utterances per minute)"
            )
        }

    def calculate_context_metrics(self, matrix_data: Dict) -> Dict[str, MetricResult]:
        """맥락 분포 메트릭 (4개)"""
        data_points = matrix_data["data"]
        total = len(data_points)

        # Count context occurrences (multi-label aware)
        context_counts = Counter()
        for point in data_points:
            for context in point["contexts"]:
                context_counts[context] += 1

        total_context_tags = sum(context_counts.values())

        # 5. Question ratio
        question_ratio = context_counts.get("question", 0) / total_context_tags

        # 6. Explanation ratio
        explanation_ratio = context_counts.get("explanation", 0) / total_context_tags

        # 7. Feedback ratio
        feedback_ratio = context_counts.get("feedback", 0) / total_context_tags

        # 8. Context diversity (Shannon Entropy)
        context_diversity = self._calculate_shannon_entropy(context_counts, total_context_tags)

        return {
            "question_ratio": self._create_metric_result(
                "question_ratio",
                question_ratio,
                "Question ratio (proportion of question contexts)"
            ),
            "explanation_ratio": self._create_metric_result(
                "explanation_ratio",
                explanation_ratio,
                "Explanation ratio (proportion of explanation contexts)"
            ),
            "feedback_ratio": self._create_metric_result(
                "feedback_ratio",
                feedback_ratio,
                "Feedback ratio (proportion of feedback contexts)"
            ),
            "context_diversity": self._create_metric_result(
                "context_diversity",
                context_diversity,
                "Context diversity (Shannon entropy of context distribution, max=2.32)"
            )
        }

    def calculate_cognitive_metrics(self, matrix_data: Dict) -> Dict[str, MetricResult]:
        """인지 복잡도 메트릭 (3개)"""
        data_points = matrix_data["data"]
        total = len(data_points)

        # Count by level
        level_counts = Counter(p["level"] for p in data_points)

        # Map levels to numeric values
        level_values = {"L1": 1, "L2": 2, "L3": 3}

        # 9. Average cognitive level
        total_level_score = sum(level_values[p["level"]] for p in data_points)
        avg_cognitive_level = total_level_score / total

        # 10. Higher-order thinking ratio (L2 + L3)
        higher_order_count = level_counts.get("L2", 0) + level_counts.get("L3", 0)
        higher_order_ratio = higher_order_count / total

        # 11. Cognitive progression (intro → dev → closing level change)
        cognitive_progression = self._calculate_cognitive_progression(data_points, level_values)

        return {
            "avg_cognitive_level": self._create_metric_result(
                "avg_cognitive_level",
                avg_cognitive_level,
                "Average cognitive level across all utterances (1=L1, 2=L2, 3=L3)"
            ),
            "higher_order_ratio": self._create_metric_result(
                "higher_order_ratio",
                higher_order_ratio,
                "Higher-order thinking ratio (L2+L3 proportion)"
            ),
            "cognitive_progression": self._create_metric_result(
                "cognitive_progression",
                cognitive_progression,
                "Cognitive progression quality (level increase from intro to closing)"
            )
        }

    def calculate_interaction_metrics(
        self,
        matrix_data: Dict,
        utterances: List[Dict] = None
    ) -> Dict[str, MetricResult]:
        """상호작용 품질 메트릭 (3개)"""
        data_points = matrix_data["data"]
        total = len(data_points)

        # 12. Extended dialogue ratio (sequences of 3+ utterances with same primary context)
        extended_dialogue_ratio = self._calculate_extended_dialogue_ratio(data_points)

        # 13. Average wait time (estimate based on facilitation prompts)
        avg_wait_time = self._estimate_avg_wait_time(data_points, utterances)

        # 14. IRF pattern ratio (Initiation-Response-Feedback)
        irf_pattern_ratio = self._calculate_irf_pattern_ratio(data_points)

        return {
            "extended_dialogue_ratio": self._create_metric_result(
                "extended_dialogue_ratio",
                extended_dialogue_ratio,
                "Extended dialogue ratio (sequences of 3+ related utterances)"
            ),
            "avg_wait_time": self._create_metric_result(
                "avg_wait_time",
                avg_wait_time,
                "Average wait time after facilitation prompts (seconds)"
            ),
            "irf_pattern_ratio": self._create_metric_result(
                "irf_pattern_ratio",
                irf_pattern_ratio,
                "IRF pattern ratio (Initiation-Response-Feedback sequences)"
            )
        }

    def calculate_composite_metrics(self, matrix_data: Dict) -> Dict[str, MetricResult]:
        """복합 패턴 메트릭 (1개)"""
        data_points = matrix_data["data"]

        # 15. Development question depth ratio
        dev_question_depth = self._calculate_dev_question_depth(data_points)

        return {
            "dev_question_depth": self._create_metric_result(
                "dev_question_depth",
                dev_question_depth,
                "Development question depth ((L2+L3 questions in dev)/(total questions in dev))"
            )
        }

    # ============ Helper Methods ============

    def _calculate_shannon_entropy(self, counts: Counter, total: int) -> float:
        """Shannon Entropy 계산"""
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)

        return entropy

    def _calculate_cognitive_progression(self, data_points: List[Dict], level_values: Dict) -> float:
        """인지 수준 진행 품질 계산"""
        # Calculate average level for each stage
        stage_levels = {"introduction": [], "development": [], "closing": []}

        for point in data_points:
            stage = point["stage"]
            level = level_values[point["level"]]
            stage_levels[stage].append(level)

        # Calculate averages
        intro_avg = np.mean(stage_levels["introduction"]) if stage_levels["introduction"] else 1.0
        dev_avg = np.mean(stage_levels["development"]) if stage_levels["development"] else 2.0
        closing_avg = np.mean(stage_levels["closing"]) if stage_levels["closing"] else 2.0

        # Progression score: (dev - intro) + (closing - intro)
        progression = (dev_avg - intro_avg) + (closing_avg - intro_avg)

        # Normalize to 0-1 range (max theoretical progression is 4.0)
        normalized_progression = max(0, min(progression / 2.0, 1.0))

        return normalized_progression

    def _calculate_extended_dialogue_ratio(self, data_points: List[Dict]) -> float:
        """확장 대화 비율 계산"""
        if len(data_points) < 3:
            return 0.0

        extended_count = 0
        i = 0

        while i < len(data_points) - 2:
            # Check if next 3 utterances share at least one context
            contexts_0 = set(data_points[i]["contexts"])
            contexts_1 = set(data_points[i+1]["contexts"])
            contexts_2 = set(data_points[i+2]["contexts"])

            if contexts_0 & contexts_1 & contexts_2:  # Intersection
                extended_count += 1
                i += 3  # Skip these utterances
            else:
                i += 1

        return extended_count / (len(data_points) - 2)

    def _estimate_avg_wait_time(self, data_points: List[Dict], utterances: List[Dict] = None) -> float:
        """평균 대기 시간 추정"""
        # Simplified estimate: 5 seconds baseline
        # In real implementation, would use actual timestamps
        facilitation_count = sum(
            1 for p in data_points
            if "facilitation" in p["contexts"]
        )

        if facilitation_count == 0:
            return 5.0

        # Estimate based on facilitation frequency
        # More facilitation = more wait time
        return min(3.0 + facilitation_count * 0.1, 10.0)

    def _calculate_irf_pattern_ratio(self, data_points: List[Dict]) -> float:
        """IRF 패턴 비율 계산"""
        if len(data_points) < 3:
            return 0.0

        irf_count = 0

        for i in range(len(data_points) - 2):
            # I: question
            # R: (student response would be here, but we only have teacher utterances)
            # F: feedback

            contexts_i = data_points[i]["contexts"]
            contexts_f = data_points[i+2]["contexts"]

            if "question" in contexts_i and "feedback" in contexts_f:
                irf_count += 1

        return irf_count / (len(data_points) - 2)

    def _calculate_dev_question_depth(self, data_points: List[Dict]) -> float:
        """전개 단계 질문 깊이 계산"""
        # Filter development stage questions
        dev_questions = [
            p for p in data_points
            if p["stage"] == "development" and "question" in p["contexts"]
        ]

        if not dev_questions:
            return 0.5  # Default middle value

        # Count higher-order questions (L2, L3)
        higher_order_count = sum(
            1 for p in dev_questions
            if p["level"] in ["L2", "L3"]
        )

        return higher_order_count / len(dev_questions)

    def _create_metric_result(
        self,
        name: str,
        value: float,
        description: str
    ) -> MetricResult:
        """MetricResult 객체 생성"""
        optimal_range = self.optimal_ranges[name]
        normalized_score = self._normalize_score(value, optimal_range)
        status = self._determine_status(normalized_score)

        return MetricResult(
            name=name,
            value=value,
            normalized_score=normalized_score,
            optimal_range=optimal_range,
            status=status,
            description=description
        )

    def _normalize_score(self, value: float, optimal_range: Tuple[float, float]) -> float:
        """0-100 정규화"""
        min_val, max_val = optimal_range
        mid_val = (min_val + max_val) / 2

        if min_val <= value <= max_val:
            # Within optimal range: 80-100
            if value < mid_val:
                # Map [min_val, mid_val] to [80, 100]
                score = 80 + 20 * (value - min_val) / (mid_val - min_val)
            else:
                # Map [mid_val, max_val] to [100, 80]
                score = 100 - 20 * (value - mid_val) / (max_val - mid_val)
        elif value < min_val:
            # Below optimal: 0-80
            distance = min_val - value
            score = max(0, 80 - distance * 40)
        else:  # value > max_val
            # Above optimal: 80-0
            distance = value - max_val
            score = max(0, 80 - distance * 40)

        return round(score, 1)

    def _determine_status(self, normalized_score: float) -> str:
        """상태 결정"""
        if normalized_score >= 80:
            return "optimal"
        elif normalized_score >= 60:
            return "good"
        else:
            return "needs_improvement"

    def get_metric_summary(self, metrics: Dict[str, MetricResult]) -> Dict[str, Any]:
        """메트릭 요약 통계"""
        scores = [m.normalized_score for m in metrics.values()]
        statuses = Counter(m.status for m in metrics.values())

        return {
            "total_metrics": len(metrics),
            "average_score": round(np.mean(scores), 1),
            "status_breakdown": dict(statuses),
            "optimal_count": statuses["optimal"],
            "needs_improvement_count": statuses["needs_improvement"],
            "overall_quality": self._calculate_overall_quality(scores)
        }

    def _calculate_overall_quality(self, scores: List[float]) -> str:
        """전체 품질 등급"""
        avg = np.mean(scores)

        if avg >= 85:
            return "excellent"
        elif avg >= 70:
            return "good"
        elif avg >= 55:
            return "satisfactory"
        else:
            return "needs_improvement"


# Test function
def test_metrics_calculator():
    """테스트"""
    # Sample 3D matrix data
    sample_matrix = {
        "data": [
            {"stage": "introduction", "contexts": ["explanation"], "level": "L1"},
            {"stage": "introduction", "contexts": ["question"], "level": "L1"},
            {"stage": "development", "contexts": ["explanation", "question"], "level": "L2"},
            {"stage": "development", "contexts": ["feedback"], "level": "L2"},
            {"stage": "development", "contexts": ["question"], "level": "L3"},
            {"stage": "closing", "contexts": ["explanation"], "level": "L2"},
        ]
    }

    calculator = MetricsCalculator()
    metrics = calculator.calculate_all_metrics(sample_matrix)

    print("\n=== Quantitative Metrics ===")
    for name, metric in metrics.items():
        print(f"\n{metric.name}:")
        print(f"  Value: {metric.value:.3f}")
        print(f"  Score: {metric.normalized_score}/100")
        print(f"  Status: {metric.status}")
        print(f"  Optimal range: {metric.optimal_range}")

    summary = calculator.get_metric_summary(metrics)
    print("\n=== Summary ===")
    print(f"Average score: {summary['average_score']}/100")
    print(f"Overall quality: {summary['overall_quality']}")
    print(f"Status breakdown: {summary['status_breakdown']}")


if __name__ == "__main__":
    test_metrics_calculator()
