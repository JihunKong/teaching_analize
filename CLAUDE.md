# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIBOA (AI-Based Observation and Analysis) is a modular classroom teaching analysis platform that uses AI to analyze teaching sessions and support teacher improvement. The system is designed for deployment on Railway platform with microservice architecture.

## Current Status (Updated: 2025-08-15)

✅ **Successfully Deployed on Railway with Full Features:**
- **Transcription Service**: https://teachinganalize-production.up.railway.app (Port 8080)
  - ✅ Selenium browser automation for YouTube transcript extraction
  - ✅ YouTube URL support with automatic caption extraction
  - ✅ Multiple export formats (JSON, SRT, TXT)
  - ✅ Async job processing with background tasks
  - ✅ API authentication with X-API-Key header
  - ⚠️ **IMPORTANT**: ONLY uses Selenium (NO WhisperX, NO Whisper API)
  
- **Analysis Service**: https://amusedfriendship-production.up.railway.app (Port 8080)
  - ✅ CBIL 7-level classification system implemented
  - ✅ Solar-mini LLM integration for Korean text analysis
  - ✅ Integration with Transcription Service
  - ✅ Statistics dashboard endpoint
  - ✅ Report generation endpoint (placeholder)

⚠️ **Pending Setup:**
- PostgreSQL database on Railway (currently using SQLite)
- Redis for Celery async task queue
- Full PDF report generation with charts
- End-to-end testing with real data

## System Architecture

The project follows a modular microservice architecture with two main independent services:

1. **Transcription Service**: Handles YouTube video to text conversion
   - Processes YouTube URLs ONLY using Selenium browser automation
   - Extracts captions directly from YouTube's transcript feature
   - Exports in JSON, SRT, TXT formats
   - FastAPI-based service on port 8000
   - **CRITICAL**: NO WhisperX, NO Whisper API, ONLY Selenium

2. **Analysis Service**: Performs CBIL (Cognitive Burden of Instructional Language) analysis
   - Analyzes text/scripts for teaching quality
   - 7-level CBIL classification system
   - Generates PDF reports and statistics
   - FastAPI-based service on port 8001

Both services use:
- PostgreSQL for data persistence
- Redis for job queuing (Celery)
- Railway Volumes for file storage

## Development Commands

### Service Setup and Deployment (Railway)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy services
railway login
railway link  # Connect to existing project

# Deploy from service directories
cd services/transcription && railway up --service teaching_analize --detach
cd services/analysis && railway up --service amused_friendship --detach

# Check deployment status
railway status
railway logs --service teaching_analize
railway logs --service amused_friendship

# Environment variables (already set in Railway dashboard)
# OPENAI_API_KEY, UPSTAGE_API_KEY, SOLAR_API_KEY
```

### Railway Deployment Lessons Learned
- ⚠️ Never use TCP Proxy for HTTP services (causes 502 errors)
- ⚠️ Don't override PORT environment variable (Railway assigns it automatically)
- ⚠️ Service names should use underscores, not hyphens
- ⚠️ Root Directory must match service structure (e.g., services/transcription)
- ⚠️ Target Port in Networking settings must match actual app port

### Local Development (if implementing)
```bash
# Python virtual environment setup
python3.11 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies (per service)
pip install -r services/transcription/requirements.txt
pip install -r services/analysis/requirements.txt

# Run services locally
uvicorn main:app --reload --port 8000  # Transcription service
uvicorn main:app --reload --port 8001  # Analysis service

# Run Celery workers
celery -A app.celery worker --loglevel=info
```

### Testing
```bash
# Run unit tests
pytest services/transcription/tests
pytest services/analysis/tests

# API testing
curl -X POST https://transcription.railway.app/api/transcribe/upload \
  -H "X-API-Key: your-api-key" \
  -F "file=@lesson.mp4"
```

## Key Implementation Details

### CBIL Analysis System
The core analysis uses a 7-level cognitive classification:
1. Simple confirmation (단순 확인)
2. Fact recall (사실 회상)
3. Concept explanation (개념 설명)
4. Analytical thinking (분석적 사고)
5. Comprehensive understanding (종합적 이해)
6. Evaluative judgment (평가적 판단)
7. Creative application (창의적 적용)

### API Authentication
All API endpoints require API key authentication via `X-API-Key` header.

### File Storage Structure
```
/data (Railway Volume)
├── uploads/       # Temporary upload files
├── transcripts/   # Generated transcripts
├── analysis/      # Analysis results
└── reports/       # PDF reports
```

### Technology Stack
- **Runtime**: Python 3.11
- **Framework**: FastAPI
- **Queue**: Celery + Redis
- **Database**: PostgreSQL
- **Storage**: Railway Volumes
- **STT**: OpenAI Whisper / YouTube API
- **LLM**: Solar-mini (Korean optimized)
- **Frontend** (optional): Next.js 14 or Streamlit

## API Endpoints Reference

### Transcription Service
- `POST /api/transcribe/upload` - Upload file for transcription
- `POST /api/transcribe/youtube` - Process YouTube URL
- `GET /api/transcribe/{job_id}` - Check job progress
- `GET /api/transcripts/{id}` - Download transcript

### Analysis Service
- `POST /api/analyze/text` - Direct text analysis
- `POST /api/analyze/transcript` - Analyze transcription result
- `GET /api/analysis/{id}` - Get analysis results
- `GET /api/reports/{id}` - Download report
- `GET /api/statistics` - View statistics dashboard

## Important Notes

- ✅ Both services are now fully implemented and deployed on Railway
- ✅ Modular architecture allows independent deployment and scaling
- ✅ Each service has comprehensive error handling and logging
- ⚠️ Currently using SQLite - migrate to PostgreSQL for production
- ⚠️ Redis setup needed for proper async task queuing
- Use Railway's environment variables for all sensitive configurations
- Follow the storage optimization strategy (30-day retention, gzip compression)

## Testing the Services

### Test Transcription Service
```bash
# Health check
curl https://teachinganalize-production.up.railway.app/health

# Upload file for transcription (requires API key)
curl -X POST https://teachinganalize-production.up.railway.app/api/transcribe/upload \
  -H "X-API-Key: test-api-key" \
  -F "file=@sample.mp3" \
  -F "language=ko"
```

### Test Analysis Service
```bash
# Health check
curl https://amusedfriendship-production.up.railway.app/health

# Analyze text (requires API key)
curl -X POST https://amusedfriendship-production.up.railway.app/api/analyze/text \
  -H "X-API-Key: test-api-key" \
  -H "Content-Type: application/json" \
  -d '{"text": "오늘 배운 내용을 설명해보세요. 왜 이것이 중요한가요?"}'
```