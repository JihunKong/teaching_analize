# # AIBOA (AI-Based Observation and Analysis) 수업 분석 시스템

## 📋 프로젝트 개요

AIBOA는 교실 수업을 AI로 분석하여 교사의 수업 개선을 지원하는 모듈형 분석 플랫폼입니다. 영상 스크립트 추출과 CBIL 분석을 독립적으로 운영할 수 있어 유연한 워크플로우를 제공합니다.

## 🎯 핵심 특징

1. **모듈형 설계**: 스크립트 추출과 분석 프로세스 분리
2. **Railway 기반 배포**: 간편한 배포와 자동 스케일링
3. **유연한 데이터 입력**: 영상, 오디오, 텍스트 등 다양한 입력 지원
4. **표준화된 CBIL 평가**: 7단계 평가 체계로 일관된 분석
5. **비용 효율적**: 필요한 모듈만 선택 사용 가능

## 🏗️ 시스템 아키텍처 (Railway 기반)

### 모듈형 마이크로서비스 구조

```
┌──────────────────────────────────────────────────────────┐
│                     Railway Platform                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │  Transcription  │         │    Analysis     │        │
│  │     Service     │         │     Service     │        │
│  │   (FastAPI)     │         │   (FastAPI)     │        │
│  └────────┬────────┘         └────────┬────────┘        │
│           │                            │                  │
│  ┌────────▼────────┐         ┌────────▼────────┐        │
│  │   PostgreSQL    │         │   PostgreSQL    │        │
│  │   (Railway)     │         │   (Railway)     │        │
│  └─────────────────┘         └─────────────────┘        │
│                                                           │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │  Redis Queue    │         │  Static Files   │        │
│  │   (Railway)     │         │  (Railway Vol)  │        │
│  └─────────────────┘         └─────────────────┘        │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## 📦 모듈 구성

### Module 1: Transcription Service (전사 서비스)
독립적으로 운영 가능한 음성-텍스트 변환 서비스

**기능:**
- 영상/오디오 파일 업로드
- YouTube URL 입력 지원
- 다양한 STT 엔진 선택 (Whisper, YouTube 자막)
- 화자 분리 (옵션)
- 타임스탬프 포함 스크립트 생성
- JSON, SRT, TXT 형식 내보내기

**엔드포인트:**
```
POST /api/transcribe/upload     # 파일 업로드
POST /api/transcribe/youtube    # YouTube URL 처리
GET  /api/transcribe/{job_id}   # 진행 상황 확인
GET  /api/transcripts/{id}      # 스크립트 다운로드
```

### Module 2: Analysis Service (분석 서비스)
텍스트 기반 CBIL 분석 서비스

**기능:**
- 텍스트/스크립트 파일 업로드
- Transcription Service와 연동
- CBIL 7단계 자동 분류
- 발화별 상세 분석
- 통계 및 시각화
- PDF 리포트 생성

**엔드포인트:**
```
POST /api/analyze/text          # 텍스트 직접 입력
POST /api/analyze/transcript    # 전사 결과 연동
GET  /api/analysis/{id}         # 분석 결과 조회
GET  /api/reports/{id}          # 리포트 다운로드
GET  /api/statistics            # 통계 대시보드
```

### Module 3: Dashboard (선택적)
웹 기반 통합 대시보드

**기능:**
- 두 서비스 통합 뷰
- 배치 작업 관리
- 실시간 진행 모니터링
- 히스토리 및 검색

## 🚀 Railway 배포 가이드

### 1. Railway 프로젝트 설정

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 새 프로젝트 생성
railway init
```

### 2. 서비스별 배포

#### Transcription Service
```yaml
# railway.toml (transcription-service)
[build]
builder = "DOCKERFILE"
dockerfilePath = "./services/transcription/Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"

[[services]]
name = "transcription-api"
port = 8000
```

#### Analysis Service
```yaml
# railway.toml (analysis-service)
[build]
builder = "DOCKERFILE"
dockerfilePath = "./services/analysis/Dockerfile"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"

[[services]]
name = "analysis-api"
port = 8001
```

### 3. 환경 변수 설정

```bash
# Railway 대시보드 또는 CLI로 설정
railway variables set OPENAI_API_KEY=xxx
railway variables set UPSTAGE_API_KEY=xxx
railway variables set SOLAR_API_KEY=xxx
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
railway variables set RAILWAY_VOLUME_PATH=/data
```

### 4. 데이터베이스 프로비저닝

```bash
# PostgreSQL 추가
railway add postgresql

# Redis 추가
railway add redis

# 마이그레이션 실행
railway run python manage.py migrate
```

## 💾 Railway 스토리지 전략

### Volume 마운트 구조
```
/data
├── uploads/          # 임시 업로드 파일
├── transcripts/      # 생성된 스크립트
├── analysis/         # 분석 결과
└── reports/          # PDF 리포트
```

### 스토리지 최적화
- 30일 이상 파일 자동 삭제
- 압축 저장 (gzip)
- CDN 연동 (Cloudflare)

## 📊 CBIL 평가 체계

### 독립적 평가 모듈
```python
class CBILAnalyzer:
    def __init__(self):
        self.levels = {
            1: "단순 확인",
            2: "사실 회상",
            3: "개념 설명",
            4: "분석적 사고",
            5: "종합적 이해",
            6: "평가적 판단",
            7: "창의적 적용"
        }
    
    def analyze_utterance(self, text, context=None):
        # 발화 분석 로직
        features = self.extract_features(text)
        level = self.classify_level(features, context)
        confidence = self.calculate_confidence(features, level)
        return {
            "text": text,
            "level": level,
            "confidence": confidence,
            "features": features
        }
```

## 🔧 기술 스택

### Core Services
- **Runtime**: Python 3.11
- **Framework**: FastAPI
- **Queue**: Celery + Redis
- **Database**: PostgreSQL (Railway)
- **Storage**: Railway Volumes

### AI/ML
- **STT**: OpenAI Whisper / YouTube API
- **LLM**: Solar-mini (한국어 최적화)
- **Embedding**: Sentence Transformers

### Frontend (선택적)
- **Framework**: Next.js 14 / Streamlit
- **UI**: Tailwind CSS / shadcn/ui
- **Charts**: Recharts

## 📈 사용 시나리오

### 시나리오 1: 영상 → 분석 (통합)
```
1. Transcription Service에 영상 업로드
2. 자동으로 스크립트 생성
3. Analysis Service로 자동 전송
4. CBIL 분석 및 리포트 생성
```

### 시나리오 2: 기존 스크립트 분석
```
1. Analysis Service에 직접 텍스트 입력
2. CBIL 분석 수행
3. 결과 확인 및 다운로드
```

### 시나리오 3: 배치 처리
```
1. 여러 파일 일괄 업로드
2. 큐에 작업 등록
3. 순차적 처리
4. 완료 시 이메일 알림
```

## 💰 비용 분석 (Railway 기준)

### 월간 예상 비용
```
Railway Hobby Plan: $5/월
- 8GB RAM
- $5 크레딧 포함

추가 사용량:
- PostgreSQL: ~$5/월 (10GB)
- Redis: ~$5/월
- 스토리지: ~$2/월 (20GB)
- 총: ~$17/월 (인프라)

API 비용:
- Whisper: $0.30 × 100개 = $30
- Solar LLM: $0.002 × 100개 = $0.2
- 총: ~$30/월 (100개 수업 기준)

전체: ~$47/월
```

## 🔐 보안 설정

### Railway 보안 기능
- 자동 HTTPS
- 환경 변수 암호화
- Private Networking
- IP Allowlist (Team Plan)

### 애플리케이션 보안
```python
# API 키 인증
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403)
```

## 📝 API 사용 예시

### 영상 전사 요청
```bash
curl -X POST https://transcription.railway.app/api/transcribe/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@lesson.mp4" \
  -F "language=ko"
```

### 분석 요청
```bash
curl -X POST https://analysis.railway.app/api/analyze/text \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "수업 전사 텍스트...",
    "metadata": {
      "subject": "국어",
      "grade": 10
    }
  }'
```

## 🚦 모니터링

### Railway 내장 모니터링
- CPU/Memory 사용량
- 요청 수 및 응답 시간
- 로그 스트리밍
- 비용 추적

### 커스텀 메트릭
```python
# Prometheus 메트릭 예시
from prometheus_client import Counter, Histogram

transcription_counter = Counter('transcriptions_total', 'Total transcriptions')
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')
```

## 🔄 CI/CD

### GitHub Actions + Railway
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: railwayapp/deploy-action@v1
        with:
          token: ${{ secrets.RAILWAY_TOKEN }}
          service: transcription-service
```

## 📚 문서 및 지원

- API 문서: https://your-app.railway.app/docs
- 사용자 가이드: /docs/user-guide.md
- 문제 해결: /docs/troubleshooting.md
- 지원: support@aiboa.edu
