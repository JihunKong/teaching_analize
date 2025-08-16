# QUICK DEPLOYMENT GUIDE - EMERGENCY FIX
## Get Services Running on Railway NOW

## IMMEDIATE ACTION (5 minutes)

### Option 1: Manual MVP Deployment (RECOMMENDED)

```bash
# 1. Deploy Transcription Service MVP
cd services/transcription
cp Dockerfile.minimal Dockerfile
cp main_minimal.py main.py
railway up --service teaching_analize --detach

# 2. Deploy Analysis Service MVP
cd ../analysis
cp Dockerfile.minimal Dockerfile
cp main_minimal.py main.py
railway up --service amused_friendship --detach
```

### Option 2: Use Deploy Script
```bash
./deploy_phase1.sh
```

## VERIFY DEPLOYMENT (2 minutes)

Check these URLs:
- https://teachinganalize-production.up.railway.app/health
- https://amusedfriendship-production.up.railway.app/health

Expected response:
```json
{
  "status": "healthy",
  "service": "transcription",
  "version": "0.1.0-mvp",
  "timestamp": "2025-08-15T...",
  "port": "8080",
  "environment": "production"
}
```

## PHASE 2: Add Core Features (After MVP Works)

```bash
# Transcription Service
cd services/transcription
cp requirements.core.txt requirements.txt
# Edit Dockerfile to use requirements.txt
railway up --service teaching_analize --detach

# Analysis Service
cd services/analysis
cp requirements.core.txt requirements.txt
# Edit Dockerfile to use requirements.txt
railway up --service amused_friendship --detach
```

## PHASE 3: Full Deployment (After Core Works)

```bash
# Use original requirements.txt with fixed versions
# Deploy with full Dockerfile
```

## TROUBLESHOOTING

### If deployment still fails:

1. **Check Railway logs:**
```bash
railway logs --service teaching_analize
railway logs --service amused_friendship
```

2. **Ultra-minimal fallback:**
Create single file `emergency.py`:
```python
from fastapi import FastAPI
import os
app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok", "port": os.environ.get("PORT")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
```

3. **Railway.toml override:**
Create `railway.toml` in service directory:
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile.minimal"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

## SUCCESS CRITERIA

✅ Services respond to /health endpoint
✅ No crash loops in logs
✅ Port correctly bound (check logs for "Starting... on PORT: 8080")
✅ Memory usage < 256MB (MVP should be tiny)

## NEXT STEPS

Once MVP is stable:
1. Add database connectivity (Phase 2)
2. Add API endpoints one by one
3. Test each feature before adding next
4. Full deployment only after all tests pass

---

**TIME TO DEPLOYMENT: 5-10 minutes for MVP**