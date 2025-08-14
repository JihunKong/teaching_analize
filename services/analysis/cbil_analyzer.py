import logging
from typing import Dict, List, Any, Tuple
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CBILFeatures:
    """Features extracted from utterance for CBIL classification"""
    question_type: str  # yes_no, what, why, how, etc.
    cognitive_verbs: List[str]  # 설명하다, 비교하다, 평가하다, etc.
    complexity_score: float  # 0-1 score based on sentence complexity
    requires_reasoning: bool
    requires_creativity: bool
    requires_evaluation: bool
    keyword_count: int
    sentence_length: int

class CBILAnalyzer:
    """CBIL (Cognitive Burden of Instructional Language) Analyzer for Korean text"""
    
    def __init__(self):
        # Korean cognitive verb patterns by CBIL level
        self.level_1_patterns = [
            "맞아", "아니야", "네", "예", "응",
            "확인", "보세요", "따라", "반복"
        ]
        
        self.level_2_patterns = [
            "기억", "말해", "써", "읽어", "찾아",
            "무엇", "언제", "어디", "누가"
        ]
        
        self.level_3_patterns = [
            "설명", "정의", "의미", "뜻",
            "개념", "원리", "이유", "때문"
        ]
        
        self.level_4_patterns = [
            "비교", "차이", "공통점", "분류",
            "관계", "연결", "분석", "구분"
        ]
        
        self.level_5_patterns = [
            "종합", "정리", "요약", "통합",
            "전체", "관점", "입장", "결론"
        ]
        
        self.level_6_patterns = [
            "평가", "판단", "비판", "장단점",
            "효과", "영향", "중요", "가치"
        ]
        
        self.level_7_patterns = [
            "창의", "새로운", "만약", "상상",
            "적용", "활용", "개발", "설계",
            "제안", "해결"
        ]
        
        # Question word patterns
        self.question_patterns = {
            "yes_no": ["맞나요", "있나요", "했나요", "될까요", "일까요"],
            "what": ["무엇", "뭐", "어떤", "어느"],
            "why": ["왜", "어째서", "이유", "때문"],
            "how": ["어떻게", "방법", "방식"],
            "evaluate": ["어떤지", "평가", "생각"],
            "create": ["만들", "새로", "창작", "설계"]
        }
    
    def analyze_utterance(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze a single utterance and classify its CBIL level
        
        Args:
            text: The utterance text to analyze
            context: Optional context (previous utterances, subject, etc.)
            
        Returns:
            Analysis result with CBIL level and reasoning
        """
        # Extract features
        features = self.extract_features(text)
        
        # Classify CBIL level
        level, confidence = self.classify_level(features, text)
        
        # Generate reasoning
        reasoning = self.generate_reasoning(level, features, text)
        
        # Extract keywords
        keywords = self.extract_keywords(text)
        
        return {
            "text": text,
            "cbil_level": level,
            "confidence": confidence,
            "reasoning": reasoning,
            "features": features.__dict__,
            "keywords": keywords
        }
    
    def extract_features(self, text: str) -> CBILFeatures:
        """Extract linguistic features from text"""
        # Determine question type
        question_type = self._detect_question_type(text)
        
        # Extract cognitive verbs
        cognitive_verbs = self._extract_cognitive_verbs(text)
        
        # Calculate complexity
        complexity_score = self._calculate_complexity(text)
        
        # Check for higher-order thinking indicators
        requires_reasoning = any(word in text for word in ["왜", "이유", "원인", "결과"])
        requires_creativity = any(word in text for word in ["만약", "상상", "새로", "창의"])
        requires_evaluation = any(word in text for word in ["평가", "판단", "비판", "생각"])
        
        # Basic metrics
        keyword_count = len(self.extract_keywords(text))
        sentence_length = len(text.split())
        
        return CBILFeatures(
            question_type=question_type,
            cognitive_verbs=cognitive_verbs,
            complexity_score=complexity_score,
            requires_reasoning=requires_reasoning,
            requires_creativity=requires_creativity,
            requires_evaluation=requires_evaluation,
            keyword_count=keyword_count,
            sentence_length=sentence_length
        )
    
    def classify_level(self, features: CBILFeatures, text: str) -> Tuple[int, float]:
        """
        Classify CBIL level based on features
        
        Returns:
            Tuple of (level, confidence)
        """
        scores = {i: 0.0 for i in range(1, 8)}
        
        # Level 1: Simple confirmation
        if features.question_type == "yes_no" or features.sentence_length < 5:
            scores[1] += 0.7
        if any(pattern in text for pattern in self.level_1_patterns):
            scores[1] += 0.3
            
        # Level 2: Fact recall
        if features.question_type == "what" and not features.requires_reasoning:
            scores[2] += 0.6
        if any(pattern in text for pattern in self.level_2_patterns):
            scores[2] += 0.4
            
        # Level 3: Concept explanation
        if "설명" in features.cognitive_verbs or "정의" in features.cognitive_verbs:
            scores[3] += 0.7
        if any(pattern in text for pattern in self.level_3_patterns):
            scores[3] += 0.3
            
        # Level 4: Analytical thinking
        if features.requires_reasoning and features.complexity_score > 0.5:
            scores[4] += 0.6
        if any(pattern in text for pattern in self.level_4_patterns):
            scores[4] += 0.4
            
        # Level 5: Comprehensive understanding
        if features.keyword_count > 3 and features.complexity_score > 0.6:
            scores[5] += 0.5
        if any(pattern in text for pattern in self.level_5_patterns):
            scores[5] += 0.5
            
        # Level 6: Evaluative judgment
        if features.requires_evaluation:
            scores[6] += 0.7
        if any(pattern in text for pattern in self.level_6_patterns):
            scores[6] += 0.3
            
        # Level 7: Creative application
        if features.requires_creativity:
            scores[7] += 0.7
        if any(pattern in text for pattern in self.level_7_patterns):
            scores[7] += 0.3
        
        # Get level with highest score
        max_level = max(scores, key=scores.get)
        confidence = min(scores[max_level], 1.0)
        
        # If confidence is too low, default to level 2
        if confidence < 0.3:
            max_level = 2
            confidence = 0.5
        
        return max_level, confidence
    
    def generate_reasoning(self, level: int, features: CBILFeatures, text: str) -> str:
        """Generate explanation for the classification"""
        reasoning_templates = {
            1: "단순한 확인이나 예/아니오 응답을 요구하는 발화입니다.",
            2: "학습한 사실이나 정보를 기억하여 답하도록 요구하는 발화입니다.",
            3: "개념이나 원리에 대한 설명을 요구하는 발화입니다.",
            4: "비교, 분석, 관계 파악 등 분석적 사고를 요구하는 발화입니다.",
            5: "여러 개념을 종합하여 전체적인 이해를 요구하는 발화입니다.",
            6: "비판적 사고와 평가적 판단을 요구하는 발화입니다.",
            7: "창의적 사고와 새로운 상황에의 적용을 요구하는 발화입니다."
        }
        
        base_reasoning = reasoning_templates.get(level, "분류 기준에 따른 판단입니다.")
        
        # Add specific feature mentions
        if features.cognitive_verbs:
            verbs = ", ".join(features.cognitive_verbs[:3])
            base_reasoning += f" 주요 인지 동사: {verbs}."
        
        if features.requires_reasoning:
            base_reasoning += " 추론적 사고를 요구합니다."
        
        if features.requires_creativity:
            base_reasoning += " 창의적 사고를 요구합니다."
        
        return base_reasoning
    
    def _detect_question_type(self, text: str) -> str:
        """Detect the type of question"""
        for q_type, patterns in self.question_patterns.items():
            if any(pattern in text for pattern in patterns):
                return q_type
        
        # Check if it's a question at all
        if text.strip().endswith("?") or any(q in text for q in ["까", "니", "나요"]):
            return "other_question"
        
        return "statement"
    
    def _extract_cognitive_verbs(self, text: str) -> List[str]:
        """Extract cognitive verbs from text"""
        cognitive_verbs = []
        
        verb_patterns = [
            "설명", "비교", "분석", "평가", "판단",
            "생각", "추론", "정리", "요약", "적용",
            "창작", "개발", "분류", "구분", "연결"
        ]
        
        for verb in verb_patterns:
            if verb in text:
                cognitive_verbs.append(verb)
        
        return cognitive_verbs
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-1)"""
        # Simple heuristic based on length and structure
        words = text.split()
        word_count = len(words)
        
        # Check for complex sentence structures
        has_conjunction = any(conj in text for conj in ["그리고", "하지만", "그러나", "따라서", "그래서"])
        has_dependent_clause = any(marker in text for marker in ["면", "때", "는데", "지만"])
        
        # Calculate score
        length_score = min(word_count / 20, 1.0)  # Normalize by 20 words
        structure_score = (0.3 if has_conjunction else 0) + (0.3 if has_dependent_clause else 0)
        
        return min(length_score * 0.6 + structure_score, 1.0)
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction (can be enhanced with Korean NLP)
        keywords = []
        
        # Academic/cognitive keywords
        important_patterns = [
            "개념", "원리", "이유", "결과", "원인",
            "차이", "공통점", "특징", "방법", "과정",
            "중요", "핵심", "의미", "목적", "기능"
        ]
        
        for pattern in important_patterns:
            if pattern in text:
                keywords.append(pattern)
        
        return keywords
    
    def analyze_batch(self, utterances: List[str], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Analyze multiple utterances"""
        results = []
        
        for i, utterance in enumerate(utterances):
            # Add previous utterances as context
            utterance_context = context or {}
            if i > 0:
                utterance_context["previous_utterance"] = utterances[i-1]
            
            result = self.analyze_utterance(utterance, utterance_context)
            result["utterance_number"] = i + 1
            results.append(result)
        
        return results