# TVAS - Teacher Voice Analysis System
## 교사 수업 발화 분석 및 코칭 시스템

통합 및 현대화된 버전 - 로컬 Docker 실행 (Apple Silicon 최적화)

---

## ⚠️ 중요: YouTube 전사 방식 정책

**YouTube 전사는 오직 Selenium 브라우저 자동화만 사용합니다**

- ❌ YouTube Transcript API 사용 절대 금지
- ❌ Playwright 사용 금지
- ✅ Selenium + Chromium만 사용

**상세 정책 및 기술 문서**: [TRANSCRIPT_METHOD.md](TRANSCRIPT_METHOD.md)

---

## 🎯 주요 기능

### 유지된 기능 (기존 teaching_analize)
- ✅ YouTube 자동 전사 (**Selenium 브라우저 자동화 전용** - [정책 문서](TRANSCRIPT_METHOD.md))
- ✅ CBIL 7단계 분석 시스템
- ✅ PDF 리포트 생성
- ✅ 다중 사용자 지원 및 데이터베이스

### 새로 추가된 기능 (AI_analize 설계)
- ✅ WhisperX 로컬 전사 + 화자 분리 (교사/학생 자동 구분)
- ✅ 3차원 매트릭스 분석 (시간×맥락×수준)
- ✅ 체크리스트 기반 일관성 보장 (연구 신뢰도 95%+)
- ✅ 15개 정량 지표 계산 (완전 결정론적)

## 🏗️ 아키텍처

```
TVAS 시스템
├── Module 1: Transcription (전사 & 화자 분리)
│   ├── YouTube: Selenium 브라우저 자동화 (Chromium + ChromeDriver)
│   │   └── 정책: API 사용 절대 금지 (TRANSCRIPT_METHOD.md 참조)
│   └── WhisperX (로컬 오디오, Apple Silicon MPS)
│
├── Module 2: Analysis (3D 매트릭스 분석)
│   ├── 단계 분류 (도입/전개/정리)
│   ├── 맥락 태깅 (설명/질문/피드백/촉진/관리)
│   └── 수준 분류 (L1/L2/L3 인지수준)
│
├── Module 3: Evaluation (평가 & 코칭)
│   ├── CBIL 7단계 분석 (기존 유지)
│   ├── 15개 정량 지표 계산
│   └── OpenAI 코칭 생성
│
├── Module 4: Reporting (리포트 생성)
│   ├── PDF 리포트
│   ├── 차트 생성
│   └── HTML 대시보드
│
└── Frontend (Next.js)
    ├── 심플하고 현대적인 UI
    ├── 업로드 페이지
    ├── 분석 결과 뷰
    └── 리포트 뷰
```

## 🚀 빠른 시작

### 1. 환경 설정

`.env` 파일이 이미 설정되어 있습니다:
- OpenAI API 키 ✅
- HuggingFace 토큰 ✅
- Database 설정 ✅

### 2. Docker 실행

```bash
# 전체 시스템 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f transcription
docker-compose logs -f analysis
```

### 3. 접속

- **Frontend**: http://localhost (포트 80)
- **API Gateway**: http://localhost/api
- **Health Check**: http://localhost/health

### 4. 서비스 재시작

```bash
# 특정 서비스만 재시작
docker-compose restart transcription

# 전체 재시작
docker-compose restart

# 종료
docker-compose down
```

## 📁 프로젝트 구조

```
teaching_analize/
├── docker-compose.yml          # Docker 설정 (Apple Silicon 최적화)
├── .env                         # 환경 변수
├── nginx/                       # Nginx 설정
│
├── services/
│   ├── transcription/          # Module 1
│   │   ├── core/
│   │   │   └── whisperx_service.py
│   │   ├── utils/
│   │   │   ├── audio_processing.py
│   │   │   └── text_preprocessing.py
│   │   ├── main.py
│   │   └── Dockerfile
│   │
│   ├── analysis/               # Module 2 (구현 중)
│   ├── evaluation/             # Module 3 (구현 중)
│   ├── reporting/              # Module 4 (구현 중)
│   └── gateway/                # API Gateway (구현 중)
│
├── frontend/                   # Next.js (재디자인 예정)
└── database/                   # PostgreSQL 스키마
```

## 🔧 개발 상태

### ✅ 완료
1. Docker Compose 환경 구성
2. Transcription Service 기본 구조
3. WhisperX 통합
4. 오디오/텍스트 처리 유틸리티

### 🚧 진행 중
1. Analysis Service (3D 매트릭스)
2. Evaluation Service (CBIL + 15개 지표)
3. Reporting Service
4. API Gateway
5. Frontend 재디자인

## 🎯 API 엔드포인트 (계획)

### Transcription Service
```
POST   /transcribe/video       # 영상 파일 업로드
POST   /transcribe/youtube     # YouTube URL
GET    /transcribe/{id}/status # 진행 상황
GET    /transcribe/{id}/result # 결과 조회
```

### Analysis Service
```
POST   /analyze                # 3D 매트릭스 분석
GET    /analyze/{id}/result    # 분석 결과
```

### Evaluation Service
```
POST   /evaluate               # 평가 및 코칭
GET    /evaluate/{id}/result   # 평가 결과
```

### Reporting Service
```
POST   /report/generate        # 리포트 생성
GET    /report/{id}/pdf        # PDF 다운로드
GET    /report/{id}/html       # HTML 뷰
```

### Gateway (통합)
```
POST   /api/workflow/analyze   # 전체 파이프라인 실행
GET    /api/workflow/{id}      # 워크플로우 상태
```

## 🔑 주요 기술

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: Next.js 14 + React 18 + TypeScript
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **AI**: OpenAI GPT-4o-mini + WhisperX large-v3
- **Container**: Docker + Docker Compose
- **GPU**: Apple Silicon MPS (Metal Performance Shaders)

## 📊 예상 성능 (Apple Silicon)

| 작업 | 예상 시간 |
|------|-----------|
| YouTube 전사 (45분) | 1-2분 |
| WhisperX 전사 (45분) | 20-30분 |
| 화자 분리 | 5-10분 |
| 3D 매트릭스 분석 | 2-5분 |
| 평가 및 코칭 | 1-2분 |
| **전체 파이프라인** | **30-50분** |

## 💰 비용 (OpenAI API)

- 체크리스트 실행: ~30,000 토큰/영상
- 코칭 생성: ~5,000 토큰
- **합계**: ~$0.05-0.10/영상 (GPT-4o-mini)

## 📝 다음 단계

1. ✅ ~~Docker 환경 구성~~
2. ✅ ~~Module 1 기본 구조~~
3. ⏳ Module 2-4 구현
4. ⏳ API Gateway 구현
5. ⏳ Frontend 재디자인
6. ⏳ 통합 테스트

## 🐛 문제 해결

### Docker 실행 오류
```bash
# 기존 컨테이너 정리
docker-compose down -v

# 이미지 재빌드
docker-compose build --no-cache

# 다시 실행
docker-compose up -d
```

### GPU 사용 확인
```python
import torch
print(f"MPS available: {torch.backends.mps.is_available()}")
print(f"MPS built: {torch.backends.mps.is_built()}")
```

### 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스
docker-compose logs -f transcription --tail=100
```

## 📚 참고 문서

- `ARCHITECTURE.md` - 시스템 아키텍처 상세
- `SPECIFICATION.md` - 기능 명세서
- `DATA_STRUCTURE.md` - 데이터 구조
- `IMPLEMENTATION.md` - 구현 가이드

---

**개발자**: 김지훈
**버전**: 2.0.0-alpha
**최종 업데이트**: 2025-11-08
