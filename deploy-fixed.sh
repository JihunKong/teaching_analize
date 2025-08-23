#!/bin/bash

# AIBOA Fixed Deployment Script
# This script deploys AIBOA with CORS fixes and port consolidation
# All traffic will go through port 80 via nginx

set -e

echo "🚀 Starting AIBOA Fixed Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if required files exist
print_header "Checking Prerequisites"

if [ ! -f "nginx.fixed.conf" ]; then
    print_error "nginx.fixed.conf not found!"
    exit 1
fi

if [ ! -f "docker-compose.fixed.yml" ]; then
    print_error "docker-compose.fixed.yml not found!"
    exit 1
fi

if [ ! -d "frontend_new/out" ]; then
    print_warning "Frontend build not found. Building frontend..."
    cd frontend_new
    npm install
    npm run build
    cd ..
fi

print_status "Prerequisites check completed"

# Create necessary directories
print_header "Creating Required Directories"

mkdir -p logs/nginx
mkdir -p ssl
print_status "Directories created"

# Stop existing containers if running
print_header "Stopping Existing Containers"

docker compose -f docker-compose.fixed.yml down --remove-orphans 2>/dev/null || true
print_status "Existing containers stopped"

# Build and start services
print_header "Building and Starting Services"

docker compose -f docker-compose.fixed.yml build --no-cache
docker compose -f docker-compose.fixed.yml up -d

print_status "Services started"

# Wait for services to be healthy
print_header "Waiting for Services to be Ready"

echo "Waiting for PostgreSQL..."
timeout 60 bash -c 'until docker exec aiboa_postgres pg_isready -U aiboa_user -d aiboa; do sleep 2; done'

echo "Waiting for Redis..."
timeout 60 bash -c 'until docker exec aiboa_redis redis-cli ping | grep PONG; do sleep 2; done'

echo "Waiting for transcription service..."
timeout 60 bash -c 'until curl -f http://localhost/transcription/health 2>/dev/null; do sleep 2; done'

echo "Waiting for analysis service..."
timeout 60 bash -c 'until curl -f http://localhost/analysis/health 2>/dev/null; do sleep 2; done'

print_status "All services are ready"

# Test the setup
print_header "Testing Deployment"

# Test frontend
print_status "Testing frontend..."
if curl -f http://localhost/ >/dev/null 2>&1; then
    print_status "✅ Frontend is accessible at http://localhost/"
else
    print_error "❌ Frontend test failed"
fi

# Test API endpoints
print_status "Testing API endpoints..."

if curl -f http://localhost/health >/dev/null 2>&1; then
    print_status "✅ Health check endpoint working"
else
    print_warning "❌ Health check endpoint failed"
fi

if curl -f http://localhost/transcription/health >/dev/null 2>&1; then
    print_status "✅ Transcription service accessible"
else
    print_warning "❌ Transcription service test failed"
fi

if curl -f http://localhost/analysis/health >/dev/null 2>&1; then
    print_status "✅ Analysis service accessible"
else
    print_warning "❌ Analysis service test failed"
fi

# Show deployment summary
print_header "Deployment Summary"

echo
print_status "🎉 AIBOA Fixed Deployment Complete!"
echo
echo -e "${BLUE}Access URLs:${NC}"
echo "  • Frontend: http://localhost/"
echo "  • Transcription Page: http://localhost/transcription/"  
echo "  • Analysis Page: http://localhost/analysis/"
echo "  • Reports Page: http://localhost/reports/"
echo
echo -e "${BLUE}API Endpoints (now accessible via nginx):${NC}"
echo "  • Transcription API: http://localhost/api/transcribe/"
echo "  • Analysis API: http://localhost/api/analyze/"
echo "  • Reports API: http://localhost/api/reports/"
echo "  • Frameworks API: http://localhost/api/frameworks/"
echo
echo -e "${BLUE}Health Checks:${NC}"
echo "  • Overall: http://localhost/health"
echo "  • Transcription: http://localhost/transcription/health"
echo "  • Analysis: http://localhost/analysis/health"
echo
echo -e "${GREEN}✅ Issues Fixed:${NC}"
echo "  • CORS errors resolved with proper headers"
echo "  • Port consolidation - everything accessible via port 80"
echo "  • Frontend uses relative API paths"
echo "  • Static files served directly by nginx"
echo "  • Proper API routing to backend services"
echo
echo -e "${BLUE}Container Status:${NC}"
docker compose -f docker-compose.fixed.yml ps
echo
print_status "Ready to use! 🚀"