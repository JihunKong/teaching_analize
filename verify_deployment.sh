#!/bin/bash

echo "🔍 Verifying AIBOA Railway Deployment"
echo "======================================"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to test endpoint
test_endpoint() {
    local url=$1
    local service=$2
    
    echo -ne "Testing ${service}... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "${url}/health" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ OK (HTTP 200)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP ${response})${NC}"
        return 1
    fi
}

# Get service URLs from Railway
echo -e "${YELLOW}Getting service URLs...${NC}"

if command -v railway &> /dev/null; then
    # Try to get URLs from Railway CLI
    TRANS_URL=$(railway status --service transcription-api 2>/dev/null | grep "URL" | awk '{print $2}')
    ANALYSIS_URL=$(railway status --service analysis-api 2>/dev/null | grep "URL" | awk '{print $2}')
fi

# Fallback to expected URLs if CLI fails
if [ -z "$TRANS_URL" ]; then
    TRANS_URL="https://transcription-api-production.up.railway.app"
fi

if [ -z "$ANALYSIS_URL" ]; then
    ANALYSIS_URL="https://analysis-api-production.up.railway.app"
fi

echo ""
echo "Service URLs:"
echo "  Transcription: ${TRANS_URL}"
echo "  Analysis: ${ANALYSIS_URL}"
echo ""

# Test services
echo "Testing Health Endpoints:"
echo "------------------------"

success=0
total=0

# Test Transcription Service
((total++))
if test_endpoint "$TRANS_URL" "Transcription Service"; then
    ((success++))
fi

# Test Analysis Service
((total++))
if test_endpoint "$ANALYSIS_URL" "Analysis Service"; then
    ((success++))
fi

echo ""
echo "Results: ${success}/${total} services healthy"

if [ $success -eq $total ]; then
    echo -e "${GREEN}✅ All services are running successfully!${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Some services are not responding. Check Railway logs for details.${NC}"
    echo ""
    echo "Troubleshooting commands:"
    echo "  railway logs --service transcription-api"
    echo "  railway logs --service analysis-api"
    exit 1
fi