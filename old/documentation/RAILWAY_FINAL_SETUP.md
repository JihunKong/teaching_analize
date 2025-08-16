# 🎯 Railway 최종 설정 가이드

## ✅ 현재 상황 (Dashboard에서 확인됨)

- **도메인**: `teachinganalize-production.up.railway.app`
- **포트**: 8080
- **TCP Proxy**: `shortline.proxy.rlwy.net:13510`
- **서비스 존재**: 확인됨

## 🔧 Dashboard에서 수정해야 할 사항

### 1. 서비스 이름 및 설정 확인

현재 **teachinganalize** 서비스가 생성되어 있습니다.

1. **Dashboard 접속**: https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f

2. **teachinganalize 서비스 클릭**

3. **Settings 탭**에서 수정:
   - **Service Name**: `transcription` 으로 변경 (또는 그대로 유지)
   - **Root Directory**: `services/transcription` 설정 ⚠️ 중요!
   - **Watch Paths**: `services/transcription/**`

4. **Variables 탭**에서 환경변수 수정:
   ```
   PORT=8000 (현재 8080 → 8000으로 변경)
   OPENAI_API_KEY=[이미 설정되어 있음]
   PYTHONUNBUFFERED=1
   API_KEY=[생성 필요]
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ```

### 2. Analysis 서비스 추가 생성

1. **"+ New"** → **"GitHub Repo"** 클릭
2. 같은 Repository 선택: `JihunKong/teaching_analize`
3. **서비스 이름**: `analysis`
4. **Settings**:
   - **Root Directory**: `services/analysis`
   - **Watch Paths**: `services/analysis/**`
5. **Variables**:
   ```
   PORT=8001
   SOLAR_API_KEY=[이미 설정됨]
   UPSTAGE_API_KEY=[이미 설정됨]
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ```

## 🚀 CLI로 배포 (서비스 설정 후)

```bash
# 1. 서비스 연결 확인
railway link -p 379dfeea-b7f3-47cf-80c8-4d6d6b72329f

# 2. 첫 번째 서비스 배포 (teachinganalize 또는 transcription)
cd services/transcription
railway up --service teachinganalize --detach
# 또는
railway up --detach  # 서비스 선택 프롬프트 나오면 선택

# 3. 두 번째 서비스 배포 (analysis)
cd ../analysis
railway up --service analysis --detach
```

## 📋 체크리스트

### Transcription Service
- [ ] Root Directory: `services/transcription` 설정
- [ ] PORT: 8000으로 변경
- [ ] OPENAI_API_KEY 설정 확인
- [ ] Dockerfile 경로: `services/transcription/Dockerfile`

### Analysis Service  
- [ ] 서비스 생성됨
- [ ] Root Directory: `services/analysis` 설정
- [ ] PORT: 8001
- [ ] SOLAR_API_KEY 설정 확인
- [ ] Dockerfile 경로: `services/analysis/Dockerfile`

### Database
- [ ] PostgreSQL 추가됨
- [ ] Redis 추가됨
- [ ] 연결 URL이 서비스에 설정됨

## 🔍 확인 방법

### 1. Health Check (배포 완료 후)
```bash
# Transcription
curl https://teachinganalize-production.up.railway.app/health

# Analysis (새 도메인 확인 필요)
curl https://[analysis-domain].railway.app/health
```

### 2. Logs 확인
```bash
railway logs --service teachinganalize
railway logs --service analysis
```

### 3. 환경변수 확인
```bash
railway variables --service teachinganalize
railway variables --service analysis
```

## ⚠️ 중요 사항

1. **Root Directory는 반드시 설정**: 이것이 없으면 Dockerfile을 찾을 수 없음
2. **포트 번호 일치**: 
   - Transcription: 8000 (Dockerfile과 일치)
   - Analysis: 8001 (Dockerfile과 일치)
3. **서비스 이름**: Dashboard에서 보이는 정확한 이름 사용

## 🛠️ 문제 해결

### "Dockerfile does not exist" 오류
→ Root Directory를 `services/transcription` 또는 `services/analysis`로 설정

### "Port mismatch" 오류
→ PORT 환경변수를 8000 (transcription) 또는 8001 (analysis)로 설정

### "Service not found" 오류
→ Dashboard에서 실제 서비스 이름 확인 후 사용

---

**현재 teachinganalize 서비스가 있으므로, Root Directory만 설정하면 바로 배포 가능합니다!**