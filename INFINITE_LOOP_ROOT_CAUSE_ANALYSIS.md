# Infinite Loop Root Cause Analysis - TVAS Transcription System

## Overview

The user reports an **infinite loop in the transcription step** of the 통합 분석 파이프라인 (Integrated Analysis Pipeline). This document identifies the root cause and provides specific remediation steps.

---

## The Problem Scenario

**User Observations:**
- User submits a YouTube URL in the pipeline page
- System shows "전사 (Transcription)" step spinning indefinitely
- No error message, just endless loading spinner
- System never progresses to analysis step

---

## Root Cause: Three-Layer Infinite Polling

The infinite loop is not a single issue but a combination of three polling mechanisms that can chain together:

### Layer 1: Frontend Polling (Client-Side Infinite Loop)

**File:** `/Users/jihunkong/teaching_analize/frontend/src/components/PipelineProgress.tsx` (line 66)

```typescript
useEffect(() => {
    if (!workflowId) return

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/workflow/status/{workflowId}`)
        const data = await response.json()

        // Update UI based on status
        // ...

        if (data.status === 'completed' && onComplete) {
          onComplete(data.data)  // <-- SHOULD STOP POLLING HERE
        } else if (data.status === 'error') {
          // Handle error
        }
        // ⚠️ NO ELSE CLAUSE FOR OTHER STATES!
      } catch (error) {
        console.error('Failed to fetch workflow status:', error)
        // ⚠️ POLLING CONTINUES EVEN ON NETWORK ERROR!
      }
    }

    // Poll every 3 seconds INDEFINITELY
    const interval = setInterval(pollStatus, 3000)
    pollStatus() // Initial call

    return () => clearInterval(interval)
}, [workflowId, onComplete])
```

**Problem:**
- `setInterval` runs FOREVER every 3 seconds
- Only stops if:
  1. `data.status === 'completed'` → calls callback to stop
  2. `data.status === 'error'` → sets error state
  3. Component unmounts → cleanup function runs
- **If status is ANY OTHER VALUE or API fails, polling continues forever**

**Polling Scenarios:**
| Scenario | Status Value | Polling Result |
|----------|--------------|---|
| Success | "completed" | Stops ✓ |
| Failure | "error" | Stops ✓ |
| Processing | "processing" | **Continues forever** ✗ |
| Network error | null/error | **Continues forever** ✗ |
| API returns 500 | error thrown | **Continues forever** ✗ |
| Workflow stuck in Redis | "in_progress" | **Continues forever** ✗ |

---

### Layer 2: Backend Workflow Polling (Server-Side Infinite Loop)

**File:** `/Users/jihunkong/teaching_analize/services/gateway/routers/workflows.py` (lines 150-180)

```python
async def run_full_analysis_workflow(...):
    # Step 1: Transcription polling loop
    max_attempts = 120  # 10 minutes
    attempt = 0
    
    while attempt < max_attempts:
        status_response = await client.get(
            f"{settings.transcription_service_url}/api/transcribe/status/{transcription_job_id}"
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            
            if status_data.get("status") == "completed":
                break  # <-- EXITS IF COMPLETED
            elif status_data.get("status") == "failed":
                raise Exception("Transcription job failed")  # <-- EXITS IF FAILED
            # ⚠️ IF STATUS IS "progress" OR OTHER, LOOP CONTINUES
        
        await asyncio.sleep(5)
        attempt += 1
    
    if attempt >= max_attempts:
        raise Exception("Transcription timeout")
```

**Problem:**
- Loop assumes status will be "completed" or "failed"
- If status is "started", "progress", or any other value, loop continues
- Only exits after 120 × 5 = 600 seconds (10 minutes)
- While looping, workflow status in Redis is still "processing"
- Frontend sees "processing" and keeps polling too (Layer 1)

**Timeout Limits:**
- Transcription polling: 120 attempts × 5 sec = **10 minutes**
- Analysis polling: 120 attempts × 5 sec = **10 minutes**
- Frontend polling: **NO LIMIT** (runs until page closes or error)

---

### Layer 3: Transcription Service Timeout (Service-Side Timeout)

**File:** `/Users/jihunkong/teaching_analize/services/transcription/main.py` (lines 228-235)

```python
TRANSCRIPTION_TIMEOUT = 300  # 5 minutes

try:
    result = await asyncio.wait_for(
        get_transcript_with_browser_scraping(video_id, language, youtube_url),
        timeout=TRANSCRIPTION_TIMEOUT
    )
except asyncio.TimeoutError:
    logger.error(f"Transcription timeout for job {job_id}")
    result = {
        "success": False,
        "error": f"Transcription timeout"
    }
```

**Problem:**
- If Selenium scraping takes >5 minutes, it times out
- But job status in Redis is never updated to "failed"
- Stays in "progress" state indefinitely
- Backend workflow layer continues polling for 10 minutes
- Frontend continues polling forever

---

## How the Infinite Loop Chain Forms

```
Timeline of Events:
├─ T0: User submits YouTube URL
├─ T0: Frontend starts polling (Layer 1)
│   └─ setInterval(pollStatus, 3000) every 3 seconds
│
├─ T0: Workflow initiated, status = "processing"
├─ T5: Backend starts transcription polling (Layer 2)
│   └─ while attempt < 120
│
├─ T5: Transcription job submitted to background
│   └─ Job status = "progress"
│
├─ T10: Selenium scraper starts (Layer 3)
│   └─ Timeout = 300 seconds
│
├─ T215: Selenium timeout occurs (>5 min elapsed)
│   └─ Job returns error result
│   └─ Job status should update to "failed"
│   └─ ⚠️ BUT IF STATUS NEVER UPDATES...
│
├─ T300: Backend polling timeout (10 minutes)
│   └─ Raises "Transcription timeout"
│   └─ Workflow status = "failed"
│   └─ Frontend receives "error" and stops
│
└─ T300+: If job status stuck in "progress":
    ├─ Backend keeps polling for full 600 sec
    ├─ Frontend keeps polling FOREVER
    └─ User sees infinite spinner
```

---

## Specific Failure Scenarios That Trigger Infinite Loop

### Scenario 1: Selenium Process Crash (MOST LIKELY)

```
Selenium WebDriver crashes (e.g., out of memory):
  ├─ get_transcript_with_browser_scraping() raises exception
  ├─ asyncio.wait_for() timeout timer expires
  ├─ Job status set to "failed" ✓
  └─ Should recover...

BUT IF:
  ├─ Exception caught but status not updated
  ├─ Job stays in "progress"
  ├─ Redis key has no expiration
  ├─ Backend polls for 10 minutes
  ├─ Frontend polls FOREVER
  └─ INFINITE LOOP ✗
```

### Scenario 2: Redis Connection Lost

```
Redis becomes unavailable:
  ├─ Job status cannot be updated
  ├─ Job stuck in "started" or "progress"
  ├─ Backend polls for 10 minutes
  ├─ Frontend polls FOREVER
  └─ INFINITE LOOP ✗
```

### Scenario 3: Selenium Hangs (Not Timing Out)

```
Chrome process hangs on page loading:
  ├─ asyncio.wait_for() timeout should trigger at 300 sec
  ├─ But Python event loop busy with blocking Selenium call
  ├─ Timeout doesn't fire
  ├─ Job never completes
  ├─ Status never updates
  ├─ Backend polls for 10 minutes
  ├─ Frontend polls FOREVER
  └─ INFINITE LOOP ✗
```

### Scenario 4: Status Field Misspelled/Missing

```
Job status dict has "state" not "status":
  ├─ Backend checks if status_data.get("status") == "completed"
  ├─ Returns None (field doesn't exist)
  ├─ Never equals "completed"
  ├─ Backend polls for 10 minutes
  ├─ Frontend polls FOREVER
  └─ INFINITE LOOP ✗
```

---

## Current Safeguards (Incomplete)

### What DOES Prevent Infinite Loop
1. **Backend timeout:** 10 minutes (600 seconds)
   - After 120 attempts, raises "Transcription timeout"
   - Workflow status updates to "error"
   - Frontend receives error and stops

2. **Transcription service timeout:** 5 minutes (300 seconds)
   - asyncio.wait_for() cancels Selenium operation
   - Sets job status to "failed"
   - Backend detects "failed" and proceeds to analysis

### What DOESN'T Prevent Infinite Loop
1. **Frontend has NO timeout**
   - setInterval runs forever
   - No max attempt limit
   - No fallback after N minutes

2. **Job status validation**
   - No check for invalid status values
   - No automatic state machine validation
   - No stuck-job detection

3. **Redis monitoring**
   - No TTL on job status keys
   - No check if status hasn't changed in X time
   - No zombie job cleanup

---

## Detection: How to Identify Infinite Loop in Production

### Frontend Symptoms
```
User Experience:
- Page shows spinner forever
- No error message appears
- Browser console shows repeated fetch calls
  └─ GET /api/workflow/status/{id} every 3 seconds
  └─ No error responses
  └─ Status always returns { status: "processing", current_step: "transcription" }
- Network tab shows 200 OK responses
- No memory leak, but continuous network activity
```

### Backend Symptoms
```
Server Logs:
- Continuous polling logs: "Checking transcription status: job_id={id}"
- Every 5 seconds for up to 10 minutes
- Workflow stays in "processing" state
- No "Transcription completed" or "Transcription failed" message
- Redis has key "workflow:{id}" stuck at status="processing"
```

### Redis State
```
KEYS "workflow:*" | GREP {workflow_id}
GET "workflow:{workflow_id}"
{
  "workflow_id": "...",
  "current_step": "transcription",
  "status": "processing",
  "message": "Transcription job submitted: {job_id}",
  "updated_at": "2025-01-13T14:32:00Z"
  // ^ Last update was 10+ minutes ago
}
```

---

## Root Cause Summary

| Layer | Issue | Duration | Impact |
|-------|-------|----------|--------|
| **Frontend** | No polling timeout | **INFINITE** | User sees spinner forever |
| **Backend** | Assumes status will eventually be completed/failed | 10 minutes | Holds workflow open |
| **Service** | May not update status on error | 5 minutes | Status stuck in progress |
| **Infrastructure** | No Redis key expiration | **INFINITE** | Stale data persists |

---

## The Fix (Priority Order)

### IMMEDIATE FIX (5 minutes)
Add frontend polling timeout:

**File:** `frontend/src/components/PipelineProgress.tsx`

```typescript
const MAX_POLLS = 600  // 30 minutes = 600 polls × 3 seconds
let pollCount = 0

const pollStatus = async () => {
  pollCount++
  
  if (pollCount > MAX_POLLS) {
    setError("Workflow took too long. Please try again.")
    clearInterval(interval)
    return
  }
  
  // ... rest of polling logic
}
```

### SECONDARY FIX (30 minutes)
Add stuck-job detection in backend:

**File:** `services/gateway/routers/workflows.py`

```python
# Track previous status
previous_status = None

while attempt < max_attempts:
    # ... get status ...
    
    if status_data.get("status") == previous_status:
        consecutive_same_status += 1
        if consecutive_same_status >= 3:  # No change for 15 seconds
            raise Exception("Transcription stuck - no status change")
    else:
        consecutive_same_status = 0
    
    previous_status = status_data.get("status")
    attempt += 1
```

### TERTIARY FIX (1 hour)
Ensure job status always updates:

**File:** `services/transcription/main.py`

```python
try:
    result = await asyncio.wait_for(...)
except asyncio.TimeoutError:
    # Ensure Redis is updated
    job_data = {
        "job_id": job_id,
        "status": "failed",
        "message": "Transcription timeout after 5 minutes",
        "error": "Browser automation exceeded time limit"
    }
    redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))
    raise
```

---

## Proof of Concept: How to Reproduce

```bash
# 1. Submit workflow with YouTube URL that Selenium cannot process:
curl -X POST http://localhost:8000/api/workflow/full-analysis \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=INVALID_ID"}'

# Response:
# {
#   "workflow_id": "abc123",
#   "status": "queued"
# }

# 2. Poll status every 3 seconds (simulate frontend):
for i in {1..200}; do
  curl http://localhost:8000/api/workflow/status/abc123
  sleep 3
done

# Result: Status stays "processing" for 10 minutes (backend limit)
#         Frontend would continue forever without the IMMEDIATE FIX
```

---

## Conclusion

The infinite loop is caused by:

1. **Frontend has NO timeout** ← CRITICAL
2. **Backend polling assumes eventual completion** ← HIGH
3. **Transcription service may not update status on error** ← MEDIUM
4. **No stuck-job detection or cleanup** ← MEDIUM

All three layers must be fixed together to prevent infinite loops under error conditions. The IMMEDIATE FIX (frontend timeout) is the most important and takes only 5 minutes.

