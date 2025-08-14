# 🚀 Railway Dashboard 설정 가이드

## 현재 상황
- 프로젝트: **lively-surprise** (production)
- 서비스: 아직 생성되지 않음
- API 키: Railway Variables에 설정 완료 (확인됨)

## 📋 Dashboard에서 설정할 단계

### 1️⃣ Transcription Service 생성

1. **Railway Dashboard 접속**: https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f

2. **새 서비스 생성**:
   - **"+ New"** 클릭
   - **"GitHub Repo"** 선택
   - Repository: **JihunKong/teaching_analize** 선택

3. **서비스 설정** (⚠️ 가장 중요):
   - 서비스 이름: **transcription** 으로 변경
   - **Settings** 탭으로 이동
   - **Service** 섹션에서:
     - **Root Directory**: `services/transcription` (앞에 / 없이!)
     - **Watch Paths**: `services/transcription/**`

4. **환경 변수 확인** (Variables 탭):
   ```
   OPENAI_API_KEY=[이미 설정됨]
   PORT=8000
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   PYTHONUNBUFFERED=1
   API_KEY=[생성 필요]
   ```

### 2️⃣ Analysis Service 생성

1. **두 번째 서비스 생성**:
   - **"+ New"** 클릭
   - **"GitHub Repo"** 선택
   - 같은 Repository 선택

2. **서비스 설정**:
   - 서비스 이름: **analysis** 으로 변경
   - **Settings** 탭:
     - **Root Directory**: `services/analysis`
     - **Watch Paths**: `services/analysis/**`

3. **환경 변수 확인**:
   ```
   SOLAR_API_KEY=[이미 설정됨]
   UPSTAGE_API_KEY=[이미 설정됨]
   PORT=8001
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   PYTHONUNBUFFERED=1
   API_KEY=[생성 필요]
   ```

### 3️⃣ Database 서비스 추가 (없다면)

1. **PostgreSQL**:
   - **"+ New"** → **"Database"** → **"Add PostgreSQL"**

2. **Redis**:
   - **"+ New"** → **"Database"** → **"Add Redis"**

## 🔍 확인 사항

각 서비스의 Deploy 탭에서 확인:

### ✅ 성공적인 빌드 로그:
```
#1 [internal] load build definition from Dockerfile
#2 [internal] load .dockerignore
#3 [base 1/X] FROM python:3.11-slim
...
Successfully built
```

### ❌ 실패 시 확인:
1. **Root Directory** 설정 확인 (/ 없이!)
2. **Dockerfile 경로**: 
   - `services/transcription/Dockerfile` ✅
   - `services/analysis/Dockerfile` ✅

## 📊 배포 후 확인

### CLI로 확인:
```bash
# 서비스 로그 확인
railway logs --service transcription | tail -20
railway logs --service analysis | tail -20

# 환경변수 확인
railway variables --service transcription
railway variables --service analysis

# 상태 확인
railway status
```

### Health Check:
```bash
# 배포 후 URL 확인 (Railway가 제공)
curl https://[transcription-url].railway.app/health
curl https://[analysis-url].railway.app/health
```

## 🎯 중요 포인트

1. **서비스 이름**: `transcription`, `analysis` (정확히 이 이름 사용)
2. **Root Directory**: 앞에 `/` 없이 상대 경로로 설정
3. **각 서비스는 독립적**: 같은 repo, 다른 디렉토리
4. **환경변수**: 이미 설정된 API 키 확인

## 🔗 서비스 간 연결

각 서비스의 Variables에 추가:

**transcription 서비스**:
```
ANALYSIS_SERVICE_URL=https://analysis.up.railway.app
```

**analysis 서비스**:
```
TRANSCRIPTION_SERVICE_URL=https://transcription.up.railway.app
```

## 📝 문제 해결

### "Dockerfile does not exist" 오류:
- Root Directory 확인 (앞에 / 없어야 함)
- 예: ✅ `services/analysis` / ❌ `/services/analysis`

### Build 실패:
- Deploy 로그 확인
- requirements.txt 파일 존재 확인
- Python 버전 호환성 확인

### 서비스 찾을 수 없음:
- 서비스 이름 확인
- railway link 다시 실행
- 프로젝트 ID 확인

---

**준비 완료!** Dashboard에서 위 단계를 따라 설정하시면 됩니다. 🚀