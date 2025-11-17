# 🚀 TVAS 시작 가이드

## ✅ 완료된 작업 (2025-11-08)

### 1. Docker 환경 구성 ✅
- `docker-compose.yml` - Apple Silicon 최적화 완료
- `.env` - OpenAI API 키 + HuggingFace 토큰 설정 완료
- `nginx/nginx.conf` - 리버스 프록시 설정 완료

### 2. Transcription Service (Module 1) ✅
- **WhisperX 통합 완료**
  - `core/whisperx_service.py` - 로컬 전사 + 화자 분리
  - `utils/audio_processing.py` - FFmpeg 오디오 추출
  - `utils/text_preprocessing.py` - 한국어 텍스트 정제
  - `main.py` - WhisperX API 엔드포인트 추가

- **기존 기능 유지**
  - YouTube 자동 전사 (3단계 fallback)
  - Browser automation
  - 데이터베이스 저장

### 3. 추가 생성된 문서
- `README_TVAS.md` - 프로젝트 전체 개요
- `QUICK_START.md` - 빠른 시작 가이드
- `START_HERE.md` - 이 파일

---

## 🎯 두 가지 실행 옵션

### Option A: 기존 시스템 실행 (안정적, 검증됨)

```bash
cd /Users/jihunkong/teaching_analize

# 기존 Docker Compose 사용
docker-compose -f docker-compose.local.yml up -d

# 로그 확인
docker-compose -f docker-compose.local.yml logs -f

# 웹 접속
open http://localhost:8080
```

**제공되는 기능**:
- ✅ YouTube URL 입력 → 자동 전사
- ✅ CBIL 7단계 분석
- ✅ PDF 리포트 생성
- ✅ 다중 사용자 지원

### Option B: 새로운 통합 시스템 (WhisperX 포함)

```bash
cd /Users/jihunkong/teaching_analize

# 새로운 Docker Compose 사용
docker-compose up --build -d

# 로그 확인
docker-compose logs -f transcription

# 웹 접속
open http://localhost
```

**추가 기능**:
- ✅ 로컬 WhisperX 전사 (Apple Silicon MPS)
- ✅ 화자 분리 (교사/학생 자동 구분)
- ✅ 교사 발화만 추출
- ⏳ 3D 매트릭스 분석 (구현 예정)

---

## 📝 WhisperX API 사용 방법

### 1. 서비스 실행 (Option B 선택 시)

```bash
# 서비스 실행
docker-compose up -d transcription redis db

# 서비스 상태 확인
docker-compose ps

# Transcription 서비스 로그
docker-compose logs -f transcription
```

### 2. 영상 파일 업로드 및 전사

```bash
# curl을 사용한 테스트
curl -X POST http://localhost:8000/api/transcribe/video/whisperx \
  -F "file=@/path/to/your/video.mp4" \
  -F "min_speakers=2" \
  -F "max_speakers=5"

# 응답 예시:
# {
#   "success": true,
#   "job_id": "abc123-def456-...",
#   "message": "Video uploaded successfully. Processing started.",
#   "status_url": "/api/jobs/abc123-def456-.../status"
# }
```

### 3. 처리 상태 확인

```bash
# job_id를 사용하여 상태 확인
curl http://localhost:8000/api/jobs/{job_id}/status

# 응답 예시 (처리 중):
# {
#   "job_id": "abc123-...",
#   "status": "processing",
#   "message": "Transcribing and separating speakers...",
#   "created_at": "2025-11-08T...",
#   "updated_at": "2025-11-08T..."
# }

# 응답 예시 (완료):
# {
#   "job_id": "abc123-...",
#   "status": "success",
#   "message": "Transcription complete",
#   "result": {
#     "success": true,
#     "method_used": "whisperx_local",
#     "teacher_speaker_id": "SPEAKER_00",
#     "teacher_utterances": [...],
#     "speaker_stats": {...},
#     "statistics": {
#       "total_segments": 150,
#       "teacher_segments": 120,
#       "teacher_ratio": 0.8,
#       "total_words": 3500,
#       "total_duration": 2700.5
#     }
#   }
# }
```

### 4. 서비스 통계 확인

```bash
curl http://localhost:8000/api/stats

# 응답:
# {
#   "total_jobs": 5,
#   "service": "transcription",
#   "whisperx_available": true,
#   "timestamp": "2025-11-08T...",
#   "status_breakdown": {
#     "success": 3,
#     "processing": 1,
#     "failed": 1
#   },
#   "transcripts_in_database": 10
# }
```

---

## 🐛 문제 해결

### 1. WhisperX 모델 다운로드 실패

```bash
# 컨테이너 내부에서 수동 다운로드
docker-compose exec transcription python -c "import whisperx; whisperx.load_model('large-v3', 'mps', language='ko')"
```

### 2. MPS (Metal) 사용 안 됨

```bash
# 환경 변수 확인
docker-compose exec transcription python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"

# CPU로 대체 (느림)
# .env 파일 수정: DEVICE=cpu
```

### 3. 메모리 부족

```bash
# Docker Desktop 메모리 증가
# Settings → Resources → Memory → 8GB 이상 권장

# 또는 작은 모델 사용
# .env 파일 수정: WHISPER_MODEL=base
```

### 4. 컨테이너 재시작

```bash
# 특정 서비스만
docker-compose restart transcription

# 전체 재시작
docker-compose restart

# 완전히 새로 빌드
docker-compose down
docker-compose build --no-cache transcription
docker-compose up -d
```

### 5. 로그 확인

```bash
# 실시간 로그
docker-compose logs -f transcription

# 최근 100줄
docker-compose logs transcription --tail=100

# 에러만 필터링
docker-compose logs transcription 2>&1 | grep -i error
```

---

## 📊 예상 처리 시간 (Apple Silicon)

| 작업 | M1/M2 Pro | M1/M2 Max |
|------|----------|-----------|
| 모델 로딩 (최초 1회) | 30초-1분 | 20-30초 |
| 15분 영상 전사 | 8-12분 | 5-8분 |
| 45분 영상 전사 | 20-30분 | 15-20분 |
| 화자 분리 | 3-5분 | 2-3분 |
| 텍스트 전처리 | 5-10초 | 3-5초 |
| **전체 (45분 영상)** | **30-40분** | **20-30분** |

---

## 💰 비용 예상

### YouTube 전사 (기존)
- **비용**: $0 (무료)
- **제한사항**: YouTube에 자막이 있어야 함

### WhisperX 로컬 (신규)
- **비용**: $0 (로컬 실행)
- **장점**: 모든 영상 처리 가능, 화자 분리 지원
- **단점**: 처리 시간 오래 걸림, GPU 필요

### 3D 매트릭스 분석 (구현 예정)
- **OpenAI API**: 영상당 $0.05-0.10 (GPT-4o-mini)
- **체크리스트 실행**: ~30,000 토큰
- **코칭 생성**: ~5,000 토큰

---

## 🎬 권장 워크플로우

### 1단계: 기존 시스템으로 시작

```bash
# Option A로 시작
docker-compose -f docker-compose.local.yml up -d

# YouTube 전사 테스트
# 웹 UI에서 YouTube URL 입력

# CBIL 분석 확인
# PDF 리포트 확인
```

### 2단계: WhisperX 테스트

```bash
# Option B로 전환
docker-compose -f docker-compose.local.yml down
docker-compose up --build -d

# 짧은 영상으로 테스트 (5-10분)
# 화자 분리 정확도 확인
```

### 3단계: 통합 사용

- YouTube 영상 → 기존 방식 (빠름)
- 로컬 영상 파일 → WhisperX (화자 분리 필요 시)
- 연구용 데이터 → WhisperX (재현성 보장)

---

## 📚 다음 단계

### 즉시 가능
1. YouTube 전사 테스트
2. CBIL 분석 테스트
3. PDF 리포트 생성 테스트

### 구현 필요
1. Analysis Service (3D 매트릭스) 🚧
2. Evaluation Service (15개 지표) 🚧
3. Frontend 재디자인 🚧
4. API Gateway 통합 🚧

---

## 📞 도움말

### 문서
- `README_TVAS.md` - 전체 프로젝트 개요
- `QUICK_START.md` - 상세 가이드
- `ARCHITECTURE.md` - 시스템 아키텍처 (AI_analize 참조)
- `SPECIFICATION.md` - 기능 명세 (AI_analize 참조)

### 로그
- Transcription: `docker-compose logs -f transcription`
- Analysis: `docker-compose logs -f analysis`
- Database: `docker-compose logs -f db`
- Redis: `docker-compose logs -f redis`

### 디버깅
```bash
# 컨테이너 내부 접속
docker-compose exec transcription /bin/bash

# Python 인터프리터 실행
docker-compose exec transcription python

# 의존성 확인
docker-compose exec transcription pip list | grep whisperx
```

---

## ✨ 주요 개선점 (기존 대비)

1. **화자 분리**: 교사/학생 음성 자동 구분 ✅
2. **로컬 실행**: 인터넷 없이도 전사 가능 ✅
3. **비용 절감**: YouTube API 제한 없음 ✅
4. **연구 신뢰도**: 재현 가능한 결과 (향후 구현)
5. **3D 분석**: 시간×맥락×수준 다차원 분석 (향후 구현)

---

**마지막 업데이트**: 2025-11-08 21:30
**다음 작업**: Analysis Service 구현 시작
**개발자**: 김지훈
