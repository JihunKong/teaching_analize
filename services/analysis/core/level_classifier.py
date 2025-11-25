"""
Level Classifier
인지 수준 분류: L1 (기억/이해) / L2 (적용/분석) / L3 (종합/평가)
Based on Bloom's Taxonomy
"""

import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from services.openai_service import OpenAIService
from utils.semantic_cache import SemanticCache

logger = logging.getLogger(__name__)


class LevelClassifier:
    """인지 수준 분류기"""

    def __init__(
        self,
        checklist_path: Optional[str] = None,
        openai_service: Optional[OpenAIService] = None,
        semantic_cache: Optional[SemanticCache] = None
    ):
        if checklist_path is None:
            current_dir = Path(__file__).parent.parent
            checklist_path = current_dir / "checklists" / "level_checklists.yaml"

        with open(checklist_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.levels = self.config["levels"]
        self.rules = self.config["classification_rules"]
        self.prompt_template = self.config["prompt_template"]
        self.openai_service = openai_service or OpenAIService()
        self.semantic_cache = semantic_cache

        logger.info("Level Classifier initialized (caching: %s)", "enabled" if semantic_cache else "disabled")

    def _build_checklist_items(self, level_name: str) -> str:
        level = self.levels[level_name]
        checklist = level["checklist"]
        items = []
        for idx, item in enumerate(checklist, 1):
            items.append(f"{idx}. {item['id']}: {item['question']}")
        return "\n".join(items)

    def _build_prompt(
        self,
        utterance: str,
        level_name: str,
        timestamp: Optional[str] = None,
        previous_utterance: Optional[str] = None,
        next_utterance: Optional[str] = None
    ) -> str:
        level = self.levels[level_name]
        level_display_name = level["name"]
        checklist_items = self._build_checklist_items(level_name)

        return self.prompt_template.format(
            utterance=utterance,
            timestamp=timestamp or "N/A",
            previous_utterance=previous_utterance or "N/A",
            next_utterance=next_utterance or "N/A",
            level_name=level_display_name,
            checklist_items=checklist_items
        )

    def _get_expected_keys(self, level_name: str) -> List[str]:
        return [item["id"] for item in self.levels[level_name]["checklist"]]

    async def classify_single_utterance(
        self,
        utterance: str,
        timestamp: Optional[str] = None,
        previous_utterance: Optional[str] = None,
        next_utterance: Optional[str] = None
    ) -> Dict[str, Any]:
        logger.info(f"Classifying cognitive level: {utterance[:50]}...")

        # ✅ Semantic Cache 확인 (일관성 보장)
        if self.semantic_cache:
            context = {
                "timestamp": timestamp,
                "has_previous": previous_utterance is not None,
                "has_next": next_utterance is not None
            }

            cached_result = self.semantic_cache.get(
                utterance_text=utterance,
                classifier_type="level",
                context=context
            )

            if cached_result:
                logger.info(f"✓ Using cached level classification (consistency guaranteed)")
                return cached_result

        level_names = ["L1", "L2", "L3"]
        checklist_results = {}

        for level_name in level_names:
            prompt = self._build_prompt(
                utterance, level_name, timestamp,
                previous_utterance, next_utterance
            )

            expected_keys = self._get_expected_keys(level_name)
            result = await self.openai_service.execute_checklist_with_majority_voting(
                prompt, expected_keys
            )

            yes_count = self.openai_service.count_yes_responses(result["results"])
            checklist_results[level_name] = {**result, "yes_count": yes_count}

        decision = self._make_classification_decision(checklist_results)

        result = {
            "level": decision["level"],
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
                classifier_type="level",
                result=result,
                context=context
            )
            logger.info(f"✓ Cached level classification for future use")

        return result

    def _make_classification_decision(self, checklist_results: Dict[str, Dict]) -> Dict[str, Any]:
        thresholds = self.rules["threshold"]
        level_scores = {}

        for level_name in ["L1", "L2", "L3"]:
            yes_count = checklist_results[level_name]["yes_count"]
            threshold = thresholds[level_name]
            avg_confidence = checklist_results[level_name]["stats"]["average_confidence"]

            meets_threshold = yes_count >= threshold
            score = yes_count * avg_confidence if meets_threshold else 0

            level_scores[level_name] = {
                "yes_count": yes_count,
                "threshold": threshold,
                "meets_threshold": meets_threshold,
                "score": score,
                "avg_confidence": avg_confidence
            }

        qualified_levels = [
            name for name, info in level_scores.items()
            if info["meets_threshold"]
        ]

        if not qualified_levels:
            fallback = self.rules["fallback"]["default"]
            return {
                "level": fallback,
                "confidence": 0.5,
                "reason": f"Fallback: {self.rules['fallback']['reason']}"
            }

        # 계층 구조 우선순위 (L3 > L2 > L1)
        priority = self.rules["hierarchy"]["priority"]
        selected = sorted(qualified_levels, key=lambda x: priority.index(x))[0]
        confidence = level_scores[selected]["avg_confidence"]

        return {
            "level": selected,
            "confidence": confidence,
            "reason": f"Qualified levels: {', '.join(qualified_levels)}, selected by hierarchy"
        }

    async def classify_multiple_utterances(
        self,
        utterances: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        logger.info(f"Classifying {len(utterances)} utterances for cognitive level")

        results = []
        for i, utterance in enumerate(utterances):
            prev_text = utterances[i-1]["text"] if i > 0 else None
            next_text = utterances[i+1]["text"] if i < len(utterances)-1 else None

            result = await self.classify_single_utterance(
                utterance["text"],
                utterance.get("timestamp"),
                prev_text,
                next_text
            )

            result["utterance_id"] = utterance.get("id")
            result["utterance_text"] = utterance["text"]
            results.append(result)

            logger.info(f"[{i+1}/{len(utterances)}] {result['utterance_id']}: {result['level']} (conf={result['confidence']})")

        return results

    def get_level_statistics(self, classification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(classification_results)
        level_counts = {"L1": 0, "L2": 0, "L3": 0}
        confidences = []

        for result in classification_results:
            level_counts[result["level"]] += 1
            confidences.append(result["confidence"])

        level_percentages = {
            level: round(count / total * 100, 1)
            for level, count in level_counts.items()
        }

        return {
            "total_utterances": total,
            "level_distribution": level_percentages,  # Use percentages, not counts
            "level_counts": level_counts,             # Add separate field for raw counts
            "level_percentages": level_percentages,   # Keep for backward compatibility
            "average_confidence": round(sum(confidences) / len(confidences), 2),
            "cognitive_complexity_score": round(
                (level_counts["L1"] * 1 + level_counts["L2"] * 2 + level_counts["L3"] * 3) / total, 2
            )
        }


async def test_level_classifier():
    classifier = LevelClassifier()

    test_utterances = [
        {"id": "utt_001", "text": "피타고라스 정리는 a²+b²=c²입니다", "timestamp": "00:05:00"},
        {"id": "utt_002", "text": "이 공식을 사용해서 문제를 풀어보세요", "timestamp": "00:10:00"},
        {"id": "utt_003", "text": "왜 이 공식이 성립할까요? 증명해봅시다", "timestamp": "00:20:00"}
    ]

    results = await classifier.classify_multiple_utterances(test_utterances)

    for result in results:
        print(f"\nUtterance: {result['utterance_text']}")
        print(f"Level: {result['level']}")
        print(f"Confidence: {result['confidence']}")

    stats = classifier.get_level_statistics(results)
    print("\nStatistics:", stats)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_level_classifier())
