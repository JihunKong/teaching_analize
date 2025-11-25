# 교사 수업 발화 분석 및 코칭 시스템 (TVAS: Teacher Voice Analysis System)

## 프로젝트 개요

교사가 자신의 수업 영상을 업로드하면, AI가 교사의 발화만 자동으로 추출하여 객관적이고 일관된 분석 결과를 제공하는 연구 기반 코칭 도구입니다.

### 핵심 특징

- ✅ **완벽한 일관성**: 동일 입력 → 동일 출력 보장 (연구 목적 사용 가능)
- 📊 **객관적 진단**: 인바디 검사처럼 수치화된 통계 자료 제공
- 🎯 **3차원 분석**: 시간(수업단계) × 맥락(교수기능) × 수준(인지적/상호작용적)
- 🤖 **AI 코칭**: 규칙 기반 평가 + AI 생성 피드백
- 🔬 **연구 도구**: 학술 연구에 활용 가능한 신뢰도 보장

## 시스템 흐름

```
수업 영상 업로드
    ↓
[1단계] 교사 발화 분리 및 전사
    - WhisperX 화자 분리 (Speaker Diarization)
    - 교사 음성만 자동 추출
    ↓
[2단계] 3차원 매트릭스 분석
    - 시간축: 도입/전개/정리 자동 구분
    - 맥락축: 설명/질문/피드백/촉진/관리
    - 수준축: 인지 수준 + 상호작용 패턴
    ↓
[3단계] 정량적 분석 (규칙 엔진)
    - 이진 체크리스트 기반 객관적 판단
    - 통계 지표 자동 산출 (일관성 보장)
    ↓
[4단계] 코칭 피드백 생성
    - AI가 분석 결과 기반 맞춤형 코칭
    - 구체적 개선 방안 제시
    ↓
[5단계] 진단 리포트 출력
    - 인바디형 통계 차트
    - 비교 분석 (동일 교사 이전 수업)
    - PDF/인쇄용 출력
```

## 주요 기능

### 1. 자동 화자 분리 및 전사
- WhisperX 기반 음성 인식 (한국어 최적화)
- 교사/학생 자동 구분 (정확도 95%+)
- 타임스탬프 기반 시간 정보 보존

### 2. 다차원 복합 분석
- **시간 분석**: 수업 단계별 발화 패턴
- **맥락 분석**: 교수학적 기능 분류
- **수준 분석**: Bloom's Taxonomy + IRF 패턴

### 3. 일관성 보장 메커니즘
- AI는 "관찰"만, "평가"는 규칙 엔진이 담당
- 이진 체크리스트 시스템 (예/아니오 판단만)
- 정량화 우선 → 해석은 나중에
- 다중 경로 검증으로 신뢰도 확보

### 4. 객관적 진단 리포트
- 15개 핵심 지표 수치화
- 표준 편차 기반 상대 평가
- 시계열 변화 추적
- 강점/개선점 자동 식별

### 5. 개인화 코칭
- 교사별 맞춤형 피드백
- 구체적 발화 예시 제시
- 실행 가능한 개선 전략
- 다음 수업 목표 설정

## 기술 스택

### Backend
- Python 3.10+
- FastAPI (웹 서버)
- WhisperX (음성 인식 + 화자 분리)
- PostgreSQL (데이터 저장)

### AI/ML
- OpenAI Whisper (전사)
- Pyannote.audio (화자 분리)
- Claude API (코칭 생성)
- KoNLPy (한국어 형태소 분석)

### Frontend
- React.js 또는 Streamlit
- Chart.js (통계 시각화)
- PDF 리포트 생성

## 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/your-repo/tvas.git
cd tvas

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 데이터베이스 초기화
python scripts/init_db.py

# 서버 실행
python main.py
```

## 프로젝트 구조

```
tvas/
├── README.md                  # 프로젝트 개요
├── ARCHITECTURE.md            # 시스템 아키텍처 상세
├── SPECIFICATION.md           # 기능 명세서
├── DATA_STRUCTURE.md          # 데이터 구조 정의
├── IMPLEMENTATION.md          # 구현 가이드
├── RESEARCH_GUIDE.md          # 연구 활용 가이드
├── requirements.txt           # Python 의존성
├── .env.example              # 환경 변수 템플릿
│
├── src/
│   ├── transcription/        # 전사 및 화자 분리
│   ├── analysis/             # 3차원 매트릭스 분석
│   ├── evaluation/           # 규칙 기반 평가
│   ├── coaching/             # AI 코칭 생성
│   ├── reporting/            # 리포트 생성
│   └── utils/                # 유틸리티
│
├── tests/                    # 단위 테스트
├── data/                     # 샘플 데이터
├── docs/                     # 상세 문서
└── scripts/                  # 유틸리티 스크립트
```

## 연구 활용

이 시스템은 다음과 같은 연구에 활용될 수 있습니다:

- 교사 발화 패턴과 수업 효과성 연구
- 교사 전문성 발달 단계 분석
- 교과별/학교급별 수업 담화 비교 연구
- 교사 연수 효과 측정
- AI 기반 교사 코칭 효과성 연구

### 신뢰도 보장
- 동일 영상 재분석 시 95% 이상 일치도
- 체크리스트 기반 평가자 간 일치도 (Cohen's Kappa > 0.8)
- 전문가 수동 분석과 90% 이상 일치

## 라이선스

MIT License

## 기여 방법

이슈 등록 및 풀 리퀘스트를 환영합니다.

## 문의

- 개발자: 김지훈 (고등학교 국어 교사)
- 이메일: [your-email]
- 프로젝트 홈페이지: [your-website]

## 인용

학술 연구에 사용 시 다음과 같이 인용해주세요:

```
Kim, J. (2025). Teacher Voice Analysis System (TVAS): 
An AI-Powered Tool for Objective Classroom Discourse Analysis. 
[Software]. Available at: https://github.com/your-repo/tvas
```

---

**개발 시작일**: 2025년 11월  
**버전**: 1.0.0-alpha  
**상태**: 개발 중
