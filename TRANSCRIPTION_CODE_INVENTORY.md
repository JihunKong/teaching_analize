# TVAS Transcription System - Complete Code Inventory

## Executive Summary

The TVAS (Teacher Voice Analysis System) transcription module has been analyzed comprehensively. The current implementation uses **ONLY Selenium-based browser automation** for YouTube transcript extraction, with all other methods disabled. However, there is a **WhisperX import statement in the core module that causes import errors** and polling logic in the workflow orchestration that could cause infinite loops under certain conditions.

---

## 1. Transcription Service Files

### 1.1 Main Service Entry Point
**File:** `/Users/jihunkong/teaching_analize/services/transcription/main.py` (625 lines)

**Key Components:**
- `TranscriptionRequest` model (lines 103-106): YouTube URL, language, export format
- `async def get_transcript_with_browser_scraping()` (lines 132-200): **ONLY METHOD CURRENTLY USED**
  - Uses Selenium browser automation (proven working)
  - Playwright disabled due to visibility issues
  - 5-minute timeout to prevent infinite loops (line 228: `TRANSCRIPTION_TIMEOUT = 300`)
- `async def process_transcription_job()` (lines 202-329): Background task processor
  - Caches results in Redis (7-day TTL)
  - Stores transcripts in PostgreSQL database
  - Job status tracking with progress updates
- REST Endpoints:
  - `POST /api/jobs/submit`: Submit transcription job with caching (tier-1 Redis, tier-2 PostgreSQL)
  - `GET /api/jobs/{job_id}/status`: Get job status
  - `GET /api/transcripts/{transcript_id}`: Retrieve transcript by ID
  - `GET /api/stats`: Service statistics

**Critical Features:**
- **3-tier caching architecture:**
  - Level 1: Redis hot cache (instant response)
  - Level 2: PostgreSQL database
  - Level 3: New transcription job
- Job status transitions: PENDING → started → progress → success/failed
- Extended Redis TTL: 86,400 seconds (24 hours)

---

### 1.2 Selenium YouTube Scraper
**File:** `/Users/jihunkong/teaching_analize/services/transcription/selenium_youtube_scraper.py` (1100+ lines)

**Main Class:** `SeleniumYouTubeScraper`

**Key Methods:**
- `start_driver()` (lines 40-103): Chrome WebDriver initialization
  - Headless mode enabled for server environments
  - Bot detection evasion options included
  - Supports Docker environment (checks for `/usr/bin/chromedriver`)
  - Uses WebDriver Manager for automatic ChromeDriver management
  - Window size optimization for faster loading
  
- `scrape_youtube_transcript()` (lines 920-1000+): Main extraction method
  - Loads YouTube page
  - Handles ads and cookie consent
  - Waits for video player to load
  - Finds and clicks "스크립트 보기" (Show transcript) button using user-provided selectors
  - Extracts transcript segments with timestamps
  - Returns text and structured segments

- Helper Methods:
  - `wait_for_ads_to_finish()`: Ad detection and skip
  - `wait_for_video_ready()`: Player initialization
  - `load_youtube_page()`: Page loading with timeout handling
  - `find_transcript_button()`: Multiple selector strategies (CSS, XPath)
  - `extract_transcript_segments()`: Parse transcript segments
  - `open_transcript_panel()`: Handle panel opening with scrolling
  - `scroll_transcript_panel_to_load_all()`: Load all segments via scrolling
  - `extract_transcript_text_fallback()`: Fallback text extraction

**Return Value:**
- Success: String containing full transcript text
- Failure: None or error object

---

### 1.3 YouTube HTML Scraper (Alternative - Not Used)
**File:** `/Users/jihunkong/teaching_analize/services/transcription/youtube_html_scraper.py` (330 lines)

**Status:** Implemented but **NOT USED** in production code

**Purpose:** Alternative HTML scraping approach without full browser simulation

**Main Method:**
- `scrape_transcript_from_html()` (lines 92-249): Attempts to extract transcripts using:
  - Page loading and consent handling
  - Button finding with user-provided selector: `"tp-yt-paper-button#expand.button.style-scope.ytd-text-inline-expander"`
  - Multiple selector strategies for transcript button
  - Segment extraction with timestamps

**Note:** This file exists in codebase but is NOT called by any production code path

---

### 1.4 Database Models
**File:** `/Users/jihunkong/teaching_analize/services/transcription/database.py` (300+ lines)

**Main Model:** `TranscriptDB`

**Columns:**
- `transcript_id`: Unique identifier (UUID)
- `source_type`: 'youtube', 'upload', 'live'
- `source_url`: YouTube URL or file path
- `video_id`: YouTube video ID
- `language`: Language code (default: 'ko')
- `method_used`: 'browser_scraping', 'whisper', 'youtube_api' (currently only 'browser_scraping' used)
- `transcript_text`: Full transcript (TEXT field)
- `segments_json`: Timestamped segments (JSON)
- `character_count`, `word_count`: Statistics
- `teacher_name`, `subject`, `grade_level`: Educational context
- `anonymized`, `research_consent`: Privacy flags
- Timestamps: `created_at`, `updated_at`
- **Composite Index:** `idx_video_language` on (video_id, language) for fast cache lookups

**Utility Functions:**
- `store_transcript()`: Insert/update transcript in database
- `get_db()`: Session dependency for FastAPI
- `init_database()`: Create tables on startup

---

### 1.5 Cache Manager
**File:** `/Users/jihunkong/teaching_analize/services/transcription/utils/cache_manager.py` (100+ lines)

**Class:** `TranscriptCacheManager`

**Configuration:**
- Cache version: "v1"
- TTL: 604,800 seconds (7 days)
- Key format: `transcript:v1:youtube:{video_id}:{language}`

**Methods:**
- `generate_youtube_key()`: Generate cache key for YouTube videos
- `generate_upload_key()`: Generate cache key for uploaded videos
- `get()`: Retrieve from Redis cache
- `set()`: Store in Redis cache
- `delete()`: Remove from cache
- `exists()`: Check if cached

**Purpose:** Prevent redundant transcription of same videos

---

### 1.6 Celery Task Definition
**File:** `/Users/jihunkong/teaching_analize/services/transcription/celery_tasks.py` (216 lines)

**Tasks:**
1. `process_transcription_task()` (lines 31-159): Main async transcription
   - Status progression: STARTED → PROGRESS → SUCCESS/FAILURE
   - Calls `get_transcript_with_browser_scraping()`
   - Stores results in Redis with 24-hour TTL
   - Retry logic: Up to 2 retries with 60-second backoff
   - Processing time tracking

2. `cleanup_old_jobs()` (lines 161-192): Maintenance task
   - Removes jobs older than 24 hours
   - Runs periodically to prevent storage bloat

3. `health_check_task()` (lines 194-216): Monitoring
   - Tests Redis connection
   - Returns service health status

**Celery Configuration:** 
- Broker: Redis
- Queue: 'transcription'
- Default task timeout: 1 hour

---

### 1.7 Core Module (Problematic)
**File:** `/Users/jihunkong/teaching_analize/services/transcription/core/__init__.py` (4 lines)

```python
from .whisperx_service import WhisperXService
__all__ = ['WhisperXService']
```

**CRITICAL ISSUE:** 
- Imports `WhisperXService` from `whisperx_service.py`
- **THIS FILE DOES NOT EXIST** (only .pyc compiled file exists)
- Causes import error when core module is imported
- Not used by production code (main.py doesn't import from core)

---

## 2. Gateway Routing & Orchestration

### 2.1 Transcription Router
**File:** `/Users/jihunkong/teaching_analize/services/gateway/routers/transcription.py` (174 lines)

**Endpoints (Proxy to Transcription Service):**
1. `POST /api/transcribe/youtube`: Submit transcription job
2. `GET /api/transcribe/{job_id}`: Get job status (legacy)
3. `GET /api/transcribe/status/{job_id}`: Get job status
4. `GET /api/transcribe/result/{job_id}`: Get transcription result
5. `GET /api/transcribe/health`: Health check

**Architecture:** Proxies requests to transcription microservice at `settings.transcription_service_url`

**Error Handling:**
- 503 Service Unavailable if transcription service down
- 404 Not Found for missing jobs
- Timeout handling (service_timeout from config)

---

### 2.2 Workflow Orchestration Router
**File:** `/Users/jihunkong/teaching_analize/services/gateway/routers/workflows.py` (355 lines)

**Key Function:** `run_full_analysis_workflow()` (lines 63-282)

**INFINITE LOOP ISSUE IDENTIFIED:**

**Step 1: Transcription (lines 102-184)**
- Submits transcription job
- Polls for completion with **MAX 120 ATTEMPTS** (10 minutes)
- **POLLING LOOP (lines 150-180):**
  ```python
  while attempt < max_attempts:
      status_response = await client.get(
          f"{settings.transcription_service_url}/api/transcribe/status/{transcription_job_id}"
      )
      if status_response.status_code == 200:
          status_data = status_response.json()
          if status_data.get("status") == "completed":
              # Success - break loop
              break
          elif status_data.get("status") == "failed":
              raise Exception("Transcription job failed")
      
      await asyncio.sleep(5)
      attempt += 1
  
  if attempt >= max_attempts:
      raise Exception("Transcription timeout")
  ```

**ISSUE:** Loop exits successfully if transcription is cached (returns "completed" immediately) OR if max_attempts reached. But if status never reaches "completed" or "failed", loop continues until timeout.

**Step 2: Analysis (lines 186-244)**
- Same polling pattern with **MAX 120 ATTEMPTS**
- Checks for "completed" or "failed" status

**Workflow Status Endpoints:**
- `POST /api/workflow/full-analysis`: Start workflow
- `GET /api/workflow/status/{workflow_id}`: Get workflow status

**Status Updates:** Stored in Redis with 2-hour TTL

---

## 3. Frontend Integration

### 3.1 Pipeline Page
**File:** `/Users/jihunkong/teaching_analize/frontend/src/app/pipeline/page.tsx` (172 lines)

**Purpose:** User interface for 통합 분석 파이프라인 (Integrated Analysis Pipeline)

**Key Features:**
- Header: "🚀 통합 분석 파이프라인"
- Form submission to `/api/workflow/full-analysis`
- Framework selection (CBIL, Diagnostic, Bloom's, Webb's)
- Language setting (ko, en, etc.)
- Use diarization toggle (currently set to true)
- Displays workflow ID after submission
- Shows 3-5 minute estimated completion time

**Flow:**
1. User enters YouTube URL
2. User selects analysis framework
3. Submit → calls workflow API
4. Displays `<PipelineProgress>` component with workflow ID

---

### 3.2 Pipeline Progress Component
**File:** `/Users/jihunkong/teaching_analize/frontend/src/components/PipelineProgress.tsx` (140 lines)

**POLLING IDENTIFIED (Line 66):**
```typescript
const interval = setInterval(pollStatus, 3000)
```
**Polls every 3 seconds** for workflow status

**Status Polling Function (lines 28-63):**
```typescript
const pollStatus = async () => {
  try {
    const response = await fetch(`/api/workflow/status/${workflowId}`)
    const data = await response.json()
    
    if (data.current_step) {
      const updatedSteps = steps.map(step => {
        if (step.id === data.current_step) {
          return { ...step, status: 'in_progress' as const, message: data.message }
        } else if (data.completed_steps?.includes(step.id)) {
          return { ...step, status: 'completed' as const }
        }
        return step
      })
      setSteps(updatedSteps)
      
      if (data.status === 'completed' && onComplete) {
        onComplete(data.data)  // Stop polling on completion
      } else if (data.status === 'error') {
        // Handle error state
      }
    }
  } catch (error) {
    console.error('Failed to fetch workflow status:', error)
  }
}
```

**How Polling Stops:**
1. `data.status === 'completed'` → calls `onComplete()` callback
2. `data.status === 'error'` → displays error
3. Component unmounts → `clearInterval(interval)` (line 69)
4. **NOTE:** If status never becomes 'completed' or 'error', polling continues indefinitely

**Displayed Steps:**
1. "전사 (Transcription)" - Blue spinner while in_progress
2. "분석 (Analysis)" - Blue spinner while in_progress  
3. "보고서 생성 (Report)" - Blue spinner while in_progress

---

## 4. API Flow Diagram

```
Frontend (pipeline/page.tsx)
    |
    ├─→ POST /api/workflow/full-analysis
    |   └─→ Gateway Workflow Router (workflows.py)
    |       ├─→ POST /api/transcribe/youtube
    |       |   └─→ Transcription Service (main.py)
    |       |       ├─→ Check Redis Cache (cache_manager.py)
    |       |       ├─→ Check PostgreSQL (database.py)
    |       |       └─→ Background Task: Selenium Scraping (selenium_youtube_scraper.py)
    |       |
    |       ├─→ POLLING: GET /api/transcribe/status/{job_id} (max 120 attempts)
    |       |
    |       ├─→ POST /api/analyze/text
    |       |   └─→ Analysis Service
    |       |
    |       └─→ POLLING: GET /api/analyze/{job_id} (max 120 attempts)
    |
    └─→ GET /api/workflow/status/{workflow_id}
        └─→ POLLING every 3 seconds (PipelineProgress.tsx)
```

---

## 5. Current Transcription Methods

### 5.1 ACTIVE Methods (Currently Used)
1. **Selenium Browser Automation** ✓
   - File: `selenium_youtube_scraper.py`
   - Method: Click "스크립트 보기" button, extract segments
   - Status: **FULLY FUNCTIONAL**
   - Return: String transcript text
   - Timeout: 300 seconds (5 minutes)

### 5.2 DISABLED/UNUSED Methods
1. **Playwright** ✗
   - Explicitly disabled in `main.py` line 192
   - Reason: Button visibility issues
   - Status: Code present but not executed

2. **YouTube API** ✗
   - Not implemented in current codebase
   - Comments suggest it was considered (database.py line 50)
   - Status: Never coded

3. **WhisperX** ✗
   - Import statement in `core/__init__.py` but file doesn't exist
   - Not called by any production code path
   - Status: **Broken import, causes errors**

---

## 6. Infinite Loop Vulnerability Analysis

### 6.1 Backend Polling Loops

**File:** `services/gateway/routers/workflows.py` (lines 150, 217)

**Vulnerability:**
```python
while attempt < max_attempts:
    status_response = await client.get(...)
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        if status_data.get("status") == "completed":
            break  # Exits loop
        elif status_data.get("status") == "failed":
            raise Exception()  # Exits loop
        # ⚠️ If status is something else (e.g., "processing"), 
        # loop continues without explicit exit condition
    
    await asyncio.sleep(5)
    attempt += 1

if attempt >= max_attempts:
    raise Exception("Timeout")
```

**Cause:** If a job gets stuck in "processing" state indefinitely, the loop will continue for 10 minutes until timeout.

**Potential Causes for Stuck Status:**
1. Transcription service crashes while processing
2. Redis failure: Job status never updated to "completed"
3. Network partition: Status updates not received
4. Selenium crash: Thread hangs indefinitely
5. Browser process zombie: Driver.quit() fails

**Max Attempts Limits:**
- Transcription: 120 attempts × 5 seconds = 10 minutes
- Analysis: 120 attempts × 5 seconds = 10 minutes
- Frontend polling: **UNLIMITED** (no max attempts)

---

### 6.2 Frontend Polling Loop

**File:** `frontend/src/components/PipelineProgress.tsx` (line 66)

**Vulnerability:**
```typescript
const interval = setInterval(pollStatus, 3000)  // Every 3 seconds

// Loop stops only when:
// 1. data.status === 'completed' → onComplete() called
// 2. data.status === 'error' → error state
// 3. Component unmounts → clearInterval()
// ⚠️ If workflow status never becomes 'completed' or 'error', polling NEVER stops
```

**Impact:** 
- Continuous API requests every 3 seconds
- Browser tab remains active indefinitely
- User sees infinite spinner without completion

**Potential Stuck States:**
1. Workflow stuck in Redis as 'processing'
2. Backend crashes: Frontend retries forever
3. Network error: Polling continues in error state
4. Status endpoint returns 500: Polling continues

---

## 7. Problem Root Causes

### 7.1 WhisperX Import Error
**Location:** `services/transcription/core/__init__.py`

**Problem:**
- Imports `WhisperXService` from non-existent file
- Creates broken import chain
- Not critical (main.py doesn't use it) but clutters codebase

**Solution:** Remove import or create dummy file

---

### 7.2 Polling Without Explicit Completion Detection
**Locations:**
- `workflows.py` lines 150-180 (transcription polling)
- `workflows.py` lines 217-241 (analysis polling)
- `PipelineProgress.tsx` line 66 (frontend polling)

**Problem:** 
- Polling loops assume status will eventually be "completed" or "failed"
- No recovery mechanism for stuck jobs
- No maximum polling duration on frontend

**Solution:** Add explicit polling limits and stuck-state detection

---

## 8. Transcription Method Decision Tree

```
User submits YouTube URL
    ↓
Extract video ID
    ↓
Check Redis Cache
    ├─ HIT → Return cached result immediately (status: completed)
    └─ MISS ↓
    
Check PostgreSQL Database
    ├─ HIT → Cache in Redis, return cached result (status: completed)
    └─ MISS ↓

Create new transcription job
    ├─ Status: PENDING
    └─ Submit background task ↓

SELENIUM BROWSER AUTOMATION (ONLY METHOD)
    ├─ Initialize Chrome WebDriver
    ├─ Load YouTube page
    ├─ Handle ads and consent
    ├─ Wait for video player
    ├─ Click "스크립트 보기" button (user-provided selector)
    ├─ Extract transcript segments with timestamps
    ├─ Return transcript text
    │
    ├─ SUCCESS → Status: success
    │   ├─ Store in PostgreSQL
    │   ├─ Cache in Redis (7 days)
    │   └─ Return to user
    │
    └─ FAILURE (after 5-minute timeout) → Status: failed
        ├─ Log error
        └─ Return error message to user
```

---

## 9. Critical Implementation Details

### 9.1 Selenium Configuration
- **Headless mode:** Enabled (faster, server-friendly)
- **Window size:** 1366×768 (optimized for fast loading)
- **User agent:** Chrome 119.0.0.0 on macOS (realistic)
- **Bot detection evasion:**
  - Disable automation controls
  - Remove webdriver property
  - Disable dev tools features
- **Performance optimizations:**
  - Disable image loading
  - Disable plugins/extensions
  - Memory pressure settings
  - Renderer backgrounding disabled
- **Timeout:** 15 seconds for individual waits
- **Total operation timeout:** 300 seconds (main.py line 228)

### 9.2 Caching Strategy
- **Tier 1 (Hot):** Redis cache
  - Key: `transcript:v1:youtube:{video_id}:{language}`
  - TTL: 604,800 seconds (7 days)
  - Response time: <100ms
  
- **Tier 2 (Warm):** PostgreSQL database
  - Fallback if Redis misses
  - Repopulates Redis cache
  - Response time: <1 second
  
- **Tier 3 (Cold):** New transcription
  - Selenium browser automation
  - Response time: 30-60 seconds

### 9.3 Job Status Lifecycle
```
PENDING (initial)
    ↓
started (acknowledged by worker)
    ↓
progress (processing)
    ↓
success ← OR → failed
    ↓
(expires after 24 hours in Redis)
```

---

## 10. File Locations Summary

### Transcription Service
- `/Users/jihunkong/teaching_analize/services/transcription/`
  - `main.py` - Main FastAPI application (625 lines)
  - `selenium_youtube_scraper.py` - Selenium browser automation (1100+ lines)
  - `youtube_html_scraper.py` - Alternative HTML scraper (330 lines, unused)
  - `database.py` - SQLAlchemy models (300+ lines)
  - `celery_tasks.py` - Async job definitions (216 lines)
  - `celery_app.py` - Celery configuration (60 lines)
  - `requirements.txt` - Python dependencies
  - `core/__init__.py` - **BROKEN** import (4 lines)
  - `utils/cache_manager.py` - Redis caching (100+ lines)
  - `utils/text_preprocessing.py` - Text utilities
  - `utils/__init__.py` - Utils package init

### Gateway/Orchestration
- `/Users/jihunkong/teaching_analize/services/gateway/routers/`
  - `transcription.py` - Transcription router (174 lines)
  - `workflows.py` - Workflow orchestration (355 lines) **POLLING LOOPS HERE**
  - `analysis.py` - Analysis routing
  - `reporting.py` - Report routing

### Frontend
- `/Users/jihunkong/teaching_analize/frontend/src/`
  - `app/pipeline/page.tsx` - Pipeline page (172 lines)
  - `components/PipelineProgress.tsx` - Status polling (140 lines) **INFINITE POLLING HERE**

---

## 11. Dependencies Analysis

**Required for Selenium method:**
- `selenium==4.15.2`
- `webdriver-manager==4.0.1`
- `fastapi==0.104.1`
- `redis==5.0.1`
- `sqlalchemy==2.0.23`
- `psycopg2-binary==2.9.9` (PostgreSQL)
- `celery==5.3.4` (Async jobs)

**Optional/Unused:**
- WhisperX libraries (none installed, import fails)
- YouTube API client (none installed)
- Playwright (code references but not installed)

---

## 12. Recommendations

### HIGH PRIORITY
1. **Remove WhisperX import** from `core/__init__.py` or create dummy file
   - **Impact:** Fixes broken imports
   - **Effort:** 5 minutes

2. **Add stuck-job detection** in workflows.py
   - **Impact:** Prevents infinite polling
   - **Effort:** 30 minutes
   - **Example:** Check if status hasn't changed for >2 consecutive polls

3. **Add frontend polling timeout**
   - **Impact:** Prevents infinite spinning
   - **Effort:** 15 minutes
   - **Example:** Max 600 polls (30 minutes) before showing timeout error

### MEDIUM PRIORITY
4. **Add job status recovery** in transcription service
   - **Impact:** Graceful handling of crashed jobs
   - **Effort:** 1 hour
   - **Example:** Monitor job age, auto-fail if >15 minutes without update

5. **Remove unused scrapers** (youtube_html_scraper.py)
   - **Impact:** Cleaner codebase
   - **Effort:** 10 minutes

6. **Add explicit Selenium error recovery**
   - **Impact:** Better resilience
   - **Effort:** 1 hour
   - **Example:** Automatic Chrome restart on crash

### ONGOING
7. **Monitor job success rate** in production
8. **Add alerting** for stuck workflows
9. **Log all polling attempts** for debugging

---

## 13. Testing Coverage

**Test File:** `/Users/jihunkong/teaching_analize/services/transcription/test_transcription.py`

**Current Tests:**
- Selenium scraping test (commented: "NO API methods allowed")
- Health endpoint test
- Job submission test
- Status polling test

**Note:** Tests verify "NO API calls (youtube-transcript-api, whisper-api)" are used

---

## Conclusion

The TVAS transcription system is **correctly using ONLY Selenium-based browser automation** as required. However:

1. **WhisperX import in `core/__init__.py` creates a broken import**
2. **Polling loops (backend and frontend) lack explicit stuck-state detection**
3. **Frontend has unlimited polling with no timeout**
4. **Unused code (youtube_html_scraper.py) should be removed**

These issues can cause infinite loops under error conditions. Recommended fixes are outlined above.

