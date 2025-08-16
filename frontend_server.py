#!/usr/bin/env python3
"""
Simple FastAPI Frontend Server with CORS Proxy
Serves the HTML UI and proxies API calls to avoid CORS issues
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
from pathlib import Path

app = FastAPI(title="AIBOA Frontend Server", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend service URLs
TRANSCRIPTION_SERVICE = "http://localhost:8000"
ANALYSIS_SERVICE = "http://localhost:8001"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main UI"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>UI file not found</h1>"

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "frontend"}

# Proxy endpoints for transcription service
@app.post("/api/transcribe/youtube")
@app.post("/api/transcribe/upload")
@app.get("/api/transcribe/{job_id}")
async def proxy_transcription(request: Request):
    """Proxy requests to transcription service"""
    
    # Get the path after /api/
    api_path = str(request.url.path)
    query_params = str(request.url.query)
    
    # Build target URL
    target_url = f"{TRANSCRIPTION_SERVICE}{api_path}"
    if query_params:
        target_url += f"?{query_params}"
    
    # Forward headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    try:
        async with httpx.AsyncClient() as client:
            # Get request body
            body = await request.body()
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code,
                headers={"Content-Type": "application/json"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

# Proxy endpoints for analysis service  
@app.post("/api/analyze/text")
@app.post("/api/analyze/transcript")
@app.get("/api/analysis/{analysis_id}")
async def proxy_analysis(request: Request):
    """Proxy requests to analysis service"""
    
    # Get the path after /api/
    api_path = str(request.url.path)
    query_params = str(request.url.query)
    
    # Build target URL
    target_url = f"{ANALYSIS_SERVICE}{api_path}"
    if query_params:
        target_url += f"?{query_params}"
    
    # Forward headers
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    try:
        async with httpx.AsyncClient() as client:
            # Get request body
            body = await request.body()
            
            # Forward the request
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code,
                headers={"Content-Type": "application/json"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)