# 🎥 YouTube API 올바른 설정 가이드

## ✅ 필요한 API: YouTube Data API v3

### 1️⃣ YouTube Data API v3 활성화
1. Google Cloud Console: https://console.cloud.google.com
2. **API 및 서비스** → **라이브러리**
3. **YouTube Data API v3** 검색
4. 클릭 후 **사용** 버튼 클릭
5. ✅ 활성화 완료

### ❌ 필요 없는 API들:
- YouTube Analytics API (분석용)
- YouTube Reporting API (리포트용)
- YouTube Embedded Player API (임베드용)
- YouTube oEmbed API (임베드용)

## 🔑 인증 방식: API 키 (OAuth 불필요!)

### API 키만 사용하는 이유:
- **공개 데이터만 접근**: 공개 YouTube 동영상의 자막/정보
- **OAuth 불필요**: 사용자 계정 접근이 필요 없음
- **간단한 설정**: API 키만 있으면 즉시 사용

### OAuth가 필요한 경우 (우리는 해당 없음):
- ❌ 비공개 동영상 접근
- ❌ 채널 관리
- ❌ 동영상 업로드
- ❌ 댓글 작성

## 📋 정확한 설정 단계

### 1단계: API 활성화 확인
```
✅ YouTube Data API v3 - 사용 중
❌ 나머지 API들 - 필요 없음
```

### 2단계: API 키 제한 설정
1. **API 및 서비스** → **사용자 인증 정보**
2. 생성한 API 키 클릭
3. **애플리케이션 제한사항**:
   - ✅ **없음** 또는 **HTTP 리퍼러** 선택
   - HTTP 리퍼러 선택 시:
     ```
     https://teachinganalize-production.up.railway.app/*
     https://*.railway.app/*
     http://localhost:*
     ```
4. **API 제한사항**:
   - ✅ **키 제한** 선택
   - ✅ **YouTube Data API v3** 만 체크
5. **저장** 클릭

### 3단계: Railway 환경 변수 설정
```bash
# CLI 방법
railway variables set YOUTUBE_API_KEY=AIzaSyDzZscl_XRZFi0nH3K45enXLObE1m9XBRw

# 또는 Dashboard에서
YOUTUBE_API_KEY=AIzaSyDzZscl_XRZFi0nH3K45enXLObE1m9XBRw
```

## 🧪 작동 테스트

### API 키 테스트 (터미널):
```bash
# YouTube API 직접 테스트
curl "https://www.googleapis.com/youtube/v3/videos?id=dQw4w9WgXcQ&key=AIzaSyDzZscl_XRZFi0nH3K45enXLObE1m9XBRw&part=snippet"

# 성공 시: JSON 데이터 반환
# 실패 시: 오류 메시지 확인
```

### AIBOA에서 테스트:
```bash
curl -X POST https://teachinganalize-production.up.railway.app/api/transcribe/youtube \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "language": "en"
  }'
```

## ⚠️ 일반적인 오류 해결

### "API key not valid" 오류:
1. API 키가 정확한지 확인
2. YouTube Data API v3가 활성화되어 있는지 확인
3. API 키 제한사항 확인

### "quotaExceeded" 오류:
- 일일 할당량 초과 (10,000 units/day)
- 다음날 자동 리셋
- 필요시 할당량 증가 요청

### "forbidden" 오류:
- API 키 제한사항이 너무 엄격함
- HTTP 리퍼러 제한 완화 또는 제거

## 📊 API 사용량

### 무료 할당량:
- **10,000 units/day** (충분함)
- 자막 가져오기: ~2-3 units
- 동영상 정보: ~1 unit

### 할당량 확인:
1. Google Cloud Console
2. **API 및 서비스** → **할당량**
3. YouTube Data API v3 선택
4. 사용량 확인

## ✅ 체크리스트

- [x] YouTube Data API v3 활성화
- [x] API 키 생성 (AIzaSyDzZscl_XRZFi0nH3K45enXLObE1m9XBRw)
- [ ] API 키 제한 설정 (선택사항)
- [ ] Railway 환경 변수 추가
- [ ] 테스트 완료

## 🎯 요약

**필요한 것:**
- ✅ YouTube Data API v3만
- ✅ API 키만 (OAuth 불필요)
- ✅ Railway 환경 변수 설정

**하지 마세요:**
- ❌ OAuth 2.0 설정
- ❌ 다른 YouTube API 활성화
- ❌ 서비스 계정 생성

---

**간단합니다! API 키만 Railway에 추가하면 됩니다.**