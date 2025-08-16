#!/bin/bash
# Phase 1: MVP Deployment Script
# Deploy minimal services to verify Railway infrastructure

echo "==================================="
echo "PHASE 1: MVP DEPLOYMENT"
echo "==================================="
echo ""
echo "This script will deploy minimal services with health checks only"
echo "Purpose: Verify Railway deployment pipeline works"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI not found!${NC}"
    echo "Install with: npm install -g @railway/cli"
    exit 1
fi

echo -e "${YELLOW}Step 1: Preparing Transcription Service for MVP deployment${NC}"
cd services/transcription

# Backup original files
cp Dockerfile Dockerfile.backup 2>/dev/null || true
cp main.py main.backup.py 2>/dev/null || true

# Use minimal files
cp Dockerfile.minimal Dockerfile
cp main_minimal.py main.py

echo -e "${GREEN}✓ Transcription service prepared${NC}"

echo -e "${YELLOW}Step 2: Deploying Transcription Service${NC}"
railway up --service teaching_analize --detach

echo -e "${YELLOW}Step 3: Preparing Analysis Service for MVP deployment${NC}"
cd ../analysis

# Backup original files
cp Dockerfile Dockerfile.backup 2>/dev/null || true
cp main.py main.backup.py 2>/dev/null || true

# Use minimal files
cp Dockerfile.minimal Dockerfile
cp main_minimal.py main.py

echo -e "${GREEN}✓ Analysis service prepared${NC}"

echo -e "${YELLOW}Step 4: Deploying Analysis Service${NC}"
railway up --service amused_friendship --detach

cd ../..

echo ""
echo -e "${GREEN}==================================="
echo "PHASE 1 DEPLOYMENT INITIATED"
echo "===================================${NC}"
echo ""
echo "Check deployment status with:"
echo "  railway status"
echo "  railway logs --service teaching_analize"
echo "  railway logs --service amused_friendship"
echo ""
echo "Health check URLs:"
echo "  https://teachinganalize-production.up.railway.app/health"
echo "  https://amusedfriendship-production.up.railway.app/health"
echo ""
echo "Once health checks pass, proceed to Phase 2"