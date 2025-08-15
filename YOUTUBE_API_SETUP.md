# 🎥 YouTube API 설정 가이드

## 📍 현재 상태
YouTube 전사 기능이 구현되었지만 Google Cloud Console API 키가 필요합니다.

## 🔑 YouTube Data API 키 발급

### 1단계: Google Cloud Console 접속
1. https://console.cloud.google.com 접속
2. Google 계정으로 로그인

### 2단계: 프로젝트 생성
1. 상단 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 클릭
3. 프로젝트 이름 입력 (예: "AIBOA")
4. "만들기" 클릭

### 3단계: YouTube Data API 활성화
1. 좌측 메뉴 → "API 및 서비스" → "라이브러리"
2. "YouTube Data API v3" 검색
3. 클릭 후 "사용" 버튼 클릭

### 4단계: API 키 생성
1. 좌측 메뉴 → "API 및 서비스" → "사용자 인증 정보"
2. "사용자 인증 정보 만들기" → "API 키" 클릭
3. 생성된 API 키 복사

### 5단계: API 키 제한 (권장)
1. 생성된 API 키 클릭
2. "애플리케이션 제한사항" → "HTTP 리퍼러"
3. Railway 도메인 추가:
   - `https://teachinganalize-production.up.railway.app/*`
   - `https://*.railway.app/*`
4. "API 제한사항" → "키 제한"
5. "YouTube Data API v3" 선택
6. "저장" 클릭

## 🚀 Railway에 API 키 설정

### Railway Dashboard에서:
1. https://railway.app/dashboard 로그인
2. `lively-surprise` 프로젝트 → `teaching_analize` 서비스
3. Settings → Variables
4. 추가:
   ```
   YOUTUBE_API_KEY=AIzaSy...your-key-here
   ```
5. 자동 재배포 시작

### Railway CLI로:
```bash
railway variables set YOUTUBE_API_KEY=AIzaSy...your-key-here
railway up --service teaching_analize
```

## ✅ 작동 확인

### 1. API 키 없을 때 (현재):
- yt-dlp로 직접 다운로드 시도
- 자막이 있으면 추출
- 없으면 오디오 다운로드 후 Whisper 전사

### 2. API 키 설정 후:
- YouTube API로 더 안정적인 자막 추출
- 자동 생성 자막 접근
- 다국어 자막 지원
- 더 빠른 처리 속도

## 🧪 테스트

### Frontend에서:
1. Streamlit UI 접속
2. Transcription 페이지
3. YouTube URL 입력:
   - 한국어 비디오: `https://www.youtube.com/watch?v=UQpjPgMRypQ`
   - 영어 비디오: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
4. Language 선택 후 Transcribe 클릭

### API로:
```bash
curl -X POST https://teachinganalize-production.up.railway.app/api/transcribe/youtube \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=UQpjPgMRypQ",
    "language": "ko"
  }'

# Job ID로 상태 확인
curl -X GET "https://teachinganalize-production.up.railway.app/api/transcribe/{job_id}" \
  -H "X-API-Key: test-api-key"
```

## 💡 참고사항

### YouTube API 할당량:
- 무료: 10,000 units/day
- 자막 가져오기: ~2 units
- 충분한 무료 할당량

### yt-dlp 대체 방법:
API 키 없어도 작동하지만:
- 속도가 느릴 수 있음
- 일부 동영상에서 실패 가능
- 자동 생성 자막 접근 제한

### 지원되는 동영상:
- 공개 동영상만 가능
- 연령 제한 동영상 불가
- 라이브 스트리밍 제한적 지원

## 🔍 문제 해결

### "quota exceeded" 오류:
- Google Cloud Console에서 할당량 확인
- 필요시 할당량 증가 요청

### "video not found" 오류:
- URL이 올바른지 확인
- 동영상이 공개 상태인지 확인
- 지역 제한이 있는지 확인

### 자막이 없는 경우:
- OPENAI_API_KEY 설정 확인
- Whisper로 자동 전사 시도
- 오디오 추출 후 처리

## 📊 성능 비교

| 방법 | YouTube API | yt-dlp only |
|------|------------|-------------|
| 속도 | ⚡ 빠름 | 🐢 보통 |
| 안정성 | ✅ 높음 | ⚠️ 보통 |
| 자막 지원 | 🌍 모든 언어 | 🌐 제한적 |
| 비용 | 🆓 무료 | 🆓 무료 |

## 🎉 완료!

YouTube API 키 설정 후:
- ✅ 더 안정적인 YouTube 전사
- ✅ 자동 생성 자막 접근
- ✅ 다국어 지원
- ✅ 빠른 처리 속도

---

**다음 단계**: Railway Dashboard에서 `YOUTUBE_API_KEY` 환경 변수 추가!