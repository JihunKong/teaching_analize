#!/usr/bin/env python3
"""
CBIL Evaluator Agent
개념기반 탐구학습(CBIL) 7단계 평가 전문 에이전트
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

from models.analysis_models import CBILEvaluationAnalysis, CBILStepScore
from models.prompt_templates import PromptTemplates
from integrations.llm_gateway import LLMGateway
from analyzers.visualization_engine import VisualizationEngine

logger = logging.getLogger(__name__)

class CBILEvaluatorAgent:
    """
    CBIL 7단계 평가 전문 에이전트
    
    기능:
    - 7단계별 개념 중심 vs 지식 중심 판단
    - 0-3점 점수화 평가
    - 1점 이하 시 대안 제시
    - 레이더 차트 생성
    - 개선 권고사항 도출
    """
    
    def __init__(self, llm_gateway: LLMGateway, viz_engine: VisualizationEngine):
        self.llm_gateway = llm_gateway
        self.viz_engine = viz_engine
        
        # CBIL 7단계 정의
        self.cbil_steps = [
            "Engage", "Focus", "Investigate", "Organize", 
            "Generalize", "Transfer", "Reflect"
        ]
        
        # 개념 중심 vs 지식 중심 판단 키워드
        self.concept_centered_keywords = [
            "속성", "관계", "일반화", "개념", "원리", "패턴", "구조", 
            "공통점", "차이점", "분류", "범주", "모델", "이론"
        ]
        
        self.knowledge_centered_keywords = [
            "암기", "정보", "사실", "감상", "정의", "외우기", "기억", 
            "단순", "감정", "느낌", "인상", "직관"
        ]
        
        # 단계별 평가 기준
        self.step_criteria = {
            "Engage": {
                "concept_indicators": ["호기심", "연결", "개념", "탐구", "문제"],
                "knowledge_indicators": ["정보", "감상", "단순", "암기"]
            },
            "Focus": {
                "concept_indicators": ["본질적", "개념", "속성", "관계", "탐구"],
                "knowledge_indicators": ["사실", "정보", "감상", "단순"]
            },
            "Investigate": {
                "concept_indicators": ["속성", "조건", "사례", "비사례", "탐색"],
                "knowledge_indicators": ["정보", "감상", "단순", "나열"]
            },
            "Organize": {
                "concept_indicators": ["구조화", "관계", "속성", "범주", "분류"],
                "knowledge_indicators": ["단편", "나열", "정리", "요약"]
            },
            "Generalize": {
                "concept_indicators": ["일반화", "대체로", "일반적으로", "확장"],
                "knowledge_indicators": ["사실", "요약", "정리", "단순"]
            },
            "Transfer": {
                "concept_indicators": ["적용", "전이", "맥락", "재해석"],
                "knowledge_indicators": ["감상", "단순", "정보", "회상"]
            },
            "Reflect": {
                "concept_indicators": ["사고변화", "개념재구성", "성찰", "메타"],
                "knowledge_indicators": ["감정", "인상", "단순", "느낌"]
            }
        }
    
    async def analyze(self, transcript: str) -> CBILEvaluationAnalysis:
        """
        CBIL 7단계 분석 실행
        
        Args:
            transcript: 수업 전사 텍스트
            
        Returns:
            CBILEvaluationAnalysis: CBIL 평가 결과
        """
        try:
            logger.info("🎯 Starting CBIL evaluation analysis")
            
            # 1. LLM 기반 분석 실행
            llm_response = await self._get_llm_analysis(transcript)
            
            # 2. 7단계별 증거 추출
            step_evidences = self._extract_step_evidences(transcript)
            
            # 3. 각 단계별 평가
            step_scores = []
            alternatives = []
            
            for i, step_name in enumerate(self.cbil_steps):
                score_data = await self._evaluate_step(
                    step_name, step_evidences.get(step_name, []), 
                    llm_response, i + 1
                )
                step_scores.append(score_data["score"])
                
                if score_data["score"].score <= 1:
                    alternative = self._generate_alternative(
                        step_name, score_data["evidence"]
                    )
                    alternatives.append(alternative)
            
            # 4. 종합 계산
            total_score = sum(score.score for score in step_scores)
            average_score = total_score / 7
            concept_centered_count = sum(1 for score in step_scores if score.is_concept_centered)
            concept_centered_percentage = (concept_centered_count / 7) * 100
            
            # 5. 레이더 차트 생성
            radar_chart_url = await self._generate_radar_chart(step_scores)
            
            # 6. 종합 평가 및 권고사항
            overall_assessment = self._generate_overall_assessment(
                step_scores, average_score, concept_centered_percentage
            )
            improvement_recommendations = alternatives[:3]  # 상위 3개
            
            result = CBILEvaluationAnalysis(
                steps=step_scores,
                total_score=total_score,
                average_score=round(average_score, 2),
                radar_chart_url=radar_chart_url,
                overall_assessment=overall_assessment,
                concept_centered_percentage=round(concept_centered_percentage, 1),
                improvement_recommendations=improvement_recommendations
            )
            
            logger.info("✅ CBIL evaluation analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ CBIL analysis failed: {e}")
            raise
    
    async def _get_llm_analysis(self, transcript: str) -> str:
        """LLM 기반 CBIL 분석 실행"""
        prompt = PromptTemplates.get_cbil_evaluation_prompt(transcript)
        
        response = await self.llm_gateway.generate_analysis(
            prompt=prompt,
            analysis_type="cbil_evaluation"
        )
        
        return response
    
    def _extract_step_evidences(self, transcript: str) -> Dict[str, List[str]]:
        """
        전사에서 각 단계별 증거 추출
        
        Args:
            transcript: 전사 텍스트
            
        Returns:
            Dict[str, List[str]]: 단계별 증거 목록
        """
        evidences = {step: [] for step in self.cbil_steps}
        
        # 발화 단위로 분리
        utterances = self._parse_utterances(transcript)
        
        for utterance in utterances:
            for step in self.cbil_steps:
                criteria = self.step_criteria.get(step, {})
                concept_indicators = criteria.get("concept_indicators", [])
                
                # 개념 중심 지표가 있으면 증거로 추가
                if any(indicator in utterance for indicator in concept_indicators):
                    evidences[step].append(utterance[:100])  # 100자 제한
        
        return evidences
    
    def _parse_utterances(self, transcript: str) -> List[str]:
        """전사를 발화 단위로 분리"""
        # 발화자별 분리
        utterances = []
        
        # 시간 태그 제거
        clean_text = re.sub(r'\d+:\d+', '', transcript)
        
        # 발화자 태그로 분리
        patterns = [
            r'교사\s*[:：]\s*([^교사학생]+)',
            r'학생\s*[:：]\s*([^교사학생]+)', 
            r'T\s*[:：]\s*([^TS]+)',
            r'S\s*[:：]\s*([^TS]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, clean_text, re.IGNORECASE)
            utterances.extend([match.strip() for match in matches if match.strip()])
        
        if not utterances:
            sentences = re.split(r'[.!?。]', clean_text)
            utterances = [s.strip() for s in sentences if s.strip()]
        
        return utterances
    
    async def _evaluate_step(
        self, 
        step_name: str, 
        evidences: List[str], 
        llm_response: str,
        step_number: int
    ) -> Dict[str, Any]:
        """
        개별 단계 평가
        
        Args:
            step_name: 단계명
            evidences: 증거 목록
            llm_response: LLM 분석 결과
            step_number: 단계 번호
            
        Returns:
            Dict: 평가 결과
        """
        # LLM 응답에서 해당 단계 정보 추출
        step_pattern = rf"#### {step_number}\.\s*{step_name}.*?\n\n(.*?)(?=####|$)"
        step_match = re.search(step_pattern, llm_response, re.DOTALL)
        step_description = step_match.group(1).strip() if step_match else ""
        
        # 개념 중심도 판단
        is_concept_centered = self._is_concept_centered(step_description + " ".join(evidences))
        
        # 점수 계산
        score = self._calculate_step_score(step_name, evidences, step_description, is_concept_centered)
        
        # 대안 제안 (1점 이하시)
        alternative = None
        if score <= 1:
            alternative = self._generate_step_alternative(step_name, evidences)
        
        cbil_step_score = CBILStepScore(
            step_name=step_name,
            step_number=step_number,
            score=score,
            description=step_description or f"{step_name} 단계 실행 수준 분석",
            evidence=evidences[:3],  # 상위 3개 증거
            is_concept_centered=is_concept_centered,
            alternative_suggestion=alternative
        )
        
        return {
            "score": cbil_step_score,
            "evidence": evidences,
            "description": step_description
        }
    
    def _is_concept_centered(self, text: str) -> bool:
        """개념 중심인지 판단"""
        concept_count = sum(1 for keyword in self.concept_centered_keywords if keyword in text)
        knowledge_count = sum(1 for keyword in self.knowledge_centered_keywords if keyword in text)
        
        return concept_count > knowledge_count
    
    def _calculate_step_score(
        self, 
        step_name: str, 
        evidences: List[str], 
        description: str,
        is_concept_centered: bool
    ) -> int:
        """
        단계별 점수 계산 (0-3점)
        
        Args:
            step_name: 단계명
            evidences: 증거 목록
            description: 단계 설명
            is_concept_centered: 개념 중심 여부
            
        Returns:
            int: 0-3점 점수
        """
        base_score = 0
        
        # 증거의 양과 질 평가
        if len(evidences) >= 3:
            base_score += 1
        elif len(evidences) >= 1:
            base_score += 0.5
        
        # 설명의 품질 평가
        if len(description) >= 100:
            base_score += 1
        elif len(description) >= 50:
            base_score += 0.5
        
        # 개념 중심도 평가
        if is_concept_centered:
            base_score += 1
        
        # 단계별 특수 기준
        criteria = self.step_criteria.get(step_name, {})
        concept_indicators = criteria.get("concept_indicators", [])
        
        concept_indicator_count = sum(
            1 for indicator in concept_indicators 
            if any(indicator in evidence for evidence in evidences)
        )
        
        if concept_indicator_count >= 2:
            base_score += 0.5
        
        # 최종 점수는 0-3점으로 제한
        final_score = min(3, max(0, int(base_score)))
        
        # 개념 중심이 명확하지 않으면 2점 이상 금지
        if not is_concept_centered and final_score >= 2:
            final_score = 1
        
        return final_score
    
    def _generate_alternative(self, step_name: str, evidences: List[str]) -> str:
        """대안 제시 생성"""
        alternatives = {
            "Engage": "교사는 학생들이 개념과의 연결을 위해 '이 상황에서 어떤 개념이 숨어있을까?'와 같은 질문으로 지적 호기심을 유도할 수 있습니다.",
            "Focus": "개념 중심 사고를 위해 '이것의 본질적 특성은 무엇인가?'와 같은 본질적 질문으로 탐구 방향을 설정할 수 있습니다.",
            "Investigate": "개념의 속성을 체계적으로 탐색하기 위해 사례-비사례 분석과 속성 비교 활동을 설계할 수 있습니다.",
            "Organize": "개념 구조화를 위해 개념 지도나 속성 분류표를 활용하여 학습 내용을 체계적으로 정리할 수 있습니다.",
            "Generalize": "일반화 유도를 위해 '이 개념이 다른 상황에서도 적용될까?'와 같은 확장 질문을 통해 개념의 일반성을 탐구할 수 있습니다.",
            "Transfer": "개념 전이를 위해 학습한 개념을 새로운 맥락이나 다른 교과에 적용해보는 활동을 설계할 수 있습니다.",
            "Reflect": "구조적 성찰을 위해 학생들이 자신의 사고 변화와 개념 이해의 발전 과정을 메타인지적으로 점검하도록 유도할 수 있습니다."
        }
        
        return alternatives.get(step_name, "해당 단계의 개념 중심 접근을 위한 교수법 개선이 필요합니다.")
    
    def _generate_step_alternative(self, step_name: str, evidences: List[str]) -> str:
        """단계별 구체적 대안 생성"""
        return self._generate_alternative(step_name, evidences)
    
    async def _generate_radar_chart(self, step_scores: List[CBILStepScore]) -> str:
        """레이더 차트 생성"""
        try:
            # 점수 데이터 준비
            scores = [score.score for score in step_scores]
            labels = [score.step_name for score in step_scores]
            
            chart_url = await self.viz_engine.create_radar_chart(
                data={"scores": scores},
                labels=labels,
                title="CBIL 7단계 수업 실행 평가",
                filename="cbil_radar_chart"
            )
            
            return chart_url
            
        except Exception as e:
            logger.error(f"❌ Radar chart generation failed: {e}")
            return ""
    
    def _generate_overall_assessment(
        self, 
        step_scores: List[CBILStepScore], 
        average_score: float,
        concept_centered_percentage: float
    ) -> str:
        """종합 평가 생성"""
        if average_score >= 2.5:
            level = "우수"
        elif average_score >= 2.0:
            level = "양호"
        elif average_score >= 1.5:
            level = "보통"
        else:
            level = "개선 필요"
        
        concept_level = "높음" if concept_centered_percentage >= 70 else "보통" if concept_centered_percentage >= 50 else "낮음"
        
        strongest_step = max(step_scores, key=lambda x: x.score)
        weakest_step = min(step_scores, key=lambda x: x.score)
        
        assessment = f"""
        CBIL 7단계 종합 평가: {level} (평균 {average_score}점)
        
        개념 중심도: {concept_level} ({concept_centered_percentage}%)
        
        강점 단계: {strongest_step.step_name} ({strongest_step.score}점)
        개선 필요 단계: {weakest_step.step_name} ({weakest_step.score}점)
        
        이 수업은 {'개념기반 탐구학습의 구조를 잘 따르고 있으며' if average_score >= 2.0 else '개념 중심 접근의 강화가 필요하며'}, 
        특히 {weakest_step.step_name} 단계의 개선을 통해 더욱 효과적인 개념기반 수업이 될 수 있습니다.
        """.strip()
        
        return assessment