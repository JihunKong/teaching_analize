# AIBOA 종합 분석 프레임워크 명세서
## Comprehensive Analysis Framework Specifications

### 개요 (Overview)
이 문서는 AIBOA 플랫폼의 13개 분석 프레임워크 전체 명세를 제공합니다. 기존 CBIL 프레임워크에 12개의 추가 프레임워크를 설계하여 교육 효과성을 다각도로 분석할 수 있도록 합니다.

**핵심 설계 원칙:**
- Temperature 0.3으로 일관된 결과 보장
- 병렬 실행으로 13개 프레임워크 동시 분석
- 토글 기반 UI로 프레임워크 간 비교 용이
- 구조화된 데이터 출력으로 차트/시각화 지원
- TypeScript 인터페이스로 타입 안전성 보장

---

## 1. CBIL (Cognitive Burden of Instructional Language) - 기존
**프레임워크 ID:** `cbil`
**상태:** ✅ 구현 완료

### 기본 정보
- **한국어명:** 인지적 부담 기반 교육언어 분석
- **영어명:** Cognitive Burden of Instructional Language Analysis
- **목적:** 교육 언어의 인지적 복잡성 7단계 분류
- **분석 범위:** 발화별 인지부하 수준 측정

---

## 2. QTA (Question Type Analysis) - 신규 프레임워크 1
**프레임워크 ID:** `qta`

### 기본 정보
- **한국어명:** 질문 유형 분석
- **영어명:** Question Type Analysis
- **목적:** 교사 질문의 유형과 패턴을 분석하여 학습자 참여도 향상 방안 제시
- **분석 범위:** 질문 형태, 인지 수준, 응답 유도 방식

### 분석 카테고리 (7단계)
1. **폐쇄형 질문 (Closed Questions)** - 단답형 응답
   - 예시: "이것이 맞나요?", "몇 개인가요?"
   
2. **개방형 질문 (Open Questions)** - 다양한 응답 가능
   - 예시: "어떻게 생각하나요?", "왜 그럴까요?"
   
3. **확인형 질문 (Checking Questions)** - 이해도 점검
   - 예시: "이해했나요?", "따라올 수 있나요?"
   
4. **유도형 질문 (Leading Questions)** - 특정 답변 유도
   - 예시: "A가 더 좋지 않나요?", "분명히 B겠죠?"
   
5. **탐구형 질문 (Inquiry Questions)** - 깊이 있는 사고 유도
   - 예시: "근거가 무엇인가요?", "다른 관점은?"
   
6. **창의형 질문 (Creative Questions)** - 창의적 사고 자극
   - 예시: "새로운 방법이 있을까요?", "다르게 접근한다면?"
   
7. **메타인지 질문 (Metacognitive Questions)** - 학습 과정 성찰
   - 예시: "어떻게 알았나요?", "왜 그렇게 생각했나요?"

### TypeScript 인터페이스
```typescript
interface QTAAnalysisResult extends BaseAnalysisResult {
  framework: 'qta'
  question_distribution: {
    closed: number
    open: number
    checking: number
    leading: number
    inquiry: number
    creative: number
    metacognitive: number
  }
  question_density: number // 질문 비율 (전체 발화 대비)
  cognitive_level_average: number // 평균 인지 수준
  engagement_score: number // 참여도 점수 (0-100)
  recommendations: string[]
  patterns: {
    sequence_analysis: string[] // 질문 연속 패턴
    wait_time_indicators: number // 대기 시간 지표
    follow_up_rate: number // 후속 질문 비율
  }
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
당신은 교육학 전문가로서 교사의 질문 패턴을 분석합니다.

다음 발화에서 질문을 찾아 7가지 유형으로 분류하세요:
1. 폐쇄형 (단답형)
2. 개방형 (다양한 답변)  
3. 확인형 (이해도 점검)
4. 유도형 (특정 답변 유도)
5. 탐구형 (깊이 있는 사고)
6. 창의형 (창의적 사고)
7. 메타인지형 (학습 과정 성찰)

분석할 텍스트: "{text}"

JSON 형식으로 응답하세요:
{
  "questions_found": [
    {
      "text": "질문 텍스트",
      "type": 1-7,
      "reasoning": "분류 근거",
      "cognitive_level": 1-7
    }
  ],
  "overall_pattern": "전체 질문 패턴 분석",
  "engagement_assessment": "참여도 평가",
  "recommendations": ["개선 제안 1", "개선 제안 2"]
}
```

### 시각화 요구사항
- **도넛 차트:** 질문 유형 분포
- **선형 차트:** 시간에 따른 질문 밀도 변화
- **히트맵:** 질문 유형별 학습자 응답률
- **막대 차트:** 인지 수준별 질문 분포

---

## 3. SEI (Student Engagement Indicators) - 신규 프레임워크 2
**프레임워크 ID:** `sei`

### 기본 정보
- **한국어명:** 학습자 참여도 지표 분석
- **영어명:** Student Engagement Indicators Analysis
- **목적:** 학습자의 능동적 참여 정도와 참여 유형을 측정하여 수업 개선점 도출
- **분석 범위:** 발언 기회, 상호작용 패턴, 응답 품질

### 분석 카테고리 (6단계)
1. **수동적 청취 (Passive Listening)** - 일방향 수업
2. **단순 응답 (Simple Response)** - 짧은 답변만 요구
3. **질문 참여 (Question Participation)** - 학생이 질문하는 상황
4. **토론 참여 (Discussion Participation)** - 의견 교환
5. **협력 활동 (Collaborative Activity)** - 그룹 활동
6. **주도적 발표 (Leading Presentation)** - 학생 주도 활동

### TypeScript 인터페이스
```typescript
interface SEIAnalysisResult extends BaseAnalysisResult {
  framework: 'sei'
  engagement_levels: {
    passive_listening: number
    simple_response: number
    question_participation: number
    discussion_participation: number
    collaborative_activity: number
    leading_presentation: number
  }
  interaction_metrics: {
    teacher_talk_ratio: number // 교사 발화 비율
    student_response_ratio: number // 학생 응답 비율
    wait_time_average: number // 평균 대기 시간
    interruption_count: number // 발화 끊김 횟수
  }
  engagement_trend: 'increasing' | 'stable' | 'decreasing'
  participation_equity: number // 참여 형평성 점수
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
교실 상호작용 전문가로서 학습자 참여도를 분석하세요.

다음 6단계로 참여 수준을 분류하세요:
1. 수동적 청취 - 일방향 강의
2. 단순 응답 - 짧은 답변
3. 질문 참여 - 학생의 질문
4. 토론 참여 - 의견 교환
5. 협력 활동 - 그룹 작업
6. 주도적 발표 - 학생 주도

분석할 텍스트: "{text}"

JSON 응답:
{
  "segments": [
    {
      "text": "해당 구간",
      "engagement_level": 1-6,
      "indicators": ["참여 지표들"],
      "student_voice_ratio": 0.0-1.0
    }
  ],
  "overall_assessment": "전체 참여도 평가",
  "interaction_quality": "상호작용 품질 분석",
  "equity_analysis": "참여 형평성 분석",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **스택 막대 차트:** 시간대별 참여 수준 변화
- **파이 차트:** 교사-학생 발화 비율
- **산점도:** 질문 빈도 vs 응답 품질
- **게이지 차트:** 전체 참여도 점수

---

## 4. LOA (Learning Objectives Alignment) - 신규 프레임워크 3
**프레임워크 ID:** `loa`

### 기본 정보
- **한국어명:** 학습목표 연계성 분석
- **영어명:** Learning Objectives Alignment Analysis
- **목적:** 수업 내용과 활동이 학습목표와 얼마나 잘 연계되어 있는지 분석
- **분석 범위:** 목표-내용 일치도, 평가 연계성, 성취기준 달성도

### 분석 카테고리 (5단계)
1. **목표 부재 (No Clear Objective)** - 명확한 목표 없음
2. **목표 언급 (Objective Mentioned)** - 목표만 제시
3. **내용 연계 (Content Aligned)** - 내용이 목표와 연결
4. **활동 연계 (Activity Aligned)** - 활동이 목표 달성 지향
5. **평가 연계 (Assessment Aligned)** - 평가까지 목표와 일치

### TypeScript 인터페이스
```typescript
interface LOAAnalysisResult extends BaseAnalysisResult {
  framework: 'loa'
  alignment_scores: {
    no_objective: number
    objective_mentioned: number
    content_aligned: number
    activity_aligned: number
    assessment_aligned: number
  }
  objective_clarity: number // 목표 명확성 (0-100)
  content_relevance: number // 내용 관련성 (0-100)
  coherence_score: number // 전체 일관성 점수 (0-100)
  achievement_indicators: string[] // 성취 지표들
  gap_analysis: {
    missing_connections: string[]
    improvement_areas: string[]
  }
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
교육과정 전문가로서 학습목표와 수업 내용의 연계성을 분석하세요.

연계성 5단계:
1. 목표 부재 - 명확한 학습목표 없음
2. 목표 언급 - 목표만 제시됨
3. 내용 연계 - 내용이 목표와 연결됨
4. 활동 연계 - 활동이 목표 달성 지향
5. 평가 연계 - 평가까지 목표와 일치

분석할 텍스트: "{text}"

JSON 응답:
{
  "identified_objectives": [
    {
      "objective": "학습목표 내용",
      "clarity_level": 1-5,
      "evidence": "근거 텍스트"
    }
  ],
  "content_segments": [
    {
      "content": "내용 구간",
      "alignment_level": 1-5,
      "objective_connection": "목표 연결점"
    }
  ],
  "coherence_assessment": "전체 일관성 평가",
  "achievement_evidence": ["성취 증거들"],
  "recommendations": ["개선 제안들"]
}
```

### 시각화 요구사항
- **방사형 차트:** 5단계 연계성 분포
- **선형 차트:** 수업 진행에 따른 목표 달성도
- **매트릭스 히트맵:** 목표-활동-평가 연계성
- **진행률 바:** 각 목표별 달성 정도

---

## 5. CEA (Communication Effectiveness Analysis) - 신규 프레임워크 4
**프레임워크 ID:** `cea`

### 기본 정보
- **한국어명:** 의사소통 효과성 분석
- **영어명:** Communication Effectiveness Analysis
- **목적:** 교사의 의사소통 방식이 학습자의 이해와 참여에 미치는 효과 분석
- **분석 범위:** 언어 명확성, 피드백 품질, 상호작용 패턴

### 분석 카테고리 (7단계)
1. **불명확 (Unclear)** - 이해하기 어려운 표현
2. **단순 전달 (Simple Delivery)** - 일방향 정보 전달
3. **명확 설명 (Clear Explanation)** - 이해하기 쉬운 설명
4. **상호작용 (Interactive)** - 양방향 소통
5. **피드백 제공 (Feedback Giving)** - 구체적 피드백
6. **격려 및 지지 (Encouragement)** - 정서적 지원
7. **맞춤형 소통 (Personalized)** - 개별 학습자 고려

### TypeScript 인터페이스
```typescript
interface CEAAnalysisResult extends BaseAnalysisResult {
  framework: 'cea'
  communication_levels: {
    unclear: number
    simple_delivery: number
    clear_explanation: number
    interactive: number
    feedback_giving: number
    encouragement: number
    personalized: number
  }
  effectiveness_metrics: {
    clarity_score: number // 명확성 점수
    interaction_quality: number // 상호작용 품질
    feedback_frequency: number // 피드백 빈도
    emotional_support: number // 정서적 지원
  }
  communication_style: 'authoritative' | 'facilitative' | 'supportive' | 'mixed'
  improvement_areas: string[]
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
의사소통 전문가로서 교사의 소통 효과성을 분석하세요.

7단계 소통 수준:
1. 불명확 - 이해하기 어려운 표현
2. 단순 전달 - 일방향 정보 전달
3. 명확 설명 - 이해하기 쉬운 설명
4. 상호작용 - 양방향 소통
5. 피드백 제공 - 구체적 피드백
6. 격려 및 지지 - 정서적 지원
7. 맞춤형 소통 - 개별 학습자 고려

분석할 텍스트: "{text}"

JSON 응답:
{
  "communication_segments": [
    {
      "text": "발화 구간",
      "level": 1-7,
      "clarity_indicators": ["명확성 지표"],
      "interaction_type": "상호작용 유형"
    }
  ],
  "overall_style": "전체 소통 스타일",
  "effectiveness_assessment": "효과성 평가",
  "emotional_tone": "정서적 톤 분석",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **레벨 막대 차트:** 7단계 소통 수준 분포
- **시계열 그래프:** 수업 중 소통 효과성 변화
- **버블 차트:** 명확성 vs 상호작용성
- **감정 분석 차트:** 긍정/중립/부정 톤 비율

---

## 6. CMA (Classroom Management Analysis) - 신규 프레임워크 5
**프레임워크 ID:** `cma`

### 기본 정보
- **한국어명:** 교실 관리 분석
- **영어명:** Classroom Management Analysis  
- **목적:** 교실 환경 조성과 학습 분위기 관리 능력 분석
- **분석 범위:** 수업 진행 관리, 행동 지도, 시간 관리, 환경 조성

### 분석 카테고리 (6단계)
1. **혼란 상황 (Chaotic)** - 관리되지 않는 상황
2. **기본 통제 (Basic Control)** - 최소한의 질서 유지
3. **체계적 진행 (Systematic Flow)** - 계획된 수업 진행
4. **적극적 관리 (Active Management)** - 능동적 환경 조성
5. **예방적 관리 (Preventive Management)** - 문제 예방 중심
6. **공동체 형성 (Community Building)** - 학습 공동체 조성

### TypeScript 인터페이스
```typescript
interface CMAAnalysisResult extends BaseAnalysisResult {
  framework: 'cma'
  management_levels: {
    chaotic: number
    basic_control: number
    systematic_flow: number
    active_management: number
    preventive_management: number
    community_building: number
  }
  management_aspects: {
    behavior_guidance: number // 행동 지도
    time_management: number // 시간 관리
    space_utilization: number // 공간 활용
    routine_establishment: number // 루틴 형성
  }
  intervention_types: string[] // 개입 유형들
  effectiveness_score: number // 관리 효과성
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
교실 관리 전문가로서 수업 관리 능력을 분석하세요.

6단계 관리 수준:
1. 혼란 상황 - 관리되지 않음
2. 기본 통제 - 최소한의 질서
3. 체계적 진행 - 계획된 진행
4. 적극적 관리 - 능동적 환경 조성
5. 예방적 관리 - 문제 예방 중심
6. 공동체 형성 - 학습 공동체 조성

분석할 텍스트: "{text}"

JSON 응답:
{
  "management_instances": [
    {
      "context": "상황 설명",
      "level": 1-6,
      "management_strategy": "관리 전략",
      "effectiveness": "효과성 평가"
    }
  ],
  "time_indicators": "시간 관리 지표",
  "behavior_interventions": ["행동 개입 사례"],
  "routine_evidence": ["루틴 형성 증거"],
  "community_aspects": ["공동체 형성 요소"],
  "recommendations": ["개선 제안들"]
}
```

### 시각화 요구사항
- **적층 영역 차트:** 시간별 관리 수준 변화
- **방사형 차트:** 4개 관리 측면 점수
- **타임라인:** 주요 관리 개입 시점
- **효과성 게이지:** 전체 관리 효과성

---

## 7. ASA (Assessment Strategy Analysis) - 신규 프레임워크 6
**프레임워크 ID:** `asa`

### 기본 정보
- **한국어명:** 평가 전략 분석
- **영어명:** Assessment Strategy Analysis
- **목적:** 수업 중 평가 활동의 유형과 효과성 분석
- **분석 범위:** 진단평가, 형성평가, 총괄평가, 피드백 제공

### 분석 카테고리 (5단계)
1. **평가 부재 (No Assessment)** - 평가 활동 없음
2. **단순 확인 (Simple Check)** - 이해도 확인만
3. **형성 평가 (Formative Assessment)** - 과정 중 평가
4. **다양한 평가 (Diverse Assessment)** - 여러 평가 방법
5. **총합적 평가 (Comprehensive Assessment)** - 체계적 종합 평가

### TypeScript 인터페이스
```typescript
interface ASAAnalysisResult extends BaseAnalysisResult {
  framework: 'asa'
  assessment_types: {
    no_assessment: number
    simple_check: number
    formative_assessment: number
    diverse_assessment: number
    comprehensive_assessment: number
  }
  assessment_methods: {
    oral_questions: number // 구두 질문
    written_tasks: number // 서면 과제
    peer_assessment: number // 동료 평가
    self_assessment: number // 자기 평가
    portfolio: number // 포트폴리오
  }
  feedback_quality: number // 피드백 품질
  assessment_frequency: number // 평가 빈도
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
교육평가 전문가로서 수업 중 평가 전략을 분석하세요.

5단계 평가 수준:
1. 평가 부재 - 평가 활동 없음
2. 단순 확인 - 이해도 확인만
3. 형성 평가 - 과정 중 평가
4. 다양한 평가 - 여러 평가 방법
5. 총합적 평가 - 체계적 종합 평가

분석할 텍스트: "{text}"

JSON 응답:
{
  "assessment_activities": [
    {
      "activity": "평가 활동",
      "type": 1-5,
      "method": "평가 방법",
      "purpose": "평가 목적"
    }
  ],
  "feedback_instances": [
    {
      "feedback": "피드백 내용",
      "quality": "품질 평가",
      "timeliness": "적시성"
    }
  ],
  "assessment_balance": "평가 균형성",
  "effectiveness": "평가 효과성",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **도넛 차트:** 평가 유형별 분포
- **매트릭스:** 평가 방법별 사용 빈도
- **품질 점수 차트:** 피드백 품질 분포
- **시퀀스 다이어그램:** 평가-피드백-개선 순환

---

## 8. DIA (Differentiation in Instruction Analysis) - 신규 프레임워크 7
**프레임워크 ID:** `dia`

### 기본 정보
- **한국어명:** 수업 차별화 분석
- **영어명:** Differentiation in Instruction Analysis
- **목적:** 학습자 개별 차이를 고려한 수업 설계와 실행 정도 분석
- **분석 범위:** 내용 차별화, 과정 차별화, 결과물 차별화, 학습 환경

### 분석 카테고리 (4단계)
1. **일률적 수업 (One-Size-Fits-All)** - 동일한 방식
2. **부분적 차별화 (Partial Differentiation)** - 일부 구간만
3. **체계적 차별화 (Systematic Differentiation)** - 계획된 차별화
4. **개별 맞춤형 (Individualized)** - 완전 개별화

### TypeScript 인터페이스
```typescript
interface DIAAnalysisResult extends BaseAnalysisResult {
  framework: 'dia'
  differentiation_levels: {
    one_size_fits_all: number
    partial_differentiation: number
    systematic_differentiation: number
    individualized: number
  }
  differentiation_aspects: {
    content: number // 내용 차별화
    process: number // 과정 차별화
    product: number // 결과물 차별화
    environment: number // 환경 차별화
  }
  learner_consideration: {
    ability_levels: boolean // 능력 수준 고려
    learning_styles: boolean // 학습 스타일 고려
    interests: boolean // 관심사 고려
    background: boolean // 배경 지식 고려
  }
  adaptation_strategies: string[]
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
교수 설계 전문가로서 수업의 차별화 정도를 분석하세요.

차별화 4단계:
1. 일률적 수업 - 모든 학생에게 동일
2. 부분적 차별화 - 일부 구간만 차별화
3. 체계적 차별화 - 계획된 차별화
4. 개별 맞춤형 - 완전한 개별화

차별화 영역:
- 내용(Content): 학습 내용의 다양화
- 과정(Process): 학습 방법의 다양화
- 결과물(Product): 평가 방식의 다양화
- 환경(Environment): 학습 환경의 조정

분석할 텍스트: "{text}"

JSON 응답:
{
  "differentiation_evidence": [
    {
      "evidence": "차별화 증거",
      "level": 1-4,
      "aspect": "차별화 영역",
      "target_group": "대상 학습자군"
    }
  ],
  "adaptation_strategies": ["적응 전략들"],
  "inclusivity_indicators": ["포용성 지표들"],
  "personalization_level": "개인화 수준",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **4각형 레이더 차트:** 차별화 4영역 점수
- **스택 바 차트:** 차별화 수준별 시간 분포
- **체크리스트 시각화:** 학습자 고려 요소
- **개선 로드맵:** 차별화 단계별 발전 계획

---

## 9. TIA (Technology Integration Analysis) - 신규 프레임워크 8
**프레임워크 ID:** `tia`

### 기본 정보
- **한국어명:** 기술 통합 분석
- **영어명:** Technology Integration Analysis
- **목적:** 교육 기술의 활용 수준과 효과성 분석 (SAMR 모델 기반)
- **분석 범위:** 기술 도구 사용, 통합 수준, 학습 향상 효과

### 분석 카테고리 (SAMR 4단계 + 미사용)
1. **기술 미사용 (No Technology)** - 전통적 수업만
2. **대체 (Substitution)** - 기존 방식을 기술로 대체
3. **강화 (Augmentation)** - 기술로 기능 향상
4. **수정 (Modification)** - 기술로 과제 재설계
5. **재정의 (Redefinition)** - 기술로 새로운 학습 경험

### TypeScript 인터페이스
```typescript
interface TIAAnalysisResult extends BaseAnalysisResult {
  framework: 'tia'
  samr_levels: {
    no_technology: number
    substitution: number
    augmentation: number
    modification: number
    redefinition: number
  }
  technology_types: {
    presentation_tools: number // 프레젠테이션 도구
    interactive_media: number // 상호작용 미디어
    collaboration_platforms: number // 협업 플랫폼
    assessment_tools: number // 평가 도구
    content_creation: number // 콘텐츠 제작
  }
  integration_effectiveness: number // 통합 효과성
  digital_literacy_support: number // 디지털 리터러시 지원
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
교육공학 전문가로서 기술 통합 수준을 SAMR 모델로 분석하세요.

SAMR 5단계:
1. 기술 미사용 - 전통적 수업
2. 대체(S) - 기존 방식을 기술로 대체
3. 강화(A) - 기술로 기능 향상
4. 수정(M) - 기술로 과제 재설계
5. 재정의(R) - 기술로 새로운 학습 경험

분석할 텍스트: "{text}"

JSON 응답:
{
  "technology_instances": [
    {
      "technology": "사용된 기술",
      "samr_level": 1-5,
      "purpose": "사용 목적",
      "effectiveness": "효과성 평가"
    }
  ],
  "integration_quality": "통합 품질 평가",
  "learning_enhancement": "학습 향상 효과",
  "digital_skills": "디지털 역량 지원",
  "accessibility": "접근성 고려",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **SAMR 피라미드 차트:** 5단계 분포
- **기술 유형 방사형 차트:** 5개 기술 영역 활용도
- **효과성 매트릭스:** 기술 유형별 학습 효과
- **통합 수준 진행률:** SAMR 단계별 발전도

---

## 10. CTA (Critical Thinking Analysis) - 신규 프레임워크 9
**프레임워크 ID:** `cta`

### 기본 정보
- **한국어명:** 비판적 사고력 분석
- **영어명:** Critical Thinking Analysis
- **목적:** 비판적 사고 능력 함양을 위한 수업 요소 분석
- **분석 범위:** 사고 과정, 논리적 추론, 증거 평가, 다양한 관점

### 분석 카테고리 (6단계)
1. **정보 수용 (Information Reception)** - 정보를 그대로 수용
2. **기본 질문 (Basic Questioning)** - 단순한 의문 제기
3. **증거 요구 (Evidence Seeking)** - 근거와 증거 요구
4. **관점 비교 (Perspective Comparison)** - 다양한 관점 비교
5. **논리 분석 (Logic Analysis)** - 논리적 타당성 검증
6. **창의적 해결 (Creative Resolution)** - 창의적 문제 해결

### TypeScript 인터페이스
```typescript
interface CTAAnalysisResult extends BaseAnalysisResult {
  framework: 'cta'
  thinking_levels: {
    information_reception: number
    basic_questioning: number
    evidence_seeking: number
    perspective_comparison: number
    logic_analysis: number
    creative_resolution: number
  }
  critical_thinking_skills: {
    analysis: number // 분석 능력
    evaluation: number // 평가 능력
    inference: number // 추론 능력
    interpretation: number // 해석 능력
    explanation: number // 설명 능력
  }
  reasoning_patterns: string[] // 추론 패턴들
  thinking_depth: number // 사고 깊이
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
비판적 사고 교육 전문가로서 사고력 함양 정도를 분석하세요.

6단계 사고 수준:
1. 정보 수용 - 정보를 그대로 받아들임
2. 기본 질문 - 단순한 의문 제기
3. 증거 요구 - 근거와 증거 요구
4. 관점 비교 - 다양한 관점 비교
5. 논리 분석 - 논리적 타당성 검증
6. 창의적 해결 - 창의적 문제 해결

분석할 텍스트: "{text}"

JSON 응답:
{
  "thinking_episodes": [
    {
      "episode": "사고 에피소드",
      "level": 1-6,
      "thinking_skill": "사고 기능",
      "reasoning_type": "추론 유형"
    }
  ],
  "questioning_patterns": ["질문 패턴들"],
  "evidence_usage": "증거 활용 정도",
  "perspective_diversity": "관점 다양성",
  "logic_quality": "논리 품질",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **사고 단계 막대 차트:** 6단계 분포
- **스킬 레이더 차트:** 5개 비판적 사고 기능
- **사고 깊이 게이지:** 전체 사고 깊이 수준
- **추론 패턴 네트워크:** 추론 연결 관계

---

## 11. CRA (Cultural Responsiveness Analysis) - 신규 프레임워크 10
**프레임워크 ID:** `cra`

### 기본 정보
- **한국어명:** 문화 반응성 분석
- **영어명:** Cultural Responsiveness Analysis
- **목적:** 다양한 문화적 배경을 가진 학습자들을 고려한 수업 실행 분석
- **분석 범위:** 문화적 인식, 포용성, 다양성 존중, 형평성

### 분석 카테고리 (5단계)
1. **문화 무시 (Cultural Ignorance)** - 문화적 차이 인식 부족
2. **표면적 인식 (Surface Awareness)** - 피상적 문화 언급
3. **문화 존중 (Cultural Respect)** - 문화적 차이 존중
4. **문화 통합 (Cultural Integration)** - 수업에 문화 요소 통합
5. **문화 주도 (Culturally Sustaining)** - 문화가 학습을 주도

### TypeScript 인터페이스
```typescript
interface CRAAnalysisResult extends BaseAnalysisResult {
  framework: 'cra'
  responsiveness_levels: {
    cultural_ignorance: number
    surface_awareness: number
    cultural_respect: number
    cultural_integration: number
    culturally_sustaining: number
  }
  cultural_aspects: {
    language_diversity: number // 언어 다양성
    cultural_references: number // 문화적 참조
    inclusive_examples: number // 포용적 예시
    equity_practices: number // 형평성 실천
  }
  inclusivity_indicators: string[]
  cultural_sensitivity: number // 문화적 민감성
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
문화 교육 전문가로서 수업의 문화 반응성을 분석하세요.

5단계 문화 반응성:
1. 문화 무시 - 문화적 차이 인식 부족
2. 표면적 인식 - 피상적 문화 언급
3. 문화 존중 - 문화적 차이 존중
4. 문화 통합 - 수업에 문화 요소 통합
5. 문화 주도 - 문화가 학습을 주도

분석할 텍스트: "{text}"

JSON 응답:
{
  "cultural_instances": [
    {
      "instance": "문화적 사례",
      "level": 1-5,
      "cultural_element": "문화 요소",
      "inclusivity": "포용성 정도"
    }
  ],
  "diversity_acknowledgment": "다양성 인정",
  "equity_evidence": ["형평성 증거들"],
  "cultural_assets": "문화적 자산 활용",
  "bias_indicators": "편견 지표들",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **문화 반응성 단계 차트:** 5단계 분포
- **포용성 점수 카드:** 4개 문화적 측면
- **다양성 지표 대시보드:** 포용성 메트릭
- **형평성 체크리스트:** 문화적 고려 사항

---

## 12. ITA (Inclusive Teaching Analysis) - 신규 프레임워크 11
**프레임워크 ID:** `ita`

### 기본 정보
- **한국어명:** 포용적 교수법 분석
- **영어명:** Inclusive Teaching Analysis
- **목적:** 모든 학습자가 참여할 수 있는 포용적 수업 환경 조성 정도 분석
- **분석 범위:** 접근성, 다양성 지원, 장벽 제거, 공평한 기회 제공

### 분석 카테고리 (4단계)
1. **배타적 (Exclusive)** - 일부 학습자 배제
2. **분리적 (Segregative)** - 별도 지원 제공
3. **통합적 (Integrative)** - 주류에 통합
4. **포용적 (Inclusive)** - 모든 학습자 완전 참여

### TypeScript 인터페이스
```typescript
interface ITAAnalysisResult extends BaseAnalysisResult {
  framework: 'ita'
  inclusion_levels: {
    exclusive: number
    segregative: number
    integrative: number
    inclusive: number
  }
  inclusion_practices: {
    universal_design: number // 보편적 설계
    accessibility: number // 접근성
    participation_equity: number // 참여 형평성
    diverse_strengths: number // 다양한 강점 인정
  }
  support_strategies: string[] // 지원 전략들
  barrier_removal: string[] // 장벽 제거 노력
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
포용 교육 전문가로서 수업의 포용성을 분석하세요.

포용성 4단계:
1. 배타적 - 일부 학습자 배제
2. 분리적 - 별도 지원 제공
3. 통합적 - 주류에 통합
4. 포용적 - 모든 학습자 완전 참여

분석할 텍스트: "{text}"

JSON 응답:
{
  "inclusion_evidence": [
    {
      "evidence": "포용성 증거",
      "level": 1-4,
      "practice": "포용 실천",
      "beneficiaries": "수혜 대상"
    }
  ],
  "accessibility_measures": "접근성 조치",
  "participation_patterns": "참여 패턴",
  "support_provisions": ["지원 제공 사항"],
  "barrier_identification": ["식별된 장벽들"],
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **포용성 단계 진행률:** 4단계 발전도
- **실천 영역 점수:** 4개 포용 실천 영역
- **장벽-지원 매트릭스:** 장벽과 지원 대응
- **참여 형평성 차트:** 학습자군별 참여도

---

## 13. RWC (Real-World Connections Analysis) - 신규 프레임워크 12
**프레임워크 ID:** `rwc`

### 기본 정보
- **한국어명:** 실생활 연계성 분석
- **영어명:** Real-World Connections Analysis
- **목적:** 학습 내용과 실제 생활의 연계성 정도 분석
- **분석 범위:** 실생활 예시, 현실 문제 해결, 사회적 맥락, 미래 적용성

### 분석 카테고리 (5단계)
1. **추상적 학습 (Abstract Learning)** - 이론적 내용만
2. **사례 제시 (Example Giving)** - 실생활 예시 제시
3. **문제 연결 (Problem Connection)** - 실제 문제와 연결
4. **실천 적용 (Practical Application)** - 실생활 적용 활동
5. **사회적 참여 (Social Engagement)** - 사회 문제 해결 참여

### TypeScript 인터페이스
```typescript
interface RWCAnalysisResult extends BaseAnalysisResult {
  framework: 'rwc'
  connection_levels: {
    abstract_learning: number
    example_giving: number
    problem_connection: number
    practical_application: number
    social_engagement: number
  }
  connection_types: {
    personal_relevance: number // 개인적 관련성
    social_issues: number // 사회 문제
    career_connections: number // 진로 연계
    community_impact: number // 지역사회 영향
  }
  authenticity_score: number // 진정성 점수
  future_application: string[] // 미래 적용 가능성
  recommendations: string[]
}
```

### LLM 분석 프롬프트 (Temperature 0.3)
```
실생활 연계 교육 전문가로서 수업의 현실 연결성을 분석하세요.

연계성 5단계:
1. 추상적 학습 - 이론적 내용만
2. 사례 제시 - 실생활 예시 제시
3. 문제 연결 - 실제 문제와 연결
4. 실천 적용 - 실생활 적용 활동
5. 사회적 참여 - 사회 문제 해결 참여

분석할 텍스트: "{text}"

JSON 응답:
{
  "connection_instances": [
    {
      "instance": "연계 사례",
      "level": 1-5,
      "connection_type": "연계 유형",
      "authenticity": "진정성 평가"
    }
  ],
  "real_world_examples": ["실생활 예시들"],
  "problem_solving": "문제 해결 연계",
  "career_relevance": "진로 관련성",
  "social_impact": "사회적 영향",
  "recommendations": ["개선 방안들"]
}
```

### 시각화 요구사항
- **연계성 단계 막대 차트:** 5단계 분포
- **연계 유형 도넛 차트:** 4개 연계 유형
- **진정성-관련성 산점도:** 진정성 vs 개인적 관련성
- **미래 적용 로드맵:** 학습-현실-미래 연결

---

## 통합 시스템 아키텍처

### 프레임워크 실행 흐름
```typescript
interface AnalysisRequest {
  text: string
  frameworks: string[] // 선택된 프레임워크 ID들
  parallel_execution: boolean // 병렬 실행 여부
  temperature: number // LLM temperature (기본값: 0.3)
}

interface ComprehensiveAnalysisResult {
  request_id: string
  frameworks_analyzed: string[]
  individual_results: Record<string, BaseAnalysisResult>
  cross_framework_insights: CrossFrameworkInsight[]
  overall_summary: OverallSummary
  recommendations: PrioritizedRecommendation[]
}
```

### 시각화 대시보드 구성
1. **프레임워크 선택기** - 13개 프레임워크 토글
2. **개별 프레임워크 뷰** - 각 프레임워크별 상세 분석
3. **비교 분석 뷰** - 여러 프레임워크 결과 비교
4. **종합 대시보드** - 전체 분석 요약

### 구현 우선순위
1. **Phase 1:** QTA, SEI, LOA, CEA (핵심 교육 요소)
2. **Phase 2:** CMA, ASA, DIA, TIA (수업 관리 및 기술)
3. **Phase 3:** CTA, CRA, ITA, RWC (고도화된 분석)

### 기술적 요구사항
- **병렬 처리:** 13개 프레임워크 동시 실행
- **일관성 보장:** Temperature 0.3으로 안정적 결과
- **확장성:** 새로운 프레임워크 추가 용이
- **성능 최적화:** 분석 시간 단축을 위한 캐싱

이 종합 분석 프레임워크를 통해 AIBOA 플랫폼은 교육의 모든 측면을 다각도로 분석하여 교사의 전문성 향상을 지원할 수 있습니다.