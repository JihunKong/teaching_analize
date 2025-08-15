# Railway Deployment Fix Guide

## Problem Analysis

Railway is stuck using an old Docker build context (context: 0t4g-D9S0) and not picking up new code changes from GitHub. The service shows old version despite multiple deployment attempts.

**Current State:**
- Service returns: `{"service": "teaching_analize", "status": "running", "port": "8080"}`
- Should return: `{"status": "healthy", "service": "Analysis Service", "version": "MVP-v2-HOTFIX", ...}`

## Root Causes

1. **Build Cache Persistence**: Railway is caching the old Docker context
2. **GitHub Webhook Failure**: Updates aren't triggering new builds
3. **Build Configuration Lock**: Railway may be locked to a specific build
4. **Service Name Mismatch**: Old service configuration persisting

## Solution Steps (Execute in Order)

### Step 1: Force Cache Clear via Railway CLI

```bash
# 1. Update Railway CLI to latest version
npm update -g @railway/cli

# 2. Login and link to project
railway login
railway link

# 3. Force redeploy with no cache
railway up --service amused_friendship --no-cache --detach

# 4. If that doesn't work, try with explicit build args
railway up --service amused_friendship --build-arg CACHEBUST=$(date +%s) --detach
```

### Step 2: Railway Dashboard Actions

1. **Go to Railway Dashboard** → Your Project → amused_friendship service

2. **Settings Tab** → **Build Configuration**:
   - Change "Root Directory" to `/` then back to `services/analysis`
   - Toggle "Watch Paths" off and on
   - Clear any "Ignored Files" entries

3. **Settings Tab** → **Deploy**:
   - Click "Redeploy" → Select "Redeploy with no cache"
   - If available, click "Clear build cache"

4. **Settings Tab** → **Source**:
   - Disconnect GitHub repo
   - Wait 30 seconds
   - Reconnect GitHub repo
   - Select main branch
   - Enable auto-deploy

### Step 3: Create New Dockerfile with Cache Busting

Create a new file `services/analysis/Dockerfile.latest`:

```dockerfile
FROM python:3.11-slim

# Cache busting layer
ARG CACHEBUST=1
RUN echo "Cache bust: ${CACHEBUST}"

WORKDIR /app

# Force fresh pip install
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    python-dotenv==1.0.0

# Copy with explicit refresh
COPY --chown=root:root main.py ./main.py

# Add deployment timestamp
RUN echo "Deployed at: $(date)" > /app/deploy.txt

# Explicit command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Update `railway.toml`:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile.latest"
```

Then commit and push:

```bash
git add -A
git commit -m "FORCE REBUILD: New Dockerfile with cache busting"
git push origin main
```

### Step 4: Manual Docker Build and Push (Nuclear Option)

If above steps fail:

```bash
# 1. Build Docker image locally
cd services/analysis
docker build -t analysis-service:latest -f Dockerfile.latest .

# 2. Tag for Railway registry
docker tag analysis-service:latest registry.railway.app/PROJECT_ID/SERVICE_ID:latest

# 3. Push to Railway (requires Railway Docker auth)
railway docker login
docker push registry.railway.app/PROJECT_ID/SERVICE_ID:latest

# 4. Deploy the pushed image
railway deploy --image registry.railway.app/PROJECT_ID/SERVICE_ID:latest
```

### Step 5: Create New Service (Last Resort)

If nothing works, create a new service:

```bash
# 1. Create new service in Railway dashboard
# Name it: analysis-service-v2

# 2. Deploy to new service
railway up --service analysis-service-v2 --detach

# 3. Once working, delete old service and rename new one
```

## Verification Commands

After each step, verify deployment:

```bash
# Check deployment status
curl https://amusedfriendship-production.up.railway.app/

# Expected response:
# {
#   "status": "healthy",
#   "service": "Analysis Service",
#   "version": "MVP-v2-HOTFIX",
#   "timestamp": "...",
#   "port": 8080,
#   "deployed": "2025-08-15"
# }

# Check Railway logs
railway logs --service amused_friendship -n 50

# Check deployment history
railway deployments --service amused_friendship
```

## Additional Debugging

### Check Build Context
```bash
# See what Railway is actually building
railway run --service amused_friendship echo $RAILWAY_GIT_COMMIT_SHA
railway run --service amused_friendship ls -la
```

### Environment Variables
Ensure these are set in Railway dashboard:
- `PORT` (should be auto-set by Railway)
- `RAILWAY_ENVIRONMENT` = "production"
- Any API keys needed

### GitHub Webhook
1. Go to GitHub repo → Settings → Webhooks
2. Find Railway webhook
3. Click "Recent Deliveries" 
4. Check for failed deliveries
5. If failures, click "Redeliver"

## Prevention for Future

1. **Always use cache busting**: Add `ARG CACHEBUST=1` to Dockerfiles
2. **Version endpoints**: Include build timestamp in health checks
3. **Use explicit tags**: Tag Docker images with commit SHA
4. **Monitor deployments**: Set up alerts for deployment failures
5. **Test locally first**: `docker build` locally before pushing

## Quick Fix Script

Save as `force-deploy.sh`:

```bash
#!/bin/bash
echo "Forcing Railway deployment..."

# Update timestamp in main.py
sed -i '' "s/deployed\": \".*\"/deployed\": \"$(date +%Y-%m-%d-%H%M%S)\"/" main.py

# Commit with timestamp
git add -A
git commit -m "FORCE DEPLOY: $(date +%s)"
git push origin main

# Force Railway deploy
railway up --service amused_friendship --no-cache --detach

# Check status
sleep 10
curl https://amusedfriendship-production.up.railway.app/
```

## Contact Railway Support

If all else fails, contact Railway support with:
- Project ID
- Service ID  
- Build context ID (0t4g-D9S0)
- This document showing attempted fixes