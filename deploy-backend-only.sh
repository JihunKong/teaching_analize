#!/bin/bash

# AIBOA Backend-Only Deployment Script
# Usage: ./deploy-backend-only.sh

set -e  # Exit on any error

SERVER_IP="3.38.107.23"
PEM_KEY="./teaching_analize.pem"
SERVER_USER="ubuntu"
PROJECT_NAME="aiboa"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting AIBOA Backend-Only deployment${NC}"
echo -e "${BLUE}Server: ${SERVER_IP}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"

# Check files
if [[ ! -f "$PEM_KEY" ]]; then
    echo -e "${RED}❌ Error: PEM key file not found: $PEM_KEY${NC}"
    exit 1
fi

if [[ ! -f "aws-lightsail/.env" ]]; then
    echo -e "${RED}❌ Error: .env file not found.${NC}"
    exit 1
fi

chmod 600 "$PEM_KEY"

echo -e "${YELLOW}📁 Transferring files...${NC}"
rsync -avz --progress \
    --exclude 'node_modules' --exclude '.git' --exclude '.next' \
    -e "ssh -i $PEM_KEY -o StrictHostKeyChecking=no" \
    ./ "$SERVER_USER@$SERVER_IP":~/$PROJECT_NAME/

scp -i "$PEM_KEY" -o StrictHostKeyChecking=no \
    aws-lightsail/.env "$SERVER_USER@$SERVER_IP":~/$PROJECT_NAME/aws-lightsail/

echo -e "${YELLOW}🚀 Deploying backend services...${NC}"
ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_IP" << ENDSSH
    cd ~/$PROJECT_NAME/aws-lightsail
    
    echo "🔽 Stopping existing services..."
    docker-compose -f docker-compose.simple.yml down --remove-orphans || true
    
    echo "🧹 Cleaning up..."
    docker system prune -f || true
    
    echo "🏗️  Building and starting backend services..."
    docker-compose -f docker-compose.simple.yml up -d --build
    
    echo "⏳ Waiting for services..."
    sleep 45
    
    echo "📊 Service status:"
    docker-compose -f docker-compose.simple.yml ps
    
    echo "🔍 Health check:"
    docker-compose -f docker-compose.simple.yml logs --tail=10
ENDSSH

echo -e "${GREEN}✅ Backend deployment completed!${NC}"
echo -e "${YELLOW}📍 Access your services:${NC}"
echo -e "${GREEN}🎙️  Transcription API: http://$SERVER_IP:8000/docs${NC}"
echo -e "${GREEN}📊 Analysis API: http://$SERVER_IP:8001/docs${NC}"
echo -e "${GREEN}🗄️  Database: $SERVER_IP:5432${NC}"
echo -e "${GREEN}🔴 Redis: $SERVER_IP:6379${NC}"

echo -e "${YELLOW}🧪 Testing YouTube functionality...${NC}"
curl -s "http://$SERVER_IP:8000/health" && echo -e "${GREEN}✅ Transcription service responding${NC}" || echo -e "${RED}❌ Transcription service down${NC}"
curl -s "http://$SERVER_IP:8001/health" && echo -e "${GREEN}✅ Analysis service responding${NC}" || echo -e "${RED}❌ Analysis service down${NC}"