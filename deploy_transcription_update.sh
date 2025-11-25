#!/bin/bash

# Deployment script for updated browser transcriber with exact DOM selectors
# This script rebuilds and restarts the transcription service

set -e  # Exit on any error

echo "🚀 Deploying Transcription Service Updates"
echo "=========================================="

# Navigate to the transcription service directory
cd "$(dirname "$0")/services_new/transcription"

echo "📁 Current directory: $(pwd)"

# Stop existing services
echo "🛑 Stopping existing transcription services..."
docker-compose down || echo "No existing services to stop"

# Remove old images to force rebuild
echo "🗑️ Removing old Docker images..."
docker image prune -f || true
docker-compose build --no-cache

# Start services with updated code
echo "▶️ Starting updated transcription services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Test the API endpoint
echo "🧪 Testing API endpoint..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is responding"
else
    echo "❌ API is not responding"
    echo "📋 Service logs:"
    docker-compose logs transcription-api --tail=20
fi

# Show logs for debugging
echo "📋 Recent service logs:"
docker-compose logs transcription-api --tail=10

echo ""
echo "🎉 Deployment completed!"
echo "📊 Monitor logs with: docker-compose logs -f"
echo "🌐 API available at: http://localhost:8000"
echo "🌸 Flower monitoring at: http://localhost:5555"