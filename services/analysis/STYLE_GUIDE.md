# TVAS 디자인 시스템 스타일 가이드

전문 의료 진단 보고서 스타일의 교육 분석 보고서 디자인 시스템

**버전**: 1.0.0
**최종 업데이트**: 2025-11-13

---

## 목차

1. [개요](#개요)
2. [색상 시스템](#색상-시스템)
3. [컴포넌트 가이드](#컴포넌트-가이드)
4. [애니메이션](#애니메이션)
5. [타이포그래피](#타이포그래피)
6. [간격 시스템](#간격-시스템)
7. [사용 예제](#사용-예제)

---

## 개요

이 디자인 시스템은 체성분 분석기 출력물의 명료하고 전문적인 스타일을 참고하여 제작되었습니다.
핵심 원칙:
- **명료성**: 데이터가 즉시 이해 가능하도록
- **일관성**: 모든 보고서에서 동일한 시각적 언어 사용
- **전문성**: 의료 진단 보고서 수준의 신뢰성
- **접근성**: 색각 이상자, 스크린 리더 사용자 고려

---

## 색상 시스템

### 상태별 색상

#### Excellent (우수) - 녹색 계열
```css
주 색상: #22c55e (green-500)
배경 gradient: linear-gradient(135deg, #ffffff 0%, rgba(34, 197, 94, 0.05) 100%)
hover glow: 0 10px 25px rgba(34, 197, 94, 0.2)
```

**사용 시기**: 점수 80점 이상, 매우 긍정적인 결과

#### Good (양호) - 파란색 계열
```css
주 색상: #3b82f6 (blue-500)
배경 gradient: linear-gradient(135deg, #ffffff 0%, rgba(59, 130, 246, 0.05) 100%)
hover glow: 0 10px 25px rgba(59, 130, 246, 0.2)
```

**사용 시기**: 점수 70-79점, 긍정적인 결과

#### Adequate (적정) - 노란색 계열
```css
주 색상: #fbbf24 (yellow-400)
배경 gradient: linear-gradient(135deg, #ffffff 0%, rgba(251, 191, 36, 0.05) 100%)
hover glow: 0 10px 25px rgba(251, 191, 36, 0.2)
```

**사용 시기**: 점수 60-69점, 주의 필요

#### Needs Improvement (개선필요) - 빨간색 계열
```css
주 색상: #ef4444 (red-500)
배경 gradient: linear-gradient(135deg, #ffffff 0%, rgba(239, 68, 68, 0.05) 100%)
hover glow: 0 10px 25px rgba(239, 68, 68, 0.2)
```

**사용 시기**: 점수 60점 미만, 개선 필요

### 색상 사용 규칙

1. **Gradient는 항상 135도 각도**로 적용
2. **배경 opacity는 3-5%**로 유지 (너무 강하지 않게)
3. **Hover glow는 20% opacity**로 통일
4. **Border는 왼쪽에만** 4px 두께로 적용

---

## 컴포넌트 가이드

### 1. Score Card (점수 카드)

**용도**: 개별 메트릭의 점수와 상태 표시

**구조**:
```html
<div class="score-card score-card--excellent">
  <div class="score-card__label">질문 빈도</div>
  <div class="score-card__value">85.3</div>
  <div class="score-card__status-bar">
    <div class="score-card__status-fill score-card__status-fill--excellent"
         style="width: 85.3%;"></div>
  </div>
</div>
```

**CSS 클래스**:
- `.score-card`: 기본 카드 스타일
- `.score-card--excellent/good/adequate/needs-improvement`: 상태별 스타일
- `.score-card__value`: 점수 값 (큰 글씨, 모노스페이스 폰트)
- `.score-card__label`: 메트릭 라벨
- `.score-card__status-bar`: 진행률 바 컨테이너
- `.score-card__status-fill`: 실제 진행률 (width로 조절)

**사용 팁**:
- 카드는 항상 grid layout으로 배치 (3열 권장)
- 점수 값은 소수점 1자리까지 표시
- Status bar는 반드시 0-100% 범위로

### 2. Insight Card (인사이트 카드)

**용도**: 강점 또는 개선 영역 표시

**구조**:
```html
<div class="insight-card insight-card--strength">
  <div class="insight-card__header">
    <div class="insight-card__icon insight-card__icon--strength">✓</div>
    <h4 class="insight-card__title">강점 1</h4>
  </div>
  <p class="insight-card__description">
    학생들에게 충분한 생각 시간을 제공하고 있습니다.
  </p>
  <div class="insight-card__example">
    발화 예시: "자, 2분 동안 생각해볼까요?"
  </div>
</div>
```

**CSS 클래스**:
- `.insight-card--strength`: 강점 (녹색 테두리)
- `.insight-card--improvement`: 개선 영역 (노란색 테두리)
- `.insight-card__icon`: 아이콘 박스
- `.insight-card__example`: 발화 예시 (선택적)

**사용 팁**:
- 강점은 최대 3개까지
- 개선 영역도 최대 3개까지
- 발화 예시는 구체적이고 짧게 (1-2문장)

### 3. Recommendation Card (권장사항 카드)

**용도**: 실행 가능한 코칭 제안

**구조**:
```html
<div class="recommendation-card">
  <div class="recommendation-card__header">
    <div class="recommendation-card__number">1</div>
    <h4 class="recommendation-card__title">
      개방형 질문 비중 늘리기
    </h4>
    <span class="recommendation-badge recommendation-badge--high">
      높은 우선순위
    </span>
  </div>
  <div class="recommendation-card__content">
    <p class="recommendation-card__description">
      현재 폐쇄형 질문이 많습니다. 개방형 질문을 늘려보세요.
    </p>
  </div>
</div>
```

**CSS 클래스**:
- `.recommendation-badge--high/medium/low`: 우선순위 표시
- `.recommendation-card__number`: 번호 원형 배지
- `.recommendation-card__why`: 이유 설명 섹션 (선택적)

**사용 팁**:
- 우선순위는 3단계 (high/medium/low)
- High는 1-2개, Medium은 2-3개, Low는 나머지
- 실행 가능한 구체적 제안만 포함

### 4. Hero Summary (종합 점수 섹션)

**용도**: 전체 교수 효과성 점수를 한눈에

**구조**:
```html
<div class="hero-summary">
  <div class="hero-summary__title">전체 교수 효과성 점수</div>
  <div class="hero-summary__score">
    82<span class="hero-summary__score-max">/100</span>
  </div>
  <div class="hero-summary__status-bar">
    <div class="hero-summary__status-fill score-card__status-fill--excellent"
         style="width: 82%;"></div>
  </div>
  <div class="hero-summary__percentile">상위 18% (우수)</div>
  <div class="hero-summary__profile">
    <div class="hero-summary__profile-label">교수 유형</div>
    <div class="hero-summary__profile-type">소크라틱 촉진자</div>
  </div>
</div>
```

**사용 팁**:
- 페이지 최상단에 배치
- 점수는 정수로 표시
- 백분위는 "상위 X%" 형식
- 교수 유형은 패턴 매칭 결과 사용

---

## 애니메이션

### 사용 가능한 애니메이션

#### 1. Fade In (서서히 나타나기)
```html
<div class="score-card animate-fade-in animate-delay-200">
  <!-- 내용 -->
</div>
```

**용도**: 카드, 섹션이 부드럽게 나타날 때
**Duration**: 0.6초
**Easing**: ease-out

#### 2. Slide Up (위로 슬라이드)
```html
<div class="insight-card animate-slide-up animate-delay-300">
  <!-- 내용 -->
</div>
```

**용도**: 리스트 항목, 카드가 아래에서 올라올 때
**Duration**: 0.8초
**Easing**: cubic-bezier(0.4, 0, 0.2, 1)
**Distance**: 30px

#### 3. Scale In (확대되며 나타나기)
```html
<div class="recommendation-card animate-scale-in animate-delay-400">
  <!-- 내용 -->
</div>
```

**용도**: 중요한 요소 강조
**Duration**: 0.5초
**Scale**: 0.95 → 1.0

#### 4. Pulse Subtle (부드러운 깜빡임)
```html
<div class="hero-summary__score animate-pulse-subtle">82</div>
```

**용도**: 주목해야 할 중요 지표
**Duration**: 2초 (무한 반복)
**Opacity**: 1.0 → 0.8 → 1.0

### 애니메이션 지연 시간

순차적 애니메이션을 위한 딜레이 클래스:
- `.animate-delay-100`: 100ms
- `.animate-delay-200`: 200ms
- `.animate-delay-300`: 300ms
- `.animate-delay-400`: 400ms
- `.animate-delay-500`: 500ms
- `.animate-delay-600`: 600ms
- `.animate-delay-700`: 700ms
- `.animate-delay-800`: 800ms

**예시 (순차적 카드 표시)**:
```html
<div class="score-card animate-slide-up animate-delay-100">...</div>
<div class="score-card animate-slide-up animate-delay-200">...</div>
<div class="score-card animate-slide-up animate-delay-300">...</div>
```

### 애니메이션 사용 규칙

1. **첫 로드 시에만** 애니메이션 적용
2. **너무 많은 애니메이션 금지**: 페이지당 최대 5-7개
3. **사용자 설정 존중**: `prefers-reduced-motion: reduce` 자동 감지
4. **순차적 애니메이션**: 100-200ms 간격 권장
5. **중요도에 따라 선택**:
   - Hero Summary: scale-in
   - Score Cards: slide-up 또는 fade-in
   - Insight Cards: slide-up
   - Recommendation Cards: fade-in

---

## 타이포그래피

### 폰트 스택
```css
기본: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
숫자/코드: "SF Mono", Monaco, "Cascadia Code", monospace
```

### 폰트 크기 계층

| 클래스 | 크기 | 사용 예 |
|--------|------|---------|
| `--text-xs` | 0.75rem (12px) | 작은 라벨, 타임스탬프 |
| `--text-sm` | 0.875rem (14px) | 본문, 설명 |
| `--text-base` | 1rem (16px) | 기본 본문 |
| `--text-lg` | 1.125rem (18px) | 카드 제목 |
| `--text-xl` | 1.25rem (20px) | 섹션 제목 |
| `--text-2xl` | 1.5rem (24px) | 페이지 제목 |
| `--text-4xl` | 2.25rem (36px) | Hero 점수 |

### 폰트 두께

| 클래스 | 값 | 사용 예 |
|--------|-----|---------|
| `--weight-normal` | 400 | 본문 |
| `--weight-medium` | 500 | 라벨 |
| `--weight-semibold` | 600 | 제목 |
| `--weight-bold` | 700 | 강조, 점수 |

---

## 간격 시스템

8px 기반 간격 시스템:

| 클래스 | 크기 | 사용 예 |
|--------|------|---------|
| `--space-1` | 0.25rem (4px) | 최소 여백 |
| `--space-2` | 0.5rem (8px) | 작은 여백 |
| `--space-3` | 0.75rem (12px) | 중간 여백 |
| `--space-4` | 1rem (16px) | 기본 여백 |
| `--space-6` | 1.5rem (24px) | 큰 여백 |
| `--space-8` | 2rem (32px) | 섹션 간 여백 |

### 사용 패턴
- 카드 내부 padding: `--space-4` (16px)
- 카드 간 margin: `--space-3` (12px)
- 섹션 간 margin: `--space-6` 또는 `--space-8` (24-32px)
- 텍스트 줄 간격: `--leading-relaxed` (1.625)

---

## 사용 예제

### 완전한 보고서 섹션 예제

```html
<!-- 종합 점수 -->
<div class="hero-summary animate-scale-in">
  <div class="hero-summary__title">전체 교수 효과성 점수</div>
  <div class="hero-summary__score animate-pulse-subtle">
    82<span class="hero-summary__score-max">/100</span>
  </div>
  <div class="hero-summary__status-bar">
    <div class="hero-summary__status-fill score-card__status-fill--excellent"
         style="width: 82%;"></div>
  </div>
  <div class="hero-summary__percentile">상위 18% (우수)</div>
</div>

<!-- 주요 메트릭 -->
<div class="grid grid-3" style="margin-top: 32px;">
  <div class="score-card score-card--excellent animate-slide-up animate-delay-100">
    <div class="score-card__label">질문 빈도</div>
    <div class="score-card__value">85.3</div>
    <div class="score-card__status-bar">
      <div class="score-card__status-fill score-card__status-fill--excellent"
           style="width: 85.3%;"></div>
    </div>
  </div>

  <div class="score-card score-card--good animate-slide-up animate-delay-200">
    <div class="score-card__label">피드백 품질</div>
    <div class="score-card__value">72.1</div>
    <div class="score-card__status-bar">
      <div class="score-card__status-fill score-card__status-fill--good"
           style="width: 72.1%;"></div>
    </div>
  </div>

  <div class="score-card score-card--adequate animate-slide-up animate-delay-300">
    <div class="score-card__label">인지 수준</div>
    <div class="score-card__value">65.8</div>
    <div class="score-card__status-bar">
      <div class="score-card__status-fill score-card__status-fill--adequate"
           style="width: 65.8%;"></div>
    </div>
  </div>
</div>

<!-- 강점 -->
<section style="margin-top: 48px;">
  <h2>주요 강점</h2>
  <div class="insight-card insight-card--strength animate-fade-in animate-delay-400">
    <div class="insight-card__header">
      <div class="insight-card__icon insight-card__icon--strength">✓</div>
      <h4 class="insight-card__title">강점 1: 학생 사고 촉진</h4>
    </div>
    <p class="insight-card__description">
      개방형 질문을 효과적으로 사용하여 학생들의 깊은 사고를 유도합니다.
    </p>
    <div class="insight-card__example">
      발화 예시: "이 개념을 다른 상황에 어떻게 적용할 수 있을까요?"
    </div>
  </div>
</section>

<!-- 권장사항 -->
<section style="margin-top: 48px;">
  <h2>실행 권장사항</h2>
  <div class="recommendation-card animate-fade-in animate-delay-500">
    <div class="recommendation-card__header">
      <div class="recommendation-card__number">1</div>
      <h4 class="recommendation-card__title">
        상위 인지 수준 질문 비중 늘리기
      </h4>
      <span class="recommendation-badge recommendation-badge--high">
        높은 우선순위
      </span>
    </div>
    <div class="recommendation-card__content">
      <p class="recommendation-card__description">
        현재 L1 (기억/이해) 수준 질문이 60%입니다.
        L3 (분석/평가/창조) 질문을 20% 이상 늘려보세요.
      </p>
      <div class="recommendation-card__why">
        <div class="recommendation-card__why-title">왜 중요한가요?</div>
        상위 인지 질문은 학생들의 비판적 사고력과 문제해결 능력을 향상시킵니다.
      </div>
    </div>
  </div>
</section>
```

---

## 반응형 디자인

### 브레이크포인트
```css
/* Mobile First */
기본: 모바일 (< 768px)
태블릿: @media (min-width: 768px)
데스크톱: @media (min-width: 1024px)
```

### 그리드 시스템
```css
/* 3열 그리드 (데스크톱) */
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* 태블릿: 2열 */
@media (max-width: 1024px) {
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
}

/* 모바일: 1열 */
@media (max-width: 768px) {
  .grid-3 { grid-template-columns: 1fr; }
}
```

---

## 접근성 체크리스트

- [ ] 모든 상호작용 요소에 `:focus` 스타일 적용
- [ ] 색상만으로 정보를 전달하지 않음 (아이콘, 텍스트 병행)
- [ ] 텍스트 대비율 4.5:1 이상 유지
- [ ] `prefers-reduced-motion` 설정 존중
- [ ] 스크린 리더를 위한 `aria-label` 제공
- [ ] 키보드 네비게이션 지원

---

## 변경 이력

### v1.0.0 (2025-11-13)
- 초기 디자인 시스템 구축
- Score Card, Insight Card, Recommendation Card 컴포넌트
- 색상 시스템 (상태별 gradient + hover glow)
- 애니메이션 시스템 (fade-in, slide-up, scale-in, pulse)
- 타이포그래피 및 간격 시스템
- 접근성 기본 지원 (reduced motion, focus styles)

---

## 라이센스

© 2025 TVAS Project. 내부 사용 전용.
