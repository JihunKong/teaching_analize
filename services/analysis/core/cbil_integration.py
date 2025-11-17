"""
CBIL Integration - Utilities for integrating CBIL framework with Module 3
Maps CBIL 7-stage analysis to 3D Matrix dimensions
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CBILStageScore:
    """Individual CBIL stage score"""
    stage: str
    score: int  # 0-3
    max_score: int  # Always 3
    percentage: float  # score/max_score * 100
    feedback: str  # Extracted feedback text


@dataclass
class CBILAnalysisResult:
    """Parsed CBIL analysis result"""
    stage_scores: Dict[str, CBILStageScore]
    total_score: int
    max_total_score: int
    overall_percentage: float
    narrative_text: str


class CBILIntegration:
    """
    Utilities for integrating CBIL (Classroom-Based Inquiry Learning) framework
    with Module 3 evaluation system
    """

    # CBIL 7 stages (in order)
    CBIL_STAGES = [
        "engage",      # 흥미 유도 및 연결
        "focus",       # 탐구 방향 설정
        "investigate", # 자료 탐색 및 개념 형성
        "organize",    # 증거 조직화
        "generalize",  # 일반화
        "transfer",    # 전이
        "reflect"      # 성찰
    ]

    # CBIL Korean names
    CBIL_STAGE_NAMES_KR = {
        "engage": "흥미 유도 및 연결",
        "focus": "탐구 방향 설정",
        "investigate": "자료 탐색 및 개념 형성",
        "organize": "증거 조직화",
        "generalize": "일반화",
        "transfer": "전이",
        "reflect": "성찰"
    }

    # Mapping: CBIL Stage → 3D Matrix Stage(s)
    # Multiple stages can map to same matrix stage
    CBIL_TO_MATRIX_STAGE = {
        "engage": "introduction",       # High correlation
        "focus": "introduction",         # Transition to development
        "investigate": "development",    # Core learning
        "organize": "development",       # Core learning
        "generalize": "development",     # Synthesis begins
        "transfer": "closing",           # Application
        "reflect": "closing"             # Metacognition
    }

    # Optimal CBIL score ranges (based on research)
    OPTIMAL_SCORE_RANGES = {
        "engage": (2, 3),      # Should be strong
        "focus": (2, 3),       # Critical for direction
        "investigate": (2, 3), # Core of inquiry
        "organize": (1, 3),    # Can vary
        "generalize": (2, 3),  # Important for understanding
        "transfer": (1, 2),    # Often challenging
        "reflect": (1, 2)      # Often overlooked
    }

    def __init__(self):
        """Initialize CBIL integration utilities"""
        logger.info("CBILIntegration initialized")

    def parse_cbil_analysis(self, cbil_text: str) -> CBILAnalysisResult:
        """
        Parse CBIL analysis text to extract scores and feedback

        Args:
            cbil_text: Raw CBIL analysis text from Solar API

        Returns:
            CBILAnalysisResult with parsed data

        Example cbil_text format:
            #### 1. Engage
            분석 내용...
            **점수: 2점**

            #### 2. Focus
            분석 내용...
            **점수: 3점**
            ...
        """
        stage_scores = {}
        total_score = 0

        # Split by stage headers
        stage_pattern = r"####\s*\d+\.\s*(\w+)"
        score_pattern = r"\*\*점수:\s*(\d+)점\*\*"

        # Find all stages
        stage_matches = list(re.finditer(stage_pattern, cbil_text, re.IGNORECASE))

        for i, match in enumerate(stage_matches):
            stage_name_raw = match.group(1).lower()

            # Map Korean/English stage names
            stage_name = self._normalize_stage_name(stage_name_raw)

            if stage_name not in self.CBIL_STAGES:
                logger.warning(f"Unknown CBIL stage: {stage_name_raw}")
                continue

            # Extract text for this stage
            start_pos = match.end()
            end_pos = stage_matches[i + 1].start() if i + 1 < len(stage_matches) else len(cbil_text)
            stage_text = cbil_text[start_pos:end_pos]

            # Extract score
            score_match = re.search(score_pattern, stage_text)
            if score_match:
                score = int(score_match.group(1))
                total_score += score
            else:
                score = 0
                logger.warning(f"Could not find score for {stage_name}")

            # Calculate percentage
            percentage = (score / 3.0) * 100

            # Store
            stage_scores[stage_name] = CBILStageScore(
                stage=stage_name,
                score=score,
                max_score=3,
                percentage=percentage,
                feedback=stage_text.strip()
            )

        # Calculate overall
        max_total = len(self.CBIL_STAGES) * 3
        overall_percentage = (total_score / max_total) * 100 if max_total > 0 else 0

        return CBILAnalysisResult(
            stage_scores=stage_scores,
            total_score=total_score,
            max_total_score=max_total,
            overall_percentage=overall_percentage,
            narrative_text=cbil_text
        )

    def _normalize_stage_name(self, stage_name: str) -> str:
        """Normalize stage name to English lowercase"""
        # Already lowercase English
        if stage_name in self.CBIL_STAGES:
            return stage_name

        # Korean to English mapping
        kr_to_en = {
            "흥미": "engage",
            "방향": "focus",
            "탐색": "investigate",
            "조직": "organize",
            "일반": "generalize",
            "전이": "transfer",
            "성찰": "reflect"
        }

        for kr, en in kr_to_en.items():
            if kr in stage_name:
                return en

        return stage_name

    def map_cbil_to_3d_matrix(
        self,
        cbil_result: CBILAnalysisResult,
        matrix_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map CBIL stages to 3D matrix stages and analyze correlation

        Args:
            cbil_result: Parsed CBIL analysis
            matrix_data: 3D matrix result from MatrixBuilder

        Returns:
            Mapping dictionary with correlation analysis
        """
        mapping = {}
        statistics = matrix_data.get('statistics', {})
        stage_stats = statistics.get('stage_stats', {})
        stage_distribution = stage_stats.get('stage_distribution', {})

        for cbil_stage in self.CBIL_STAGES:
            matrix_stage = self.CBIL_TO_MATRIX_STAGE[cbil_stage]

            cbil_score_obj = cbil_result.stage_scores.get(cbil_stage)
            if not cbil_score_obj:
                continue

            cbil_score = cbil_score_obj.score
            cbil_percentage = cbil_score_obj.percentage

            # Get corresponding matrix stage percentage
            matrix_percentage = stage_distribution.get(matrix_stage, 0)

            mapping[cbil_stage] = {
                'cbil_score': cbil_score,
                'cbil_percentage': cbil_percentage,
                'maps_to_matrix_stage': matrix_stage,
                'matrix_stage_percentage': matrix_percentage,
                'optimal_range': self.OPTIMAL_SCORE_RANGES[cbil_stage],
                'status': self._get_stage_status(cbil_score, cbil_stage)
            }

        return mapping

    def _get_stage_status(self, score: int, stage: str) -> str:
        """Get status for CBIL stage score"""
        min_optimal, max_optimal = self.OPTIMAL_SCORE_RANGES[stage]

        if score >= min_optimal:
            return "optimal"
        elif score == min_optimal - 1:
            return "acceptable"
        else:
            return "needs_improvement"

    def calculate_cbil_alignment_score(
        self,
        cbil_result: CBILAnalysisResult,
        pattern_match: Dict[str, Any]
    ) -> float:
        """
        Calculate how well CBIL scores align with Module 3 pattern matching

        Args:
            cbil_result: Parsed CBIL analysis
            pattern_match: Pattern matching result from PatternMatcher

        Returns:
            Alignment score (0-1), where 1 is perfect alignment
        """
        pattern_name = pattern_match.get('pattern_name', '')
        similarity_score = pattern_match.get('similarity_score', 0)

        # Different patterns emphasize different CBIL stages
        pattern_stage_weights = {
            'Inquiry-Based Learning': {
                'investigate': 0.30,
                'organize': 0.20,
                'generalize': 0.20,
                'focus': 0.15,
                'engage': 0.10,
                'transfer': 0.03,
                'reflect': 0.02
            },
            'Concept Understanding': {
                'focus': 0.25,
                'investigate': 0.20,
                'organize': 0.20,
                'generalize': 0.15,
                'engage': 0.10,
                'transfer': 0.05,
                'reflect': 0.05
            },
            'Discussion-Centered': {
                'investigate': 0.25,
                'organize': 0.20,
                'reflect': 0.20,
                'engage': 0.15,
                'generalize': 0.10,
                'focus': 0.05,
                'transfer': 0.05
            },
            'Skill Training': {
                'focus': 0.25,
                'organize': 0.20,
                'transfer': 0.20,
                'investigate': 0.15,
                'engage': 0.10,
                'generalize': 0.05,
                'reflect': 0.05
            }
        }

        weights = pattern_stage_weights.get(pattern_name, {
            stage: 1.0 / 7 for stage in self.CBIL_STAGES
        })

        # Calculate weighted score alignment
        total_weighted_score = 0.0
        total_weight = 0.0

        for stage in self.CBIL_STAGES:
            weight = weights.get(stage, 0)
            cbil_score_obj = cbil_result.stage_scores.get(stage)

            if cbil_score_obj:
                normalized_score = cbil_score_obj.score / 3.0  # 0-1
                total_weighted_score += normalized_score * weight
                total_weight += weight

        cbil_weighted_avg = total_weighted_score / total_weight if total_weight > 0 else 0

        # Alignment = combination of pattern similarity and CBIL weighted average
        alignment = (similarity_score * 0.6) + (cbil_weighted_avg * 0.4)

        return max(0.0, min(1.0, alignment))

    def generate_cbil_specific_coaching(
        self,
        cbil_result: CBILAnalysisResult,
        cbil_matrix_mapping: Dict[str, Any]
    ) -> List[str]:
        """
        Generate CBIL-specific coaching recommendations

        Args:
            cbil_result: Parsed CBIL analysis
            cbil_matrix_mapping: CBIL to matrix stage mapping

        Returns:
            List of coaching recommendations
        """
        recommendations = []

        # Identify weak stages (score < 2)
        weak_stages = []
        for stage, score_obj in cbil_result.stage_scores.items():
            if score_obj.score < 2:
                weak_stages.append((stage, score_obj.score))

        # Generate recommendations for weak stages
        for stage, score in weak_stages:
            stage_kr = self.CBIL_STAGE_NAMES_KR[stage]
            mapping_info = cbil_matrix_mapping.get(stage, {})
            matrix_stage = mapping_info.get('maps_to_matrix_stage', '')

            if stage == 'engage':
                recommendations.append(
                    f"**{stage_kr} 단계 강화 필요** (현재: {score}/3점)\n"
                    f"  - 실생활과 연계된 질문으로 수업을 시작하세요\n"
                    f"  - 학생들의 사전 경험을 공유하도록 유도하세요\n"
                    f"  - 개념에 대한 호기심을 자극하는 활동을 추가하세요"
                )

            elif stage == 'focus':
                recommendations.append(
                    f"**{stage_kr} 단계 강화 필요** (현재: {score}/3점)\n"
                    f"  - 명확한 탐구 질문을 제시하세요\n"
                    f"  - 학습 목표를 학생 관점에서 구체화하세요\n"
                    f"  - 탐구 방향을 학생들과 함께 설정하세요"
                )

            elif stage == 'investigate':
                recommendations.append(
                    f"**{stage_kr} 단계 강화 필요** (현재: {score}/3점)\n"
                    f"  - 학생들이 자료를 직접 탐색할 기회를 늘리세요\n"
                    f"  - 개방형 질문으로 사고를 촉진하세요\n"
                    f"  - 다양한 자료와 관점을 제공하세요"
                )

            elif stage == 'organize':
                recommendations.append(
                    f"**{stage_kr} 단계 강화 필요** (현재: {score}/3점)\n"
                    f"  - 증거를 정리하고 분류하는 활동을 추가하세요\n"
                    f"  - 그래프, 표, 다이어그램 활용을 지도하세요\n"
                    f"  - 패턴과 관계를 찾도록 안내하세요"
                )

            elif stage == 'generalize':
                recommendations.append(
                    f"**{stage_kr} 단계 강화 필요** (현재: {score}/3점)\n"
                    f"  - 개별 사례에서 일반 원리를 도출하도록 유도하세요\n"
                    f"  - '항상 그럴까?', '다른 경우에도 적용될까?' 질문하세요\n"
                    f"  - 학생들이 자신의 말로 개념을 정의하게 하세요"
                )

            elif stage == 'transfer':
                recommendations.append(
                    f"**{stage_kr} 단계 강화 필요** (현재: {score}/3점)\n"
                    f"  - 새로운 상황에 적용하는 과제를 제공하세요\n"
                    f"  - 다른 교과나 실생활과의 연결을 탐색하세요\n"
                    f"  - 창의적 문제해결 기회를 제공하세요"
                )

            elif stage == 'reflect':
                recommendations.append(
                    f"**{stage_kr} 단계 강화 필요** (현재: {score}/3점)\n"
                    f"  - 학습 과정을 되돌아보는 시간을 충분히 확보하세요\n"
                    f"  - '무엇을 배웠나?', '어떻게 배웠나?' 질문하세요\n"
                    f"  - 어려웠던 점과 해결 전략을 공유하세요"
                )

        # Add overall CBIL improvement suggestion
        if cbil_result.overall_percentage < 60:
            recommendations.append(
                f"**전체 CBIL 점수 향상 필요** ({cbil_result.total_score}/{cbil_result.max_total_score}점, "
                f"{cbil_result.overall_percentage:.1f}%)\n"
                f"  - CBIL 프레임워크의 각 단계를 의도적으로 설계하세요\n"
                f"  - 학생 중심의 탐구 활동을 늘리세요\n"
                f"  - 각 단계가 자연스럽게 연결되도록 수업을 구성하세요"
            )

        if not recommendations:
            recommendations.append(
                f"**CBIL 프레임워크 실행이 우수합니다!** ({cbil_result.total_score}/{cbil_result.max_total_score}점)\n"
                f"  - 현재의 우수한 실행을 유지하세요"
            )

        return recommendations

    def to_dict(self, cbil_result: CBILAnalysisResult) -> Dict[str, Any]:
        """Convert CBILAnalysisResult to dictionary"""
        return {
            'stage_scores': {
                stage: {
                    'score': score_obj.score,
                    'max_score': score_obj.max_score,
                    'percentage': score_obj.percentage,
                    'feedback': score_obj.feedback
                }
                for stage, score_obj in cbil_result.stage_scores.items()
            },
            'total_score': cbil_result.total_score,
            'max_total_score': cbil_result.max_total_score,
            'overall_percentage': cbil_result.overall_percentage,
            'narrative_text': cbil_result.narrative_text
        }


# ============ Demo/Test Code ============

if __name__ == "__main__":
    print("=" * 60)
    print("CBIL Integration Demo")
    print("=" * 60)

    # Mock CBIL analysis text
    mock_cbil_text = """
#### 1. Engage (흥미 유도 및 연결)

교사가 실생활 예시를 활용하여 학생들의 흥미를 유발하고 있습니다.

**점수: 2점**

#### 2. Focus (탐구 방향 설정)

명확한 탐구 질문을 제시하고 있습니다.

**점수: 3점**

#### 3. Investigate (자료 탐색 및 개념 형성)

학생들이 자료를 탐색할 기회가 부족합니다.

**점수: 1점**

#### 4. Organize (증거 조직화)

증거 조직화 활동이 거의 없습니다.

**점수: 1점**

#### 5. Generalize (일반화)

일반화 과정이 부족합니다.

**점수: 1점**

#### 6. Transfer (전이)

다른 상황으로의 전이 활동이 있습니다.

**점수: 2점**

#### 7. Reflect (성찰)

성찰 시간이 충분합니다.

**점수: 2점**
    """

    integrator = CBILIntegration()
    print("\nParsing CBIL analysis...")

    cbil_result = integrator.parse_cbil_analysis(mock_cbil_text)

    print(f"\nTotal Score: {cbil_result.total_score}/{cbil_result.max_total_score} ({cbil_result.overall_percentage:.1f}%)")
    print("\nStage Scores:")
    for stage in integrator.CBIL_STAGES:
        if stage in cbil_result.stage_scores:
            score_obj = cbil_result.stage_scores[stage]
            print(f"  {stage:12s}: {score_obj.score}/3 ({score_obj.percentage:.0f}%) - {integrator.CBIL_STAGE_NAMES_KR[stage]}")

    # Mock pattern match
    mock_pattern_match = {
        'pattern_name': 'Inquiry-Based Learning',
        'similarity_score': 0.75
    }

    alignment = integrator.calculate_cbil_alignment_score(cbil_result, mock_pattern_match)
    print(f"\nCBIL-Pattern Alignment: {alignment:.3f}")

    # Mock matrix data
    mock_matrix_data = {
        'statistics': {
            'stage_stats': {
                'stage_distribution': {
                    'introduction': 15,
                    'development': 70,
                    'closing': 15
                }
            }
        }
    }

    mapping = integrator.map_cbil_to_3d_matrix(cbil_result, mock_matrix_data)
    print("\nCBIL to Matrix Mapping:")
    for stage, info in mapping.items():
        print(f"  {stage:12s} → {info['maps_to_matrix_stage']:12s} (status: {info['status']})")

    recommendations = integrator.generate_cbil_specific_coaching(cbil_result, mapping)
    print("\nCBIL-Specific Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec}")

    print("\n" + "=" * 60)
    print("CBIL Integration Demo Complete!")
    print("=" * 60)
