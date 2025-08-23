"""
Solar LLM Client for CBIL Analysis
Using Upstage Solar LLM API for Korean educational content analysis
"""

import os
import requests
import logging
from typing import Dict, List, Any, Optional
import json
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass 
class CBILAnalysisResult:
    """CBIL Analysis Result Structure"""
    utterance: str
    cbil_level: int
    confidence: float
    reasoning: str
    keywords: List[str]
    cognitive_load_score: float
    
class SolarLLMClient:
    """Solar LLM Client for CBIL Analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('SOLAR_API_KEY')
        self.base_url = "https://api.upstage.ai/v1/solar"
        self.model = "solar-1-mini-chat"
        
        if not self.api_key:
            logger.warning("⚠️ SOLAR_API_KEY not found. Using fallback rule-based analysis.")
            self.use_fallback = True
        else:
            self.use_fallback = False
            logger.info("✅ Solar LLM Client initialized successfully")
        
        # CBIL Level definitions for prompt
        self.cbil_definitions = {
            1: "단순 확인 (Simple Confirmation): 예/아니오 응답, 단순 반복",
            2: "사실 회상 (Fact Recall): 학습한 사실이나 정보를 기억하여 답변",
            3: "개념 설명 (Concept Explanation): 개념이나 원리에 대한 설명",
            4: "분석적 사고 (Analytical Thinking): 비교, 분석, 관계 파악",
            5: "종합적 이해 (Comprehensive Understanding): 여러 개념의 종합적 이해",
            6: "평가적 판단 (Evaluative Judgment): 비판적 사고와 평가적 판단",
            7: "창의적 적용 (Creative Application): 창의적 사고와 새로운 적용"
        }
    
    def analyze_utterance(self, utterance: str, context: Dict = None) -> CBILAnalysisResult:
        """
        Analyze single utterance for CBIL classification using Solar LLM
        
        Args:
            utterance: Text to analyze
            context: Optional context information
            
        Returns:
            CBILAnalysisResult object
        """
        if self.use_fallback:
            return self._fallback_analysis(utterance)
        
        try:
            prompt = self._create_cbil_prompt(utterance, context)
            response = self._call_solar_api(prompt)
            
            if response:
                return self._parse_solar_response(utterance, response)
            else:
                logger.warning("Solar API call failed, using fallback")
                return self._fallback_analysis(utterance)
                
        except Exception as e:
            logger.error(f"Solar LLM analysis failed: {e}")
            return self._fallback_analysis(utterance)
    
    def analyze_batch(self, utterances: List[str], context: Dict = None) -> List[CBILAnalysisResult]:
        """
        Analyze multiple utterances in batch
        
        Args:
            utterances: List of texts to analyze
            context: Optional context information
            
        Returns:
            List of CBILAnalysisResult objects
        """
        results = []
        
        for i, utterance in enumerate(utterances):
            # Add processing delay to avoid rate limits
            if i > 0 and not self.use_fallback:
                time.sleep(0.5)
            
            result = self.analyze_utterance(utterance, context)
            result.utterance = utterance
            results.append(result)
            
            logger.info(f"분석 완료 ({i+1}/{len(utterances)}): CBIL Level {result.cbil_level}")
        
        return results
    
    def _create_cbil_prompt(self, utterance: str, context: Dict = None) -> str:
        """Create optimized prompt for Solar LLM CBIL analysis"""
        
        context_info = ""
        if context:
            if context.get('subject'):
                context_info += f"수업 과목: {context['subject']}\n"
            if context.get('grade_level'):
                context_info += f"학년: {context['grade_level']}\n"
        
        prompt = f"""당신은 교육 전문가입니다. 다음 교사의 발화를 CBIL (Cognitive Burden of Instructional Language) 7단계로 분석해주세요.

{context_info}
**CBIL 7단계 분류 기준:**
1. 단순 확인: 예/아니오, 단순 반복, 확인 질문
2. 사실 회상: 학습한 정보나 사실을 기억하여 답변
3. 개념 설명: 개념, 정의, 원리에 대한 설명
4. 분석적 사고: 비교, 대조, 관계 분석, 분류
5. 종합적 이해: 여러 개념의 통합, 전체적 이해
6. 평가적 판단: 비판적 사고, 평가, 판단, 중요도 결정
7. 창의적 적용: 새로운 상황 적용, 창의적 해결책, 혁신

**분석할 발화:** "{utterance}"

**응답 형식 (JSON):**
{{
    "cbil_level": 숫자(1-7),
    "confidence": 소수(0.0-1.0),
    "reasoning": "상세한 분석 근거",
    "keywords": ["주요", "키워드", "목록"],
    "cognitive_load_score": 소수(0.0-1.0)
}}

위 형식으로만 응답해주세요."""

        return prompt
    
    def _call_solar_api(self, prompt: str) -> Optional[str]:
        """Call Solar LLM API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "당신은 교육학 전문가로서 교사의 발화를 CBIL 기준으로 정확히 분석합니다. 반드시 요청된 JSON 형식으로만 응답하세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1  # Low temperature for consistent analysis
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Solar API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Solar API call exception: {e}")
            return None
    
    def _parse_solar_response(self, utterance: str, response: str) -> CBILAnalysisResult:
        """Parse Solar LLM response into CBILAnalysisResult"""
        try:
            # Extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-3]
            elif response.startswith("```"):
                response = response[3:-3]
            
            data = json.loads(response)
            
            return CBILAnalysisResult(
                utterance=utterance,
                cbil_level=max(1, min(7, data.get("cbil_level", 2))),
                confidence=max(0.0, min(1.0, data.get("confidence", 0.5))),
                reasoning=data.get("reasoning", "Solar LLM 분석 결과"),
                keywords=data.get("keywords", []),
                cognitive_load_score=max(0.0, min(1.0, data.get("cognitive_load_score", 0.5)))
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse Solar response: {e}")
            return self._fallback_analysis(utterance)
    
    def _fallback_analysis(self, utterance: str) -> CBILAnalysisResult:
        """Fallback rule-based analysis when Solar LLM is unavailable"""
        from cbil_analyzer import CBILAnalyzer
        
        analyzer = CBILAnalyzer()
        result = analyzer.analyze_utterance(utterance)
        
        return CBILAnalysisResult(
            utterance=utterance,
            cbil_level=result["cbil_level"],
            confidence=result["confidence"],
            reasoning=f"규칙 기반 분석: {result['reasoning']}",
            keywords=result["keywords"],
            cognitive_load_score=result["cbil_level"] / 7.0
        )
    
    def get_comprehensive_analysis(self, utterances: List[str], context: Dict = None) -> Dict[str, Any]:
        """
        Get comprehensive CBIL analysis with statistics
        
        Args:
            utterances: List of teacher utterances to analyze
            context: Optional context (subject, grade level, etc.)
            
        Returns:
            Comprehensive analysis results
        """
        # Analyze each utterance
        results = self.analyze_batch(utterances, context)
        
        # Calculate statistics
        total_utterances = len(results)
        if total_utterances == 0:
            return {"error": "No utterances to analyze"}
        
        # CBIL level distribution
        level_counts = {i: 0 for i in range(1, 8)}
        total_cognitive_load = 0
        total_confidence = 0
        all_keywords = []
        
        for result in results:
            level_counts[result.cbil_level] += 1
            total_cognitive_load += result.cognitive_load_score
            total_confidence += result.confidence
            all_keywords.extend(result.keywords)
        
        # Calculate percentages
        level_percentages = {
            level: (count / total_utterances) * 100
            for level, count in level_counts.items()
        }
        
        # Categorize levels
        low_level_percentage = sum(level_percentages[i] for i in [1, 2, 3])
        mid_level_percentage = sum(level_percentages[i] for i in [4, 5])
        high_level_percentage = sum(level_percentages[i] for i in [6, 7])
        
        # Calculate weighted CBIL score
        weighted_score = sum(
            level * count for level, count in level_counts.items()
        ) / total_utterances
        
        # Generate recommendations
        recommendations = self._generate_recommendations(level_percentages)
        
        # Most common keywords
        from collections import Counter
        keyword_frequency = Counter(all_keywords)
        top_keywords = dict(keyword_frequency.most_common(10))
        
        return {
            "total_utterances": total_utterances,
            "cbil_distribution": {
                "counts": level_counts,
                "percentages": {str(k): round(v, 1) for k, v in level_percentages.items()}
            },
            "level_categories": {
                "low_level": round(low_level_percentage, 1),
                "mid_level": round(mid_level_percentage, 1),
                "high_level": round(high_level_percentage, 1)
            },
            "overall_metrics": {
                "weighted_cbil_score": round(weighted_score, 2),
                "average_cognitive_load": round(total_cognitive_load / total_utterances, 2),
                "average_confidence": round(total_confidence / total_utterances, 2),
                "analysis_quality": "excellent" if total_confidence / total_utterances > 0.8 else "good"
            },
            "top_keywords": top_keywords,
            "recommendations": recommendations,
            "detailed_results": [
                {
                    "utterance": r.utterance,
                    "cbil_level": r.cbil_level,
                    "confidence": round(r.confidence, 2),
                    "reasoning": r.reasoning,
                    "keywords": r.keywords
                } for r in results
            ],
            "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_method": "solar_llm" if not self.use_fallback else "rule_based_fallback"
        }
    
    def _generate_recommendations(self, level_percentages: Dict[int, float]) -> List[str]:
        """Generate teaching recommendations based on CBIL analysis"""
        recommendations = []
        
        # Check for low-level dominance
        if level_percentages[1] + level_percentages[2] > 60:
            recommendations.append("💡 고차원적 사고를 요구하는 질문의 비중을 늘려보세요")
        
        # Check for high-level thinking
        if level_percentages[6] + level_percentages[7] < 10:
            recommendations.append("🎯 비판적 사고와 창의적 적용을 촉진하는 질문을 추가해보세요")
        
        # Check for balanced distribution
        if level_percentages[4] + level_percentages[5] < 20:
            recommendations.append("🔍 분석적 사고와 종합적 이해를 위한 질문을 보강해보세요")
        
        # Check for overly complex questions
        if level_percentages[7] > 30:
            recommendations.append("⚖️ 학습자 수준을 고려하여 난이도 균형을 맞춰보세요")
        
        # Positive feedback for good balance
        if 20 <= level_percentages[4] + level_percentages[5] <= 40:
            recommendations.append("✅ 분석적 사고 질문의 균형이 적절합니다")
        
        if not recommendations:
            recommendations.append("📊 전반적으로 균형잡힌 질문 구성입니다")
        
        return recommendations

# Singleton instance for reuse
solar_client = SolarLLMClient()

def get_solar_client() -> SolarLLMClient:
    """Get singleton Solar LLM client instance"""
    return solar_client