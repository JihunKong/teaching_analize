#!/bin/bash

# Railway CLI Deployment Script
# This script deploys both services to Railway using the CLI

set -e

echo "🚀 Railway CLI Deployment for AIBOA System"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "services" ]; then
    echo -e "${RED}Error: 'services' directory not found.${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Function to check command status
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

echo -e "${YELLOW}Checking Railway CLI installation...${NC}"
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI is not installed.${NC}"
    echo "Installing Railway CLI..."
    curl -sSL https://railway.app/install.sh | sh
    check_status "Railway CLI installation"
fi

echo -e "${GREEN}✓ Railway CLI is installed${NC}"
echo ""

# Project is already linked
echo -e "${BLUE}Project: lively-surprise${NC}"
echo -e "${BLUE}Environment: production${NC}"
echo ""

# Deploy Transcription Service
echo -e "${YELLOW}Deploying Transcription Service...${NC}"
echo "----------------------------------------"

cd services/transcription

# Create railway.json for this service
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF

echo "Deploying transcription service..."
railway up --service transcription-service --detach || {
    echo -e "${YELLOW}Service might not exist, creating new service...${NC}"
    railway up --detach
}

check_status "Transcription service deployment"

cd ../..

# Deploy Analysis Service
echo ""
echo -e "${YELLOW}Deploying Analysis Service...${NC}"
echo "----------------------------------------"

cd services/analysis

# Create railway.json for this service
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
EOF

echo "Deploying analysis service..."
railway up --service analysis-service --detach || {
    echo -e "${YELLOW}Service might not exist, creating new service...${NC}"
    railway up --detach
}

check_status "Analysis service deployment"

cd ../..

# Check deployment status
echo ""
echo -e "${YELLOW}Checking deployment status...${NC}"
echo "----------------------------------------"

railway status

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}       Deployment Complete! 🎉         ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Check the Railway dashboard for service URLs"
echo "2. Verify health endpoints:"
echo "   - Transcription: https://[your-url]/health"
echo "   - Analysis: https://[your-url]/health"
echo ""
echo "To view logs:"
echo "  railway logs --service transcription-service"
echo "  railway logs --service analysis-service"
echo ""
echo "To check environment variables:"
echo "  railway variables --service transcription-service"
echo "  railway variables --service analysis-service"
echo ""
echo -e "${BLUE}Dashboard: https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f${NC}"