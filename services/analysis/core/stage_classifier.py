"""
Stage Classifier
수업 단계 분류: 도입(Introduction) / 전개(Development) / 정리(Closing)
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from services.openai_service import OpenAIService
from utils.semantic_cache import SemanticCache

logger = logging.getLogger(__name__)


class StageClassifier:
    """수업 단계 분류기"""

    def __init__(
        self,
        checklist_path: Optional[str] = None,
        openai_service: Optional[OpenAIService] = None,
        semantic_cache: Optional[SemanticCache] = None
    ):
        """
        Args:
            checklist_path: 체크리스트 YAML 파일 경로
            openai_service: OpenAI 서비스 인스턴스
            semantic_cache: Semantic cache 인스턴스 (일관성 보장용)
        """
        # 체크리스트 로드
        if checklist_path is None:
            current_dir = Path(__file__).parent.parent
            checklist_path = current_dir / "checklists" / "stage_checklists.yaml"

        with open(checklist_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.stages = self.config["stages"]
        self.rules = self.config["classification_rules"]
        self.prompt_template = self.config["prompt_template"]

        # OpenAI 서비스
        self.openai_service = openai_service or OpenAIService()

        # Semantic cache (일관성 보장)
        self.semantic_cache = semantic_cache

        logger.info("Stage Classifier initialized (caching: %s)", "enabled" if semantic_cache else "disabled")

    def _build_checklist_items(self, stage_name: str) -> str:
        """
        체크리스트 항목을 프롬프트용 텍스트로 변환

        Args:
            stage_name: "introduction", "development", "closing"

        Returns:
            formatted checklist string
        """
        stage = self.stages[stage_name]
        checklist = stage["checklist"]

        items = []
        for idx, item in enumerate(checklist, 1):
            item_id = item["id"]
            question = item["question"]
            items.append(f"{idx}. {item_id}: {question}")

        return "\n".join(items)

    def _build_prompt(
        self,
        utterance: str,
        stage_name: str,
        timestamp: Optional[str] = None,
        previous_utterance: Optional[str] = None,
        next_utterance: Optional[str] = None
    ) -> str:
        """
        체크리스트 실행을 위한 프롬프트 생성

        Args:
            utterance: 분류할 발화
            stage_name: 체크할 단계
            timestamp: 발화 시간
            previous_utterance: 이전 발화
            next_utterance: 다음 발화

        Returns:
            프롬프트 문자열
        """
        stage = self.stages[stage_name]
        stage_display_name = stage["name"]
        checklist_items = self._build_checklist_items(stage_name)

        prompt = self.prompt_template.format(
            utterance=utterance,
            timestamp=timestamp or "N/A",
            previous_utterance=previous_utterance or "N/A",
            next_utterance=next_utterance or "N/A",
            stage_name=stage_display_name,
            checklist_items=checklist_items
        )

        return prompt

    def _get_expected_keys(self, stage_name: str) -> List[str]:
        """해당 단계의 체크리스트 키 목록 반환"""
        stage = self.stages[stage_name]
        return [item["id"] for item in stage["checklist"]]

    async def classify_single_utterance(
        self,
        utterance: str,
        timestamp: Optional[str] = None,
        previous_utterance: Optional[str] = None,
        next_utterance: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        단일 발화의 수업 단계 분류

        Args:
            utterance: 분류할 발화
            timestamp: 발화 시간
            previous_utterance: 이전 발화
            next_utterance: 다음 발화

        Returns:
            {
                "stage": "introduction" | "development" | "closing",
                "confidence": 0.85,
                "checklist_results": {
                    "introduction": {"results": {...}, "yes_count": 3, ...},
                    "development": {...},
                    "closing": {...}
                },
                "decision_reason": "..."
            }
        """
        logger.info(f"Classifying utterance: {utterance[:50]}...")

        # ✅ Semantic Cache 확인 (일관성 보장)
        if self.semantic_cache:
            # 캐시 키에 포함할 컨텍스트
            context = {
                "timestamp": timestamp,
                "has_previous": previous_utterance is not None,
                "has_next": next_utterance is not None
            }

            cached_result = self.semantic_cache.get(
                utterance_text=utterance,
                classifier_type="stage",
                context=context
            )

            if cached_result:
                logger.info(f"✓ Using cached stage classification (consistency guaranteed)")
                return cached_result

        # 모든 단계에 대해 체크리스트 실행
        stage_names = ["introduction", "development", "closing"]
        checklist_results = {}

        for stage_name in stage_names:
            # 프롬프트 생성
            prompt = self._build_prompt(
                utterance=utterance,
                stage_name=stage_name,
                timestamp=timestamp,
                previous_utterance=previous_utterance,
                next_utterance=next_utterance
            )

            # 체크리스트 실행 (3회 다수결)
            expected_keys = self._get_expected_keys(stage_name)
            result = await self.openai_service.execute_checklist_with_majority_voting(
                prompt=prompt,
                expected_keys=expected_keys
            )

            # Yes 개수 세기
            yes_count = self.openai_service.count_yes_responses(result["results"])

            checklist_results[stage_name] = {
                **result,
                "yes_count": yes_count
            }

        # 분류 결정
        decision = self._make_classification_decision(checklist_results)

        result = {
            "stage": decision["stage"],
            "confidence": decision["confidence"],
            "checklist_results": checklist_results,
            "decision_reason": decision["reason"]
        }

        # ✅ Semantic Cache에 결과 저장 (일관성 보장)
        if self.semantic_cache:
            context = {
                "timestamp": timestamp,
                "has_previous": previous_utterance is not None,
                "has_next": next_utterance is not None
            }

            self.semantic_cache.set(
                utterance_text=utterance,
                classifier_type="stage",
                result=result,
                context=context
            )
            logger.info(f"✓ Cached stage classification for future use")

        return result

    def _make_classification_decision(
        self,
        checklist_results: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        체크리스트 결과를 바탕으로 최종 단계 결정

        Args:
            checklist_results: 각 단계별 체크리스트 결과

        Returns:
            {
                "stage": "introduction",
                "confidence": 0.85,
                "reason": "..."
            }
        """
        thresholds = self.rules["threshold"]

        # 각 단계의 임계값 충족 여부 확인
        stage_scores = {}
        for stage_name in ["introduction", "development", "closing"]:
            yes_count = checklist_results[stage_name]["yes_count"]
            threshold = thresholds[stage_name]
            avg_confidence = checklist_results[stage_name]["stats"]["average_confidence"]

            # 임계값 충족 시 점수 부여
            meets_threshold = yes_count >= threshold
            score = yes_count * avg_confidence if meets_threshold else 0

            stage_scores[stage_name] = {
                "yes_count": yes_count,
                "threshold": threshold,
                "meets_threshold": meets_threshold,
                "score": score,
                "avg_confidence": avg_confidence
            }

        # 임계값을 넘는 단계들 찾기
        qualified_stages = [
            name for name, info in stage_scores.items()
            if info["meets_threshold"]
        ]

        if not qualified_stages:
            # 임계값을 넘는 단계가 없으면 fallback
            fallback_stage = self.rules["fallback"]["default"]
            fallback_reason = self.rules["fallback"]["reason"]

            return {
                "stage": fallback_stage,
                "confidence": 0.5,
                "reason": f"Fallback: {fallback_reason}"
            }

        elif len(qualified_stages) == 1:
            # 하나만 충족하면 그것 선택
            selected_stage = qualified_stages[0]
            confidence = stage_scores[selected_stage]["avg_confidence"]

            return {
                "stage": selected_stage,
                "confidence": confidence,
                "reason": f"Only {selected_stage} met threshold"
            }

        else:
            # 여러 단계가 충족하면 우선순위 또는 점수로 결정
            priority = self.rules["tie_breaking"]["priority"]

            # 우선순위 기준으로 정렬
            qualified_stages_sorted = sorted(
                qualified_stages,
                key=lambda x: priority.index(x)
            )

            selected_stage = qualified_stages_sorted[0]
            confidence = stage_scores[selected_stage]["avg_confidence"]

            return {
                "stage": selected_stage,
                "confidence": confidence,
                "reason": f"Multiple stages qualified, selected by priority: {', '.join(qualified_stages)}"
            }

    async def classify_multiple_utterances(
        self,
        utterances: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        여러 발화를 배치로 분류

        Args:
            utterances: [
                {
                    "text": "...",
                    "timestamp": "...",
                    "id": "..."
                },
                ...
            ]

        Returns:
            각 발화의 분류 결과 리스트
        """
        logger.info(f"Classifying {len(utterances)} utterances")

        results = []
        for i, utterance in enumerate(utterances):
            # 이전/다음 발화 컨텍스트
            prev_text = utterances[i-1]["text"] if i > 0 else None
            next_text = utterances[i+1]["text"] if i < len(utterances)-1 else None

            result = await self.classify_single_utterance(
                utterance=utterance["text"],
                timestamp=utterance.get("timestamp"),
                previous_utterance=prev_text,
                next_utterance=next_text
            )

            # 메타데이터 추가
            result["utterance_id"] = utterance.get("id")
            result["utterance_text"] = utterance["text"]

            results.append(result)

            logger.info(
                f"[{i+1}/{len(utterances)}] {utterance.get('id')}: "
                f"{result['stage']} (conf={result['confidence']})"
            )

        return results

    def get_stage_statistics(
        self,
        classification_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        분류 결과 통계 계산

        Args:
            classification_results: classify_multiple_utterances의 결과

        Returns:
            {
                "total_utterances": 100,
                "stage_distribution": {
                    "introduction": 15,
                    "development": 70,
                    "closing": 15
                },
                "stage_percentages": {...},
                "average_confidence": 0.85,
                "low_confidence_count": 5
            }
        """
        total = len(classification_results)

        # 단계별 분포
        stage_counts = {
            "introduction": 0,
            "development": 0,
            "closing": 0
        }

        confidences = []
        low_confidence_count = 0

        for result in classification_results:
            stage = result["stage"]
            stage_counts[stage] += 1

            confidence = result["confidence"]
            confidences.append(confidence)

            if confidence < 0.7:
                low_confidence_count += 1

        # 백분율 계산
        stage_percentages = {
            stage: round(count / total * 100, 1)
            for stage, count in stage_counts.items()
        }

        return {
            "total_utterances": total,
            "stage_distribution": stage_percentages,  # Use percentages, not counts
            "stage_counts": stage_counts,             # Add separate field for raw counts
            "stage_percentages": stage_percentages,   # Keep for backward compatibility
            "average_confidence": round(sum(confidences) / len(confidences), 2),
            "low_confidence_count": low_confidence_count
        }


async def test_stage_classifier():
    """테스트 함수"""
    classifier = StageClassifier()

    # 테스트 발화
    test_utterances = [
        {
            "id": "utt_001",
            "text": "오늘은 피타고라스 정리에 대해 배워보겠습니다",
            "timestamp": "00:00:30"
        },
        {
            "id": "utt_002",
            "text": "이제 공식을 적용해서 문제를 풀어봅시다",
            "timestamp": "00:15:00"
        },
        {
            "id": "utt_003",
            "text": "오늘 배운 내용을 정리하면, 피타고라스 정리는 a²+b²=c²였습니다",
            "timestamp": "00:40:00"
        }
    ]

    results = await classifier.classify_multiple_utterances(test_utterances)

    for result in results:
        print(f"\nUtterance: {result['utterance_text']}")
        print(f"Stage: {result['stage']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reason: {result['decision_reason']}")

    stats = classifier.get_stage_statistics(results)
    print("\nStatistics:", stats)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_stage_classifier())
