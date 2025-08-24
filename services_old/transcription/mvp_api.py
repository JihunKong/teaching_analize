#!/usr/bin/env python3
"""
MVP YouTube Transcript API
Simple API for YouTube video transcript extraction - MVP Demo
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

# Set up logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/logs/mvp_api.log')
    ]
)
logger = logging.getLogger(__name__)

# Import our YouTube handlers
from youtube_handler import YouTubeHandler
from browser_youtube_handler import BrowserYouTubeHandler, get_handler_stats

# Import Celery components (optional)
try:
    from celery_app import app as celery_app
    from background_tasks import extract_youtube_transcript_task
    CELERY_AVAILABLE = True
    logger.info("Celery components imported successfully")
except ImportError as e:
    logger.warning(f"Celery components not available: {e}")
    CELERY_AVAILABLE = False

# Try to import OAuth components (optional)
try:
    from youtube_oauth import YouTubeOAuth
    from oauth_web_handler import OAuthWebHandler
    OAUTH_AVAILABLE = True
    logger.info("OAuth components imported successfully")
except ImportError as e:
    logger.warning(f"OAuth components not available: {e}")
    OAUTH_AVAILABLE = False

# Request/Response models
class YouTubeTranscriptRequest(BaseModel):
    """Request model for YouTube transcript"""
    url: str
    language: str = "ko"
    format: str = "text"  # text, json, srt

class TranscriptResponse(BaseModel):
    """Response model for transcript"""
    success: bool
    video_url: str
    video_id: Optional[str] = None
    transcript: Optional[str] = None
    language: str
    character_count: int = 0
    processing_time: float = 0
    method_used: str = "unknown"
    error: Optional[str] = None
    timestamp: str

# New models for async processing
class JobSubmissionResponse(BaseModel):
    """Response model for job submission"""
    job_id: str
    status: str
    message: str
    submitted_at: str
    estimated_completion: str

class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str  # PENDING, STARTED, PROGRESS, SUCCESS, FAILURE
    meta: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    submitted_at: Optional[str] = None
    completed_at: Optional[str] = None

# Create FastAPI app
app = FastAPI(
    title="YouTube Transcript MVP",
    description="MVP API for extracting transcripts from YouTube videos",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize YouTube handlers
youtube_handler = YouTubeHandler()
browser_handler = BrowserYouTubeHandler()

# Initialize OAuth components if available
youtube_oauth = None
oauth_handler = None

if OAUTH_AVAILABLE:
    try:
        youtube_oauth = YouTubeOAuth()
        oauth_handler = OAuthWebHandler(app)
        logger.info("✅ OAuth components initialized")
    except Exception as e:
        logger.warning(f"OAuth initialization failed: {e}")
        OAUTH_AVAILABLE = False

# Global stats for MVP
stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "start_time": datetime.now()
}

@app.get("/", response_class=HTMLResponse)
async def root():
    """MVP Demo Landing Page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Transcript - Async Job System</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px; 
                margin: 20px auto; 
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            h1 { 
                color: #2c3e50; 
                text-align: center;
                margin-bottom: 20px;
            }
            .system-info {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }
            .feature-highlight {
                background: #e8f8f5;
                border-left: 4px solid #27ae60;
                padding: 15px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }
            .form-group { 
                margin-bottom: 15px; 
            }
            label { 
                display: block; 
                margin-bottom: 5px; 
                font-weight: 600;
                color: #34495e;
            }
            input, select { 
                width: 100%; 
                padding: 10px; 
                border: 2px solid #ddd; 
                border-radius: 6px;
                font-size: 16px;
                box-sizing: border-box;
            }
            input:focus, select:focus {
                border-color: #3498db;
                outline: none;
            }
            button { 
                background: #27ae60; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 6px;
                cursor: pointer; 
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s;
                margin-right: 10px;
            }
            button:hover { 
                background: #229954; 
                transform: translateY(-1px);
            }
            button:disabled {
                background: #bdc3c7;
                cursor: not-allowed;
                transform: none;
            }
            .btn-cancel {
                background: #e74c3c;
            }
            .btn-cancel:hover {
                background: #c0392b;
            }
            .job-queue {
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .job-queue h2 {
                background: #34495e;
                color: white;
                margin: 0;
                padding: 20px;
                font-size: 18px;
            }
            .job-item {
                border-bottom: 1px solid #ecf0f1;
                padding: 20px;
                transition: background 0.3s;
            }
            .job-item:hover {
                background: #f8f9fa;
            }
            .job-item:last-child {
                border-bottom: none;
            }
            .job-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .job-url {
                font-weight: 600;
                color: #2c3e50;
                text-decoration: none;
            }
            .job-url:hover {
                color: #3498db;
            }
            .job-status {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }
            .status-pending { background: #f39c12; color: white; }
            .status-started { background: #3498db; color: white; }
            .status-progress { background: #e67e22; color: white; }
            .status-success { background: #27ae60; color: white; }
            .status-failure { background: #e74c3c; color: white; }
            .progress-bar {
                width: 100%;
                height: 6px;
                background: #ecf0f1;
                border-radius: 3px;
                overflow: hidden;
                margin: 10px 0;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #3498db, #2ecc71);
                transition: width 0.3s;
                border-radius: 3px;
            }
            .job-meta {
                font-size: 12px;
                color: #7f8c8d;
                margin-bottom: 10px;
            }
            .job-result {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                padding: 15px;
                margin-top: 10px;
                max-height: 200px;
                overflow-y: auto;
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 12px;
            }
            .example-urls {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
            }
            .example-url {
                display: inline-block;
                color: #3498db;
                text-decoration: none;
                margin: 5px 10px 5px 0;
                cursor: pointer;
                padding: 5px 10px;
                border: 1px solid #3498db;
                border-radius: 4px;
                font-size: 12px;
            }
            .example-url:hover {
                background: #3498db;
                color: white;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-number {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
            .stat-label {
                font-size: 12px;
                color: #7f8c8d;
                text-transform: uppercase;
            }
        </style>
    </head>
    <body>
        <h1>🚀 YouTube Transcript - Async Job System</h1>
        
        <div class="system-info">
            <h3>⚡ PHASE 3 COMPLETE: Background Processing System</h3>
            <p>✅ Redis + Celery + FastAPI | ✅ Real-time Progress | ✅ Multi-job Queue | ✅ Non-blocking UX</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-requests">0</div>
                <div class="stat-label">Total Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="success-rate">0%</div>
                <div class="stat-label">Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="active-jobs">0</div>
                <div class="stat-label">Active Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="cached-items">0</div>
                <div class="stat-label">Cached Results</div>
            </div>
        </div>

        <div class="container">
            <div class="feature-highlight">
                🎯 <strong>New Experience:</strong> Submit jobs instantly → Get immediate job ID → Watch real-time progress → Continue working!
            </div>
            
            <div class="example-urls">
                <strong>📺 Quick Test URLs:</strong>
                <a class="example-url" onclick="setUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ')">Rick Roll (EN)</a>
                <a class="example-url" onclick="setUrl('https://www.youtube.com/watch?v=arj7oStGLkU')">TED Talk (KO)</a>
                <a class="example-url" onclick="setUrl('https://youtu.be/dQw4w9WgXcQ')">Short URL</a>
            </div>
            
            <form id="jobForm">
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 15px; align-items: end;">
                    <div class="form-group">
                        <label for="url">YouTube URL:</label>
                        <input type="url" id="url" name="url" required 
                               placeholder="https://www.youtube.com/watch?v=...">
                    </div>
                    <div class="form-group">
                        <label for="language">Language:</label>
                        <select id="language" name="language">
                            <option value="en">English</option>
                            <option value="ko">한국어</option>
                            <option value="ja">日本語</option>
                            <option value="zh">中文</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="format">Format:</label>
                        <select id="format" name="format">
                            <option value="text">Text</option>
                            <option value="json">JSON</option>
                            <option value="srt">SRT</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <button type="submit" id="submitBtn">🚀 Submit Job</button>
                    </div>
                </div>
            </form>
        </div>

        <div class="job-queue">
            <h2>📋 Job Queue & Results</h2>
            <div id="job-list">
                <div style="padding: 40px; text-align: center; color: #7f8c8d;">
                    No jobs submitted yet. Submit your first job above! 🎬
                </div>
            </div>
        </div>

        <script>
            // Global state
            const jobs = new Map();
            const activePolls = new Set();

            // Load initial stats
            updateStats();
            setInterval(updateStats, 5000);

            function updateStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('total-requests').textContent = data.total_requests;
                        document.getElementById('success-rate').textContent = data.success_rate + '%';
                        document.getElementById('cached-items').textContent = data.cache_stats.cached_results;
                        
                        // Count active jobs
                        const activeCount = Array.from(jobs.values())
                            .filter(job => ['PENDING', 'STARTED', 'PROGRESS'].includes(job.status)).length;
                        document.getElementById('active-jobs').textContent = activeCount;
                    })
                    .catch(err => console.error('Stats error:', err));
            }

            function setUrl(url) {
                document.getElementById('url').value = url;
            }

            function getStatusClass(status) {
                return `status-${status.toLowerCase()}`;
            }

            function getStatusEmoji(status) {
                const emojis = {
                    'PENDING': '🟡',
                    'STARTED': '🔵', 
                    'PROGRESS': '🟠',
                    'SUCCESS': '🟢',
                    'FAILURE': '🔴'
                };
                return emojis[status] || '⚪';
            }

            function getProgress(job) {
                if (job.status === 'SUCCESS') return 100;
                if (job.status === 'FAILURE') return 100;
                if (job.status === 'PROGRESS' && job.meta && job.meta.progress) {
                    return job.meta.progress;
                }
                if (job.status === 'STARTED') return 25;
                if (job.status === 'PENDING') return 10;
                return 0;
            }

            function formatDuration(seconds) {
                if (seconds < 60) return `${seconds.toFixed(1)}s`;
                const minutes = Math.floor(seconds / 60);
                const secs = (seconds % 60).toFixed(0);
                return `${minutes}m ${secs}s`;
            }

            function renderJob(job) {
                const progress = getProgress(job);
                const isCompleted = ['SUCCESS', 'FAILURE'].includes(job.status);
                
                return `
                    <div class="job-item" data-job-id="${job.job_id}">
                        <div class="job-header">
                            <a href="${job.video_url}" target="_blank" class="job-url">
                                📺 ${job.video_url.substring(0, 50)}...
                            </a>
                            <div>
                                <span class="job-status ${getStatusClass(job.status)}">
                                    ${getStatusEmoji(job.status)} ${job.status}
                                </span>
                                ${!isCompleted ? `<button class="btn-cancel" onclick="cancelJob('${job.job_id}')">Cancel</button>` : ''}
                            </div>
                        </div>
                        
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        
                        <div class="job-meta">
                            🔤 ${job.language.toUpperCase()} | 📄 ${job.format.toUpperCase()} | 
                            ⏱️ ${job.processing_time ? formatDuration(job.processing_time) : 'Processing...'} |
                            🆔 ${job.job_id.substring(0, 8)}
                            ${job.status === 'PROGRESS' && job.meta ? ` | ${job.meta.status || ''}` : ''}
                        </div>
                        
                        ${job.status === 'SUCCESS' && job.result ? `
                            <div class="job-result">
                                <strong>✅ Success - ${job.result.character_count} characters extracted via ${job.result.method_used}</strong>
                                
${job.result.transcript.substring(0, 500)}${job.result.transcript.length > 500 ? '...' : ''}
                            </div>
                        ` : ''}
                        
                        ${job.status === 'FAILURE' && job.meta ? `
                            <div class="job-result" style="border-color: #e74c3c; background: #fadbd8;">
                                <strong>❌ Failed:</strong> ${job.meta.error || 'Unknown error'}
                            </div>
                        ` : ''}
                    </div>
                `;
            }

            function updateJobList() {
                const jobList = document.getElementById('job-list');
                
                if (jobs.size === 0) {
                    jobList.innerHTML = `
                        <div style="padding: 40px; text-align: center; color: #7f8c8d;">
                            No jobs submitted yet. Submit your first job above! 🎬
                        </div>
                    `;
                    return;
                }
                
                // Sort jobs by submission time (newest first)
                const sortedJobs = Array.from(jobs.values())
                    .sort((a, b) => new Date(b.submitted_at || 0) - new Date(a.submitted_at || 0));
                
                jobList.innerHTML = sortedJobs.map(renderJob).join('');
            }

            async function pollJobStatus(jobId) {
                if (activePolls.has(jobId)) return;
                
                activePolls.add(jobId);
                
                try {
                    const response = await fetch(`/api/jobs/${jobId}/status`);
                    const jobStatus = await response.json();
                    
                    // Update job data
                    const existingJob = jobs.get(jobId);
                    const updatedJob = {
                        ...existingJob,
                        ...jobStatus,
                        processing_time: jobStatus.result?.processing_time
                    };
                    
                    jobs.set(jobId, updatedJob);
                    updateJobList();
                    
                    // Continue polling if not finished
                    if (!['SUCCESS', 'FAILURE'].includes(jobStatus.status)) {
                        setTimeout(() => {
                            activePolls.delete(jobId);
                            pollJobStatus(jobId);
                        }, 2000);
                    } else {
                        activePolls.delete(jobId);
                        updateStats(); // Refresh stats when job completes
                    }
                    
                } catch (error) {
                    console.error(`Polling error for job ${jobId}:`, error);
                    activePolls.delete(jobId);
                }
            }

            async function cancelJob(jobId) {
                try {
                    await fetch(`/api/jobs/${jobId}`, { method: 'DELETE' });
                    
                    // Update job status locally
                    const job = jobs.get(jobId);
                    if (job) {
                        job.status = 'CANCELLED';
                        jobs.set(jobId, job);
                        updateJobList();
                    }
                    
                    activePolls.delete(jobId);
                } catch (error) {
                    alert('Failed to cancel job: ' + error.message);
                }
            }

            // Form submission
            document.getElementById('jobForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const submitBtn = document.getElementById('submitBtn');
                submitBtn.disabled = true;
                submitBtn.textContent = '⏳ Submitting...';
                
                try {
                    const formData = new FormData(e.target);
                    const data = {
                        url: formData.get('url'),
                        language: formData.get('language'),
                        format: formData.get('format')
                    };
                    
                    // Submit job
                    const response = await fetch('/api/jobs/submit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        // Add job to local state
                        const newJob = {
                            job_id: result.job_id,
                            status: result.status,
                            video_url: data.url,
                            language: data.language,
                            format: data.format,
                            submitted_at: result.submitted_at
                        };
                        
                        jobs.set(result.job_id, newJob);
                        updateJobList();
                        
                        // Start polling
                        pollJobStatus(result.job_id);
                        
                        // Clear form
                        document.getElementById('url').value = '';
                        
                        // Show success message briefly
                        submitBtn.textContent = '✅ Job Submitted!';
                        setTimeout(() => {
                            submitBtn.textContent = '🚀 Submit Job';
                        }, 1500);
                        
                    } else {
                        throw new Error(result.detail || 'Failed to submit job');
                    }
                    
                } catch (error) {
                    alert('Error: ' + error.message);
                    submitBtn.textContent = '🚀 Submit Job';
                }
                
                submitBtn.disabled = false;
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "youtube-transcript-mvp",
        "timestamp": datetime.now().isoformat(),
        "uptime": (datetime.now() - stats["start_time"]).total_seconds()
    }

@app.get("/api/stats")
async def get_stats():
    """Get service statistics including cache and concurrency info"""
    total = stats["total_requests"]
    success_rate = (stats["successful_requests"] / max(total, 1)) * 100
    
    # 캐시 및 동시 처리 통계 추가
    handler_stats = get_handler_stats()
    
    return {
        "total_requests": total,
        "successful_requests": stats["successful_requests"],
        "failed_requests": stats["failed_requests"],
        "success_rate": round(success_rate, 1),
        "uptime": (datetime.now() - stats["start_time"]).total_seconds(),
        "cache_stats": {
            "cached_results": handler_stats["valid_cached"],
            "total_cached": handler_stats["total_cached"]
        },
        "concurrency": {
            "max_concurrent": handler_stats["concurrent_limit"],
            "currently_running": handler_stats["current_running"],
            "available_slots": handler_stats["concurrent_limit"] - handler_stats["current_running"]
        }
    }

@app.post("/api/transcript", response_model=TranscriptResponse)
async def extract_transcript(request: YouTubeTranscriptRequest):
    """Extract transcript from YouTube URL - MVP endpoint"""
    start_time = datetime.now()
    stats["total_requests"] += 1
    
    logger.info(f"🎬 Processing YouTube URL: {request.url}")
    
    try:
        # Extract video ID
        video_id = youtube_handler._extract_video_id(request.url)
        if not video_id:
            stats["failed_requests"] += 1
            raise HTTPException(status_code=400, detail="유효하지 않은 YouTube URL입니다")
        
        # Try OAuth method first if available
        transcript = None
        method_used = "unknown"
        
        # 1. Try OAuth YouTube API (best success rate) if available
        if youtube_oauth:
            try:
                transcript = youtube_oauth.get_transcript_from_url(request.url)
                if transcript:
                    method_used = "oauth_youtube_api"
                    logger.info("✅ Successfully extracted via OAuth YouTube API")
            except Exception as e:
                logger.warning(f"OAuth method failed: {e}")
        
        # 2. Try browser scraping method
        if not transcript:
            try:
                transcript = await browser_handler.extract_transcript(request.url)
                if transcript:
                    method_used = "browser_scraping"
                    logger.info("✅ Successfully extracted via browser scraping")
            except Exception as e:
                logger.warning(f"Browser scraping failed: {e}")
        
        # 3. Fallback to existing methods
        if not transcript:
            transcript = youtube_handler.get_captions(request.url, request.language)
            if transcript:
                method_used = "fallback_methods"
        
        if not transcript:
            stats["failed_requests"] += 1
            return TranscriptResponse(
                success=False,
                video_url=request.url,
                video_id=video_id,
                language=request.language,
                error="이 비디오의 전사/자막을 찾을 수 없습니다",
                timestamp=datetime.now().isoformat(),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        
        # Format transcript based on request
        formatted_transcript = _format_transcript(transcript, request.format)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        stats["successful_requests"] += 1
        
        logger.info(f"✅ Success: {len(transcript)} characters in {processing_time:.2f}s")
        
        return TranscriptResponse(
            success=True,
            video_url=request.url,
            video_id=video_id,
            transcript=formatted_transcript,
            language=request.language,
            character_count=len(transcript),
            processing_time=processing_time,
            method_used=method_used,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        stats["failed_requests"] += 1
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error processing {request.url}: {e}")
        
        return TranscriptResponse(
            success=False,
            video_url=request.url,
            video_id=video_id if 'video_id' in locals() else None,
            language=request.language,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            processing_time=processing_time
        )

def _format_transcript(transcript: str, format_type: str) -> str:
    """Format transcript for different output types"""
    
    if format_type == "text":
        return transcript
    
    elif format_type == "json":
        import json
        return json.dumps({
            "transcript": transcript,
            "word_count": len(transcript.split()),
            "character_count": len(transcript),
            "paragraphs": transcript.split('\n\n') if '\n\n' in transcript else [transcript]
        }, ensure_ascii=False, indent=2)
    
    elif format_type == "srt":
        # Simple SRT format (without real timestamps)
        sentences = transcript.replace('. ', '.\n').split('\n')
        srt_content = ""
        
        for i, sentence in enumerate(sentences, 1):
            if sentence.strip():
                start_time = f"00:{(i-1)*3//60:02d}:{(i-1)*3%60:02d},000"
                end_time = f"00:{i*3//60:02d}:{i*3%60:02d},000"
                srt_content += f"{i}\n{start_time} --> {end_time}\n{sentence.strip()}\n\n"
        
        return srt_content
    
    else:
        return transcript

# New async endpoints for background processing
@app.post("/api/jobs/submit", response_model=JobSubmissionResponse)
async def submit_transcript_job(request: YouTubeTranscriptRequest):
    """Submit transcript extraction job for background processing"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Background processing not available")
    
    try:
        # Submit job to Celery
        task = extract_youtube_transcript_task.delay(
            video_url=request.url,
            language=request.language,
            format_type=request.format
        )
        
        logger.info(f"📋 Job submitted: {task.id} for URL: {request.url}")
        
        return JobSubmissionResponse(
            job_id=task.id,
            status="PENDING",
            message="Job submitted successfully. Use job_id to check status.",
            submitted_at=datetime.now().isoformat(),
            estimated_completion=(datetime.now().timestamp() + 60).__str__()  # Estimate 1 minute
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to submit job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")

@app.get("/api/jobs/{job_id}/status", response_model=JobStatusResponse) 
async def get_job_status(job_id: str):
    """Get status of background transcript extraction job"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Background processing not available")
    
    try:
        # Get task result from Celery
        task_result = celery_app.AsyncResult(job_id)
        
        response_data = {
            "job_id": job_id,
            "status": task_result.status,
            "submitted_at": None,
            "completed_at": None
        }
        
        if task_result.status == 'PENDING':
            response_data["meta"] = {"message": "Job is waiting to be processed"}
            
        elif task_result.status in ['STARTED', 'PROGRESS']:
            response_data["meta"] = task_result.info or {"message": "Job is being processed"}
            
        elif task_result.status == 'SUCCESS':
            response_data["result"] = task_result.result
            response_data["completed_at"] = datetime.now().isoformat()
            response_data["meta"] = {"message": "Job completed successfully"}
            
        elif task_result.status == 'FAILURE':
            response_data["meta"] = {
                "error": str(task_result.info) if task_result.info else "Unknown error",
                "message": "Job failed"
            }
            response_data["completed_at"] = datetime.now().isoformat()
            
        else:
            response_data["meta"] = {"message": f"Unknown status: {task_result.status}"}
        
        return JobStatusResponse(**response_data)
        
    except Exception as e:
        logger.error(f"❌ Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@app.delete("/api/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a background job"""
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Background processing not available")
    
    try:
        celery_app.control.revoke(job_id, terminate=True)
        logger.info(f"🚫 Job cancelled: {job_id}")
        
        return {"message": f"Job {job_id} cancelled successfully"}
        
    except Exception as e:
        logger.error(f"❌ Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

@app.get("/api/browser-stats")
async def get_browser_stats():
    """브라우저 핸들러 상세 통계"""
    handler_stats = get_handler_stats()
    
    return {
        "service": "Browser YouTube Handler",
        "concurrent_processing": {
            "max_concurrent_users": handler_stats["concurrent_limit"],
            "currently_processing": handler_stats["current_running"],
            "available_slots": handler_stats["concurrent_limit"] - handler_stats["current_running"],
            "utilization_rate": f"{(handler_stats['current_running'] / handler_stats['concurrent_limit']) * 100:.1f}%"
        },
        "cache_performance": {
            "total_cached_videos": handler_stats["total_cached"],
            "valid_cached_videos": handler_stats["valid_cached"],
            "cache_ttl_hours": 1,
            "cache_hit_potential": f"{(handler_stats['valid_cached'] / max(handler_stats['total_cached'], 1)) * 100:.1f}%"
        },
        "optimizations": {
            "selenium_timeout_reduced": "74초 → 25초 예상",
            "concurrent_users_supported": 3,
            "cache_enabled": True
        }
    }

@app.get("/api/demo")
async def demo_endpoint():
    """Demo endpoint with sample data"""
    sample_urls = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "title": "Rick Astley - Never Gonna Give You Up",
            "language": "en",
            "description": "Famous music video with English lyrics"
        },
        {
            "url": "https://www.youtube.com/watch?v=arj7oStGLkU", 
            "title": "TED Talk Korean",
            "language": "ko",
            "description": "TED talk with Korean subtitles"
        }
    ]
    
    return {
        "service": "YouTube Transcript MVP",
        "version": "1.0.0",
        "description": "Extract transcripts from YouTube videos",
        "sample_urls": sample_urls,
        "supported_languages": ["ko", "en", "ja", "zh", "es", "fr", "de"],
        "supported_formats": ["text", "json", "srt"],
        "stats": {
            "total_requests": stats["total_requests"],
            "success_rate": f"{(stats['successful_requests'] / max(stats['total_requests'], 1)) * 100:.1f}%"
        }
    }

if __name__ == "__main__":
    # Create required directories
    os.makedirs("/app/data/uploads", exist_ok=True)
    os.makedirs("/app/data/transcripts", exist_ok=True)
    os.makedirs("/app/logs", exist_ok=True)
    
    logger.info("🚀 Starting YouTube Transcript MVP API")
    uvicorn.run(app, host="0.0.0.0", port=8000)