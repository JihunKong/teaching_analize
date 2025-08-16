# 🔑 API Keys Setup Guide for AIBOA

## 📍 현재 상태
✅ 실제 기능 구현 완료 - API 키만 설정하면 작동합니다!

## 🎯 필요한 API 키

### 1. OpenAI API Key (전사 기능)
- **용도**: Whisper API를 통한 음성/비디오 전사
- **가격**: ~$0.006/분 (오디오)
- **획득 방법**:
  1. https://platform.openai.com 접속
  2. 계정 생성 또는 로그인
  3. API Keys 메뉴에서 "Create new secret key" 클릭
  4. 키 복사 (sk-... 형식)

### 2. Upstage Solar API Key (분석 기능)
- **용도**: 한국어 최적화 LLM으로 CBIL 분석
- **가격**: ~$0.002/1K 토큰
- **획득 방법**:
  1. https://www.upstage.ai 접속
  2. 계정 생성 및 로그인
  3. Console → API Keys
  4. "Create API Key" 클릭
  5. 키 복사

## 🚀 Railway에 API 키 설정하기

### 방법 1: Railway Dashboard (권장)
1. https://railway.app/dashboard 로그인
2. `lively-surprise` 프로젝트 선택
3. `teaching_analize` 서비스 클릭
4. **Settings** → **Variables** 탭
5. 다음 변수 추가:
   ```
   OPENAI_API_KEY=sk-your-openai-key-here
   SOLAR_API_KEY=your-upstage-key-here
   API_KEY=your-secure-api-key
   ```
6. **Deploy** 클릭하여 재배포

### 방법 2: Railway CLI
```bash
# 프로젝트 연결
railway link

# API 키 설정
railway variables set OPENAI_API_KEY=sk-your-openai-key-here
railway variables set SOLAR_API_KEY=your-upstage-key-here
railway variables set API_KEY=your-secure-api-key

# 재배포
railway up --service teaching_analize
```

## ✅ 설정 확인

### 1. 로그 확인
```bash
railway logs --service teaching_analize
```

성공 메시지:
- "WhisperClient initialized with OpenAI API"
- "SolarLLMClient initialized"

### 2. API 테스트

#### 전사 테스트
```bash
curl -X POST https://teachinganalize-production.up.railway.app/api/transcribe/youtube \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://youtube.com/watch?v=test", "language": "ko"}'
```

#### 분석 테스트
```bash
curl -X POST https://teachinganalize-production.up.railway.app/api/analyze/text \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "오늘 배운 내용을 설명해보세요. 왜 이것이 중요한가요?"}'
```

## 🎨 Frontend에서 확인
1. Streamlit UI 접속
2. Transcription 페이지에서 파일 업로드 또는 YouTube URL 입력
3. Analysis 페이지에서 텍스트 분석
4. 실제 결과 확인!

## ⚠️ 주의사항

### API 키 보안
- GitHub에 절대 커밋하지 마세요
- Railway 환경 변수로만 관리
- 주기적으로 키 순환

### 비용 관리
- OpenAI: 월 사용량 제한 설정 권장
- Upstage: 무료 크레딧 확인
- Railway 로그에서 사용량 모니터링

### 문제 해결

#### "API key not configured" 오류
- Railway Variables 확인
- 키 앞뒤 공백 제거
- 재배포 필요

#### "Invalid API key" 오류
- 키가 올바른지 확인
- 계정 결제 정보 확인
- API 사용 권한 확인

## 📊 예상 비용

### 월 100시간 처리 기준
- OpenAI Whisper: ~$36
- Upstage Solar: ~$10
- Railway 호스팅: ~$17
- **총**: ~$63/월

### 비용 절감 팁
1. YouTube 자막 우선 사용 (무료)
2. 짧은 파일만 처리
3. 캐싱 구현
4. 배치 처리 활용

## 🎉 축하합니다!

API 키 설정 후 AIBOA가 실제로 작동합니다:
- ✅ 실제 음성/비디오 전사
- ✅ AI 기반 CBIL 분석
- ✅ 한국어 최적화
- ✅ 실시간 처리

## 📞 지원

문제 발생시:
1. Railway 로그 확인
2. API 제공자 대시보드 확인
3. GitHub Issues 생성

---

**다음 단계**: PostgreSQL과 Redis 추가로 프로덕션 준비 완료!