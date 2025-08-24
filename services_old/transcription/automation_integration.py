#!/usr/bin/env python3
"""
Automation Platform Integration
Provides optimized endpoints for n8n, Zapier, Make, etc.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List
import logging
import asyncio
from datetime import datetime

from youtube_handler import YouTubeHandler
from mcp_youtube_client import MCPYouTubeClientSync

logger = logging.getLogger(__name__)

# Request/Response models for automation platforms
class YouTubeTranscriptRequest(BaseModel):
    """Request model for YouTube transcript extraction"""
    url: HttpUrl
    language: str = "en"
    format: str = "text"  # text, json, srt
    webhook_url: Optional[HttpUrl] = None  # For async processing
    metadata: Optional[Dict[str, Any]] = {}  # Additional data to pass through

class AutomationResponse(BaseModel):
    """Standardized response for automation platforms"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str
    processing_time: Optional[float] = None
    webhook_sent: bool = False

class YouTubeTranscriptResponse(BaseModel):
    """Response model for transcript extraction"""
    success: bool
    transcript: Optional[str] = None
    metadata: Dict[str, Any] = {}
    video_info: Dict[str, Any] = {}
    error: Optional[str] = None
    timestamp: str
    processing_time: float

class AutomationAPI:
    """API specifically designed for automation platforms"""
    
    def __init__(self):
        self.youtube_handler = YouTubeHandler()
        
        # Try to initialize MCP client
        try:
            self.mcp_client = MCPYouTubeClientSync()
            if not self.mcp_client.health_check():
                self.mcp_client = None
        except:
            self.mcp_client = None
    
    async def extract_youtube_transcript(self, request: YouTubeTranscriptRequest) -> YouTubeTranscriptResponse:
        """
        Extract transcript from YouTube URL - optimized for automation platforms
        """
        start_time = datetime.now()
        
        try:
            url = str(request.url)
            logger.info(f"🎬 Processing YouTube URL for automation: {url}")
            
            # Extract video info
            video_id = self.youtube_handler._extract_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
            
            # Try to get transcript using best available method
            transcript = None
            method_used = "unknown"
            
            # First try MCP client if available
            if self.mcp_client:
                try:
                    transcript = self.mcp_client.get_transcript(url, request.language)
                    if transcript:
                        method_used = "mcp_server"
                        logger.info("✅ Used MCP server for transcript")
                except Exception as e:
                    logger.warning(f"MCP client failed: {e}")
            
            # Fallback to YouTube handler
            if not transcript:
                try:
                    transcript = self.youtube_handler.get_captions(url, request.language)
                    if transcript:
                        method_used = "youtube_handler"
                        logger.info("✅ Used YouTube handler for transcript")
                except Exception as e:
                    logger.warning(f"YouTube handler failed: {e}")
            
            if not transcript:
                raise HTTPException(status_code=404, detail="No transcript found for this video")
            
            # Format transcript based on request
            formatted_transcript = self._format_transcript(transcript, request.format)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare response
            response = YouTubeTranscriptResponse(
                success=True,
                transcript=formatted_transcript,
                metadata={
                    "video_id": video_id,
                    "language": request.language,
                    "format": request.format,
                    "method_used": method_used,
                    "character_count": len(transcript),
                    **request.metadata
                },
                video_info={
                    "video_id": video_id,
                    "url": url,
                    "platform": "youtube"
                },
                timestamp=datetime.now().isoformat(),
                processing_time=processing_time
            )
            
            logger.info(f"✅ Transcript extracted: {len(transcript)} chars in {processing_time:.2f}s")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Transcript extraction failed: {e}")
            
            return YouTubeTranscriptResponse(
                success=False,
                error=str(e),
                metadata=request.metadata,
                video_info={"url": str(request.url)},
                timestamp=datetime.now().isoformat(),
                processing_time=processing_time
            )
    
    def _format_transcript(self, transcript: str, format_type: str) -> str:
        """Format transcript for different automation platform needs"""
        
        if format_type == "text":
            return transcript
        
        elif format_type == "json":
            # Return as JSON string for easy parsing in automation tools
            import json
            return json.dumps({
                "transcript": transcript,
                "word_count": len(transcript.split()),
                "character_count": len(transcript)
            })
        
        elif format_type == "srt":
            # Simple SRT-like format
            # Note: This is basic - real SRT would need timestamps
            lines = transcript.split('. ')
            srt_content = ""
            for i, line in enumerate(lines, 1):
                if line.strip():
                    srt_content += f"{i}\n00:{i:02d}:00,000 --> 00:{i:02d}:05,000\n{line.strip()}\n\n"
            return srt_content
        
        elif format_type == "markdown":
            # Format as markdown with paragraphs
            paragraphs = transcript.split('. ')
            markdown = "# YouTube Transcript\n\n"
            for para in paragraphs:
                if para.strip():
                    markdown += f"{para.strip()}.\n\n"
            return markdown
        
        else:
            return transcript
    
    async def send_webhook(self, webhook_url: str, data: Dict[str, Any]) -> bool:
        """Send result to webhook URL for async processing"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=data) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Webhook send failed: {e}")
            return False

# FastAPI integration functions
def create_automation_endpoints(app: FastAPI):
    """Add automation-friendly endpoints to FastAPI app"""
    
    automation_api = AutomationAPI()
    
    @app.post("/api/automation/youtube/transcript", response_model=YouTubeTranscriptResponse)
    async def get_youtube_transcript_automation(request: YouTubeTranscriptRequest):
        """
        Extract YouTube transcript - optimized for automation platforms
        
        Perfect for:
        - n8n HTTP Request nodes
        - Zapier Webhooks
        - Make HTTP modules
        - Power Automate HTTP actions
        """
        return await automation_api.extract_youtube_transcript(request)
    
    @app.post("/api/automation/youtube/transcript/async")
    async def get_youtube_transcript_async(request: YouTubeTranscriptRequest, background_tasks: BackgroundTasks):
        """
        Async transcript extraction - returns immediately and sends result to webhook
        
        Use when processing might take longer than automation platform timeout
        """
        if not request.webhook_url:
            raise HTTPException(status_code=400, detail="webhook_url required for async processing")
        
        # Start background task
        background_tasks.add_task(process_transcript_async, automation_api, request)
        
        return AutomationResponse(
            success=True,
            data={"status": "processing", "video_url": str(request.url)},
            timestamp=datetime.now().isoformat(),
            webhook_sent=False
        )
    
    @app.get("/api/automation/health")
    async def automation_health_check():
        """Health check for automation platforms"""
        
        health_status = {
            "service": "youtube_transcript_automation",
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "youtube_handler": True,
                "mcp_client": automation_api.mcp_client is not None,
                "proxy_manager": automation_api.youtube_handler.proxy_manager is not None
            }
        }
        
        # Check MCP client if available
        if automation_api.mcp_client:
            try:
                health_status["components"]["mcp_client"] = automation_api.mcp_client.health_check()
            except:
                health_status["components"]["mcp_client"] = False
        
        # Overall health
        all_critical_healthy = health_status["components"]["youtube_handler"]
        health_status["status"] = "healthy" if all_critical_healthy else "degraded"
        
        return health_status
    
    @app.get("/api/automation/docs")
    async def automation_documentation():
        """Documentation for automation platform integration"""
        
        return {
            "service": "YouTube Transcript Automation API",
            "description": "Extract transcripts from YouTube videos for automation platforms",
            "endpoints": [
                {
                    "path": "/api/automation/youtube/transcript",
                    "method": "POST",
                    "description": "Extract transcript synchronously",
                    "use_cases": ["n8n workflows", "Zapier zaps", "Make scenarios"],
                    "timeout": "60 seconds"
                },
                {
                    "path": "/api/automation/youtube/transcript/async", 
                    "method": "POST",
                    "description": "Extract transcript asynchronously with webhook",
                    "use_cases": ["Long-running processes", "Batch processing"],
                    "timeout": "Immediate response"
                }
            ],
            "supported_platforms": [
                "n8n",
                "Zapier", 
                "Make (Integromat)",
                "Power Automate",
                "IFTTT",
                "Custom webhooks"
            ],
            "example_workflows": [
                {
                    "platform": "n8n",
                    "description": "YouTube URL → Transcript → Google Sheets",
                    "steps": [
                        "Webhook trigger with YouTube URL",
                        "HTTP Request to /api/automation/youtube/transcript",
                        "Google Sheets node to save transcript"
                    ]
                },
                {
                    "platform": "Zapier",
                    "description": "YouTube URL → Transcript → Notion",
                    "steps": [
                        "Trigger: Webhook",
                        "Action: Webhooks by Zapier (POST to API)",
                        "Action: Notion - Create page with transcript"
                    ]
                }
            ]
        }

async def process_transcript_async(automation_api: AutomationAPI, request: YouTubeTranscriptRequest):
    """Background task for async transcript processing"""
    try:
        # Process transcript
        result = await automation_api.extract_youtube_transcript(request)
        
        # Send to webhook
        webhook_data = {
            "success": result.success,
            "transcript": result.transcript,
            "metadata": result.metadata,
            "video_info": result.video_info,
            "error": result.error,
            "timestamp": result.timestamp,
            "processing_time": result.processing_time
        }
        
        if request.webhook_url:
            webhook_sent = await automation_api.send_webhook(str(request.webhook_url), webhook_data)
            logger.info(f"Webhook sent: {webhook_sent}")
        
    except Exception as e:
        logger.error(f"Async processing failed: {e}")
        
        # Send error to webhook
        if request.webhook_url:
            error_data = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "video_url": str(request.url)
            }
            await automation_api.send_webhook(str(request.webhook_url), error_data)

# Example usage configurations for different platforms
PLATFORM_EXAMPLES = {
    "n8n": {
        "name": "n8n Workflow",
        "description": "HTTP Request node configuration",
        "config": {
            "method": "POST",
            "url": "https://your-server.com/api/automation/youtube/transcript",
            "headers": {
                "Content-Type": "application/json",
                "X-API-Key": "your-api-key"
            },
            "body": {
                "url": "{{$json['youtube_url']}}",
                "language": "en",
                "format": "text",
                "metadata": {
                    "source": "n8n_workflow",
                    "user_id": "{{$json['user_id']}}"
                }
            }
        }
    },
    "zapier": {
        "name": "Zapier Webhook",
        "description": "Webhooks by Zapier action",
        "config": {
            "url": "https://your-server.com/api/automation/youtube/transcript",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "X-API-Key": "your-api-key"
            },
            "data": {
                "url": "{{youtube_url}}",
                "language": "en", 
                "format": "markdown"
            }
        }
    },
    "make": {
        "name": "Make HTTP Module",
        "description": "HTTP Make a request module",
        "config": {
            "url": "https://your-server.com/api/automation/youtube/transcript",
            "method": "POST",
            "headers": [
                {"name": "Content-Type", "value": "application/json"},
                {"name": "X-API-Key", "value": "your-api-key"}
            ],
            "body": {
                "url": "{{youtube_url}}",
                "language": "en",
                "format": "json"
            }
        }
    }
}

if __name__ == "__main__":
    # Test the automation API
    import asyncio
    
    async def test_automation_api():
        api = AutomationAPI()
        
        request = YouTubeTranscriptRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            language="en",
            format="text",
            metadata={"test": True}
        )
        
        result = await api.extract_youtube_transcript(request)
        print(f"Success: {result.success}")
        print(f"Length: {len(result.transcript) if result.transcript else 0}")
        print(f"Time: {result.processing_time:.2f}s")
    
    asyncio.run(test_automation_api())