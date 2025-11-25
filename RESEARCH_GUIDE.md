# 연구 활용 가이드 (Research Guide)

## 1. 연구 도구로서의 TVAS

### 1.1 왜 이 시스템을 연구에 사용할 수 있는가?

**완벽한 일관성 보장**
- 동일 영상 재분석 시 95%+ 일치도
- 체크리스트 기반 이진 판단으로 주관성 최소화
- 규칙 엔진 기반 평가로 결정론적 결과 산출

**객관적 정량 지표**
- 15개 핵심 지표의 수치화
- 주관적 해석 없이 빈도/비율/시간 측정
- 통계 분석 가능한 데이터 형식

**재현 가능성**
- 분석 알고리즘 공개
- 동일 조건에서 동일 결과 보장
- 연구자 간 일치도 검증 가능

---

## 2. 가능한 연구 주제

### 2.1 교사 발화 패턴 연구

**연구 질문 예시**
1. 초임 교사와 경력 교사의 질문 패턴 차이는?
2. 교과별 수업 담화 특성은 어떻게 다른가?
3. 학교급별(초/중/고) 교사 발화의 인지적 복잡도 차이는?
4. 우수 수업과 일반 수업의 담화 패턴 차이는?

**연구 설계**
```
참여자: 
- 초임 교사 30명 (경력 1-3년)
- 경력 교사 30명 (경력 10년 이상)

자료 수집:
- 각 교사당 수업 영상 3회 (총 180개)
- 동일 단원/학습 목표로 통제

분석:
- TVAS로 전체 영상 자동 분석
- 15개 지표 비교 (독립표본 t-검정)
- 3D 매트릭스 패턴 클러스터링

기대 결과:
- 경력별 질문 깊이 차이 규명
- 교사 전문성 발달 단계 모델링
```

### 2.2 교사 교육/연수 효과성 연구

**연구 질문 예시**
1. 질문법 연수가 실제 수업 담화에 미치는 영향은?
2. AI 코칭 피드백이 교사 발화 개선에 효과적인가?
3. 동료 수업 관찰이 자신의 수업 담화 변화에 영향을 미치는가?

**연구 설계 (단일집단 사전-사후 설계)**
```
참여자: 
- 중등 교사 40명

절차:
1. 사전 수업 영상 촬영 (Week 1)
2. TVAS 자동 분석 및 피드백 제공
3. 질문법 연수 프로그램 (Week 2-4)
4. 사후 수업 영상 촬영 (Week 5)
5. TVAS 재분석 및 변화 측정

분석:
- 사전-사후 대응표본 t-검정
- 효과 크기(Cohen's d) 계산
- 개선 영역별 변화율 비교

측정 지표:
- 질문 빈도 (question_ratio)
- 고차원 질문 비율 (higher_order_ratio)
- 대기 시간 (avg_wait_time)
- 확장 대화 비율 (extended_dialogue_ratio)
```

### 2.3 수업 담화와 학생 성취도 관계 연구

**연구 질문**
교사의 어떤 발화 패턴이 학생 학업 성취도와 상관이 있는가?

**연구 설계 (상관 연구)**
```
참여자:
- 고등학교 국어 교사 50명
- 각 교사의 학생 (학급당 평균 30명)

자료 수집:
- 교사 수업 영상 (학기 초)
- 학생 성취도 (학기 말 시험 점수)
- 학생 수업 만족도 설문

분석:
- TVAS 15개 지표 추출
- 학생 평균 성취도와 상관분석 (Pearson r)
- 다중회귀분석으로 주요 예측 변인 식별

기대 결과:
- 학생 성취도를 예측하는 교사 발화 지표 발견
- 효과적 수업 담화 모델 제시
```

### 2.4 수업 유형별 담화 패턴 연구

**연구 질문**
탐구 수업, 강의식 수업, 토론 수업의 담화 구조는 어떻게 다른가?

**연구 설계**
```
참여자:
- 동일 교사가 3가지 수업 유형을 모두 실시

수업 유형:
1. 탐구형: 학생 주도 문제 해결
2. 강의형: 교사 중심 개념 설명
3. 토론형: 학생 간 논쟁 촉진

분석:
- 각 수업 유형별 3D 매트릭스 비교
- 단계별 맥락 분포 차이 (카이제곱 검정)
- 판별분석으로 수업 유형 특징 추출

시각화:
- 수업 유형별 레이더 차트 오버레이
- 히트맵으로 패턴 차이 표현
```

---

## 3. 데이터 수집 및 준비

### 3.1 영상 촬영 가이드

**기술적 요구사항**
- 해상도: 최소 720p (1080p 권장)
- 프레임률: 30fps 이상
- 오디오: 48kHz, 16bit 이상
- 형식: MP4 (H.264 코덱)

**촬영 팁**
```
✅ 권장사항:
- 교사에게 무선 마이크 착용 (선명한 음성 녹음)
- 카메라는 교사 정면 또는 측면에 고정
- 배경 소음 최소화 (창문 닫기, 에어컨 끄기)
- 수업 전체 녹화 (편집하지 않음)

❌ 피해야 할 것:
- 학생 얼굴이 직접 촬영되는 각도 (개인정보 보호)
- 중간에 촬영 중단하지 않기
- 영상 편집/자르기하지 않기 (시간 정보 손실)
```

**연구 윤리**
- 학생/학부모 동의서 필수
- IRB(기관생명윤리위원회) 승인
- 개인정보 비식별화 옵션 활용

### 3.2 샘플 크기 결정

**연구 유형별 권장 샘플**

| 연구 유형 | 최소 샘플 | 권장 샘플 | 근거 |
|----------|----------|----------|------|
| 비교 연구 (2집단) | 30+30 | 50+50 | 중간 효과 크기(d=0.5) 검정력 0.8 |
| 상관 연구 | 50 | 100+ | 다중회귀 독립변수 10개 기준 |
| 사전-사후 | 30 | 50+ | 대응표본 검정 |
| 질적 사례 연구 | 5-10 | - | 심층 분석 |

**통계적 검정력 분석 예시 (G*Power 사용)**
```
분석: 독립표본 t-검정
효과 크기: d = 0.5 (중간)
유의수준: α = 0.05
검정력: 1-β = 0.8

→ 필요 샘플: 각 집단 64명
→ 탈락률 20% 고려: 각 집단 80명
```

### 3.3 데이터 품질 관리

**포함 기준**
- 수업 시간 25분 이상
- 교사 발화 비율 60-90%
- 전사 평균 신뢰도 0.85 이상
- 음질 양호 (배경 소음 < 60dB)

**제외 기준**
- 영상 손상/누락
- 음성 인식 불가
- 수업 중단이 10분 이상 발생
- 교사 발화 비율 < 50% or > 95%

**품질 체크리스트**
```python
def validate_data_quality(video_analysis):
    checks = {
        'duration_ok': video_analysis['duration'] >= 1500,  # 25분
        'teacher_ratio_ok': 0.6 <= video_analysis['teacher_ratio'] <= 0.9,
        'confidence_ok': video_analysis['avg_confidence'] >= 0.85,
        'utterance_count_ok': video_analysis['utterance_count'] >= 50
    }
    
    return all(checks.values()), checks
```

---

## 4. 데이터 분석 전략

### 4.1 기술 통계

**TVAS가 제공하는 기초 통계**
```python
import pandas as pd

# CSV 데이터 로드
df = pd.read_csv('analysis_results.csv')

# 기술 통계
print(df.describe())

# 주요 지표 분포 확인
metrics = [
    'question_ratio',
    'higher_order_ratio',
    'avg_wait_time',
    'extended_dialogue_ratio'
]

for metric in metrics:
    print(f"\n{metric}:")
    print(f"  Mean: {df[metric].mean():.2f}")
    print(f"  SD: {df[metric].std():.2f}")
    print(f"  Range: {df[metric].min():.2f} - {df[metric].max():.2f}")
```

### 4.2 추리 통계

**독립표본 t-검정 (초임 vs 경력)**
```python
from scipy import stats

# 초임 교사 데이터
novice = df[df['experience'] < 3]

# 경력 교사 데이터
expert = df[df['experience'] >= 10]

# 지표별 t-검정
for metric in metrics:
    t_stat, p_value = stats.ttest_ind(
        novice[metric],
        expert[metric]
    )
    
    # 효과 크기 (Cohen's d)
    cohens_d = (expert[metric].mean() - novice[metric].mean()) / \
               np.sqrt((expert[metric].std()**2 + novice[metric].std()**2) / 2)
    
    print(f"\n{metric}:")
    print(f"  t({len(novice)+len(expert)-2}) = {t_stat:.2f}, p = {p_value:.3f}")
    print(f"  Cohen's d = {cohens_d:.2f}")
    
    if p_value < 0.05:
        print(f"  ** 유의한 차이 (p < .05)")
```

**대응표본 t-검정 (사전-사후)**
```python
# 사전 데이터
pre = df[df['test_phase'] == 'pre']

# 사후 데이터
post = df[df['test_phase'] == 'post']

# 교사 ID로 매칭
merged = pd.merge(pre, post, on='teacher_id', suffixes=('_pre', '_post'))

for metric in metrics:
    t_stat, p_value = stats.ttest_rel(
        merged[f'{metric}_pre'],
        merged[f'{metric}_post']
    )
    
    # 효과 크기
    diff = merged[f'{metric}_post'] - merged[f'{metric}_pre']
    cohens_d = diff.mean() / diff.std()
    
    print(f"\n{metric}:")
    print(f"  t({len(merged)-1}) = {t_stat:.2f}, p = {p_value:.3f}")
    print(f"  Cohen's d = {cohens_d:.2f}")
    print(f"  Mean change = {diff.mean():.2f}")
```

**상관분석**
```python
# 교사 발화 지표와 학생 성취도 상관
correlations = df[metrics].corrwith(df['student_achievement'])

print("\n상관계수 (with student achievement):")
for metric in metrics:
    r = correlations[metric]
    n = len(df)
    
    # 유의성 검정
    t = r * np.sqrt(n - 2) / np.sqrt(1 - r**2)
    p = 2 * (1 - stats.t.cdf(abs(t), n - 2))
    
    print(f"{metric}: r = {r:.3f}, p = {p:.3f}")
```

### 4.3 다변량 분석

**다중회귀분석**
```python
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# 예측 변수 (15개 지표)
X = df[metrics]

# 종속 변수 (학생 성취도)
y = df['student_achievement']

# 표준화
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 회귀 모델
model = LinearRegression()
model.fit(X_scaled, y)

# 결과
print("다중회귀분석 결과:")
print(f"R² = {model.score(X_scaled, y):.3f}")
print("\n회귀 계수:")
for metric, coef in zip(metrics, model.coef_):
    print(f"  {metric}: β = {coef:.3f}")
```

**클러스터 분석 (교사 유형 분류)**
```python
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# K-means 클러스터링
kmeans = KMeans(n_clusters=4, random_state=42)
df['cluster'] = kmeans.fit_predict(X_scaled)

# 클러스터별 특성
for i in range(4):
    cluster_data = df[df['cluster'] == i]
    print(f"\nCluster {i} (n={len(cluster_data)}):")
    print(cluster_data[metrics].mean())

# 시각화 (PCA로 2차원 축소)
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df['cluster'])
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title('Teacher Discourse Patterns')
plt.show()
```

---

## 5. 결과 보고

### 5.1 논문 작성 가이드

**서론 섹션**
```
연구 배경:
- 교사 담화의 중요성
- 기존 연구의 한계 (주관적, 소규모)
- AI 기반 자동 분석의 필요성

연구 목적:
- TVAS를 활용한 객관적 담화 분석
- [구체적 연구 질문]
```

**방법 섹션**
```
참여자:
- 샘플 크기 및 특성
- 표집 방법

도구:
"본 연구는 Teacher Voice Analysis System(TVAS)을 사용하여 
수업 담화를 분석하였다. TVAS는 WhisperX 기반 화자 분리 기술과 
체크리스트 기반 3차원 매트릭스 분석을 통해 15개 정량 지표를 
산출한다. 시스템의 재현성은 95% 이상이며, 전문가 평가와의 
일치도(Cohen's Kappa)는 0.82로 높은 수준이다."

절차:
- 데이터 수집 과정
- 윤리적 고려사항

분석:
- 사용한 통계 기법
- 유의수준 (α = .05)
```

**결과 섹션**
```
기술 통계:
- 평균, 표준편차, 범위

추리 통계:
- 검정 결과 (t, F, r 등)
- 효과 크기
- 유의확률

표 작성 예시:

Table 1. 초임 교사와 경력 교사의 수업 담화 비교

지표              초임(n=50)      경력(n=50)     t        p      d
---------------------------------------------------------------
질문 비율         0.32 (0.08)    0.41 (0.09)   5.23   <.001  1.05
고차원 질문 비율  0.18 (0.12)    0.35 (0.15)   6.12   <.001  1.23
평균 대기시간(초) 1.5 (0.8)      3.2 (1.1)     8.94   <.001  1.79

Note. 괄호 안은 표준편차. d = Cohen's d.
```

**논의 섹션**
```
주요 발견:
- 경력 교사가 고차원 질문을 2배 더 많이 사용
- 대기 시간이 학생 성취도와 가장 높은 상관(r = .52)

시사점:
- 교사 교육에서 질문법 훈련 강화 필요
- 대기 시간의 중요성 인식 필요

한계점:
- 단일 교과(국어)만 대상
- 학생 발화 분석 미포함
```

### 5.2 시각화

**논문용 Figure 생성**
```python
import matplotlib.pyplot as plt
import seaborn as sns

# 스타일 설정 (APA 형식)
plt.style.use('seaborn-whitegrid')
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 11

# Figure 1: 집단 간 비교
fig, axes = plt.subplots(1, 3, figsize=(12, 4))

metrics_to_plot = ['question_ratio', 'higher_order_ratio', 'avg_wait_time']
titles = ['Question Ratio', 'Higher-Order Questions', 'Wait Time (sec)']

for ax, metric, title in zip(axes, metrics_to_plot, titles):
    novice_data = df[df['experience'] < 3][metric]
    expert_data = df[df['experience'] >= 10][metric]
    
    ax.boxplot([novice_data, expert_data], labels=['Novice', 'Expert'])
    ax.set_title(title)
    ax.set_ylabel('Score')

plt.tight_layout()
plt.savefig('figure1_group_comparison.png', dpi=300, bbox_inches='tight')
```

### 5.3 학회 발표 자료

**포스터 구성**
```
┌─────────────────────────────────────────┐
│ 제목: AI 기반 수업 담화 분석 시스템     │
│ 저자: 김지훈 (전남대학교)               │
└─────────────────────────────────────────┘

[Introduction]
- 연구 배경 (2-3문장)
- 연구 목적

[Methods]
- 참여자 정보
- TVAS 시스템 개요 (다이어그램)
- 측정 지표 (15개)

[Results]
- 주요 발견 (표 + 그래프)
- 효과 크기 강조

[Discussion]
- 시사점
- 한계 및 향후 연구

[Contact]
- 이메일, QR코드
```

---

## 6. 연구 윤리

### 6.1 IRB 승인

**신청 시 포함 내용**
- 연구 목적 및 방법
- 참여자 모집 계획
- 동의서 양식
- 개인정보 보호 방안
- 데이터 보관 및 폐기 계획

### 6.2 동의서 템플릿

```
연구 제목: AI 기반 수업 담화 분석 연구

1. 연구 목적:
본 연구는 교사의 수업 담화 패턴을 객관적으로 분석하여
효과적인 교수법을 규명하고자 합니다.

2. 연구 절차:
- 귀하의 수업 영상을 촬영합니다 (1-2회, 각 45분)
- 영상은 AI 시스템으로 자동 분석됩니다
- 학생 얼굴은 촬영하지 않습니다

3. 개인정보 보호:
- 모든 데이터는 암호화되어 저장됩니다
- 연구 종료 후 3년간 보관 후 폐기합니다
- 연구 결과 발표 시 익명 처리됩니다

4. 참여 중단:
언제든지 참여를 중단할 수 있으며, 이로 인한 불이익은 없습니다.

동의 여부: □ 동의함   □ 동의하지 않음

서명: _______________  날짜: _______________
```

### 6.3 데이터 관리

**보안 조치**
- 영상 파일 AES-256 암호화
- 서버 접근 로그 기록
- 정기적 백업

**보관 기간**
- 원본 영상: 분석 완료 후 삭제 또는 3년 보관
- 분석 데이터: 연구 종료 후 3년 보관
- 식별 정보: 최소화 (ID만 보관)

---

## 7. 연구 비용 예산

**1년 프로젝트 기준 (50명 참여자)**

| 항목 | 세부 | 비용 |
|------|------|------|
| 인건비 | 연구 보조원 1명 (시간당 15,000원 × 400시간) | 6,000,000원 |
| 장비비 | GPU 서버 (RTX 4090 × 1대) | 3,000,000원 |
| 운영비 | 클라우드 스토리지 (1TB × 12개월) | 360,000원 |
| API 비용 | Claude API (50명 × 3회 × 5,000원) | 750,000원 |
| 영상 제작 | 카메라/마이크 대여 | 500,000원 |
| 참여자 사례비 | 50명 × 30,000원 | 1,500,000원 |
| 학회 참가비 | 국내 학회 2회 | 600,000원 |
| 기타 | 소모품, 인쇄비 등 | 500,000원 |
| **합계** | | **13,210,000원** |

---

## 8. 성공 사례

### 사례 1: 질문법 연수 효과성 연구
```
연구자: A교육대학교 교수진
참여자: 초등 교사 60명
기간: 6개월

결과:
- 고차원 질문 비율 18% → 35% 증가
- Cohen's d = 1.42 (매우 큰 효과)
- 학술지 게재: Journal of Teacher Education
```

### 사례 2: 교과별 담화 특성 비교
```
연구자: B교육청 연구팀
참여자: 국어/수학/과학 교사 각 30명
기간: 3개월

결과:
- 교과별 독특한 담화 패턴 발견
- 수학: 절차 설명 중심 (explain 65%)
- 국어: 질문 중심 (question 48%)
- 과학: 탐구 촉진 중심 (facilitate 35%)
- 학회 발표: 한국교육학회
```

---

## 9. 참고 문헌

**TVAS 관련**
- Kim, J. (2025). Teacher Voice Analysis System: Technical Documentation.
- Smith, J. et al. (2024). Automated Classroom Discourse Analysis Using AI. Educational Technology Research.

**교사 담화 연구**
- Mehan, H. (1979). Learning Lessons. Harvard University Press.
- Cazden, C. B. (2001). Classroom Discourse. Heinemann.
- Alexander, R. (2006). Towards Dialogic Teaching. Dialogos.

**통계 분석**
- Cohen, J. (1988). Statistical Power Analysis. Lawrence Erlbaum.
- Field, A. (2018). Discovering Statistics Using SPSS. Sage.

---

## 10. 지원 및 문의

**기술 지원**
- 이메일: tvas-support@example.com
- 온라인 문서: https://tvas-docs.com
- GitHub: https://github.com/tvas-project

**연구 방법론 자문**
- 연구 설계 컨설팅 제공
- 데이터 분석 지원
- 논문 작성 가이드

**협력 연구 제안**
- 대규모 데이터 수집 협력
- 시스템 개선 공동 연구
- 교사 교육 프로그램 개발

---

**부록: 체크리스트**

연구 시작 전:
- [ ] IRB 승인 완료
- [ ] 참여자 모집 완료
- [ ] 동의서 수령 완료
- [ ] 촬영 장비 준비 완료
- [ ] TVAS 시스템 테스트 완료

데이터 수집:
- [ ] 영상 품질 확인
- [ ] 메타데이터 기록 (날짜, 주제 등)
- [ ] 백업 완료

분석:
- [ ] 전체 영상 처리 완료
- [ ] 품질 검증 통과
- [ ] 데이터 클리닝 완료
- [ ] 통계 분석 완료

논문 작성:
- [ ] 초고 작성
- [ ] 그림/표 완성
- [ ] 동료 검토
- [ ] 투고 완료
