# 🔑 YouTube API Key 즉시 설정하기

## YouTube API Key 받음!
```
AIzaSyDzZscl_XRZFi0nH3K45enXLObE1m9XBRw
```

## 🚀 Railway에 지금 설정하기

### 방법 1: Railway CLI (빠름)
```bash
railway link
railway variables set YOUTUBE_API_KEY=AIzaSyDzZscl_XRZFi0nH3K45enXLObE1m9XBRw
```

### 방법 2: Railway Dashboard (쉬움)
1. https://railway.app/dashboard 접속
2. `lively-surprise` 프로젝트 클릭
3. `teaching_analize` 서비스 클릭
4. **Settings** → **Variables** 탭
5. **New Variable** 클릭
6. 입력:
   - Key: `YOUTUBE_API_KEY`
   - Value: `AIzaSyDzZscl_XRZFi0nH3K45enXLObE1m9XBRw`
7. **Add** 클릭
8. 자동 재배포 시작 (2-3분)

## ✅ 설정 후 테스트

### 1. Railway 재배포 확인
```bash
railway logs --service teaching_analize | grep "YouTube"
```

### 2. YouTube 전사 테스트
```bash
curl -X POST https://teachinganalize-production.up.railway.app/api/transcribe/youtube \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "language": "en"
  }'
```

### 3. Frontend에서 테스트
1. Streamlit UI 접속
2. Transcription 페이지
3. YouTube URL 입력
4. 실제 자막 추출 확인!

## 🎉 API 키 설정 후 가능한 것들

- ✅ YouTube 자막 실제 추출
- ✅ 자동 생성 자막 접근
- ✅ 다국어 자막 지원
- ✅ Bot 보호 우회
- ✅ 더 안정적인 처리

## ⚠️ 중요

**지금 바로 Railway Dashboard에서 설정하세요!**

설정 후 YouTube 전사가 실제로 작동합니다.

---

**Railway Dashboard 바로가기**: https://railway.app/dashboard