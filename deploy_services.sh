#!/bin/bash
set -e

echo "🚀 Deploying AIBOA Services to Railway"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI not found. Please install it first:${NC}"
    echo "brew install railway (macOS)"
    echo "curl -fsSL https://railway.app/install.sh | sh (Linux)"
    exit 1
fi

# Login to Railway
echo -e "${YELLOW}📝 Checking Railway authentication...${NC}"
railway whoami || railway login

# Link to project
echo -e "${YELLOW}🔗 Linking to Railway project...${NC}"
railway link 379dfeea-b7f3-47cf-80c8-4d6d6b72329f

# Deploy Transcription Service
echo -e "${GREEN}🎙️ Deploying Transcription Service...${NC}"
cd services/transcription

# Create service if it doesn't exist
railway service create transcription-api 2>/dev/null || echo "Service already exists"

# Deploy with correct root directory
railway up --service transcription-api

echo -e "${GREEN}✅ Transcription Service deployed${NC}"

# Deploy Analysis Service
echo -e "${GREEN}🔍 Deploying Analysis Service...${NC}"
cd ../analysis

# Create service if it doesn't exist
railway service create analysis-api 2>/dev/null || echo "Service already exists"

# Deploy with correct root directory
railway up --service analysis-api

echo -e "${GREEN}✅ Analysis Service deployed${NC}"

# Return to root
cd ../..

# Verify deployments
echo -e "${YELLOW}🔍 Verifying deployments...${NC}"

# Get service URLs
TRANS_URL=$(railway status --service transcription-api | grep "URL" | awk '{print $2}')
ANALYSIS_URL=$(railway status --service analysis-api | grep "URL" | awk '{print $2}')

echo -e "${GREEN}📍 Service URLs:${NC}"
echo "  Transcription: ${TRANS_URL}"
echo "  Analysis: ${ANALYSIS_URL}"

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Set environment variables in Railway dashboard"
echo "2. Run database migrations"
echo "3. Test the health endpoints"