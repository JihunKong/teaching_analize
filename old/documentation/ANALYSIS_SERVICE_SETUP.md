# 📦 Analysis Service 설정 가이드

## 🎯 Analysis 서비스 추가 단계

### 1️⃣ 서비스 생성
1. Railway Dashboard에서 **"+ New"** 클릭
2. **"GitHub Repo"** 선택
3. Repository: **JihunKong/teaching_analize** 선택
4. 서비스가 생성되면 자동으로 배포 시작됨

### 2️⃣ Root Directory 설정 (가장 중요!)
1. 생성된 서비스 클릭
2. **Settings** 탭으로 이동
3. **Service** 섹션 찾기
4. **Root Directory** 필드에 입력:
   ```
   services/analysis
   ```
   ⚠️ 주의: 앞에 `/` 없이 입력!
5. **Save** 또는 자동 저장 확인

### 3️⃣ 환경변수 설정 (PORT 설정)
1. **Variables** 탭으로 이동
2. **"+ New Variable"** 클릭 또는 **Raw Editor** 사용
3. 다음 환경변수 추가:

```env
# 필수 환경변수
PORT=8001
PYTHONUNBUFFERED=1
SERVICE_NAME=analysis

# API 키 (이미 설정되어 있다면 확인만)
SOLAR_API_KEY=[귀하의 Solar API 키]
UPSTAGE_API_KEY=[귀하의 Upstage API 키]

# 데이터베이스 (Railway가 자동으로 제공)
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# 서비스 간 통신
TRANSCRIPTION_SERVICE_URL=https://teachinganalize-production.up.railway.app
```

### 4️⃣ PORT 설정이 안 되는 경우 해결책

#### 방법 1: Raw Editor 사용
1. Variables 탭에서 **"Raw Editor"** 모드로 전환
2. 다음과 같이 직접 입력:
```
PORT=8001
```

#### 방법 2: Railway CLI 사용
```bash
# Analysis 서비스의 정확한 이름 확인 후
railway variables set PORT=8001 --service [서비스이름]
```

#### 방법 3: Dockerfile에서 기본값 설정
Analysis 서비스의 Dockerfile을 수정하여 기본 포트 설정:

```dockerfile
# services/analysis/Dockerfile 마지막 줄 수정
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8001}"]
```

또는 main.py에서 포트 설정:

```python
# services/analysis/app/main.py 수정
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 5️⃣ 배포 확인

#### Deploy 로그 확인
1. **Deployments** 탭으로 이동
2. 최신 배포 클릭
3. 로그에서 확인할 내용:
   - "Building from services/analysis"
   - "Successfully built"
   - "Listening on port 8001"

#### Health Check
배포 완료 후 URL 확인:
```bash
# Analysis 서비스 도메인 확인 후
curl https://[analysis-domain].railway.app/health
```

## 🔧 트러블슈팅

### "PORT 변경이 안 됨" 문제
1. **환경변수 우선순위**:
   - Railway Variables > Dockerfile ENV > 코드 기본값
   
2. **확인 방법**:
   ```bash
   railway variables --service [analysis-service-name]
   ```

3. **강제 설정**:
   - Variables 탭에서 기존 PORT 변수 삭제
   - 새로 PORT=8001 추가
   - Redeploy 클릭

### "Root Directory not found" 오류
- Settings > Service > Root Directory: `services/analysis` (앞에 / 없이!)
- 저장 후 Redeploy

### "Module not found" 오류
- requirements.txt 파일 확인
- Python 버전 호환성 확인 (3.11)

## 📝 체크리스트

- [ ] 서비스 생성 완료
- [ ] Root Directory: `services/analysis` 설정
- [ ] PORT=8001 환경변수 설정
- [ ] API 키 설정 (SOLAR_API_KEY, UPSTAGE_API_KEY)
- [ ] Database URL 연결
- [ ] 배포 성공 확인
- [ ] Health endpoint 응답 확인

## 🚀 최종 확인

성공적으로 배포되면:
1. 서비스 상태: 🟢 Active
2. Health Check: `/health` returns 200 OK
3. Logs: "Uvicorn running on http://0.0.0.0:8001"

---

**참고**: PORT 환경변수는 Railway의 Variables 탭에서 설정하는 것이며, Settings의 Root Directory와는 별개입니다!