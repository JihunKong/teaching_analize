#!/usr/bin/env python3
"""Simple test application for Railway deployment"""

from fastapi import FastAPI
import uvicorn
import os

# Create a simple FastAPI app for testing
app = FastAPI(title="AIBOA Service")

@app.get("/")
async def root():
    return {
        "service": "AIBOA Teaching Analysis",
        "status": "running",
        "port": os.getenv("PORT", "8000"),
        "service_type": os.getenv("SERVICE", "test")
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/status")
async def status():
    return {
        "status": "operational",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)