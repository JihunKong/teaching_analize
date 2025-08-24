#!/usr/bin/env python3
"""
Teaching Coach Agent
15개 항목 수업 설계와 실행 코칭 분석 전문 에이전트
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from models.analysis_models import TeachingCoachAnalysis, TeachingCoachItem
from models.prompt_templates import PromptTemplates
from integrations.llm_gateway import LLMGateway

logger = logging.getLogger(__name__)

class TeachingCoachAgent:
    """
    수업 설계와 실행 코칭 분석 전문 에이전트
    
    기능:
    - 15개 항목 체계적 분석
    - 비교모드 vs 실행모드 자동 분기
    - 필수 문장 삽입 검증
    - 발화 인용 및 평가 판단
    """
    
    def __init__(self, llm_gateway: LLMGateway):
        self.llm_gateway = llm_gateway
        self.required_sentence = "학생이 목표를 자기 언어로 재진술하거나 짧은 퀴즈로 확인하도록 하면 목표가 자연스럽게 내면화된다."
        self.mode_keywords = ["학습목표", "도입", "전개", "활동", "평가", "차시"]
        
    async def analyze(self, transcript: str, lesson_plan: Optional[str] = None) -> TeachingCoachAnalysis:
        """
        교육 코칭 분석 실행
        
        Args:
            transcript: 수업 전사 텍스트
            lesson_plan: 수업 계획안 (선택적)
            
        Returns:
            TeachingCoachAnalysis: 15개 항목 분석 결과
        """
        try:
            logger.info("🎯 Starting teaching coach analysis")
            
            # 1. 모드 분기 결정
            mode = self._detect_mode(lesson_plan or "")
            logger.info(f"📝 Analysis mode: {mode}")
            
            # 2. LLM 프롬프트 생성 및 실행
            prompt = PromptTemplates.get_teaching_coach_prompt(
                lesson_plan or "없음", 
                transcript
            )
            
            llm_response = await self.llm_gateway.generate_analysis(
                prompt=prompt,
                analysis_type="teaching_coach"
            )
            
            # 3. LLM 응답 파싱
            items = self._parse_llm_response(llm_response)
            
            # 4. 필수 문장 검증
            self._validate_required_sentence(items)
            
            # 5. 종합 분석 생성
            overall_summary = self._generate_summary(items, mode)
            strengths = self._extract_strengths(items)
            improvement_areas = self._extract_improvements(items)
            
            result = TeachingCoachAnalysis(
                mode=mode,
                items=items,
                overall_summary=overall_summary,
                strengths=strengths,
                improvement_areas=improvement_areas
            )
            
            logger.info("✅ Teaching coach analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Teaching coach analysis failed: {e}")
            raise
    
    def _detect_mode(self, lesson_plan: str) -> str:
        """
        분석 모드 감지 (비교모드 vs 실행모드)
        
        Args:
            lesson_plan: 수업 계획안 텍스트
            
        Returns:
            str: "비교모드" 또는 "실행모드"
        """
        if not lesson_plan or lesson_plan.strip() == "없음":
            return "실행모드"
        
        # 계획 키워드 검사
        keyword_found = any(keyword in lesson_plan for keyword in self.mode_keywords)
        return "비교모드" if keyword_found else "실행모드"
    
    def _parse_llm_response(self, llm_response: str) -> List[TeachingCoachItem]:
        """
        LLM 응답을 파싱하여 15개 항목 추출
        
        Args:
            llm_response: LLM 원본 응답
            
        Returns:
            List[TeachingCoachItem]: 파싱된 15개 항목
        """
        items = []
        
        # 정규식으로 항목 분리
        pattern = r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]\s*([^\n]+)\n\n([^①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]+)'
        matches = re.findall(pattern, llm_response, re.DOTALL)
        
        if len(matches) != 15:
            logger.warning(f"⚠️ Expected 15 items, found {len(matches)}")
            # 대체 파싱 시도
            matches = self._alternative_parsing(llm_response)
        
        for i, (title, content) in enumerate(matches[:15], 1):
            # 발화 인용 추출
            evidence = self._extract_evidence(content)
            
            # 평가 판단 추출
            assessment = self._extract_assessment(content)
            
            # 내용 정제
            clean_content = self._clean_content(content)
            
            item = TeachingCoachItem(
                item_number=i,
                title=title.strip(),
                content=clean_content,
                assessment=assessment,
                evidence=evidence
            )
            items.append(item)
        
        return items
    
    def _alternative_parsing(self, text: str) -> List[Tuple[str, str]]:
        """
        대체 파싱 방법 (정규식 실패시)
        """
        # 다른 방식으로 항목 분리 시도
        lines = text.split('\n')
        items = []
        current_item = {"title": "", "content": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 항목 번호 감지
            if any(symbol in line for symbol in ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩', '⑪', '⑫', '⑬', '⑭', '⑮']):
                if current_item["title"]:
                    items.append((current_item["title"], current_item["content"]))
                
                current_item = {"title": line, "content": ""}
            else:
                current_item["content"] += line + " "
        
        # 마지막 항목 추가
        if current_item["title"]:
            items.append((current_item["title"], current_item["content"]))
            
        return items
    
    def _extract_evidence(self, content: str) -> List[str]:
        """
        발화 인용 추출
        
        Args:
            content: 항목 내용
            
        Returns:
            List[str]: 추출된 발화 인용들
        """
        # 큰따옴표로 둘러싸인 발화 추출
        quotes = re.findall(r'"([^"]+)"', content)
        return quotes[:3]  # 최대 3개까지
    
    def _extract_assessment(self, content: str) -> str:
        """
        평가 판단 추출
        
        Args:
            content: 항목 내용
            
        Returns:
            str: 평가 판단 (높은 일치, 부분 일치 등)
        """
        # 마지막 문장에서 판단 추출
        sentences = content.split('.')
        last_sentence = sentences[-1] if sentences else content
        
        assessment_keywords = [
            "높은 일치", "부분 일치", "표면적 구현", 
            "적절", "효과적", "미흡", "제한적"
        ]
        
        for keyword in assessment_keywords:
            if keyword in last_sentence:
                return keyword
                
        return "일반적 수준"
    
    def _clean_content(self, content: str) -> str:
        """
        내용 정제 (길이 조정, 불필요한 문구 제거)
        
        Args:
            content: 원본 내용
            
        Returns:
            str: 정제된 내용 (270-350자)
        """
        # 기본 정제
        content = content.strip()
        content = re.sub(r'\s+', ' ', content)  # 공백 정규화
        
        # 길이 조정
        if len(content) < 270:
            # 너무 짧으면 경고
            logger.warning(f"⚠️ Content too short: {len(content)} chars")
        elif len(content) > 350:
            # 너무 길면 자르기
            content = content[:347] + "..."
            
        return content
    
    def _validate_required_sentence(self, items: List[TeachingCoachItem]) -> None:
        """
        필수 문장 포함 검증 (첫 번째 항목)
        
        Args:
            items: 분석 항목들
            
        Raises:
            ValueError: 필수 문장이 없거나 잘못된 경우
        """
        if not items:
            raise ValueError("No items found for validation")
            
        first_item = items[0]
        if self.required_sentence not in first_item.content:
            logger.warning("⚠️ Required sentence not found in first item")
            # 자동 삽입 시도
            first_item.content = self._insert_required_sentence(first_item.content)
    
    def _insert_required_sentence(self, content: str) -> str:
        """
        필수 문장 자동 삽입
        
        Args:
            content: 원본 내용
            
        Returns:
            str: 필수 문장이 삽입된 내용
        """
        # 적절한 위치에 삽입
        sentences = content.split('.')
        if len(sentences) >= 3:
            # 중간 부분에 삽입
            insert_pos = len(sentences) // 2
            sentences.insert(insert_pos, self.required_sentence)
            return '.'.join(sentences)
        else:
            # 끝에 추가
            return content + ". " + self.required_sentence
    
    def _generate_summary(self, items: List[TeachingCoachItem], mode: str) -> str:
        """
        종합 분석 요약 생성
        
        Args:
            items: 분석 항목들
            mode: 분석 모드
            
        Returns:
            str: 종합 요약
        """
        positive_assessments = [
            item for item in items 
            if any(keyword in item.assessment for keyword in ["높은", "효과적", "적절"])
        ]
        
        total_evidence = sum(len(item.evidence) for item in items)
        
        summary = f"""
        {mode} 기반으로 15개 항목을 분석한 결과, 
        전체 {len(items)}개 항목 중 {len(positive_assessments)}개 항목에서 긍정적 평가를 받았습니다.
        총 {total_evidence}개의 구체적 발화 사례가 확인되었으며,
        수업의 전반적인 실행 수준은 {'우수' if len(positive_assessments) >= 10 else '보통' if len(positive_assessments) >= 7 else '개선 필요'}한 것으로 판단됩니다.
        """.strip()
        
        return summary
    
    def _extract_strengths(self, items: List[TeachingCoachItem]) -> List[str]:
        """
        강점 영역 추출
        
        Args:
            items: 분석 항목들
            
        Returns:
            List[str]: 강점 영역들
        """
        strengths = []
        
        for item in items:
            if any(keyword in item.assessment for keyword in ["높은", "효과적", "적절"]):
                strengths.append(f"{item.title}: {item.assessment}")
                
        return strengths[:5]  # 상위 5개만
    
    def _extract_improvements(self, items: List[TeachingCoachItem]) -> List[str]:
        """
        개선 영역 추출
        
        Args:
            items: 분석 항목들
            
        Returns:
            List[str]: 개선이 필요한 영역들
        """
        improvements = []
        
        for item in items:
            if any(keyword in item.assessment for keyword in ["미흡", "제한적", "부분"]):
                improvements.append(f"{item.title}: {item.assessment}")
                
        return improvements[:3]  # 상위 3개만