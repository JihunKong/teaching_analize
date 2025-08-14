# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIBOA (AI-Based Observation and Analysis) is a modular classroom teaching analysis platform that uses AI to analyze teaching sessions and support teacher improvement. The system is designed for deployment on Railway platform with microservice architecture.

## System Architecture

The project follows a modular microservice architecture with two main independent services:

1. **Transcription Service**: Handles video/audio to text conversion
   - Processes video/audio files and YouTube URLs
   - Uses OpenAI Whisper or YouTube captions for STT
   - Exports in JSON, SRT, TXT formats
   - FastAPI-based service on port 8000

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
railway init
railway up

# Run database migrations
railway run python manage.py migrate

# Set environment variables
railway variables set OPENAI_API_KEY=xxx
railway variables set UPSTAGE_API_KEY=xxx
railway variables set SOLAR_API_KEY=xxx
```

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

- This is currently a specification/planning repository with comprehensive documentation
- Implementation should follow the modular architecture described in README.md
- Each service should be independently deployable
- Use Railway's environment variables for all sensitive configurations
- Implement proper error handling and logging for production deployment
- Follow the storage optimization strategy (30-day retention, gzip compression)