#!/usr/bin/env python3
"""Simple test app for Railway deployment"""

from fastapi import FastAPI
import os

app = FastAPI(title="Teaching Analize Service")

@app.get("/")
async def root():
    return {
        "service": "teaching_analize",
        "status": "running",
        "port": os.getenv("PORT", "8000")
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