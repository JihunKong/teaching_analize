# TVAS 빠른 시작 가이드

## 🎯 목표

기존 teaching_analize의 YouTube 전사 + CBIL 분석 기능에 **WhisperX 화자 분리**와 **3D 매트릭스 분석**을 추가하여 연구용 교사 발화 분석 시스템 완성

## ✅ 현재 상태 (2025-11-08)

### 완료된 작업
1. ✅ Docker Compose 환경 구성 (Apple Silicon 최적화)
2. ✅ `.env` 파일 설정 (OpenAI API + HuggingFace 토큰)
3. ✅ Nginx 리버스 프록시 설정
4. ✅ Transcription Service 업데이트
   - WhisperX 통합 코드 추가
   - 오디오/텍스트 처리 유틸리티
   - 화자 분리 로직

### 다음 단계
1. 🚧 Analysis Service 구현 (3D 매트릭스)
2. 🚧 Evaluation Service 통합 (CBIL + 15개 지표)
3. 🚧 Frontend 재디자인

## 🚀 지금 바로 실행하기

### 방법 1: 기존 시스템 그대로 사용 (YouTube 전사 + CBIL)

```bash
cd /Users/jihunkong/teaching_analize

# 기존 Docker Compose 사용
docker-compose -f docker-compose.local.yml up -d

# 접속
open http://localhost:8080
```

**기능**:
- YouTube URL 입력 → 자동 전사 (3단계 fallback)
- CBIL 7단계 분석
- PDF 리포트 생성

### 방법 2: 새로운 통합 시스템 (WhisperX 추가)

```bash
cd /Users/jihunkong/teaching_analize

# 새로운 docker-compose.yml 사용
docker-compose up -d

# 접속
open http://localhost
```

**추가 기능**:
- 로컬 WhisperX 전사 + 화자 분리
- 교사/학생 음성 자동 구분
- (구현 예정) 3D 매트릭스 분석

## 📝 현재 구현 상태 상세

### Module 1: Transcription Service ✅

**위치**: `/services/transcription/`

**완료된 부분**:
- `core/whisperx_service.py` - WhisperX 통합 (화자 분리 포함)
- `utils/audio_processing.py` - FFmpeg 오디오 추출
- `utils/text_preprocessing.py` - 한국어 텍스트 정제
- `requirements.txt` - 의존성 업데이트 (WhisperX, PyTorch, Pyannote)
- Dockerfile - FFmpeg + git 추가

**아직 필요한 작업**:
- `main.py`에 WhisperX 엔드포인트 추가
- 기존 YouTube 전사와 통합
- 데이터베이스 스키마 업데이트 (화자 정보 저장)

### Module 2: Analysis Service 🚧

**위치**: `/services/analysis/`

**기존 상태**:
- Dockerfile ✅
- requirements.txt ✅
- main.py (CBIL 분석 가능) ✅

**추가 필요**:
- 3D 매트릭스 분석 로직
- 체크리스트 시스템
- OpenAI API 통합 (체크리스트 실행용)

### Module 3: Evaluation Service 🚧

**기존 기능**: CBIL 분석, PDF 생성

**추가 필요**:
- 15개 정량 지표 계산
- 패턴 매칭
- OpenAI 코칭 생성

### Module 4: Reporting Service 🚧

**기존 기능**: PDF 생성, 차트

**추가 필요**:
- 3D 히트맵
- 레이더 차트 (15개 지표)
- 인바디형 리포트

## 🔧 개발 워크플로우

### 1. 기존 시스템 테스트

```bash
# 기존 시스템 실행
docker-compose -f docker-compose.local.yml up -d

# Transcription 서비스 테스트
curl -X POST http://localhost:8002/transcribe \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://youtube.com/watch?v=VIDEO_ID", "language": "ko"}'

# Analysis 서비스 테스트
curl http://localhost:8003/health
```

### 2. WhisperX 테스트 (새로운 기능)

```bash
# 새로운 시스템 실행
docker-compose up -d

# WhisperX 서비스 확인
docker-compose logs -f transcription

# 테스트 (구현 완료 후)
# 영상 파일 업로드 → WhisperX 전사 → 화자 분리
```

### 3. 개발 중 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스
docker-compose logs -f transcription --tail=100
docker-compose logs -f analysis --tail=100
```

## 📊 통합 계획

### Phase 1: Transcription Service 완성 (현재 진행 중)

**목표**: WhisperX를 기존 YouTube 전사와 통합

**작업**:
1. `main.py`에 새로운 엔드포인트 추가:
   ```python
   @app.post("/transcribe/video/whisperx")
   async def transcribe_with_whisperx(file: UploadFile):
       # WhisperX 사용
       # 화자 분리
       # 교사 발화 추출
       return result
   ```

2. 데이터베이스 스키마 확장:
   ```sql
   ALTER TABLE transcription_results
   ADD COLUMN speaker_info JSONB;
   ```

3. Frontend에서 선택 가능:
   - "YouTube URL 전사" (기존)
   - "영상 파일 업로드 + WhisperX" (신규)

### Phase 2: Analysis Service 확장

**목표**: CBIL 분석 + 3D 매트릭스 분석

**작업**:
1. 체크리스트 YAML 파일 작성
2. OpenAI API 호출 로직 (3회 다수결)
3. 3D 매트릭스 빌더
4. 기존 CBIL과 병합

### Phase 3: Evaluation & Reporting

**목표**: 통합 리포트

**작업**:
1. 15개 지표 계산 로직
2. 차트 생성 (Matplotlib)
3. PDF 템플릿 업데이트

### Phase 4: Frontend 재디자인

**목표**: 심플하고 현대적인 UI

**변경**:
- 그라데이션 제거
- 플랫 디자인
- 단일 액센트 색상

## 🎬 다음 즉시 할 일

### Option A: WhisperX 완성하여 테스트 가능하게 만들기

```bash
# 1. main.py에 WhisperX 엔드포인트 추가
# 2. Docker 빌드 및 실행
docker-compose build transcription
docker-compose up -d transcription

# 3. 테스트
# (영상 파일 업로드 테스트)
```

### Option B: 기존 시스템부터 확인

```bash
# 기존이 잘 동작하는지 먼저 확인
docker-compose -f docker-compose.local.yml up -d

# 웹 인터페이스 확인
open http://localhost:8080

# YouTube 전사 테스트
# CBIL 분석 테스트
```

## 💡 권장 진행 방식

1. **먼저**: 기존 시스템 실행 및 테스트 (Option B)
   - YouTube 전사 동작 확인
   - CBIL 분석 확인
   - PDF 리포트 확인

2. **그 다음**: WhisperX 통합 완성 (Option A)
   - Transcription Service 업데이트
   - 테스트용 짧은 영상 준비
   - 화자 분리 정확도 확인

3. **마지막**: 3D 매트릭스 분석 추가
   - Analysis Service 구현
   - 체크리스트 작성
   - OpenAI API 통합

## ❓ 자주 묻는 질문

### Q1: 기존 데이터는 어떻게 되나요?
A: PostgreSQL 데이터베이스가 유지되므로 기존 전사/분석 결과는 그대로 보존됩니다.

### Q2: 두 시스템을 동시에 실행할 수 있나요?
A: 포트가 다르므로 가능합니다:
- 기존: 포트 8080
- 신규: 포트 80

### Q3: WhisperX 처리 시간은?
A: Apple Silicon M1/M2 기준 45분 영상 → 20-30분 예상

### Q4: 비용은 얼마나 드나요?
A: OpenAI API 비용만 발생 (영상당 $0.05-0.10, GPT-4o-mini 기준)

### Q5: GPU가 없으면요?
A: CPU로도 동작하지만 매우 느립니다 (45분 영상 → 2-3시간)

## 📞 문의

- 개발자: 김지훈
- 이메일: [your-email]
- 프로젝트: /Users/jihunkong/teaching_analize

---

**마지막 업데이트**: 2025-11-08
**다음 작업**: Transcription Service `main.py` 업데이트
