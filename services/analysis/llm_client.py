import logging
import json
from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from config import settings

logger = logging.getLogger(__name__)

class SolarLLMClient:
    """Client for Solar-mini LLM (Korean-optimized)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.SOLAR_API_KEY or settings.UPSTAGE_API_KEY
        self.base_url = "https://api.upstage.ai/v1/solar"
        self.model = "solar-mini"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def analyze_cbil(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Use Solar LLM to analyze CBIL level with enhanced understanding
        
        Args:
            text: Utterance to analyze
            context: Additional context (subject, grade, etc.)
            
        Returns:
            CBIL analysis result
        """
        prompt = self._create_cbil_prompt(text, context)
        
        try:
            response = await self._call_api(prompt)
            return self._parse_cbil_response(response)
        except Exception as e:
            logger.error(f"Solar LLM analysis failed: {str(e)}")
            # Fallback to rule-based analysis
            return {
                "cbil_level": 2,
                "confidence": 0.5,
                "reasoning": "LLM 분석 실패, 기본 규칙 기반 분석 사용",
                "enhanced": False
            }
    
    def _create_cbil_prompt(self, text: str, context: Dict[str, Any] = None) -> str:
        """Create prompt for CBIL analysis"""
        
        subject = context.get("subject", "일반") if context else "일반"
        grade = context.get("grade", "중등") if context else "중등"
        
        prompt = f"""교사의 발화를 CBIL(Cognitive Burden of Instructional Language) 7단계로 분류해주세요.

CBIL 7단계 분류 기준:
1. 단순 확인: 예/아니오, 단답형 응답 요구
2. 사실 회상: 배운 내용을 기억하여 답하기
3. 개념 설명: 개념이나 원리를 설명하기
4. 분석적 사고: 비교, 분류, 관계 파악하기
5. 종합적 이해: 여러 개념을 통합하여 이해하기
6. 평가적 판단: 비판적 사고로 평가하기
7. 창의적 적용: 새로운 상황에 창의적으로 적용하기

교과목: {subject}
학년: {grade}
교사 발화: "{text}"

다음 형식으로 JSON 응답해주세요:
{{
    "cbil_level": 1-7 사이의 숫자,
    "confidence": 0-1 사이의 확신도,
    "reasoning": "분류 이유 설명",
    "cognitive_verbs": ["발화에 포함된 인지 동사들"],
    "keywords": ["핵심 키워드들"]
}}"""
        
        return prompt
    
    async def _call_api(self, prompt: str) -> str:
        """Call Solar API"""
        if not self.api_key:
            raise ValueError("Solar API key not configured")
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "당신은 한국어 교육 분석 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API call failed: {response.status} - {error_text}")
                
                result = await response.json()
                return result["choices"][0]["message"]["content"]
    
    def _parse_cbil_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response to extract CBIL analysis"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                parsed["enhanced"] = True
                return parsed
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
        
        # Fallback parsing
        return {
            "cbil_level": 2,
            "confidence": 0.5,
            "reasoning": response[:200] if response else "파싱 실패",
            "enhanced": False
        }
    
    async def enhance_analysis_batch(
        self,
        utterances: List[str],
        base_analyses: List[Dict[str, Any]],
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Enhance batch of analyses with LLM insights
        
        Args:
            utterances: List of utterance texts
            base_analyses: Initial rule-based analyses
            context: Additional context
            
        Returns:
            Enhanced analysis results
        """
        if not self.api_key:
            logger.warning("Solar API key not configured, returning base analyses")
            return base_analyses
        
        # Process in batches to avoid rate limits
        batch_size = 5
        enhanced_results = []
        
        for i in range(0, len(utterances), batch_size):
            batch = utterances[i:i+batch_size]
            batch_base = base_analyses[i:i+batch_size]
            
            # Create tasks for concurrent processing
            tasks = []
            for text, base in zip(batch, batch_base):
                task = self.analyze_cbil(text, context)
                tasks.append(task)
            
            # Wait for all tasks to complete
            try:
                batch_results = await asyncio.gather(*tasks)
                
                # Merge with base analyses
                for base, enhanced in zip(batch_base, batch_results):
                    if enhanced.get("enhanced"):
                        # Use LLM result but keep some base analysis
                        merged = {**base, **enhanced}
                        enhanced_results.append(merged)
                    else:
                        enhanced_results.append(base)
            
            except Exception as e:
                logger.error(f"Batch enhancement failed: {str(e)}")
                enhanced_results.extend(batch_base)
            
            # Rate limiting
            await asyncio.sleep(1)
        
        return enhanced_results
    
    async def generate_summary(self, analyses: List[Dict[str, Any]], context: Dict[str, Any] = None) -> str:
        """Generate a summary of the analysis results"""
        
        if not analyses:
            return "분석 결과가 없습니다."
        
        # Calculate statistics
        total = len(analyses)
        level_counts = {i: 0 for i in range(1, 8)}
        for analysis in analyses:
            level = analysis.get("cbil_level", 1)
            level_counts[level] += 1
        
        avg_level = sum(a.get("cbil_level", 1) for a in analyses) / total
        
        prompt = f"""다음 수업 분석 결과를 바탕으로 종합적인 피드백을 작성해주세요.

총 발화 수: {total}
평균 CBIL 레벨: {avg_level:.2f}
레벨 분포:
- 레벨 1 (단순 확인): {level_counts[1]}개
- 레벨 2 (사실 회상): {level_counts[2]}개
- 레벨 3 (개념 설명): {level_counts[3]}개
- 레벨 4 (분석적 사고): {level_counts[4]}개
- 레벨 5 (종합적 이해): {level_counts[5]}개
- 레벨 6 (평가적 판단): {level_counts[6]}개
- 레벨 7 (창의적 적용): {level_counts[7]}개

다음 관점에서 피드백을 제공해주세요:
1. 전반적인 수업의 인지적 수준
2. 개선이 필요한 부분
3. 잘하고 있는 부분
4. 구체적인 개선 방안 2-3가지"""
        
        try:
            response = await self._call_api(prompt)
            return response
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return self._generate_fallback_summary(level_counts, avg_level, total)
    
    def _generate_fallback_summary(self, level_counts: Dict[int, int], avg_level: float, total: int) -> str:
        """Generate fallback summary without LLM"""
        
        summary = f"총 {total}개 발화를 분석했습니다.\n\n"
        summary += f"평균 CBIL 레벨: {avg_level:.2f}\n\n"
        
        # Find dominant levels
        max_count = max(level_counts.values())
        dominant_levels = [k for k, v in level_counts.items() if v == max_count]
        
        if avg_level < 3:
            summary += "수업이 주로 낮은 인지 수준(단순 확인, 사실 회상)에 머물러 있습니다. "
            summary += "더 높은 수준의 사고를 요구하는 질문을 늘려보세요.\n"
        elif avg_level < 5:
            summary += "적절한 인지 수준의 수업이 진행되고 있습니다. "
            summary += "창의적 사고와 평가적 판단을 요구하는 활동을 추가해보세요.\n"
        else:
            summary += "높은 인지 수준의 수업이 진행되고 있습니다. "
            summary += "학생들의 이해도를 확인하며 균형잡힌 수업을 유지하세요.\n"
        
        return summary