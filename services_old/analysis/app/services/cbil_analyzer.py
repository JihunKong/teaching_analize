from typing import List, Dict, Any, Optional, Tuple
import re
import logging
from dataclasses import dataclass
from enum import Enum

from ..models import CBILLevel, CBILAnalysis, Utterance
from .solar_llm import SolarLLMService

logger = logging.getLogger(__name__)

@dataclass
class CBILFeatures:
    """Features extracted from utterance for CBIL classification"""
    word_count: int
    sentence_count: int
    question_words: List[str]
    comparison_words: List[str]
    reasoning_words: List[str]
    creative_words: List[str]
    has_evidence: bool
    has_examples: bool
    complexity_score: float

class CBILAnalyzer:
    """
    CBIL 7-level analyzer for Korean classroom discourse
    """
    
    def __init__(self):
        self.solar_service = SolarLLMService()
        
        # Korean keyword patterns for each level
        self.level_patterns = {
            1: {
                "keywords": ["네", "아니오", "예", "아니요", "맞아요", "틀려요", "응", "어"],
                "max_words": 5,
                "patterns": [r"^(네|아니오|예|아니요|맞아요|틀려요)\.?$"]
            },
            2: {
                "keywords": ["입니다", "이에요", "예요", "있어요", "없어요"],
                "word_range": (5, 15),
                "patterns": [r".+(입니다|이에요|예요)\.?$", r"^.+는\s+.+(입니다|이에요)"]
            },
            3: {
                "keywords": ["즉", "다시 말하면", "의미는", "뜻은", "설명하면"],
                "word_range": (15, 30),
                "patterns": [r"(즉|다시 말하면|쉽게 말하면)"]
            },
            4: {
                "keywords": ["비교하면", "차이점은", "공통점은", "반면에", "그러나", "하지만"],
                "indicators": ["comparison", "classification", "analysis"],
                "patterns": [r"(비교|차이|공통|대조|분류)"]
            },
            5: {
                "keywords": ["따라서", "그러므로", "결과적으로", "종합하면", "전체적으로"],
                "indicators": ["synthesis", "integration", "causation"],
                "patterns": [r"(따라서|그러므로|결과적으로|종합하면)"]
            },
            6: {
                "keywords": ["왜냐하면", "근거는", "이유는", "판단하건대", "평가하면"],
                "indicators": ["evaluation", "judgment", "critique"],
                "patterns": [r"(왜냐하면|근거|증거|판단|평가)"]
            },
            7: {
                "keywords": ["만약", "새로운", "창의적", "제안", "개선", "혁신적"],
                "indicators": ["creativity", "innovation", "novel_application"],
                "patterns": [r"(만약|새로운|창의|혁신|제안)"]
            }
        }
        
        # Question words in Korean
        self.question_words = [
            "무엇", "뭐", "누가", "누구", "언제", "어디", "어떻게", 
            "왜", "얼마나", "어느", "어떤"
        ]
        
        # Reasoning indicators
        self.reasoning_indicators = [
            "왜냐하면", "이유는", "때문에", "따라서", "그러므로",
            "결과적으로", "근거로", "증거는"
        ]
        
        # Comparison indicators
        self.comparison_indicators = [
            "비교", "대조", "차이", "공통", "반면", "그러나",
            "하지만", "같은", "다른", "비슷한"
        ]
        
        # Creative indicators
        self.creative_indicators = [
            "새로운", "창의적", "혁신", "독특한", "참신한",
            "만약", "가정", "제안", "개선"
        ]
    
    async def analyze_utterance(
        self,
        utterance: str,
        context: Optional[List[str]] = None,
        use_llm: bool = True
    ) -> CBILAnalysis:
        """
        Analyze a single utterance for CBIL level
        
        Args:
            utterance: The utterance to analyze
            context: Previous/next utterances for context
            use_llm: Whether to use LLM for analysis
            
        Returns:
            CBILAnalysis object with level and details
        """
        try:
            # Extract features
            features = self._extract_features(utterance)
            
            # Rule-based initial classification
            rule_based_level = self._classify_with_rules(utterance, features)
            
            # If LLM is enabled, get LLM classification
            if use_llm:
                llm_result = await self.solar_service.classify_cbil(
                    utterance, 
                    context
                )
                
                # Combine rule-based and LLM results
                final_level = self._combine_classifications(
                    rule_based_level,
                    llm_result.get("level", rule_based_level),
                    features
                )
                
                reasoning = llm_result.get("reasoning", "")
                keywords = llm_result.get("keywords", [])
                confidence = llm_result.get("confidence", 0.5)
            else:
                final_level = rule_based_level
                reasoning = self._generate_reasoning(final_level, features)
                keywords = self._extract_keywords(utterance)
                confidence = self._calculate_confidence(final_level, features)
            
            return CBILAnalysis(
                utterance_id=0,  # Will be set by caller
                text=utterance,
                cbil_level=CBILLevel(final_level),
                confidence=confidence,
                reasoning=reasoning,
                keywords=keywords,
                context_considered=context is not None
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze utterance: {str(e)}")
            # Return default low-confidence result
            return CBILAnalysis(
                utterance_id=0,
                text=utterance,
                cbil_level=CBILLevel.SIMPLE_CONFIRMATION,
                confidence=0.3,
                reasoning="Analysis failed, defaulting to level 1",
                keywords=[],
                context_considered=False
            )
    
    def _extract_features(self, utterance: str) -> CBILFeatures:
        """Extract linguistic features from utterance"""
        # Clean text
        text = utterance.strip()
        
        # Count words (Korean word segmentation is complex, using simple space split)
        words = text.split()
        word_count = len(words)
        
        # Count sentences (Korean uses different punctuation)
        sentence_count = len(re.split(r'[.!?。！？]', text))
        
        # Find question words
        question_words = [w for w in self.question_words if w in text]
        
        # Find comparison words
        comparison_words = [w for w in self.comparison_indicators if w in text]
        
        # Find reasoning words
        reasoning_words = [w for w in self.reasoning_indicators if w in text]
        
        # Find creative words
        creative_words = [w for w in self.creative_indicators if w in text]
        
        # Check for evidence/examples
        has_evidence = any(marker in text for marker in ["예를 들어", "예시", "증거", "사례"])
        has_examples = any(marker in text for marker in ["예를 들면", "예컨대", "가령"])
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(text, word_count)
        
        return CBILFeatures(
            word_count=word_count,
            sentence_count=sentence_count,
            question_words=question_words,
            comparison_words=comparison_words,
            reasoning_words=reasoning_words,
            creative_words=creative_words,
            has_evidence=has_evidence,
            has_examples=has_examples,
            complexity_score=complexity_score
        )
    
    def _classify_with_rules(self, utterance: str, features: CBILFeatures) -> int:
        """Rule-based CBIL classification"""
        text = utterance.strip()
        
        # Level 1: Simple confirmation
        if features.word_count <= 5:
            for pattern in self.level_patterns[1]["patterns"]:
                if re.match(pattern, text):
                    return 1
            if any(keyword in text for keyword in self.level_patterns[1]["keywords"]):
                return 1
        
        # Level 2: Fact recall
        if 5 < features.word_count <= 15:
            if any(keyword in text for keyword in self.level_patterns[2]["keywords"]):
                if not features.reasoning_words and not features.comparison_words:
                    return 2
        
        # Level 3: Concept explanation
        if 15 < features.word_count <= 30:
            if any(keyword in text for keyword in self.level_patterns[3]["keywords"]):
                return 3
            if features.has_examples:
                return 3
        
        # Level 4: Analytical thinking
        if features.comparison_words:
            return 4
        
        # Level 5: Comprehensive understanding
        if features.reasoning_words and features.word_count > 30:
            if any(keyword in text for keyword in self.level_patterns[5]["keywords"]):
                return 5
        
        # Level 6: Evaluative judgment
        if features.has_evidence or (features.reasoning_words and features.complexity_score > 0.7):
            return 6
        
        # Level 7: Creative application
        if features.creative_words and features.complexity_score > 0.8:
            return 7
        
        # Default based on word count
        if features.word_count <= 5:
            return 1
        elif features.word_count <= 15:
            return 2
        elif features.word_count <= 30:
            return 3
        else:
            return 4
    
    def _combine_classifications(
        self,
        rule_based: int,
        llm_based: int,
        features: CBILFeatures
    ) -> int:
        """Combine rule-based and LLM classifications"""
        # If they agree, use that level
        if rule_based == llm_based:
            return rule_based
        
        # If close (within 1 level), average and round
        if abs(rule_based - llm_based) == 1:
            return round((rule_based + llm_based) / 2)
        
        # If very different, trust LLM more for complex utterances
        if features.complexity_score > 0.7:
            return llm_based
        
        # For simple utterances, trust rules more
        if features.word_count < 20:
            return rule_based
        
        # Default to LLM
        return llm_based
    
    def _calculate_complexity(self, text: str, word_count: int) -> float:
        """Calculate linguistic complexity score (0-1)"""
        if word_count == 0:
            return 0.0
        
        # Factors for complexity
        factors = []
        
        # Length factor
        length_score = min(word_count / 50, 1.0)
        factors.append(length_score)
        
        # Conjunction usage
        conjunctions = ["그리고", "그러나", "하지만", "그래서", "따라서", "그러므로"]
        conjunction_score = min(sum(1 for c in conjunctions if c in text) / 3, 1.0)
        factors.append(conjunction_score)
        
        # Subordinate clause indicators
        subordinate_markers = ["때문에", "므로", "면서", "도록", "듯이"]
        subordinate_score = min(sum(1 for m in subordinate_markers if m in text) / 2, 1.0)
        factors.append(subordinate_score)
        
        # Academic vocabulary (simplified check)
        academic_words = ["분석", "종합", "평가", "비교", "대조", "추론", "가설", "이론"]
        academic_score = min(sum(1 for w in academic_words if w in text) / 3, 1.0)
        factors.append(academic_score)
        
        # Average all factors
        return sum(factors) / len(factors)
    
    def _generate_reasoning(self, level: int, features: CBILFeatures) -> str:
        """Generate reasoning for classification"""
        reasoning_templates = {
            1: f"단순 응답 ({features.word_count}단어)",
            2: f"사실 진술 ({features.word_count}단어, 단순 정보 제공)",
            3: f"개념 설명 ({features.word_count}단어, {'예시 포함' if features.has_examples else '재구성'})",
            4: f"분석적 사고 (비교/대조 표현 {len(features.comparison_words)}개)",
            5: f"종합적 이해 (인과관계 표현 {len(features.reasoning_words)}개)",
            6: f"평가적 판단 ({'증거 제시' if features.has_evidence else '비판적 사고'})",
            7: f"창의적 적용 (창의적 표현 {len(features.creative_words)}개)"
        }
        
        return reasoning_templates.get(level, "분류 기준 미상")
    
    def _extract_keywords(self, utterance: str) -> List[str]:
        """Extract key words from utterance"""
        # Simple keyword extraction (can be enhanced with NLP libraries)
        keywords = []
        
        # Add question words
        for qw in self.question_words:
            if qw in utterance:
                keywords.append(qw)
        
        # Add reasoning indicators
        for ri in self.reasoning_indicators:
            if ri in utterance:
                keywords.append(ri)
        
        # Add comparison indicators
        for ci in self.comparison_indicators:
            if ci in utterance:
                keywords.append(ci)
        
        return keywords[:5]  # Limit to 5 keywords
    
    def _calculate_confidence(self, level: int, features: CBILFeatures) -> float:
        """Calculate confidence score for classification"""
        base_confidence = 0.5
        
        # Adjust based on word count appropriateness
        if level == 1 and features.word_count <= 5:
            base_confidence += 0.3
        elif level == 2 and 5 < features.word_count <= 15:
            base_confidence += 0.2
        elif level == 3 and 15 < features.word_count <= 30:
            base_confidence += 0.2
        elif level >= 4 and features.word_count > 30:
            base_confidence += 0.1
        
        # Adjust based on keyword presence
        if level == 4 and features.comparison_words:
            base_confidence += 0.2
        elif level == 5 and features.reasoning_words:
            base_confidence += 0.2
        elif level == 6 and features.has_evidence:
            base_confidence += 0.2
        elif level == 7 and features.creative_words:
            base_confidence += 0.2
        
        return min(base_confidence, 0.95)