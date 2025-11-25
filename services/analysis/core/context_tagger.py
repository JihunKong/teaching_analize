"""
Context Tagger
수업 맥락 태깅: 설명 / 질문 / 피드백 / 촉진 / 관리
(Multi-label classification: 하나의 발화가 여러 맥락을 가질 수 있음)
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from services.openai_service import OpenAIService
from utils.semantic_cache import SemanticCache

logger = logging.getLogger(__name__)


class ContextTagger:
    """수업 맥락 태거 (Multi-label classifier)"""

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
            checklist_path = current_dir / "checklists" / "context_checklists.yaml"

        with open(checklist_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.contexts = self.config["contexts"]
        self.rules = self.config["classification_rules"]
        self.prompt_template = self.config["prompt_template"]

        # OpenAI 서비스
        self.openai_service = openai_service or OpenAIService()

        # Semantic cache (일관성 보장)
        self.semantic_cache = semantic_cache

        logger.info("Context Tagger initialized (caching: %s)", "enabled" if semantic_cache else "disabled")

    def _build_checklist_items(self, context_name: str) -> str:
        """
        체크리스트 항목을 프롬프트용 텍스트로 변환

        Args:
            context_name: "explanation", "question", "feedback", "facilitation", "management"

        Returns:
            formatted checklist string
        """
        context = self.contexts[context_name]
        checklist = context["checklist"]

        items = []
        for idx, item in enumerate(checklist, 1):
            item_id = item["id"]
            question = item["question"]
            items.append(f"{idx}. {item_id}: {question}")

        return "\n".join(items)

    def _build_prompt(
        self,
        utterance: str,
        context_name: str,
        timestamp: Optional[str] = None,
        previous_utterance: Optional[str] = None,
        next_utterance: Optional[str] = None
    ) -> str:
        """
        체크리스트 실행을 위한 프롬프트 생성

        Args:
            utterance: 태깅할 발화
            context_name: 체크할 맥락
            timestamp: 발화 시간
            previous_utterance: 이전 발화
            next_utterance: 다음 발화

        Returns:
            프롬프트 문자열
        """
        context = self.contexts[context_name]
        context_display_name = context["name"]
        checklist_items = self._build_checklist_items(context_name)

        prompt = self.prompt_template.format(
            utterance=utterance,
            timestamp=timestamp or "N/A",
            previous_utterance=previous_utterance or "N/A",
            next_utterance=next_utterance or "N/A",
            context_name=context_display_name,
            checklist_items=checklist_items
        )

        return prompt

    def _get_expected_keys(self, context_name: str) -> List[str]:
        """해당 맥락의 체크리스트 키 목록 반환"""
        context = self.contexts[context_name]
        return [item["id"] for item in context["checklist"]]

    async def tag_single_utterance(
        self,
        utterance: str,
        timestamp: Optional[str] = None,
        previous_utterance: Optional[str] = None,
        next_utterance: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        단일 발화의 맥락 태깅 (Multi-label)

        Args:
            utterance: 태깅할 발화
            timestamp: 발화 시간
            previous_utterance: 이전 발화
            next_utterance: 다음 발화

        Returns:
            {
                "contexts": ["explanation", "question"],
                "context_scores": {
                    "explanation": 0.85,
                    "question": 0.75,
                    ...
                },
                "checklist_results": {
                    "explanation": {...},
                    "question": {...},
                    ...
                },
                "primary_context": "explanation"
            }
        """
        logger.info(f"Tagging utterance: {utterance[:50]}...")

        # ✅ Semantic Cache 확인 (일관성 보장)
        if self.semantic_cache:
            context = {
                "timestamp": timestamp,
                "has_previous": previous_utterance is not None,
                "has_next": next_utterance is not None
            }

            cached_result = self.semantic_cache.get(
                utterance_text=utterance,
                classifier_type="context",
                context=context
            )

            if cached_result:
                logger.info(f"✓ Using cached context tagging (consistency guaranteed)")
                return cached_result

        # 모든 맥락에 대해 체크리스트 실행
        context_names = ["explanation", "question", "feedback", "facilitation", "management"]
        checklist_results = {}

        for context_name in context_names:
            # 프롬프트 생성
            prompt = self._build_prompt(
                utterance=utterance,
                context_name=context_name,
                timestamp=timestamp,
                previous_utterance=previous_utterance,
                next_utterance=next_utterance
            )

            # 체크리스트 실행 (3회 다수결)
            expected_keys = self._get_expected_keys(context_name)
            result = await self.openai_service.execute_checklist_with_majority_voting(
                prompt=prompt,
                expected_keys=expected_keys
            )

            # Yes 개수 세기
            yes_count = self.openai_service.count_yes_responses(result["results"])

            checklist_results[context_name] = {
                **result,
                "yes_count": yes_count
            }

        # 태깅 결정 (Multi-label)
        decision = self._make_tagging_decision(checklist_results)

        result = {
            "contexts": decision["contexts"],
            "context_scores": decision["scores"],
            "checklist_results": checklist_results,
            "primary_context": decision["primary_context"]
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
                classifier_type="context",
                result=result,
                context=context
            )
            logger.info(f"✓ Cached context tagging for future use")

        return result

    def _make_tagging_decision(
        self,
        checklist_results: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        체크리스트 결과를 바탕으로 맥락 태깅 결정 (Multi-label)

        Args:
            checklist_results: 각 맥락별 체크리스트 결과

        Returns:
            {
                "contexts": ["explanation", "question"],
                "scores": {"explanation": 0.85, "question": 0.75, ...},
                "primary_context": "explanation"
            }
        """
        threshold = self.rules["threshold"]["per_context"]
        min_contexts = self.rules["minimum_contexts"]

        # 각 맥락의 점수 계산
        context_scores = {}
        qualified_contexts = []

        for context_name in ["explanation", "question", "feedback", "facilitation", "management"]:
            yes_count = checklist_results[context_name]["yes_count"]
            avg_confidence = checklist_results[context_name]["stats"]["average_confidence"]

            # 임계값 충족 여부
            meets_threshold = yes_count >= threshold

            # 점수 = yes_count * avg_confidence
            score = yes_count * avg_confidence if meets_threshold else 0
            context_scores[context_name] = round(score, 2)

            if meets_threshold:
                qualified_contexts.append(context_name)

        # 최소 맥락 수 보장
        if len(qualified_contexts) < min_contexts:
            # 점수가 가장 높은 맥락 선택
            fallback_context = self.rules["fallback"]["default"]
            if fallback_context not in qualified_contexts:
                qualified_contexts = [fallback_context]

        # Primary context 결정 (점수가 가장 높은 것)
        primary_context = max(context_scores.items(), key=lambda x: x[1])[0]

        return {
            "contexts": qualified_contexts,
            "scores": context_scores,
            "primary_context": primary_context
        }

    async def tag_multiple_utterances(
        self,
        utterances: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        여러 발화를 배치로 태깅

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
            각 발화의 태깅 결과 리스트
        """
        logger.info(f"Tagging {len(utterances)} utterances")

        results = []
        for i, utterance in enumerate(utterances):
            # 이전/다음 발화 컨텍스트
            prev_text = utterances[i-1]["text"] if i > 0 else None
            next_text = utterances[i+1]["text"] if i < len(utterances)-1 else None

            result = await self.tag_single_utterance(
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
                f"{', '.join(result['contexts'])} (primary={result['primary_context']})"
            )

        return results

    def get_context_statistics(
        self,
        tagging_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        태깅 결과 통계 계산

        Args:
            tagging_results: tag_multiple_utterances의 결과

        Returns:
            {
                "total_utterances": 100,
                "context_distribution": {
                    "explanation": 60,
                    "question": 40,
                    ...
                },
                "context_percentages": {...},
                "average_contexts_per_utterance": 1.5,
                "multi_label_count": 30,
                "common_combinations": [
                    ("explanation", "question", 15),
                    ...
                ]
            }
        """
        total = len(tagging_results)

        # 맥락별 출현 횟수
        context_counts = {
            "explanation": 0,
            "question": 0,
            "feedback": 0,
            "facilitation": 0,
            "management": 0
        }

        # 맥락 조합 추적
        combinations = []
        multi_label_count = 0

        for result in tagging_results:
            contexts = result["contexts"]

            # 각 맥락 카운트
            for ctx in contexts:
                context_counts[ctx] += 1

            # Multi-label 여부
            if len(contexts) > 1:
                multi_label_count += 1

            # 조합 기록
            if len(contexts) > 1:
                combinations.append(tuple(sorted(contexts)))

        # 백분율 계산
        context_percentages = {
            ctx: round(count / total * 100, 1)
            for ctx, count in context_counts.items()
        }

        # 평균 맥락 수
        total_contexts = sum(len(r["contexts"]) for r in tagging_results)
        avg_contexts = round(total_contexts / total, 2)

        # 일반적인 조합 찾기
        from collections import Counter
        common_combos = Counter(combinations).most_common(5)

        return {
            "total_utterances": total,
            "context_distribution": context_percentages,  # Use percentages, not counts
            "context_counts": context_counts,             # Add separate field for raw counts
            "context_percentages": context_percentages,   # Keep for backward compatibility
            "average_contexts_per_utterance": avg_contexts,
            "multi_label_count": multi_label_count,
            "multi_label_percentage": round(multi_label_count / total * 100, 1),
            "common_combinations": [
                {
                    "contexts": list(combo),
                    "count": count,
                    "percentage": round(count / multi_label_count * 100, 1) if multi_label_count > 0 else 0
                }
                for combo, count in common_combos
            ]
        }


async def test_context_tagger():
    """테스트 함수"""
    tagger = ContextTagger()

    # 테스트 발화
    test_utterances = [
        {
            "id": "utt_001",
            "text": "피타고라스 정리는 a²+b²=c²입니다",
            "timestamp": "00:05:00"
        },
        {
            "id": "utt_002",
            "text": "이 공식을 이해했나요? 어려운 부분이 있나요?",
            "timestamp": "00:05:30"
        },
        {
            "id": "utt_003",
            "text": "네, 잘 이해했네요. 그럼 이제 문제를 풀어봅시다",
            "timestamp": "00:06:00"
        },
        {
            "id": "utt_004",
            "text": "조용히 해주세요. 집중이 안 되잖아요",
            "timestamp": "00:10:00"
        }
    ]

    results = await tagger.tag_multiple_utterances(test_utterances)

    for result in results:
        print(f"\nUtterance: {result['utterance_text']}")
        print(f"Contexts: {', '.join(result['contexts'])}")
        print(f"Primary: {result['primary_context']}")
        print(f"Scores: {result['context_scores']}")

    stats = tagger.get_context_statistics(results)
    print("\nStatistics:")
    print(f"  Total: {stats['total_utterances']}")
    print(f"  Distribution: {stats['context_distribution']}")
    print(f"  Multi-label: {stats['multi_label_count']} ({stats['multi_label_percentage']}%)")
    print(f"  Common combinations:")
    for combo in stats['common_combinations']:
        print(f"    {', '.join(combo['contexts'])}: {combo['count']} ({combo['percentage']}%)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_context_tagger())
