"""
Test Diagnostic Report Integration
Quick test to verify Diagnostic report generator works with real analysis data structure
"""

from diagnostic_report_generator import DiagnosticReportGenerator

# Create generator
generator = DiagnosticReportGenerator()

# Mock comprehensive analysis result
mock_analysis_data = {
    "analysis_id": "test_integration_001",
    "framework": "cbil_comprehensive",
    "quantitative_metrics": {
        "dev_time_ratio": {
            "value": 0.72,
            "normalized_score": 88.5,
            "status": "optimal"
        },
        "context_diversity": {
            "value": 1.65,
            "normalized_score": 85.0,
            "status": "optimal"
        },
        "avg_cognitive_level": {
            "value": 2.15,
            "normalized_score": 82.0,
            "status": "optimal"
        },
        "question_ratio": {
            "value": 0.28,
            "normalized_score": 79.0,
            "status": "optimal"
        },
        "feedback_ratio": {
            "value": 0.22,
            "normalized_score": 76.5,
            "status": "good"
        },
        "higher_order_ratio": {
            "value": 0.35,
            "normalized_score": 84.0,
            "status": "optimal"
        },
        "cognitive_progression": {
            "value": 0.68,
            "normalized_score": 81.0,
            "status": "optimal"
        }
    },
    "matrix_analysis": {
        "statistics": {
            "total_utterances": 120,
            "stage_stats": {
                "stage_distribution": {
                    "introduction": 12.5,
                    "development": 72.0,
                    "closing": 15.5
                }
            },
            "context_stats": {
                "context_distribution": {
                    "explanation": 38.0,
                    "question": 28.0,
                    "feedback": 22.0,
                    "facilitation": 8.0,
                    "management": 4.0
                }
            },
            "level_stats": {
                "level_distribution": {
                    "L1": 35.0,
                    "L2": 45.0,
                    "L3": 20.0
                }
            }
        }
    },
    "pattern_matching": {
        "best_match": {
            "pattern_name": "균형잡힌 촉진자",
            "pattern_description": "전개 단계 중심, 다양한 맥락 활용",
            "similarity_score": 0.87
        },
        "all_pattern_similarities": [
            {"pattern_name": "균형잡힌 촉진자", "similarity": 0.87},
            {"pattern_name": "질문 중심 탐구자", "similarity": 0.72},
            {"pattern_name": "체계적 설명자", "similarity": 0.68},
            {"pattern_name": "피드백 강화형", "similarity": 0.65},
            {"pattern_name": "학습자 중심 촉진자", "similarity": 0.61}
        ]
    },
    "coaching_feedback": {
        "overall_assessment": "이 수업은 전반적으로 우수한 교수 전략을 보여줍니다. 전개 단계 중심의 균형잡힌 시간 배분과 높은 맥락 다양성이 돋보입니다.",
        "strengths": [
            "전개 단계 시간 배분이 최적 범위(70-75%) 내에 있어 학습 내용 전달이 충분합니다",
            "맥락 다양성이 높아(1.65) 설명, 질문, 피드백의 균형이 우수합니다",
            "고차원적 사고를 촉진하는 질문이 35%로 높은 수준입니다"
        ],
        "areas_for_growth": [
            "정리 단계 시간 확보 필요 - 현재 15.5%로 학습 정리가 다소 부족할 수 있습니다",
            "피드백 비율 증가 권장 - 22%에서 25% 이상으로 높이면 학습 효과가 증대됩니다",
            "L3 인지 수준 비율 향상 - 20%에서 25% 이상으로 높여 평가/창조 활동을 강화하세요"
        ],
        "priority_actions": [
            "정리 단계를 최소 10% 이상 확보하기 - 수업 마지막 10분을 핵심 내용 요약에 할애",
            "학생 응답 후 즉각적 피드백 제공하기 - 'IRF 패턴'을 의식적으로 활용",
            "고차원 질문 비율 유지하기 - 분석/평가 질문을 지속적으로 제기",
            "학습자 중심 활동 시간 늘리기 - 교사 설명 비중을 줄이고 학생 탐구 시간 확대",
            "인지 수준 단계적 상승 유도 - L1→L2→L3로 자연스럽게 전환하는 발문 설계"
        ]
    }
}

# Test
print("=" * 60)
print("Diagnostic Report Integration Test")
print("=" * 60)

overall_score = generator.calculate_overall_score(mock_analysis_data["quantitative_metrics"])
print(f"\nOverall Score: {overall_score:.1f}/100")

try:
    html_report = generator.generate_html_report(mock_analysis_data)
    print(f"✓ Report generated: {len(html_report):,} characters")
    
    with open("test_diagnostic_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("✓ Saved to: test_diagnostic_report.html")
    print("\nTest PASSED!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
