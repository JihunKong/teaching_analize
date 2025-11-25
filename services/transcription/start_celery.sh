#!/bin/bash
# Celery worker startup script for the proven transcription method
# This matches the worker configuration from TRANSCRIPT_METHOD.md

# Start Xvfb for headless browser automation
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping > /dev/null 2>&1; do
    sleep 1
done
echo "Redis is ready"

# Start Celery worker with configuration from proven method
exec celery -A celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=50 \
    --time-limit=600 \
    --soft-time-limit=480 \
    -Q transcription \
    -n worker@%h