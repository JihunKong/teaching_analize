#!/usr/bin/env python3
"""Minimal test app to verify Railway deployment"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="Test Transcription Service")

@app.get("/")
async def root():
    return {"service": "transcription", "status": "running", "port": os.getenv("PORT", "8000")}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "transcription"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)