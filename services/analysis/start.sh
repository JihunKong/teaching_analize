#!/bin/sh
# Analysis Service 시작 스크립트
# Railway의 PORT 환경변수를 사용하거나 기본값 8001 사용

PORT=${PORT:-8001}
echo "Starting Analysis Service on port $PORT"
uvicorn app.main:app --host 0.0.0.0 --port $PORT