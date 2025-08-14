import os
import json
import httpx
import asyncio
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class SolarLLMService:
    """
    Service for interacting with Solar LLM (Upstage) for Korean language processing
    """
    
    def __init__(self):
        self.api_key = os.getenv("SOLAR_API_KEY") or os.getenv("UPSTAGE_API_KEY")
        if not self.api_key:
            logger.warning("Solar/Upstage API key not set")
        
        self.base_url = "https://api.upstage.ai/v1/solar"
        self.model = "solar-1-mini-chat"  # Korean-optimized model
        
        # CBIL classification prompt
        self.cbil_system_prompt = """당신은 한국어 수업 대화를 CBIL(Cognitive Burden of Instructional Language) 7단계로 분류하는 전문가입니다.

CBIL 7단계 정의:
1. 단순 확인 (Simple Confirmation): 예/아니오, 단답형 응답 (5단어 이하)
2. 사실 회상 (Fact Recall): 단순 정보 반복, 암기된 내용 (5-15단어)
3. 개념 설명 (Concept Explanation): 자신의 언어로 재구성 (15-30단어)
4. 분석적 사고 (Analytical Thinking): 비교, 대조, 분류, 관계 파악
5. 종합적 이해 (Comprehensive Understanding): 여러 개념 통합, 인과관계 설명
6. 평가적 판단 (Evaluative Judgment): 비판적 사고, 근거 있는 판단
7. 창의적 적용 (Creative Application): 새로운 상황 적용, 독창적 아이디어

각 발화를 분석하여 JSON 형식으로 응답하세요:
{
    "level": 1-7의 정수,
    "reasoning": "분류 근거 설명",
    "keywords": ["핵심", "키워드", "리스트"],
    "confidence": 0.0-1.0의 신뢰도
}"""

    async def classify_cbil(
        self,
        utterance: str,
        context: Optional[List[str]] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Classify utterance using Solar LLM
        
        Args:
            utterance: The utterance to classify
            context: Context utterances
            temperature: LLM temperature for response variability
            
        Returns:
            Classification result dictionary
        """
        try:
            # Build user prompt
            user_prompt = self._build_classification_prompt(utterance, context)
            
            # Make API call
            response = await self._call_solar_api(
                system_prompt=self.cbil_system_prompt,
                user_prompt=user_prompt,
                temperature=temperature
            )
            
            # Parse response
            result = self._parse_classification_response(response)
            
            return result
            
        except Exception as e:
            logger.error(f"Solar LLM classification failed: {str(e)}")
            return {
                "level": 1,
                "reasoning": "LLM classification failed",
                "keywords": [],
                "confidence": 0.3
            }
    
    async def analyze_teaching_pattern(
        self,
        utterances: List[str],
        cbil_levels: List[int]
    ) -> Dict[str, Any]:
        """
        Analyze teaching patterns from utterances and CBIL levels
        
        Args:
            utterances: List of utterances
            cbil_levels: Corresponding CBIL levels
            
        Returns:
            Teaching pattern analysis
        """
        try:
            prompt = self._build_pattern_analysis_prompt(utterances, cbil_levels)
            
            response = await self._call_solar_api(
                system_prompt="당신은 교육 패턴 분석 전문가입니다. 수업 대화를 분석하여 교사의 교수 패턴과 효과성을 평가합니다.",
                user_prompt=prompt,
                temperature=0.5
            )
            
            return self._parse_pattern_response(response)
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {str(e)}")
            return {"patterns": [], "effectiveness": 0.5}
    
    async def generate_recommendations(
        self,
        statistics: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate teaching recommendations based on analysis
        
        Args:
            statistics: CBIL statistics
            patterns: Teaching patterns identified
            
        Returns:
            List of recommendations
        """
        try:
            prompt = self._build_recommendation_prompt(statistics, patterns)
            
            response = await self._call_solar_api(
                system_prompt="당신은 교육 컨설턴트입니다. CBIL 분석 결과를 바탕으로 구체적이고 실용적인 교수법 개선 제안을 제공합니다.",
                user_prompt=prompt,
                temperature=0.7
            )
            
            return self._parse_recommendations(response)
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return ["분석 결과를 바탕으로 한 추천을 생성할 수 없습니다."]
    
    async def _call_solar_api(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.5,
        max_tokens: int = 500
    ) -> str:
        """Make API call to Solar LLM"""
        if not self.api_key:
            raise ValueError("Solar API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except httpx.HTTPStatusError as e:
                logger.error(f"Solar API HTTP error: {e.response.status_code}")
                raise
            except httpx.TimeoutException:
                logger.error("Solar API request timed out")
                raise
            except Exception as e:
                logger.error(f"Solar API request failed: {str(e)}")
                raise
    
    def _build_classification_prompt(
        self,
        utterance: str,
        context: Optional[List[str]] = None
    ) -> str:
        """Build prompt for CBIL classification"""
        prompt = f"다음 발화를 CBIL 7단계로 분류하세요:\n\n발화: \"{utterance}\"\n"
        
        if context:
            prompt += "\n맥락 (이전/다음 발화):\n"
            for i, ctx in enumerate(context, 1):
                prompt += f"{i}. \"{ctx}\"\n"
        
        prompt += "\nJSON 형식으로 응답하세요."
        
        return prompt
    
    def _parse_classification_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM classification response"""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # Validate and clean result
                return {
                    "level": min(7, max(1, int(result.get("level", 1)))),
                    "reasoning": result.get("reasoning", ""),
                    "keywords": result.get("keywords", []),
                    "confidence": min(1.0, max(0.0, float(result.get("confidence", 0.5))))
                }
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
        
        # Return default if parsing fails
        return {
            "level": 1,
            "reasoning": "Response parsing failed",
            "keywords": [],
            "confidence": 0.3
        }
    
    def _build_pattern_analysis_prompt(
        self,
        utterances: List[str],
        cbil_levels: List[int]
    ) -> str:
        """Build prompt for pattern analysis"""
        prompt = "다음 수업 대화와 CBIL 레벨을 분석하여 교수 패턴을 파악하세요:\n\n"
        
        for i, (utt, level) in enumerate(zip(utterances[:20], cbil_levels[:20]), 1):
            prompt += f"{i}. [Level {level}] \"{utt}\"\n"
        
        prompt += "\n다음을 분석하세요:\n"
        prompt += "1. 주요 교수 패턴 (질문, 설명, 피드백 등)\n"
        prompt += "2. 인지적 수준 변화 패턴\n"
        prompt += "3. 효과적인 교수 전략\n"
        prompt += "4. 개선이 필요한 부분\n"
        
        return prompt
    
    def _parse_pattern_response(self, response: str) -> Dict[str, Any]:
        """Parse pattern analysis response"""
        # Simple parsing - could be enhanced
        patterns = []
        
        if "질문" in response:
            patterns.append({"type": "questioning", "frequency": "high"})
        if "설명" in response:
            patterns.append({"type": "explaining", "frequency": "medium"})
        if "피드백" in response:
            patterns.append({"type": "feedback", "frequency": "low"})
        
        return {
            "patterns": patterns,
            "effectiveness": 0.7,
            "analysis": response
        }
    
    def _build_recommendation_prompt(
        self,
        statistics: Dict[str, Any],
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for recommendations"""
        prompt = f"""CBIL 분석 결과:
- 평균 레벨: {statistics.get('average_level', 0):.2f}
- 고차원 사고 비율: {statistics.get('high_level_ratio', 0):.1%}
- 레벨 분포: {statistics.get('level_distribution', {})}

교수 패턴:
"""
        for pattern in patterns:
            prompt += f"- {pattern.get('type')}: {pattern.get('frequency')}\n"
        
        prompt += """
위 분석을 바탕으로 다음을 제공하세요:
1. 강점 (2-3개)
2. 개선점 (2-3개)
3. 구체적인 실천 방안 (3-5개)

한국어 교육 맥락에 맞는 실용적인 제안을 해주세요."""
        
        return prompt
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """Parse recommendations from response"""
        recommendations = []
        
        # Split response into lines and extract recommendations
        lines = response.split("\n")
        for line in lines:
            line = line.strip()
            if line and (
                line[0].isdigit() or
                line.startswith("-") or
                line.startswith("•") or
                line.startswith("*")
            ):
                # Clean up the line
                clean_line = re.sub(r'^[\d\-\•\*\.\s]+', '', line)
                if clean_line:
                    recommendations.append(clean_line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def summarize_transcript(
        self,
        transcript: str,
        max_length: int = 500
    ) -> str:
        """
        Summarize a transcript
        
        Args:
            transcript: Full transcript text
            max_length: Maximum summary length
            
        Returns:
            Summary text
        """
        try:
            prompt = f"다음 수업 대화를 {max_length}자 이내로 요약하세요:\n\n{transcript[:3000]}"
            
            response = await self._call_solar_api(
                system_prompt="당신은 교육 내용 요약 전문가입니다. 핵심 내용과 중요한 교육적 순간을 중심으로 요약합니다.",
                user_prompt=prompt,
                temperature=0.5,
                max_tokens=max_length
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return "요약을 생성할 수 없습니다."