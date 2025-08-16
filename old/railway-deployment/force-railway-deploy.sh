#!/bin/bash

# Force Railway Deployment Script
# This script forces Railway to rebuild and deploy from scratch

echo "========================================="
echo "Railway Force Deployment Script"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service name
SERVICE="amused_friendship"

echo -e "${YELLOW}Step 1: Adding cache-bust timestamp to Dockerfile...${NC}"
TIMESTAMP=$(date +%s)
sed -i.bak "s/ARG CACHEBUST=.*/ARG CACHEBUST=${TIMESTAMP}/" services/analysis/Dockerfile.latest
rm services/analysis/Dockerfile.latest.bak

echo -e "${YELLOW}Step 2: Updating deployment timestamp in main.py...${NC}"
DEPLOY_TIME=$(date +%Y-%m-%d-%H%M%S)
sed -i.bak "s/\"deployed\": \".*\"/\"deployed\": \"${DEPLOY_TIME}\"/" services/analysis/main.py
rm services/analysis/main.py.bak

echo -e "${YELLOW}Step 3: Committing changes...${NC}"
git add -A
git commit -m "FORCE REBUILD [${TIMESTAMP}]: Cache bust deployment with new Dockerfile"

echo -e "${YELLOW}Step 4: Pushing to GitHub...${NC}"
git push origin main

echo -e "${YELLOW}Step 5: Forcing Railway deployment...${NC}"
echo "Attempting deployment with --no-cache flag..."
railway up --service ${SERVICE} --no-cache --detach

echo -e "${YELLOW}Waiting 30 seconds for deployment to start...${NC}"
sleep 30

echo -e "${YELLOW}Step 6: Checking deployment status...${NC}"
echo "Fetching logs..."
railway logs --service ${SERVICE} -n 20

echo -e "${YELLOW}Step 7: Testing deployed service...${NC}"
echo "Testing https://amusedfriendship-production.up.railway.app/ ..."
RESPONSE=$(curl -s https://amusedfriendship-production.up.railway.app/)
echo "Response: ${RESPONSE}"

# Check if deployment was successful
if [[ $RESPONSE == *"MVP-v2-HOTFIX-LATEST"* ]]; then
    echo -e "${GREEN}✓ Deployment successful! New version is live.${NC}"
else
    echo -e "${RED}✗ Deployment may have failed. Old version still running.${NC}"
    echo ""
    echo -e "${YELLOW}Try these manual steps:${NC}"
    echo "1. Go to Railway Dashboard → amused_friendship service"
    echo "2. Click Settings → Deploy → 'Redeploy with no cache'"
    echo "3. Or disconnect and reconnect GitHub repo in Settings → Source"
    echo "4. Check Recent Deliveries in GitHub Webhooks settings"
fi

echo ""
echo "========================================="
echo "Deployment attempt complete"
echo "========================================="