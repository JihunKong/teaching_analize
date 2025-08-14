#!/usr/bin/env python3
"""Simple main entry point for Railway deployment"""

import os
import sys

# Add services to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Determine which service to run based on SERVICE env var or default
SERVICE = os.getenv("SERVICE", "transcription").lower()

if SERVICE == "transcription":
    from services.transcription.app.main import app
    print(f"Starting Transcription Service on port {os.getenv('PORT', '8000')}")
elif SERVICE == "analysis":
    from services.analysis.app.main import app
    print(f"Starting Analysis Service on port {os.getenv('PORT', '8001')}")
else:
    raise ValueError(f"Unknown service: {SERVICE}")

# Import uvicorn and run
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)