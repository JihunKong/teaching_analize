from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(title="Analysis Service MVP v2")

@app.get("/")
async def root():
    return {
        "status": "healthy", 
        "service": "Analysis Service",
        "version": "MVP-v2-HOTFIX-LATEST",
        "timestamp": datetime.now().isoformat(),
        "port": int(os.environ.get('PORT', 8080)),
        "deployed": "2025-08-15-FORCE-REBUILD",
        "build_id": "latest-cache-bust"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "MVP-v2"
    }

@app.get("/api/status")
async def status():
    return {
        "status": "operational",
        "features": "minimal",
        "deployment": "Railway MVP v2",
        "build": "HOTFIX-2025-08-15"
    }