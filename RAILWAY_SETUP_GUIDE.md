# 🚀 Railway Setup Guide - Step by Step

## ⚠️ Current Error: "Dockerfile does not exist"

This happens when Railway's root directory isn't properly configured.

## ✅ Solution: Correct Service Configuration

### Step 1: Delete Any Failed Services
1. Go to: https://railway.com/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f
2. Click on any failed service
3. Go to Settings → Delete Service

### Step 2: Create Transcription Service

1. **Click "+ New" → "Empty Service"** (not GitHub Repo yet)
2. **Name it**: `transcription-service`
3. **Click on the service** to open settings
4. **Go to "Settings" tab**
5. **Under "Service"**:
   - Find **"Connect Repo"** button
   - Click it and select `JihunKong/teaching_analize`
6. **CRITICAL - Set Build Configuration**:
   - **Root Directory**: `services/transcription` (NO leading slash!)
   - **Watch Paths**: `services/transcription/**`
7. **Go to "Variables" tab** and add:
   ```
   OPENAI_API_KEY=[Your OpenAI API key - starts with sk-proj-...]
   API_KEY=aiboa-transcription-key
   PORT=8000
   PYTHONUNBUFFERED=1
   ```
8. **Deploy** → Railway should now find the Dockerfile at `services/transcription/Dockerfile`

### Step 3: Create Analysis Service

1. **Click "+ New" → "Empty Service"**
2. **Name it**: `analysis-service`
3. **Click on the service**
4. **Go to "Settings" tab**
5. **Under "Service"**:
   - Connect to same repo: `JihunKong/teaching_analize`
6. **Set Build Configuration**:
   - **Root Directory**: `services/analysis` (NO leading slash!)
   - **Watch Paths**: `services/analysis/**`
7. **Go to "Variables" tab** and add:
   ```
   SOLAR_API_KEY=[Your Upstage/Solar API key - starts with up_...]
   UPSTAGE_API_KEY=[Same as SOLAR_API_KEY]
   API_KEY=aiboa-analysis-key
   PORT=8001
   PYTHONUNBUFFERED=1
   ```

### Step 4: Add Databases

1. **PostgreSQL**:
   - Click "+ New" → "Database" → "Add PostgreSQL"
   
2. **Redis**:
   - Click "+ New" → "Database" → "Add Redis"

### Step 5: Link Database URLs to Both Services

For **BOTH** services, add these variables:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

### Step 6: Add Service Cross-References

In **transcription-service** variables:
```
ANALYSIS_SERVICE_URL=https://analysis-service.up.railway.app
```

In **analysis-service** variables:
```
TRANSCRIPTION_SERVICE_URL=https://transcription-service.up.railway.app
```

## 🔍 Verification Checklist

After setting up, verify each service shows:

✅ **Build Settings**:
- Root Directory: `services/transcription` or `services/analysis`
- Builder: Dockerfile (auto-detected)

✅ **Source**:
- Repo: JihunKong/teaching_analize
- Branch: main

✅ **Deploy Logs** should show:
```
#1 [internal] load build definition from Dockerfile
#2 [internal] load .dockerignore
#3 [base 1/4] FROM python:3.11-slim
...
```

## 🐛 Troubleshooting

### If "Dockerfile not found" persists:

1. **Check Root Directory Format**:
   - ✅ Correct: `services/analysis`
   - ❌ Wrong: `/services/analysis` (no leading slash!)
   - ❌ Wrong: `./services/analysis`

2. **Try Nixpacks Instead**:
   - Remove the Dockerfile temporarily
   - Let Nixpacks auto-detect Python from requirements.txt
   - In Settings → Build → Builder: Set to "Nixpacks"

3. **Manual Build Command Override**:
   - Settings → Build → Build Command:
     ```bash
     cd services/analysis && pip install -r requirements.txt
     ```
   - Start Command:
     ```bash
     cd services/analysis && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

## 📊 Expected Result

When correctly configured, you should see:

1. **Build logs showing**:
   - "Using Dockerfile at services/analysis/Dockerfile"
   - "Successfully built image"

2. **Deploy logs showing**:
   - "Starting service..."
   - "Uvicorn running on http://0.0.0.0:8001"

3. **Health check passing**:
   - Green checkmark on service
   - `/health` endpoint returning 200 OK

## 🆘 Alternative: Use Railway CLI

If the UI isn't working, try the CLI:

```bash
# Install Railway CLI
curl -sSL https://railway.app/install.sh | sh

# Login
railway login

# Link project
railway link 379dfeea-b7f3-47cf-80c8-4d6d6b72329f

# Deploy transcription service
cd services/transcription
railway up --service transcription-service

# Deploy analysis service  
cd ../analysis
railway up --service analysis-service
```

## 📝 Notes

- **Region**: asia-southeast1 (as shown in your error)
- **Each service** needs its own Railway service instance
- **Root Directory** must be relative (no leading slash)
- **Dockerfiles** are at:
  - `services/transcription/Dockerfile` ✅
  - `services/analysis/Dockerfile` ✅

The key is ensuring Railway looks in the right directory for each service!