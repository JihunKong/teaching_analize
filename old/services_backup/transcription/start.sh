#!/bin/sh
# Transcription Service 시작 스크립트
# Railway의 PORT 환경변수를 사용하거나 기본값 8000 사용

PORT=${PORT:-8000}
echo "Starting Transcription Service on port $PORT"
uvicorn app.main:app --host 0.0.0.0 --port $PORT