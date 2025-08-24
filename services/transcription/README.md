# AIBOA Robust YouTube Transcription Service

## Overview

This is a robust YouTube transcription service implementing the proven multi-method approach documented in `TRANSCRIPT_METHOD.md`. The system provides **3-layer fallback strategy** to handle even the most difficult YouTube videos, including those with disabled transcripts.

## 🎯 Key Features

### Multi-Method Transcription Strategy
1. **YouTube Transcript API** (Primary) - Fast, direct access to existing captions
2. **OpenAI Whisper API** (Secondary) - High-quality audio transcription
3. **Browser Automation** (Final Fallback) - Handles videos with disabled transcripts

### Proven Architecture
- **Async Processing**: Celery + Redis for robust job handling
- **Real-time Monitoring**: Progress tracking and status updates
- **Browser Automation**: Playwright with Xvfb for headless operation
- **API Compatibility**: Matches proven endpoint structure from successful deployment

### Robustness Features
- Handles transcript-disabled videos
- Multiple YouTube URL formats support
- Comprehensive error handling with detailed feedback
- Automatic fallback between methods
- Docker containerization with all dependencies

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (for Whisper fallback)

### 1. Environment Setup
```bash
# Create environment file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
REDIS_HOST=redis
REDIS_PORT=6379
EOF
```

### 2. Start Services
```bash
# Start all services (API, Celery workers, Redis)
docker-compose up -d

# Check service health
curl http://localhost:8000/health
```

### 3. Test Transcription
```bash
# Submit transcription job (proven endpoint structure)
curl -X POST "http://localhost:8000/api/jobs/submit" \\
  -H "Content-Type: application/json" \\
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "language": "ko",
    "export_format": "json"
  }'

# Check job status
curl "http://localhost:8000/api/jobs/{job_id}/status"
```

## 📡 API Endpoints

### Proven Method Endpoints (Primary)
- `POST /api/jobs/submit` - Submit transcription job
- `GET /api/jobs/{job_id}/status` - Get job status
- `GET /health` - Service health check
- `GET /api/stats` - Service statistics

### Legacy Endpoints (Backward Compatibility)
- `POST /api/transcribe/youtube` - Legacy transcription endpoint
- `GET /api/transcribe/{job_id}` - Legacy status check

## 🧪 Testing

### Run Comprehensive Tests
```bash
# Test all transcription methods
python test_transcription.py
```

### Test Individual Methods
```python
# Test YouTube API method
from main import get_transcript_with_fallbacks
result = await get_transcript_with_fallbacks("dQw4w9WgXcQ", "ko")

# Test Whisper API method
from whisper_transcriber import transcribe_with_whisper
result = await transcribe_with_whisper("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Test Browser Automation method
from browser_transcriber import transcribe_with_browser
result = await transcribe_with_browser("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

## 🔧 Configuration

### Celery Worker Settings (From Proven Method)
- **Concurrency**: 4 workers (CELERYD_CONCURRENCY)
- **Task Time Limit**: 10 minutes (CELERY_TASK_TIME_LIMIT)
- **Max Tasks Per Child**: 50 tasks (prevent memory leaks)

### Browser Automation Settings
- **Headless Mode**: Xvfb with virtual display
- **Browser**: Chromium with optimized flags
- **Viewport**: 1920x1080 for consistent rendering

## 🐛 Troubleshooting

### Common Issues

**1. Transcripts Disabled Error**
```
Solution: System will automatically fallback to Whisper API or Browser Automation
Status: This is expected behavior for the fallback system
```

**2. Browser Automation Fails**
```bash
# Check Xvfb is running
ps aux | grep Xvfb

# Check display setting
echo $DISPLAY  # Should be :99

# Restart with proper display
docker-compose restart transcription-api celery-worker
```

**3. Celery Workers Not Processing**
```bash
# Check worker status
docker-compose exec celery-worker celery -A celery_app inspect active

# Check Redis connection
docker-compose exec redis redis-cli ping

# View worker logs
docker-compose logs celery-worker
```

### Performance Optimization

**For High-Volume Usage:**
1. Increase Celery worker concurrency
2. Add more worker containers
3. Use Redis Cluster for scaling
4. Implement result caching

**For Memory Management:**
1. Reduce max-tasks-per-child if memory usage is high
2. Monitor browser processes
3. Clean up temporary files regularly

## 📊 Monitoring

### Service Status
```bash
# Check all services
docker-compose ps

# View real-time logs
docker-compose logs -f transcription-api

# Monitor Celery with Flower
# Access http://localhost:5555
```

### Performance Metrics
- **Success Rate**: Track method-wise success rates
- **Processing Time**: Monitor transcription duration
- **Queue Depth**: Watch Redis queue length
- **Memory Usage**: Monitor browser automation memory

## 🌟 Success Indicators

When working correctly, you should see:
- ✅ **Method 1 Success**: Direct YouTube API transcription
- ✅ **Method 2 Fallback**: Whisper API for disabled transcripts
- ✅ **Method 3 Fallback**: Browser automation for difficult cases
- ✅ **Real-time Status**: Progress updates during processing
- ✅ **Robust Error Handling**: Detailed error messages for debugging

## 📚 Architecture Details

This implementation recreates the successful architecture documented in `TRANSCRIPT_METHOD.md`:

- **Proven Endpoint Structure**: `/api/jobs/submit` with job ID system
- **Status Progression**: PENDING → STARTED → PROGRESS → SUCCESS/FAILURE
- **Multi-method Strategy**: Exactly matches the documented successful approach
- **Browser Automation**: Playwright with Xvfb headless environment
- **Async Processing**: Celery workers with Redis backend

The system is designed to handle the exact failure case mentioned: "*Transcripts are disabled for this video*" by automatically falling back to alternative transcription methods.

## 🔗 Related Documentation
- `TRANSCRIPT_METHOD.md` - Complete proven methodology
- `test_transcription.py` - Comprehensive test suite
- `docker-compose.yml` - Full service orchestration