# 🚨 즉시 실행: Railway Dashboard에서 YouTube API 키 설정

## 📍 현재 상태
- ✅ YouTube API 키 작동 확인됨
- ❌ Railway에 아직 설정 안됨
- ⚠️ Mock 데이터만 반환 중

## 🎯 바로 실행 (2분 소요)

### Railway Dashboard 설정:

1. **Railway Dashboard 접속**
   👉 https://railway.app/dashboard

2. **프로젝트 선택**
   - `lively-surprise` 클릭

3. **서비스 선택**
   - `teaching_analize` 클릭 (또는 현재 배포된 서비스)

4. **Variables 탭 이동**
   - 상단 메뉴에서 **Settings** 클릭
   - **Variables** 섹션으로 스크롤

5. **새 변수 추가**
   - **New Variable** 버튼 클릭
   - 또는 Raw Editor 사용

6. **입력**
   ```
   변수명: YOUTUBE_API_KEY
   값: ***REMOVED***
   ```

7. **저장**
   - **Add** 또는 **Save** 클릭
   - 자동으로 재배포 시작 (2-3분)

## ✅ 설정 확인

### 1. 배포 상태 확인
Railway Dashboard에서:
- Deployments 탭 확인
- "Deploy successful" 메시지 대기

### 2. YouTube 전사 테스트
```bash
# 실제 YouTube 동영상으로 테스트
curl -X POST https://teachinganalize-production.up.railway.app/api/transcribe/youtube \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "language": "en"
  }'
```

### 3. Job 상태 확인
```bash
# Job ID로 결과 확인 (위 명령에서 받은 job_id 사용)
curl -X GET "https://teachinganalize-production.up.railway.app/api/transcribe/{job_id}" \
  -H "X-API-Key: test-api-key"
```

## 🎉 설정 후 가능한 것

### Before (현재):
```
❌ "YouTube 보호 메커니즘 활성화됨"
❌ Mock 데이터만 반환
❌ 실제 자막 추출 불가
```

### After (설정 후):
```
✅ 실제 YouTube 자막 추출
✅ 자동 생성 자막 접근
✅ 다국어 자막 지원
✅ 정확한 타임스탬프
```

## 🔍 문제 해결

### 여전히 Mock 데이터가 나온다면:
1. Railway 재배포 완료 확인 (3-5분 대기)
2. 변수명 정확히 `YOUTUBE_API_KEY` 확인
3. API 키 앞뒤 공백 제거
4. Railway 로그 확인

### Railway 로그 확인:
```bash
# 배포 로그 확인
railway logs --service teaching_analize | grep -i youtube
```

## 📊 예상 결과

### 성공 시:
```json
{
  "job_id": "...",
  "status": "completed",
  "result": {
    "text": "실제 YouTube 자막 내용...",
    "source": "youtube_captions",
    "language": "en"
  }
}
```

### 실패 시 (API 키 미설정):
```json
{
  "result": {
    "text": "[YouTube 보호 메커니즘 활성화됨]...",
    "source": "mock_due_to_bot_protection"
  }
}
```

## ⚡ 중요!

**지금 바로 Railway Dashboard에서 설정하세요!**

1. 👉 https://railway.app/dashboard
2. Variables에 `YOUTUBE_API_KEY` 추가
3. 2-3분 후 실제 YouTube 전사 가능!

---

**도움이 필요하면 Railway Support 또는 GitHub Issues에 문의하세요.**