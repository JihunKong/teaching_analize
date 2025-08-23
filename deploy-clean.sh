#!/bin/bash
# AIBOA Clean Architecture Deployment Script

set -e

echo "🚀 AIBOA Clean Architecture Deployment"
echo "======================================"

# Configuration
SERVER_IP="43.203.128.246"
SERVER_USER="ubuntu"
PEM_KEY="teaching_analize.pem"
PROJECT_DIR="/home/ubuntu/aiboa_clean"

echo "📋 Pre-deployment checks..."

# Check if PEM key exists
if [ ! -f "$PEM_KEY" ]; then
    echo "❌ PEM key file not found: $PEM_KEY"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "📝 Please edit .env file with your configuration"
        echo "   Especially: POSTGRES_PASSWORD, REDIS_PASSWORD, JWT_SECRET_KEY"
        read -p "Press Enter after editing .env file..."
    else
        echo "❌ .env.template not found"
        exit 1
    fi
fi

echo "🔧 Building frontend..."
cd frontend_new
npm install
npm run build
cd ..

echo "📦 Creating deployment package..."
TEMP_DIR=$(mktemp -d)
rsync -av --exclude-from=.gitignore . "$TEMP_DIR/"
cd "$TEMP_DIR"

echo "🚀 Deploying to server..."
# Create project directory on server
ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_IP" "mkdir -p $PROJECT_DIR"

# Copy files to server
rsync -av -e "ssh -i $PEM_KEY" . "$SERVER_USER@$SERVER_IP:$PROJECT_DIR/"

echo "📋 Setting up server environment..."
ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
cd /home/ubuntu/aiboa_clean

# Stop any existing services
docker-compose -f docker-compose.clean.yml down || true

# Load environment variables
set -a
source .env
set +a

# Build and start services
docker-compose -f docker-compose.clean.yml build
docker-compose -f docker-compose.clean.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose -f docker-compose.clean.yml ps

# Test endpoints
echo "🧪 Testing endpoints..."
curl -f http://localhost:8000/health || echo "❌ Transcription service unhealthy"
curl -f http://localhost:8001/health || echo "❌ Analysis service unhealthy"
curl -f http://localhost:8002/health || echo "❌ Auth service unhealthy"
curl -f http://localhost:8004/health || echo "❌ Reporting service unhealthy"
curl -f http://localhost/health || echo "❌ Nginx unhealthy"

echo "✅ Deployment completed!"
echo "🌐 Access your application at: http://43.203.128.246/"
EOF

echo "🎉 AIBOA Clean Architecture deployed successfully!"
echo "🌐 Application URL: http://$SERVER_IP/"
echo ""
echo "📊 Service endpoints:"
echo "  - Main app: http://$SERVER_IP/"
echo "  - Transcription: http://$SERVER_IP/api/transcribe/"
echo "  - Analysis: http://$SERVER_IP/api/analyze/"
echo "  - Auth: http://$SERVER_IP/api/auth/"
echo "  - Reports: http://$SERVER_IP/api/reports/"

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo ""
echo "🔍 To check logs:"
echo "  ssh -i $PEM_KEY $SERVER_USER@$SERVER_IP"
echo "  cd $PROJECT_DIR"
echo "  docker-compose -f docker-compose.clean.yml logs -f"