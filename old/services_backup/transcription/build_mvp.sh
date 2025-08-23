#!/bin/bash

# Build and run YouTube Transcript MVP locally
# This script creates a local Docker demo for MVP presentation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Building YouTube Transcript MVP"
echo "================================="

# Create required directories
mkdir -p "$SCRIPT_DIR/data/uploads"
mkdir -p "$SCRIPT_DIR/data/transcripts" 
mkdir -p "$SCRIPT_DIR/logs"

echo "✅ Created data directories"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Stop any existing MVP containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.mvp.yml down --remove-orphans 2>/dev/null || true

# Build the MVP image
echo "🔨 Building MVP Docker image..."
docker-compose -f docker-compose.mvp.yml build

# Start the MVP service
echo "🎬 Starting MVP service..."
docker-compose -f docker-compose.mvp.yml up -d

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ MVP service is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Attempt $attempt/$max_attempts - waiting for service..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Service failed to start after $max_attempts attempts"
    echo "📋 Checking logs..."
    docker-compose -f docker-compose.mvp.yml logs
    exit 1
fi

# Test the service
echo "🧪 Testing MVP functionality..."

# Test health endpoint
echo "📡 Testing health endpoint..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi

# Test demo endpoint
echo "📡 Testing demo endpoint..."
if curl -s http://localhost:8000/api/demo | grep -q "YouTube Transcript MVP"; then
    echo "✅ Demo endpoint working"
else
    echo "❌ Demo endpoint failed"
fi

# Show service info
echo ""
echo "🎉 MVP Service Successfully Started!"
echo "=================================="
echo ""
echo "🌐 Web Interface:"
echo "   URL: http://localhost:8000"
echo "   Demo: http://localhost:8000/api/demo"
echo ""
echo "📋 API Endpoints:"
echo "   Health: http://localhost:8000/health"
echo "   Stats: http://localhost:8000/api/stats"
echo "   Transcript: POST http://localhost:8000/api/transcript"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.mvp.yml logs -f"
echo "   Stop service: docker-compose -f docker-compose.mvp.yml down"
echo "   Restart: docker-compose -f docker-compose.mvp.yml restart"
echo ""
echo "📱 Quick Test URLs:"
echo "   영어: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
echo "   한국어: https://www.youtube.com/watch?v=arj7oStGLkU"
echo ""
echo "💡 MVP Features:"
echo "   ✅ Web UI for easy testing"
echo "   ✅ Real YouTube transcript extraction"
echo "   ✅ Multiple output formats (Text, JSON, SRT)"
echo "   ✅ Real-time statistics"
echo "   ✅ Error handling and fallbacks"
echo ""

# Open browser (optional)
if command -v open >/dev/null 2>&1; then
    echo "🌐 Opening browser..."
    open http://localhost:8000
elif command -v xdg-open >/dev/null 2>&1; then
    echo "🌐 Opening browser..."
    xdg-open http://localhost:8000
fi

echo ""
echo "🎬 Ready for MVP demo!"
echo "Just visit http://localhost:8000 and test with any YouTube URL"