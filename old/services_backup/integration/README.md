# 교육 분석 통합 서비스 (Integration Service)

YouTube 영상 전사와 교육 분석을 연결하는 통합 워크플로우 서비스입니다.

## 기능

### 🔄 통합 워크플로우
- **YouTube URL → 전사 → 교육 분석** 원스톱 처리
- 비동기 작업 추적 및 상태 관리
- 실패 시 재시도 및 에러 핸들링
- 결과 통합 및 리포트 생성

### 📊 지원하는 분석 유형
1. **교육 코칭 분석** (`teaching-coach`): 15개 항목 수업 설계/실행 분석
2. **대화 패턴 분석** (`dialogue-patterns`): 질문 유형 및 대화 패턴 정량 분석
3. **CBIL 평가** (`cbil-evaluation`): 개념기반 탐구학습 7단계 평가
4. **종합 분석** (`comprehensive`): 위 3가지 분석을 모두 포함

## 설치 및 실행

### 1. 의존성 설치
```bash
cd services/integration
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
export TRANSCRIPTION_SERVICE_URL="https://teachinganalize-production.up.railway.app"
export ANALYSIS_SERVICE_URL="http://localhost:8001"
export API_KEY="your-api-key"
```

### 3. 서비스 실행
```bash
python main.py
```
서비스는 http://localhost:8002 에서 실행됩니다.

## API 사용법

### 📹 YouTube 영상 분석 시작
```bash
curl -X POST "http://localhost:8002/api/analyze-youtube" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "language": "ko",
    "analysis_types": ["comprehensive"]
  }'
```

**응답:**
```json
{
  "workflow_id": "workflow_1698765432_1234",
  "status": "pending",
  "message": "분석 워크플로우가 시작되었습니다.",
  "estimated_completion_time": "약 5분 후"
}
```

### 📊 워크플로우 상태 확인
```bash
curl "http://localhost:8002/api/workflow/{workflow_id}/status"
```

**응답:**
```json
{
  "workflow_id": "workflow_1698765432_1234",
  "status": "analyzing",
  "current_step": "교육 분석 중...",
  "progress_percentage": 60,
  "created_at": "2023-10-31T12:00:00Z"
}
```

### 📋 최종 결과 조회
```bash
curl "http://localhost:8002/api/workflow/{workflow_id}/results"
```

## 데모 클라이언트 사용

터미널에서 대화식으로 전체 워크플로우를 테스트할 수 있습니다:

```bash
python demo_client.py
```

**데모 실행 과정:**
1. YouTube URL 입력
2. 분석 유형 선택
3. 서비스 연결 상태 확인
4. 분석 실행 및 진행률 모니터링
5. 결과 요약 출력
6. JSON 파일로 결과 저장 (옵션)

## 워크플로우 단계

### 1. 전사 단계 (Transcription)
- YouTube URL에서 오디오 추출
- Whisper API 또는 YouTube 자막 이용
- 한국어 전사 텍스트 생성

### 2. 분석 단계 (Analysis)
- 전사 텍스트를 각 분석 엔진에 전달
- 교육 코칭, 대화 패턴, CBIL 평가 병렬 실행
- LLM 기반 정성/정량 분석

### 3. 통합 단계 (Integration)
- 분석 결과 통합 및 요약
- 시각화 차트 생성
- 최종 리포트 작성

## 서비스 연동

### 전사 서비스
- **URL**: https://teachinganalize-production.up.railway.app
- **역할**: YouTube 영상 → 한국어 텍스트 변환
- **API**: `/api/transcribe/youtube`

### 분석 서비스
- **URL**: http://localhost:8001 (로컬 배포 시)
- **역할**: 전사 텍스트 → 교육 분석 결과
- **API**: `/api/analyze/*`

## 모니터링

### 활성 워크플로우 조회
```bash
curl "http://localhost:8002/api/workflows"
```

### 서비스 상태 테스트
```bash
curl "http://localhost:8002/api/test/services"
```

### 워크플로우 정리
```bash
curl -X POST "http://localhost:8002/api/workflows/cleanup?older_than_hours=24"
```

## 예상 처리 시간

- **전사**: 3-5분 (영상 길이에 따라)
- **교육 코칭 분석**: 1-2분
- **대화 패턴 분석**: 30초-1분
- **CBIL 평가**: 1-2분
- **종합 분석**: 3-4분 (병렬 처리)

**총 예상 시간**: 5-10분 (분석 유형에 따라)

## 에러 처리

- **연결 실패**: 서비스 URL 및 네트워크 확인
- **인증 실패**: API 키 설정 확인
- **시간 초과**: 영상 길이가 너무 긴 경우 분할 처리 권장
- **분석 실패**: LLM API 한도 또는 서비스 상태 확인

## 로그 확인

서비스 로그는 `integration_service.log` 파일에 저장됩니다:

```bash
tail -f integration_service.log
```

## 개발 및 확장

### 새로운 분석 유형 추가
1. `analysis_types` 리스트에 새 유형 추가
2. 분석 서비스에 해당 엔드포인트 구현
3. 워크플로우 오케스트레이터에 매핑 추가

### 결과 저장소 연동
현재는 메모리 기반이지만, Redis나 PostgreSQL 연동 가능:
- 워크플로우 상태 영구 저장
- 결과 파일 클라우드 스토리지 업로드
- 사용자별 워크플로우 관리

## Railway 배포

추후 Railway 플랫폼에 배포 예정:
- 전사 서비스와 동일한 인프라 환경
- 환경 변수 자동 주입
- 로드 밸런싱 및 스케일링