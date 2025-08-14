#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Railway Deployment Verification"
echo "=================================="

# Get the deployment URL
echo -e "${YELLOW}Enter your Railway app URL (e.g., white-snow-production.up.railway.app):${NC}"
read -r APP_URL

if [ -z "$APP_URL" ]; then
    echo -e "${RED}No URL provided. Exiting.${NC}"
    exit 1
fi

# Remove https:// if provided
APP_URL=${APP_URL#https://}
APP_URL=${APP_URL#http://}

echo ""
echo "Testing endpoints on: https://$APP_URL"
echo ""

# Test health endpoint
echo -n "Testing /health endpoint... "
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://$APP_URL/health")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Success (200)${NC}"
    curl -s "https://$APP_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "https://$APP_URL/health"
else
    echo -e "${RED}✗ Failed (HTTP $HEALTH_RESPONSE)${NC}"
fi

echo ""

# Test root endpoint
echo -n "Testing / endpoint... "
ROOT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://$APP_URL/")
if [ "$ROOT_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Success (200)${NC}"
    curl -s "https://$APP_URL/" | python3 -m json.tool 2>/dev/null || curl -s "https://$APP_URL/"
else
    echo -e "${RED}✗ Failed (HTTP $ROOT_RESPONSE)${NC}"
fi

echo ""

# Test debug endpoint
echo -n "Testing /debug endpoint... "
DEBUG_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://$APP_URL/debug")
if [ "$DEBUG_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Success (200)${NC}"
    echo "(Debug output suppressed - check manually if needed)"
else
    echo -e "${RED}✗ Failed (HTTP $DEBUG_RESPONSE)${NC}"
fi

echo ""
echo "=================================="

if [ "$HEALTH_RESPONSE" = "200" ] && [ "$ROOT_RESPONSE" = "200" ]; then
    echo -e "${GREEN}🎉 Deployment is working correctly!${NC}"
else
    echo -e "${RED}⚠️  Deployment may have issues. Check Railway logs.${NC}"
    echo ""
    echo "To view logs, run:"
    echo "  railway logs --tail 100"
fi
