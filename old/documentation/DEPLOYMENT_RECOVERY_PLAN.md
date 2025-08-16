# EMERGENCY DEPLOYMENT RECOVERY PLAN
## Railway Service Restoration - 2025-08-15

## CRITICAL ISSUES IDENTIFIED
1. ❌ yt-dlp==2024.1.0 doesn't exist (future version)
2. ❌ Missing system dependencies for psycopg2-binary
3. ❌ Missing compilation tools for pandas/numpy
4. ❌ Overly complex dependencies for MVP

## RECOVERY STRATEGY: 3-PHASE DEPLOYMENT

### PHASE 1: MINIMAL VIABLE DEPLOYMENT (Deploy TODAY)
**Goal:** Get services running with health checks only

### PHASE 2: CORE FUNCTIONALITY (Deploy after Phase 1 stable)
**Goal:** Enable basic transcription and analysis features

### PHASE 3: FULL FEATURES (Deploy after Phase 2 stable)
**Goal:** Complete feature set with all dependencies

---

## IMMEDIATE ACTIONS (DO NOW)

### Step 1: Create MVP Requirements Files

#### Transcription Service MVP
```bash
# services/transcription/requirements.minimal.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

#### Analysis Service MVP
```bash
# services/analysis/requirements.minimal.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
```

### Step 2: Create Phased Requirements

#### Transcription Service Phase 2
```bash
# services/transcription/requirements.core.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
openai==1.6.1
yt-dlp==2023.12.30  # Fixed version
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
aiofiles==23.2.1
httpx==0.25.1
```

#### Analysis Service Phase 2
```bash
# services/analysis/requirements.core.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
openai==1.6.1
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0
aiofiles==23.2.1
httpx==0.25.1
```

### Step 3: Update Dockerfiles

#### MVP Dockerfile (both services)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install minimal requirements
COPY requirements.minimal.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PYTHONUNBUFFERED=1

# Start script
RUN echo '#!/bin/sh\n\
echo "Starting service on PORT: $PORT"\n\
exec uvicorn main:app --host 0.0.0.0 --port $PORT' > start.sh && chmod +x start.sh

CMD ["sh", "start.sh"]
```

#### Production Dockerfile with proper dependencies
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Complete system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN pip install --upgrade pip wheel setuptools

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PYTHONUNBUFFERED=1

# Create storage directories
RUN mkdir -p /data/uploads /data/transcripts /data/analysis /data/reports

# Start script
RUN echo '#!/bin/sh\n\
echo "Starting service on PORT: $PORT"\n\
exec uvicorn main:app --host 0.0.0.0 --port $PORT' > start.sh && chmod +x start.sh

CMD ["sh", "start.sh"]
```

---

## DEPLOYMENT SEQUENCE

### PHASE 1: MVP DEPLOYMENT (15 minutes)
1. Create minimal main.py files with health check only
2. Use requirements.minimal.txt
3. Deploy to Railway
4. Verify health endpoints work

### PHASE 2: CORE FEATURES (30 minutes)
1. Add database connectivity
2. Add basic API endpoints
3. Use requirements.core.txt
4. Deploy and test

### PHASE 3: FULL FEATURES (1 hour)
1. Add all features
2. Fix remaining dependency issues
3. Use full requirements.txt
4. Final deployment

---

## ROLLBACK STRATEGY

If deployment fails at any phase:
1. **Phase 1 Failure:** Use ultra-minimal Flask app instead
2. **Phase 2 Failure:** Rollback to Phase 1, debug locally
3. **Phase 3 Failure:** Stay at Phase 2 until issues resolved

### Emergency Ultra-Minimal Deployment
```python
# emergency_main.py
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "alive", "port": os.environ.get("PORT", "unknown")}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

## MONITORING & VALIDATION

### Health Check URLs
- Transcription: https://teachinganalize-production.up.railway.app/health
- Analysis: https://amusedfriendship-production.up.railway.app/health

### Success Criteria
- [ ] Services respond to health checks
- [ ] No crash loops in Railway logs
- [ ] Memory usage < 512MB
- [ ] Response time < 1000ms

---

## LONG-TERM FIXES

After services are stable:
1. Implement proper CI/CD pipeline
2. Add staging environment
3. Create comprehensive test suite
4. Document all dependency requirements
5. Set up monitoring and alerting

---

## CONTACT & ESCALATION

If critical issues persist:
1. Check Railway status page
2. Review Railway community forums
3. Consider alternative platforms (Render, Fly.io)
4. Implement local Docker testing first

---

**PRIORITY: Get Phase 1 deployed within 15 minutes**