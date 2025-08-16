# 🚨 Railway Nixpacks Build Error - Solution Guide

## The Problem
You're seeing: **"Nixpacks was unable to generate a build plan for this app"**

This happens because Railway is trying to build from the `services/` directory and finding two subdirectories (`analysis/` and `transcription/`) without knowing which one to build.

## ✅ Quick Fix (Railway Dashboard)

### Step 1: Delete Failed Service
1. Go to your Railway project: https://railway.com/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f
2. Click on the failed service
3. Go to Settings → Delete Service

### Step 2: Create Transcription Service
1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repository: `JihunKong/teaching_analize`
3. **IMPORTANT**: Before deploying, click on the service
4. Go to **Settings** tab
5. Find **"Root Directory"** field
6. Set it to: `/services/transcription`
7. Click **"Save"**
8. Go to **Variables** tab and add:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   API_KEY=your-secure-api-key
   PORT=8000
   ```

### Step 3: Create Analysis Service
1. Click **"+ New"** → **"GitHub Repo"** again
2. Select the same repository
3. Click on the new service
4. Go to **Settings** → **"Root Directory"**
5. Set it to: `/services/analysis`
6. Click **"Save"**
7. Go to **Variables** tab and add:
   ```
   SOLAR_API_KEY=your-solar-api-key-here
   UPSTAGE_API_KEY=your-upstage-api-key-here
   API_KEY=your-secure-api-key
   PORT=8001
   ```

### Step 4: Add Databases (if not already added)
1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Click **"+ New"** → **"Database"** → **"Add Redis"**

### Step 5: Link Database URLs
For both services, add these variables (Railway will auto-fill the values):
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

## 🖥️ Alternative: CLI Method

If the dashboard method doesn't work, use the CLI:

```bash
# 1. Make the script executable
chmod +x deploy_railway_services.sh

# 2. Run the deployment script
./deploy_railway_services.sh
```

## 🔍 Verify Deployment

Check if services are running:

```bash
# Check deployment status
railway status

# View service logs
railway logs --service transcription
railway logs --service analysis

# Test health endpoints (after deployment completes)
curl https://[your-transcription-url].railway.app/health
curl https://[your-analysis-url].railway.app/health
```

## 📝 Important Notes

1. **Root Directory is Critical**: Each service MUST have its root directory set correctly
   - Transcription: `/services/transcription`
   - Analysis: `/services/analysis`

2. **Separate Services**: You need TWO separate Railway services, not one

3. **Environment Variables**: Each service needs its own set of environment variables

4. **Build Detection**: Railway will automatically detect:
   - Python app (via requirements.txt)
   - Docker build (via Dockerfile)
   - Both services have these files, so detection should work

## 🆘 If Still Failing

### Check 1: Verify Files Exist
```bash
ls -la services/transcription/
# Should show: Dockerfile, requirements.txt, railway.toml, app/

ls -la services/analysis/
# Should show: Dockerfile, requirements.txt, railway.toml, app/
```

### Check 2: Force Docker Build
In Railway Settings for each service:
1. Go to Settings → Build
2. Set **"Builder"** to **"Dockerfile"**
3. Save changes

### Check 3: Manual Build Command
If Nixpacks still fails, override with:
1. Go to Settings → Build
2. Set **"Build Command"** to:
   ```
   docker build -t service .
   ```
3. Set **"Start Command"** to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

## 🎯 Expected Result

After successful deployment:
- ✅ Two separate services running
- ✅ Each with its own URL
- ✅ PostgreSQL and Redis connected
- ✅ Health checks passing

## 💡 Pro Tips

1. **Watch the build logs** - They'll tell you exactly what's failing
2. **Deploy one service at a time** - Easier to debug
3. **Check environment variables** - Missing API keys cause runtime failures
4. **Use Railway's support** - They're helpful with monorepo setups

## 📞 Need More Help?

1. Check Railway docs: https://docs.railway.app/deploy/monorepo
2. Railway Discord: https://discord.gg/railway
3. Check the build logs for specific error messages

---

**Remember**: The key is telling Railway WHERE to build from. Each service needs its own Railway service with the correct root directory!