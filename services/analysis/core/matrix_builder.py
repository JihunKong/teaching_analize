"""
3D Matrix Builder
시간(Stage) × 맥락(Context) × 수준(Level) 3차원 매트릭스 생성
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np

from core.stage_classifier import StageClassifier
from core.context_tagger import ContextTagger
from core.level_classifier import LevelClassifier
from services.openai_service import OpenAIService
from utils.semantic_cache import SemanticCache

logger = logging.getLogger(__name__)


class MatrixBuilder:
    """3D 매트릭스 빌더"""

    def __init__(
        self,
        stage_classifier: Optional[StageClassifier] = None,
        context_tagger: Optional[ContextTagger] = None,
        level_classifier: Optional[LevelClassifier] = None,
        openai_service: Optional[OpenAIService] = None,
        semantic_cache: Optional[SemanticCache] = None
    ):
        """
        Args:
            stage_classifier: Optional StageClassifier instance
            context_tagger: Optional ContextTagger instance
            level_classifier: Optional LevelClassifier instance
            openai_service: Optional OpenAIService instance
            semantic_cache: Optional SemanticCache for consistency guarantee
        """
        self.openai_service = openai_service or OpenAIService()
        self.semantic_cache = semantic_cache

        # Initialize classifiers with semantic cache for consistency
        self.stage_classifier = stage_classifier or StageClassifier(
            openai_service=self.openai_service,
            semantic_cache=self.semantic_cache
        )
        self.context_tagger = context_tagger or ContextTagger(
            openai_service=self.openai_service,
            semantic_cache=self.semantic_cache
        )
        self.level_classifier = level_classifier or LevelClassifier(
            openai_service=self.openai_service,
            semantic_cache=self.semantic_cache
        )

        logger.info(
            "3D Matrix Builder initialized (caching: %s)",
            "enabled" if semantic_cache else "disabled"
        )

    async def build_3d_matrix(
        self,
        utterances: List[Dict[str, Any]],
        include_raw_data: bool = False
    ) -> Dict[str, Any]:
        """
        발화 리스트로부터 3D 매트릭스 구축

        Args:
            utterances: [{"text": "...", "timestamp": "...", "id": "..."}, ...]
            include_raw_data: 원본 분류 결과 포함 여부

        Returns:
            {
                "matrix": {
                    "dimensions": {
                        "stages": ["introduction", "development", "closing"],
                        "contexts": ["explanation", "question", "feedback", "facilitation", "management"],
                        "levels": ["L1", "L2", "L3"]
                    },
                    "data": [
                        # 각 발화의 3D 좌표
                        {
                            "utterance_id": "utt_001",
                            "stage": "introduction",
                            "contexts": ["explanation"],
                            "level": "L1",
                            "timestamp": "00:05:00"
                        },
                        ...
                    ],
                    "counts": {
                        # Stage × Context × Level 빈도 행렬
                        "introduction": {
                            "explanation": {"L1": 5, "L2": 2, "L3": 0},
                            "question": {"L1": 3, "L2": 1, "L3": 0},
                            ...
                        },
                        ...
                    },
                    "heatmap_data": [
                        # Stage × Context 평면 (Level별로 분리)
                        {
                            "level": "L1",
                            "matrix": [[5, 3, 2, 1, 0], [30, 15, 10, 8, 5], [3, 2, 1, 0, 0]]
                        },
                        ...
                    ]
                },
                "statistics": {
                    "total_utterances": 100,
                    "stage_stats": {...},
                    "context_stats": {...},
                    "level_stats": {...}
                },
                "raw_classifications": {  # include_raw_data=True인 경우에만
                    "stage_results": [...],
                    "context_results": [...],
                    "level_results": [...]
                }
            }
        """
        logger.info(f"Building 3D matrix from {len(utterances)} utterances")

        # 1. 모든 분류기 실행
        logger.info("Step 1/4: Classifying stages...")
        stage_results = await self.stage_classifier.classify_multiple_utterances(utterances)

        logger.info("Step 2/4: Tagging contexts...")
        context_results = await self.context_tagger.tag_multiple_utterances(utterances)

        logger.info("Step 3/4: Classifying cognitive levels...")
        level_results = await self.level_classifier.classify_multiple_utterances(utterances)

        # 2. 3D 데이터 구축
        logger.info("Step 4/4: Building matrix...")
        matrix_data = self._build_matrix_data(
            utterances,
            stage_results,
            context_results,
            level_results
        )

        # 3. 통계 계산
        statistics = self._calculate_statistics(
            stage_results,
            context_results,
            level_results,
            matrix_data
        )

        result = {
            "matrix": matrix_data,
            "statistics": statistics
        }

        if include_raw_data:
            result["raw_classifications"] = {
                "stage_results": stage_results,
                "context_results": context_results,
                "level_results": level_results
            }

        logger.info("3D matrix build complete")
        return result

    def _build_matrix_data(
        self,
        utterances: List[Dict],
        stage_results: List[Dict],
        context_results: List[Dict],
        level_results: List[Dict]
    ) -> Dict[str, Any]:
        """매트릭스 데이터 구조 생성"""

        # 차원 정의
        stages = ["introduction", "development", "closing"]
        contexts = ["explanation", "question", "feedback", "facilitation", "management"]
        levels = ["L1", "L2", "L3"]

        # 각 발화의 3D 좌표
        data_points = []
        for i in range(len(utterances)):
            point = {
                "utterance_id": utterances[i].get("id"),
                "utterance_text": utterances[i]["text"],
                "timestamp": utterances[i].get("timestamp"),
                "stage": stage_results[i]["stage"],
                "contexts": context_results[i]["contexts"],
                "level": level_results[i]["level"]
            }
            data_points.append(point)

        # 빈도 카운트 행렬 초기화
        counts = {}
        for stage in stages:
            counts[stage] = {}
            for context in contexts:
                counts[stage][context] = {level: 0 for level in levels}

        # 빈도 계산
        for point in data_points:
            stage = point["stage"]
            point_contexts = point["contexts"]
            level = point["level"]

            for context in point_contexts:
                counts[stage][context][level] += 1

        # 히트맵 데이터 생성 (Level별로 Stage × Context 행렬)
        heatmap_data = []
        for level in levels:
            matrix = []
            for stage in stages:
                row = []
                for context in contexts:
                    row.append(counts[stage][context][level])
                matrix.append(row)

            heatmap_data.append({
                "level": level,
                "matrix": matrix,
                "total": sum(sum(row) for row in matrix)
            })

        return {
            "dimensions": {
                "stages": stages,
                "contexts": contexts,
                "levels": levels
            },
            "data": data_points,
            "counts": counts,
            "heatmap_data": heatmap_data
        }

    def _calculate_statistics(
        self,
        stage_results: List[Dict],
        context_results: List[Dict],
        level_results: List[Dict],
        matrix_data: Dict
    ) -> Dict[str, Any]:
        """통합 통계 계산"""

        # 각 분류기의 통계
        stage_stats = self.stage_classifier.get_stage_statistics(stage_results)
        context_stats = self.context_tagger.get_context_statistics(context_results)
        level_stats = self.level_classifier.get_level_statistics(level_results)

        # 3D 매트릭스 고유 통계
        total_utterances = len(stage_results)

        # 가장 빈번한 조합 찾기
        combination_counts = {}
        for point in matrix_data["data"]:
            for context in point["contexts"]:
                key = (point["stage"], context, point["level"])
                combination_counts[key] = combination_counts.get(key, 0) + 1

        # Top 10 조합
        top_combinations = sorted(
            combination_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        top_combinations_formatted = [
            {
                "stage": combo[0],
                "context": combo[1],
                "level": combo[2],
                "count": count,
                "percentage": round(count / total_utterances * 100, 1)
            }
            for combo, count in top_combinations
        ]

        # 교육적 복잡도 지표
        edu_complexity = self._calculate_educational_complexity(matrix_data)

        return {
            "total_utterances": total_utterances,
            "stage_stats": stage_stats,
            "context_stats": context_stats,
            "level_stats": level_stats,
            "top_combinations": top_combinations_formatted,
            "educational_complexity": edu_complexity
        }

    def _calculate_educational_complexity(self, matrix_data: Dict) -> Dict[str, Any]:
        """
        교육적 복잡도 지표 계산

        Returns:
            {
                "cognitive_diversity": 0.75,  # 인지 수준 다양성
                "instructional_variety": 0.68,  # 수업 맥락 다양성
                "progression_quality": 0.82,  # 단계 진행 품질
                "overall_complexity": 0.75
            }
        """
        counts = matrix_data["counts"]
        total = len(matrix_data["data"])

        # 인지 수준 다양성 (L2, L3 비율이 높을수록 높음)
        level_dist = {}
        for stage in counts:
            for context in counts[stage]:
                for level, count in counts[stage][context].items():
                    level_dist[level] = level_dist.get(level, 0) + count

        cognitive_diversity = (
            (level_dist.get("L2", 0) * 1.5 + level_dist.get("L3", 0) * 2) / total
        )

        # 수업 맥락 다양성 (5가지 맥락이 골고루 사용되었는지)
        context_dist = {}
        for stage in counts:
            for context in counts[stage]:
                total_count = sum(counts[stage][context].values())
                context_dist[context] = context_dist.get(context, 0) + total_count

        # Shannon entropy로 다양성 측정
        context_probs = [c / total for c in context_dist.values() if c > 0]
        entropy = -sum(p * np.log(p) for p in context_probs)
        max_entropy = np.log(5)  # 5개 맥락
        instructional_variety = entropy / max_entropy if max_entropy > 0 else 0

        # 단계 진행 품질 (도입 → 전개 → 정리 순서로 잘 진행되었는지)
        stage_order = [p["stage"] for p in matrix_data["data"]]
        progression_score = self._assess_stage_progression(stage_order)

        # 전체 복잡도 (0-1)
        overall = (
            cognitive_diversity * 0.4 +
            instructional_variety * 0.3 +
            progression_score * 0.3
        )

        return {
            "cognitive_diversity": round(min(cognitive_diversity, 1.0), 2),
            "instructional_variety": round(instructional_variety, 2),
            "progression_quality": round(progression_score, 2),
            "overall_complexity": round(overall, 2)
        }

    def _assess_stage_progression(self, stage_order: List[str]) -> float:
        """
        수업 단계 진행의 자연스러움 평가

        이상적: intro → dev → closing 순서
        """
        if not stage_order:
            return 0.0

        # 예상 순서
        expected_progression = {
            ("introduction", "introduction"): 1.0,
            ("introduction", "development"): 1.0,  # 자연스러운 전환
            ("introduction", "closing"): 0.3,      # 비정상적
            ("development", "development"): 1.0,
            ("development", "closing"): 1.0,       # 자연스러운 전환
            ("development", "introduction"): 0.5,  # 복습 등으로 가능
            ("closing", "closing"): 1.0,
            ("closing", "introduction"): 0.2,      # 비정상적
            ("closing", "development"): 0.3,       # 비정상적
        }

        scores = []
        for i in range(len(stage_order) - 1):
            current = stage_order[i]
            next_stage = stage_order[i + 1]
            score = expected_progression.get((current, next_stage), 0.5)
            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.5

    def export_to_numpy(self, matrix_data: Dict) -> np.ndarray:
        """
        3D 매트릭스를 NumPy 배열로 변환

        Returns:
            shape (3, 5, 3) array [stages × contexts × levels]
        """
        counts = matrix_data["counts"]
        stages = matrix_data["dimensions"]["stages"]
        contexts = matrix_data["dimensions"]["contexts"]
        levels = matrix_data["dimensions"]["levels"]

        arr = np.zeros((len(stages), len(contexts), len(levels)))

        for i, stage in enumerate(stages):
            for j, context in enumerate(contexts):
                for k, level in enumerate(levels):
                    arr[i, j, k] = counts[stage][context][level]

        return arr


async def test_matrix_builder():
    """테스트"""
    builder = MatrixBuilder()

    test_utterances = [
        {"id": "utt_001", "text": "오늘은 피타고라스 정리를 배워볼게요", "timestamp": "00:00:30"},
        {"id": "utt_002", "text": "피타고라스 정리는 a²+b²=c²입니다", "timestamp": "00:05:00"},
        {"id": "utt_003", "text": "이 공식을 사용해서 문제를 풀어보세요", "timestamp": "00:15:00"},
        {"id": "utt_004", "text": "오늘 배운 내용을 정리하면 a²+b²=c²였습니다", "timestamp": "00:40:00"}
    ]

    result = await builder.build_3d_matrix(test_utterances, include_raw_data=True)

    print("Matrix Dimensions:", result["matrix"]["dimensions"])
    print("\nMatrix Data Points:")
    for point in result["matrix"]["data"]:
        print(f"  {point['utterance_id']}: {point['stage']} × {point['contexts']} × {point['level']}")

    print("\nTop Combinations:")
    for combo in result["statistics"]["top_combinations"][:5]:
        print(f"  {combo['stage']} × {combo['context']} × {combo['level']}: {combo['count']} ({combo['percentage']}%)")

    print("\nEducational Complexity:", result["statistics"]["educational_complexity"])


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_matrix_builder())
