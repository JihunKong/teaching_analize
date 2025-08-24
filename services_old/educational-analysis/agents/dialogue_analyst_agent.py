#!/usr/bin/env python3
"""
Dialogue Analyst Agent
질문 유형과 대화 패턴의 정량적 분석 전문 에이전트
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from collections import Counter

from models.analysis_models import (
    DialoguePatternsAnalysis, QuestionTypeAnalysis, FollowupQuestionAnalysis,
    DialogueTypeAnalysis, FrequencyScale
)
from models.prompt_templates import PromptTemplates
from integrations.llm_gateway import LLMGateway
from analyzers.visualization_engine import VisualizationEngine

logger = logging.getLogger(__name__)

class DialogueAnalystAgent:
    """
    대화 패턴 분석 전문 에이전트
    
    기능:
    - 질문 유형 3종 정량 분석
    - 후속 질문 5종 빈도 계산
    - 수업대화 7종 패턴 분석
    - 7단계 빈도 구간 변환
    - 실시간 시각화 생성
    """
    
    def __init__(self, llm_gateway: LLMGateway, viz_engine: VisualizationEngine):
        self.llm_gateway = llm_gateway
        self.viz_engine = viz_engine
        
        # 분석 패턴 정의
        self.question_patterns = {
            "사실적": [
                r"무엇을?", r"언제?", r"어디서?", r"누가?", r"몇 개?", r"어떤 것?",
                r"기억나는", r"알고 있는", r"정의", r"뜻", r"의미"
            ],
            "해석적": [
                r"왜?", r"어떻게?", r"이유", r"원인", r"결과", r"관계", r"차이점", 
                r"공통점", r"느낌", r"생각", r"의견"
            ],
            "평가적": [
                r"옳은가?", r"적절한가?", r"바람직한가?", r"판단", r"평가", 
                r"비판", r"찬성", r"반대", r"우선순위"
            ]
        }
        
        self.followup_patterns = {
            "명료화": [
                r"다시 말해서", r"구체적으로", r"명확히", r"정확히",
                r"무엇을 의미", r"어떤 뜻"
            ],
            "초점화": [
                r"핵심은", r"중요한 것은", r"집중하면", r"요점은",
                r"본질적으로", r"가장 중요한"
            ],
            "정교화": [
                r"자세히", r"더 구체적으로", r"예를 들어", r"부연하면",
                r"상세히", r"세밀하게"
            ],
            "확장화": [
                r"다른 관점", r"추가로", r"또한", r"더 나아가",
                r"확장하면", r"연결하면"
            ],
            "입증화": [
                r"근거는", r"증거는", r"어떻게 알", r"확신하는 이유",
                r"뒷받침", r"입증"
            ]
        }
        
        self.dialogue_patterns = {
            "추가하기": [
                r"덧붙이면", r"추가하면", r"또한", r"더불어",
                r"보충하면", r"한 가지 더"
            ],
            "참여하기": [
                r"참여", r"함께", r"같이", r"어떻게 생각",
                r"의견", r"생각을 나누"
            ],
            "반응하기": [
                r"좋은", r"훌륭한", r"맞습니다", r"그렇습니다",
                r"동감", r"공감"
            ],
            "유보하기": [
                r"잠깐", r"잠시만", r"더 생각", r"판단 보류",
                r"확실하지", r"확신이"
            ],
            "수용하기": [
                r"받아들", r"인정", r"동의", r"찬성",
                r"옳다", r"맞다"
            ],
            "반대하기": [
                r"반대", r"다른 의견", r"그러나", r"하지만",
                r"반면", r"다르게 생각"
            ],
            "변환하기": [
                r"다시 말하면", r"바꿔 말하면", r"즉", r"다른 표현으로",
                r"재정의", r"전환"
            ]
        }
    
    async def analyze(self, transcript: str) -> DialoguePatternsAnalysis:
        """
        대화 패턴 분석 실행
        
        Args:
            transcript: 수업 전사 텍스트
            
        Returns:
            DialoguePatternsAnalysis: 정량적 대화 분석 결과
        """
        try:
            logger.info("📊 Starting dialogue patterns analysis")
            
            # 1. 발화 단위로 분리
            utterances = self._parse_utterances(transcript)
            logger.info(f"📝 Parsed {len(utterances)} utterances")
            
            # 2. 유형별 빈도 계산
            question_counts = self._count_question_types(utterances)
            followup_counts = self._count_followup_types(utterances)
            dialogue_counts = self._count_dialogue_types(utterances)
            
            # 3. 7단계 구간 변환
            question_analysis = self._create_question_analysis(question_counts)
            followup_analysis = self._create_followup_analysis(followup_counts)
            dialogue_analysis = self._create_dialogue_analysis(dialogue_counts)
            
            # 4. 시각화 생성
            chart_urls = await self._generate_visualizations(
                question_counts, followup_counts, dialogue_counts
            )
            
            # 5. 분석 요약 생성
            summary_text = self._generate_summary(
                question_counts, followup_counts, dialogue_counts
            )
            
            # 6. 지배적 패턴 추출
            dominant_patterns = self._extract_dominant_patterns(
                question_counts, followup_counts, dialogue_counts
            )
            
            result = DialoguePatternsAnalysis(
                question_types=question_analysis,
                followup_questions=followup_analysis,
                dialogue_types=dialogue_analysis,
                chart_urls=chart_urls,
                summary_text=summary_text,
                dominant_patterns=dominant_patterns
            )
            
            logger.info("✅ Dialogue patterns analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Dialogue analysis failed: {e}")
            raise
    
    def _parse_utterances(self, transcript: str) -> List[str]:
        """
        전사 텍스트를 발화 단위로 분리
        
        Args:
            transcript: 전사 텍스트
            
        Returns:
            List[str]: 발화 목록
        """
        # 발화자별 분리 (교사:, 학생:, T:, S: 등)
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
        
        # 발화자 태그가 없는 경우 문장 단위로 분리
        if not utterances:
            sentences = re.split(r'[.!?。]', clean_text)
            utterances = [s.strip() for s in sentences if s.strip()]
        
        return utterances
    
    def _count_question_types(self, utterances: List[str]) -> Dict[str, int]:
        """
        질문 유형별 빈도 계산
        
        Args:
            utterances: 발화 목록
            
        Returns:
            Dict[str, int]: 질문 유형별 개수
        """
        counts = {qtype: 0 for qtype in self.question_patterns.keys()}
        
        for utterance in utterances:
            # 질문인지 확인
            if not ('?' in utterance or '까' in utterance or '나요' in utterance):
                continue
                
            for qtype, patterns in self.question_patterns.items():
                if any(re.search(pattern, utterance, re.IGNORECASE) for pattern in patterns):
                    counts[qtype] += 1
                    break  # 첫 번째 매치만 카운트
        
        return counts
    
    def _count_followup_types(self, utterances: List[str]) -> Dict[str, int]:
        """
        후속 질문 유형별 빈도 계산
        
        Args:
            utterances: 발화 목록
            
        Returns:
            Dict[str, int]: 후속 질문 유형별 개수
        """
        counts = {ftype: 0 for ftype in self.followup_patterns.keys()}
        
        for utterance in utterances:
            for ftype, patterns in self.followup_patterns.items():
                if any(re.search(pattern, utterance, re.IGNORECASE) for pattern in patterns):
                    counts[ftype] += 1
                    break  # 첫 번째 매치만 카운트
        
        return counts
    
    def _count_dialogue_types(self, utterances: List[str]) -> Dict[str, int]:
        """
        수업대화 유형별 빈도 계산
        
        Args:
            utterances: 발화 목록
            
        Returns:
            Dict[str, int]: 대화 유형별 개수
        """
        counts = {dtype: 0 for dtype in self.dialogue_patterns.keys()}
        
        for utterance in utterances:
            for dtype, patterns in self.dialogue_patterns.items():
                if any(re.search(pattern, utterance, re.IGNORECASE) for pattern in patterns):
                    counts[dtype] += 1
                    break  # 첫 번째 매치만 카운트
        
        return counts
    
    def _create_question_analysis(self, counts: Dict[str, int]) -> QuestionTypeAnalysis:
        """질문 유형 분석 결과 생성"""
        return QuestionTypeAnalysis(
            factual=FrequencyScale(
                count=counts["사실적"],
                scale=PromptTemplates.count_to_scale(counts["사실적"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["사실적"])
                )
            ),
            interpretive=FrequencyScale(
                count=counts["해석적"],
                scale=PromptTemplates.count_to_scale(counts["해석적"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["해석적"])
                )
            ),
            evaluative=FrequencyScale(
                count=counts["평가적"],
                scale=PromptTemplates.count_to_scale(counts["평가적"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["평가적"])
                )
            )
        )
    
    def _create_followup_analysis(self, counts: Dict[str, int]) -> FollowupQuestionAnalysis:
        """후속 질문 분석 결과 생성"""
        return FollowupQuestionAnalysis(
            clarification=FrequencyScale(
                count=counts["명료화"],
                scale=PromptTemplates.count_to_scale(counts["명료화"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["명료화"])
                )
            ),
            focusing=FrequencyScale(
                count=counts["초점화"],
                scale=PromptTemplates.count_to_scale(counts["초점화"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["초점화"])
                )
            ),
            elaboration=FrequencyScale(
                count=counts["정교화"],
                scale=PromptTemplates.count_to_scale(counts["정교화"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["정교화"])
                )
            ),
            expansion=FrequencyScale(
                count=counts["확장화"],
                scale=PromptTemplates.count_to_scale(counts["확장화"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["확장화"])
                )
            ),
            verification=FrequencyScale(
                count=counts["입증화"],
                scale=PromptTemplates.count_to_scale(counts["입증화"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["입증화"])
                )
            )
        )
    
    def _create_dialogue_analysis(self, counts: Dict[str, int]) -> DialogueTypeAnalysis:
        """대화 유형 분석 결과 생성"""
        return DialogueTypeAnalysis(
            adding=FrequencyScale(
                count=counts["추가하기"],
                scale=PromptTemplates.count_to_scale(counts["추가하기"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["추가하기"])
                )
            ),
            participating=FrequencyScale(
                count=counts["참여하기"],
                scale=PromptTemplates.count_to_scale(counts["참여하기"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["참여하기"])
                )
            ),
            responding=FrequencyScale(
                count=counts["반응하기"],
                scale=PromptTemplates.count_to_scale(counts["반응하기"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["반응하기"])
                )
            ),
            reserving=FrequencyScale(
                count=counts["유보하기"],
                scale=PromptTemplates.count_to_scale(counts["유보하기"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["유보하기"])
                )
            ),
            accepting=FrequencyScale(
                count=counts["수용하기"],
                scale=PromptTemplates.count_to_scale(counts["수용하기"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["수용하기"])
                )
            ),
            opposing=FrequencyScale(
                count=counts["반대하기"],
                scale=PromptTemplates.count_to_scale(counts["반대하기"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["반대하기"])
                )
            ),
            transforming=FrequencyScale(
                count=counts["변환하기"],
                scale=PromptTemplates.count_to_scale(counts["변환하기"]),
                description=PromptTemplates.get_frequency_description(
                    PromptTemplates.count_to_scale(counts["변환하기"])
                )
            )
        )
    
    async def _generate_visualizations(
        self, 
        question_counts: Dict[str, int],
        followup_counts: Dict[str, int], 
        dialogue_counts: Dict[str, int]
    ) -> List[str]:
        """시각화 생성"""
        chart_urls = []
        
        try:
            # 질문 유형 차트
            question_chart = await self.viz_engine.create_bar_chart(
                data=question_counts,
                title="질문 유형별 빈도 분석",
                labels=list(question_counts.keys()),
                filename="question_types_chart"
            )
            chart_urls.append(question_chart)
            
            # 후속 질문 차트  
            followup_chart = await self.viz_engine.create_bar_chart(
                data=followup_counts,
                title="후속 질문 유형별 빈도 분석",
                labels=list(followup_counts.keys()),
                filename="followup_types_chart"
            )
            chart_urls.append(followup_chart)
            
            # 대화 유형 차트 (빈도순 정렬)
            sorted_dialogue = dict(sorted(dialogue_counts.items(), key=lambda x: x[1], reverse=True))
            dialogue_chart = await self.viz_engine.create_bar_chart(
                data=sorted_dialogue,
                title="수업대화 유형별 빈도 분석 (빈도순)",
                labels=list(sorted_dialogue.keys()),
                filename="dialogue_types_chart"
            )
            chart_urls.append(dialogue_chart)
            
        except Exception as e:
            logger.error(f"❌ Visualization generation failed: {e}")
            
        return chart_urls
    
    def _generate_summary(
        self,
        question_counts: Dict[str, int],
        followup_counts: Dict[str, int],
        dialogue_counts: Dict[str, int]
    ) -> str:
        """분석 요약 생성"""
        total_questions = sum(question_counts.values())
        total_followups = sum(followup_counts.values())
        total_dialogues = sum(dialogue_counts.values())
        
        # 가장 빈번한 유형들
        top_question = max(question_counts.items(), key=lambda x: x[1])
        top_followup = max(followup_counts.items(), key=lambda x: x[1])
        top_dialogue = max(dialogue_counts.items(), key=lambda x: x[1])
        
        summary = f"""
        수업 대화 패턴 분석 결과:
        
        - 총 질문 {total_questions}회 (가장 많은 유형: {top_question[0]} {top_question[1]}회)
        - 총 후속질문 {total_followups}회 (가장 많은 유형: {top_followup[0]} {top_followup[1]}회)  
        - 총 대화참여 {total_dialogues}회 (가장 많은 유형: {top_dialogue[0]} {top_dialogue[1]}회)
        
        이 수업은 {'활발한' if total_dialogues >= 20 else '적당한' if total_dialogues >= 10 else '제한적인'} 
        대화 참여와 {'다양한' if len([c for c in question_counts.values() if c > 0]) >= 2 else '단조로운'} 
        질문 유형을 보였습니다.
        """.strip()
        
        return summary
    
    def _extract_dominant_patterns(
        self,
        question_counts: Dict[str, int],
        followup_counts: Dict[str, int],
        dialogue_counts: Dict[str, int]
    ) -> List[str]:
        """지배적 패턴 추출"""
        patterns = []
        
        # 질문 패턴
        if question_counts["해석적"] > question_counts["사실적"]:
            patterns.append("해석적 질문 중심의 수업")
        elif question_counts["사실적"] > question_counts["해석적"]:
            patterns.append("사실적 질문 중심의 수업")
            
        # 대화 참여 패턴
        sorted_dialogue = sorted(dialogue_counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_dialogue[0][1] > 5:
            patterns.append(f"{sorted_dialogue[0][0]} 중심의 대화 패턴")
            
        # 후속 질문 패턴
        if followup_counts["정교화"] > 3:
            patterns.append("정교화 중심의 깊이 있는 대화")
        elif followup_counts["명료화"] > 3:
            patterns.append("명료화 중심의 이해 확인 대화")
            
        return patterns[:3]  # 상위 3개만