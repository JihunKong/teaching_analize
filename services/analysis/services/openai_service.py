"""
OpenAI Service for Checklist Execution
3회 실행 후 다수결 투표로 최종 결과 결정

Fallback Strategy: Upstage Solar Pro 2 → Anthropic Claude Sonnet
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from collections import Counter
import asyncio

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available - fallback disabled")


class OpenAIService:
    """OpenAI API를 사용한 체크리스트 실행 서비스"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = None,  # ⚠️ CHANGED: Now reads from GPT_MODEL env var
        num_runs: int = 3
    ):
        """
        Args:
            api_key: OpenAI API key (기본값: 환경변수 OPENAI_API_KEY)
            model: 사용할 모델 (기본값: 환경변수 GPT_MODEL 또는 solar-pro2)
            num_runs: 실행 횟수 (기본값: 3) - majority voting으로 일관성 보장

        Note:
            Upstage Solar Pro 2 uses temperature=0 (configurable)
            일관성은 majority voting (num_runs=3) + structured output으로 보장

        Fallback:
            If Upstage API fails (401/billing), automatically fallback to Anthropic Claude
        """
        # Determine API Key (Upstage priority)
        upstage_key = os.getenv("UPSTAGE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        self.api_key = api_key or upstage_key or openai_key
        
        if not self.api_key:
            raise ValueError("No API Key (UPSTAGE_API_KEY or OPENAI_API_KEY) found")

        # Read base_url from environment for Upstage compatibility
        base_url = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1")

        # Initialize Upstage client
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)

        # Initialize Claude fallback client
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_client = None
        if self.anthropic_key and ANTHROPIC_AVAILABLE:
            self.anthropic_client = AsyncAnthropic(api_key=self.anthropic_key)
            logger.info("Claude fallback enabled")
        else:
            logger.warning("Claude fallback not available (missing API key or library)")

        # Read model from environment or use default
        self.model = model or os.getenv("GPT_MODEL", "solar-pro2")
        self.claude_model = "claude-sonnet-4-20250514"
        self.num_runs = num_runs
        self.use_fallback = False  # Track if we're using fallback

        logger.info(f"OpenAI Service initialized: model={self.model}, base_url={base_url}, runs={num_runs}")

    async def _execute_with_claude(
        self,
        prompt: str,
        expected_keys: List[str]
    ) -> Dict[str, str]:
        """
        Claude fallback 실행

        Args:
            prompt: 체크리스트 프롬프트
            expected_keys: 예상되는 응답 키 목록

        Returns:
            {"exp_01": "Yes", "exp_02": "No", ...}
        """
        if not self.anthropic_client:
            logger.error("Claude fallback requested but not available")
            return {key: "No" for key in expected_keys}

        try:
            response = await self.anthropic_client.messages.create(
                model=self.claude_model,
                max_tokens=1024,
                temperature=0,
                system="You are an expert in educational analysis. Answer each checklist question with only 'Yes' or 'No'. Provide your answer in JSON format only, without any additional explanation.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract JSON from response
            content = response.content[0].text

            # Parse JSON
            result = json.loads(content)

            # Validate response
            validated_result = {}
            for key in expected_keys:
                value = result.get(key, "No")
                if isinstance(value, str):
                    value = value.strip().capitalize()
                    if value not in ["Yes", "No"]:
                        logger.warning(f"Invalid value for {key}: {value}, defaulting to 'No'")
                        value = "No"
                else:
                    value = "No"
                validated_result[key] = value

            logger.info("✓ Claude fallback successful")
            return validated_result

        except json.JSONDecodeError as e:
            logger.error(f"Claude JSON decode error: {e}")
            return {key: "No" for key in expected_keys}

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {key: "No" for key in expected_keys}

    async def execute_checklist_once(
        self,
        prompt: str,
        expected_keys: List[str]
    ) -> Dict[str, str]:
        """
        체크리스트를 1회 실행 (Upstage → Claude fallback)

        Args:
            prompt: 체크리스트 프롬프트
            expected_keys: 예상되는 응답 키 목록 (예: ["exp_01", "exp_02", ...])

        Returns:
            {"exp_01": "Yes", "exp_02": "No", ...}
        """
        # Try Upstage first (unless already using fallback)
        if not self.use_fallback:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert in educational analysis. Answer each checklist question with only 'Yes' or 'No'. Provide your answer in JSON format only, without any additional explanation."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"}
                )

                # JSON 파싱
                content = response.choices[0].message.content
                result = json.loads(content)

                # 응답 검증
                validated_result = {}
                for key in expected_keys:
                    value = result.get(key, "No")
                    if isinstance(value, str):
                        value = value.strip().capitalize()
                        if value not in ["Yes", "No"]:
                            logger.warning(f"Invalid value for {key}: {value}, defaulting to 'No'")
                            value = "No"
                    else:
                        value = "No"
                    validated_result[key] = value

                return validated_result

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return {key: "No" for key in expected_keys}

            except Exception as e:
                error_str = str(e).lower()

                # Check if it's a 401/billing error
                if "401" in error_str or "insufficient credit" in error_str or "api_key" in error_str:
                    logger.warning(f"⚠️  Upstage API billing issue detected: {e}")
                    logger.warning("→ Switching to Claude fallback for all subsequent requests")
                    self.use_fallback = True

                    # Try Claude fallback
                    return await self._execute_with_claude(prompt, expected_keys)
                else:
                    logger.error(f"Upstage API error: {e}")
                    return {key: "No" for key in expected_keys}

        # If already using fallback, go straight to Claude
        else:
            return await self._execute_with_claude(prompt, expected_keys)

    async def execute_checklist_with_majority_voting(
        self,
        prompt: str,
        expected_keys: List[str]
    ) -> Dict[str, Any]:
        """
        체크리스트를 3회 실행하고 다수결로 최종 결과 결정

        Args:
            prompt: 체크리스트 프롬프트
            expected_keys: 예상되는 응답 키 목록

        Returns:
            {
                "results": {"exp_01": "Yes", "exp_02": "No", ...},
                "confidence": {"exp_01": 1.0, "exp_02": 0.67, ...},
                "raw_runs": [run1, run2, run3],
                "stats": {
                    "total_keys": 5,
                    "unanimous": 3,
                    "majority": 2,
                    "average_confidence": 0.87
                }
            }
        """
        logger.info(f"Executing checklist {self.num_runs} times for majority voting")

        # 병렬 실행
        tasks = [
            self.execute_checklist_once(prompt, expected_keys)
            for _ in range(self.num_runs)
        ]
        raw_runs = await asyncio.gather(*tasks)

        # 다수결 투표
        final_results = {}
        confidence_scores = {}

        for key in expected_keys:
            # 각 실행에서 해당 키의 결과 수집
            votes = [run.get(key, "No") for run in raw_runs]
            vote_counts = Counter(votes)

            # 최다 득표 결과 선택
            most_common = vote_counts.most_common(1)[0]
            final_result = most_common[0]
            vote_count = most_common[1]

            # 신뢰도 계산 (득표 비율)
            confidence = vote_count / self.num_runs

            final_results[key] = final_result
            confidence_scores[key] = round(confidence, 2)

        # 통계 계산
        unanimous_count = sum(1 for conf in confidence_scores.values() if conf == 1.0)
        majority_count = sum(1 for conf in confidence_scores.values() if conf >= 0.67)
        average_confidence = sum(confidence_scores.values()) / len(confidence_scores)

        stats = {
            "total_keys": len(expected_keys),
            "unanimous": unanimous_count,  # 만장일치 (100%)
            "majority": majority_count,     # 다수결 (67% 이상)
            "average_confidence": round(average_confidence, 2)
        }

        logger.info(
            f"Voting complete: {unanimous_count}/{len(expected_keys)} unanimous, "
            f"avg confidence={stats['average_confidence']}"
        )

        return {
            "results": final_results,
            "confidence": confidence_scores,
            "raw_runs": raw_runs,
            "stats": stats
        }

    async def batch_execute_checklists(
        self,
        prompts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        여러 체크리스트를 병렬로 실행

        Args:
            prompts: [
                {
                    "prompt": "...",
                    "expected_keys": ["exp_01", ...],
                    "metadata": {"utterance_id": "...", ...}
                },
                ...
            ]

        Returns:
            각 체크리스트의 실행 결과 리스트
        """
        logger.info(f"Batch executing {len(prompts)} checklists")

        tasks = []
        for item in prompts:
            task = self.execute_checklist_with_majority_voting(
                item["prompt"],
                item["expected_keys"]
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # 메타데이터 추가
        for i, result in enumerate(results):
            if "metadata" in prompts[i]:
                result["metadata"] = prompts[i]["metadata"]

        return results

    def count_yes_responses(self, results: Dict[str, str]) -> int:
        """Yes 응답 개수 세기"""
        return sum(1 for value in results.values() if value == "Yes")

    def meets_threshold(
        self,
        results: Dict[str, str],
        threshold: int
    ) -> bool:
        """
        임계값 충족 여부 확인

        Args:
            results: 체크리스트 결과
            threshold: 최소 Yes 개수

        Returns:
            True if yes_count >= threshold
        """
        yes_count = self.count_yes_responses(results)
        return yes_count >= threshold

    async def generate_text(
        self,
        prompt: str,
        max_completion_tokens: int = 500,
        system_prompt: str = None
    ) -> str:
        """
        일반 텍스트 생성 (코칭, 요약 등) with Claude fallback

        Args:
            prompt: 생성 프롬프트
            max_completion_tokens: 최대 완료 토큰 수
            system_prompt: 시스템 프롬프트 (선택)

        Returns:
            생성된 텍스트
        """
        # Try Upstage first (unless already using fallback)
        if not self.use_fallback:
            try:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_completion_tokens=max_completion_tokens
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                error_str = str(e).lower()

                # Check if it's a 401/billing error
                if "401" in error_str or "insufficient credit" in error_str or "api_key" in error_str:
                    logger.warning(f"⚠️  Upstage API billing issue in text generation: {e}")
                    logger.warning("→ Switching to Claude fallback")
                    self.use_fallback = True

                    # Try Claude fallback
                    return await self._generate_text_with_claude(prompt, max_completion_tokens, system_prompt)
                else:
                    logger.error(f"Text generation error: {e}")
                    return ""

        # If already using fallback, go straight to Claude
        else:
            return await self._generate_text_with_claude(prompt, max_completion_tokens, system_prompt)

    async def _generate_text_with_claude(
        self,
        prompt: str,
        max_tokens: int = 500,
        system_prompt: str = None
    ) -> str:
        """
        Claude fallback for text generation

        Args:
            prompt: 생성 프롬프트
            max_tokens: 최대 토큰 수
            system_prompt: 시스템 프롬프트

        Returns:
            생성된 텍스트
        """
        if not self.anthropic_client:
            logger.error("Claude fallback requested but not available")
            return ""

        try:
            system_text = system_prompt or "You are a helpful assistant"

            response = await self.anthropic_client.messages.create(
                model=self.claude_model,
                max_tokens=max_tokens,
                temperature=0,
                system=system_text,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            logger.info("✓ Claude text generation successful")
            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Claude text generation error: {e}")
            return ""


# 유틸리티 함수들

def calculate_agreement_rate(raw_runs: List[Dict[str, str]]) -> float:
    """
    3회 실행 간 일치율 계산

    Args:
        raw_runs: 3회 실행 결과

    Returns:
        0.0 ~ 1.0 (평균 일치율)
    """
    if not raw_runs or len(raw_runs) < 2:
        return 1.0

    keys = list(raw_runs[0].keys())
    agreement_scores = []

    for key in keys:
        votes = [run.get(key, "No") for run in raw_runs]
        vote_counts = Counter(votes)
        most_common_count = vote_counts.most_common(1)[0][1]
        agreement = most_common_count / len(raw_runs)
        agreement_scores.append(agreement)

    return sum(agreement_scores) / len(agreement_scores)


def identify_low_confidence_items(
    confidence_scores: Dict[str, float],
    threshold: float = 0.67
) -> List[str]:
    """
    낮은 신뢰도 항목 식별

    Args:
        confidence_scores: {"exp_01": 0.67, "exp_02": 1.0, ...}
        threshold: 신뢰도 임계값 (기본값: 0.67)

    Returns:
        신뢰도가 threshold 미만인 키 리스트
    """
    return [
        key for key, score in confidence_scores.items()
        if score < threshold
    ]


async def test_openai_service():
    """테스트 함수"""
    service = OpenAIService()

    # 테스트 프롬프트
    test_prompt = """
다음은 교사의 수업 발화입니다.

**발화 내용:**
"오늘은 피타고라스 정리에 대해 배워보겠습니다"

**체크리스트:**
1. intro_01: 학습 목표를 명시적으로 제시하고 있습니까?
2. intro_02: 이전 학습 내용을 복습하고 있습니까?
3. intro_03: 학생들의 흥미를 유발하고 있습니까?

각 질문에 대해 "Yes" 또는 "No"로 답변하세요:
{
  "intro_01": "Yes/No",
  "intro_02": "Yes/No",
  "intro_03": "Yes/No"
}
"""

    expected_keys = ["intro_01", "intro_02", "intro_03"]

    result = await service.execute_checklist_with_majority_voting(
        test_prompt,
        expected_keys
    )

    print("Final Results:", result["results"])
    print("Confidence:", result["confidence"])
    print("Stats:", result["stats"])
    print("Agreement Rate:", calculate_agreement_rate(result["raw_runs"]))


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_openai_service())
