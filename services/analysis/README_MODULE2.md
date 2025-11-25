# Module 2: 3D Matrix Analysis Service

## 개요

교사 발화를 3차원으로 분석하는 서비스입니다:
- **시간 차원 (Stage)**: 도입 / 전개 / 정리
- **맥락 차원 (Context)**: 설명 / 질문 / 피드백 / 촉진 / 관리
- **수준 차원 (Level)**: L1 (기억/이해) / L2 (적용/분석) / L3 (종합/평가)

## 핵심 기능

### 1. 체크리스트 기반 분류
- OpenAI GPT-4o-mini 사용
- 3회 실행 후 다수결 투표로 일관성 보장
- 연구 신뢰도 95%+ 목표

### 2. Multi-label Classification
- Context는 하나의 발화가 여러 맥락을 동시에 가질 수 있음
- 예: "이 공식을 이해했나요? 어려운 부분이 있나요?" → [질문, 피드백]

### 3. 교육적 복잡도 지표
- **Cognitive Diversity**: 인지 수준 다양성 (L2, L3 비율)
- **Instructional Variety**: 수업 맥락 다양성 (Shannon entropy)
- **Progression Quality**: 단계 진행 자연스러움
- **Overall Complexity**: 전체 교육적 복잡도 (0-1)

## 디렉토리 구조

```
services/analysis/
├── checklists/
│   ├── stage_checklists.yaml       # 수업 단계 분류 체크리스트
│   ├── context_checklists.yaml     # 수업 맥락 분류 체크리스트
│   └── level_checklists.yaml       # 인지 수준 분류 체크리스트
│
├── core/
│   ├── stage_classifier.py         # Stage Classifier
│   ├── context_tagger.py           # Context Tagger (multi-label)
│   ├── level_classifier.py         # Level Classifier
│   └── matrix_builder.py           # 3D Matrix Builder
│
├── services/
│   └── openai_service.py           # OpenAI API 래퍼 (3회 다수결)
│
├── main_3d_matrix.py               # FastAPI 엔드포인트
├── requirements.txt
└── README_MODULE2.md               # 이 파일
```

## API 사용 예시

### 1. 직접 발화 리스트로 분석

```bash
curl -X POST http://localhost:8001/api/analyze/3d-matrix \
  -H "Content-Type: application/json" \
  -d '{
    "utterances": [
      {
        "id": "utt_001",
        "text": "오늘은 피타고라스 정리를 배워볼게요",
        "timestamp": "00:00:30"
      },
      {
        "id": "utt_002",
        "text": "이 공식을 사용해서 문제를 풀어보세요",
        "timestamp": "00:15:00"
      }
    ],
    "include_raw_data": false
  }'

# 응답
{
  "analysis_id": "abc123-def456-...",
  "status": "pending",
  "message": "3D matrix analysis job submitted",
  "submitted_at": "2025-11-08T21:30:00"
}
```

### 2. 전사 결과로부터 분석

```bash
curl -X POST http://localhost:8001/api/analyze/transcript/3d-matrix \
  -H "Content-Type: application/json" \
  -d '{
    "transcript_id": "xyz789-abc123-...",
    "speaker_filter": "teacher",
    "include_raw_data": false
  }'
```

### 3. 분석 상태 조회

```bash
curl http://localhost:8001/api/analyze/3d-matrix/{job_id}

# 응답 (완료 시)
{
  "job_id": "abc123-...",
  "status": "completed",
  "result": {
    "matrix": {
      "dimensions": {
        "stages": ["introduction", "development", "closing"],
        "contexts": ["explanation", "question", "feedback", "facilitation", "management"],
        "levels": ["L1", "L2", "L3"]
      },
      "data": [
        {
          "utterance_id": "utt_001",
          "stage": "introduction",
          "contexts": ["explanation"],
          "level": "L1"
        }
      ],
      "counts": {
        "introduction": {
          "explanation": {"L1": 5, "L2": 2, "L3": 0}
        }
      },
      "heatmap_data": [
        {
          "level": "L1",
          "matrix": [[5, 3, 2, 1, 0], [30, 15, 10, 8, 5], [3, 2, 1, 0, 0]],
          "total": 77
        }
      ]
    },
    "statistics": {
      "total_utterances": 100,
      "top_combinations": [
        {
          "stage": "development",
          "context": "explanation",
          "level": "L2",
          "count": 25,
          "percentage": 25.0
        }
      ],
      "educational_complexity": {
        "cognitive_diversity": 0.75,
        "instructional_variety": 0.68,
        "progression_quality": 0.82,
        "overall_complexity": 0.75
      }
    }
  }
}
```

### 4. 시각화 데이터 조회

```bash
curl http://localhost:8001/api/analyze/3d-matrix/{job_id}/visualization

# 응답
{
  "analysis_id": "abc123-...",
  "heatmap_data": [...],  # Chart.js 또는 D3.js로 렌더링
  "dimensions": {...},
  "top_combinations": [...],
  "stage_distribution": {"introduction": 15, "development": 70, "closing": 15},
  "context_distribution": {"explanation": 40, "question": 25, ...},
  "level_distribution": {"L1": 30, "L2": 50, "L3": 20},
  "educational_complexity": {...}
}
```

## 체크리스트 예시

### Stage Checklist (도입 단계)

```yaml
introduction:
  checklist:
    - id: "intro_01"
      question: "이 발화에서 오늘의 학습 목표나 주제를 명시적으로 제시하고 있습니까?"
      examples:
        positive:
          - "오늘은 이차방정식의 근의 공식에 대해 배워보겠습니다"
        negative:
          - "그러면 이 문제를 풀어볼까요?" # 전개 단계

    - id: "intro_02"
      question: "이 발화에서 이전 학습 내용을 상기시키거나 복습하고 있습니까?"
      ...
```

### Context Checklist (설명 맥락)

```yaml
explanation:
  checklist:
    - id: "exp_01"
      question: "이 발화에서 개념의 정의나 의미를 설명하고 있습니까?"
      examples:
        positive:
          - "이차방정식이란 x²항을 포함하는 방정식을 말합니다"
        negative:
          - "이차방정식이 뭐죠?" # 질문
```

## 처리 시간 예상

| 발화 수 | 예상 시간 (GPT-4o-mini) |
|---------|-------------------------|
| 10개    | 1-2분                   |
| 50개    | 5-7분                   |
| 100개   | 10-15분                 |
| 200개   | 20-30분                 |

**최적화 팁**:
- 각 발화마다 3개 차원 × 3회 실행 = 9회 API 호출
- 병렬 처리로 시간 단축 가능
- temperature=0으로 일관성 최대화

## 비용 예상 (OpenAI API)

- 체크리스트 1회 실행: ~300 토큰 (입력+출력)
- 발화 1개당: 9회 × 300 토큰 = 2,700 토큰
- 100개 발화: 270,000 토큰
- **비용**: ~$0.05-0.10 (GPT-4o-mini 기준)

## 통합 방법

### 기존 CBIL 분석과 통합

```python
# services/analysis/main.py에 추가

from main_3d_matrix import (
    analyze_3d_matrix,
    analyze_transcript_3d_matrix,
    get_matrix_analysis_status,
    get_matrix_visualization_data
)

# 라우트 추가
app.include_router(matrix_router, prefix="/api")
```

## 테스트 방법

### 1. Stage Classifier 테스트

```bash
cd /Users/jihunkong/teaching_analize/services/analysis
python -m core.stage_classifier
```

### 2. Context Tagger 테스트

```bash
python -m core.context_tagger
```

### 3. Level Classifier 테스트

```bash
python -m core.level_classifier
```

### 4. 3D Matrix Builder 테스트

```bash
python -m core.matrix_builder
```

## 환경 변수

```bash
# .env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.0
OPENAI_NUM_RUNS=3

REDIS_HOST=redis
REDIS_PORT=6379
```

## 향후 개선 사항

1. **캐싱**: 동일 발화 재분석 방지
2. **배치 처리**: 여러 발화 동시 처리로 속도 향상
3. **신뢰도 임계값**: 낮은 신뢰도 항목 재분류
4. **사용자 피드백**: 분류 결과에 대한 교정 기능
5. **다국어 지원**: 영어, 중국어 등 확장

## 참고 문서

- `checklists/stage_checklists.yaml` - Stage 분류 기준 상세
- `checklists/context_checklists.yaml` - Context 분류 기준 상세
- `checklists/level_checklists.yaml` - Level 분류 기준 상세
- `/Users/jihunkong/AI_analize/SPECIFICATION.md` - 전체 시스템 명세

---

**개발자**: 김지훈
**마지막 업데이트**: 2025-11-08
**버전**: 2.0.0-alpha
