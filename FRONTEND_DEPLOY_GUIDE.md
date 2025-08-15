# 🎨 AIBOA Frontend 배포 가이드

## 📍 현재 상태
- ✅ Backend API 배포 완료: https://teachinganalize-production.up.railway.app
- ✅ Frontend 코드 준비 완료 (Streamlit)
- ⏳ Frontend 배포 필요

## 🚀 Railway Dashboard에서 Frontend 배포하기

### 방법 1: 기존 프로젝트에 서비스 추가 (권장)

1. **Railway Dashboard 접속**
   - https://railway.app 로그인
   - 기존 프로젝트 (lively-surprise) 선택

2. **새 서비스 생성**
   - 프로젝트 내에서 **"New Service"** 클릭
   - **"GitHub Repo"** 선택
   - `JihunKong/teaching_analize` 레포지토리 선택

3. **서비스 설정**
   - **Service Name**: `aiboa-frontend`
   - **Root Directory**: `/frontend` (중요!)
   - **Branch**: `main`

4. **환경 변수 설정**
   ```
   TRANSCRIPTION_API_URL=https://teachinganalize-production.up.railway.app
   ANALYSIS_API_URL=https://teachinganalize-production.up.railway.app
   API_KEY=test-api-key
   ```

5. **배포 확인**
   - 자동으로 빌드 시작
   - 2-3분 후 URL 생성됨
   - 예상 URL: `https://aiboa-frontend-production.up.railway.app`

### 방법 2: Railway CLI 사용 (새 프로젝트)

```bash
# frontend 디렉토리로 이동
cd /Users/jihunkong/teaching_analize/frontend

# 새 Railway 프로젝트 생성
railway init

# 프로젝트 이름 입력: aiboa-frontend

# 배포
railway up

# 환경 변수 설정
railway variables set TRANSCRIPTION_API_URL=https://teachinganalize-production.up.railway.app
railway variables set ANALYSIS_API_URL=https://teachinganalize-production.up.railway.app
railway variables set API_KEY=test-api-key

# 도메인 생성
railway domain
```

## 🔍 배포 확인

### 1. 빌드 로그 확인
- Railway Dashboard → 서비스 → Build Logs
- `Successfully installed streamlit` 메시지 확인

### 2. 배포 로그 확인
```
Starting Container
You can now view your Streamlit app in your browser.
```

### 3. 앱 접속
- Frontend URL 방문
- 대시보드가 정상적으로 표시되는지 확인

## ✅ 배포 후 테스트

### 1. 대시보드 확인
- 메인 페이지 로딩 확인
- 통계 차트 표시 확인

### 2. 전사 서비스 테스트
- 사이드바에서 "📝 Transcription" 선택
- YouTube URL 입력: `https://youtube.com/watch?v=test`
- Submit 클릭 → Job ID 생성 확인

### 3. 분석 서비스 테스트
- 사이드바에서 "🔍 Analysis" 선택
- 샘플 텍스트 입력
- Analyze 클릭 → CBIL 차트 표시 확인

### 4. 통계 페이지 확인
- 사이드바에서 "📊 Statistics" 선택
- 플랫폼 통계 표시 확인

## 🎯 최종 URL 구조

배포 완료 후 다음 URL들이 활성화됩니다:

- **Frontend (Streamlit UI)**: 
  - `https://aiboa-frontend-production.up.railway.app`
  
- **Backend API**: 
  - `https://teachinganalize-production.up.railway.app`
  - API Docs: `/docs`
  
- **주요 페이지**:
  - 대시보드: `/`
  - 전사: `/Transcription`
  - 분석: `/Analysis`
  - 통계: `/Statistics`

## 🛠 문제 해결

### Streamlit 앱이 로드되지 않는 경우
1. Railway 빌드 로그 확인
2. PORT 환경 변수가 자동 설정되는지 확인
3. requirements.txt의 모든 패키지가 설치되었는지 확인

### API 연결 오류
1. 환경 변수 확인 (TRANSCRIPTION_API_URL, ANALYSIS_API_URL)
2. API_KEY가 올바른지 확인
3. Backend 서비스가 실행 중인지 확인

### 빌드 실패
1. Python 버전 확인 (3.11 필요)
2. requirements.txt 패키지 버전 충돌 확인
3. Railway 빌드 캐시 초기화 시도

## 📞 지원

문제가 지속되면:
1. Railway Dashboard에서 Support 탭 클릭
2. GitHub Issues: https://github.com/JihunKong/teaching_analize/issues

## 🎉 완료!

Frontend 배포가 완료되면 AIBOA 플랫폼이 완전히 작동합니다:
- 사용자 친화적인 웹 인터페이스
- 실시간 전사 및 분석
- 아름다운 데이터 시각화
- 모바일 반응형 디자인