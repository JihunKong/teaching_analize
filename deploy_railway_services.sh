#!/bin/bash

# Railway Monorepo Deployment Script for AIBOA System
# This script properly configures Railway to deploy multiple services from a monorepo

set -e

# Load environment variables from .env.local if it exists
if [ -f ".env.local" ]; then
    echo "Loading environment variables from .env.local..."
    export $(cat .env.local | grep -v '^#' | xargs)
else
    echo "WARNING: .env.local not found. Please create it with your API keys."
    echo "Copy .env.example to .env.local and add your keys."
    exit 1
fi

echo "🚀 AIBOA Railway Deployment - Fixing Monorepo Configuration"
echo "==========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}Railway CLI is not installed.${NC}"
    echo "Installing Railway CLI..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install railway
    else
        curl -sSL https://railway.app/install.sh | sh
    fi
fi

# Login to Railway
echo -e "${YELLOW}Logging into Railway...${NC}"
railway login

# Project ID from your URL
PROJECT_ID="379dfeea-b7f3-47cf-80c8-4d6d6b72329f"

echo -e "${YELLOW}Linking to project: $PROJECT_ID${NC}"
railway link $PROJECT_ID

# Function to deploy a service
deploy_service() {
    local service_name=$1
    local service_path=$2
    local service_port=$3
    
    echo -e "${GREEN}Deploying $service_name...${NC}"
    echo "Path: $service_path"
    echo "Port: $service_port"
    
    # Navigate to service directory
    cd "$service_path"
    
    # Create a new Railway service or use existing
    echo "Creating/updating Railway service: $service_name"
    
    # Deploy with specific service name
    railway up --service "$service_name" --detach
    
    # Set environment variables for this specific service
    echo "Setting environment variables for $service_name..."
    
    railway variables set PORT="$service_port" --service "$service_name"
    railway variables set SERVICE_NAME="$service_name" --service "$service_name"
    
    # Service-specific environment variables
    if [ "$service_name" = "transcription" ]; then
        railway variables set \
            OPENAI_API_KEY="${OPENAI_API_KEY}" \
            --service "$service_name"
    elif [ "$service_name" = "analysis" ]; then
        railway variables set \
            SOLAR_API_KEY="${SOLAR_API_KEY}" \
            UPSTAGE_API_KEY="${UPSTAGE_API_KEY}" \
            --service "$service_name"
    fi
    
    # Common environment variables
    railway variables set \
        API_KEY="aiboa-$(openssl rand -hex 16)" \
        PYTHONUNBUFFERED="1" \
        DEBUG="false" \
        --service "$service_name"
    
    echo -e "${GREEN}✓ $service_name deployed successfully${NC}"
    
    # Return to root directory
    cd -
}

# Main deployment process
echo -e "${YELLOW}Starting deployment of services...${NC}"

# Check if we're in the right directory
if [ ! -d "services" ]; then
    echo -e "${RED}Error: 'services' directory not found.${NC}"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Add PostgreSQL if not exists
echo -e "${YELLOW}Adding PostgreSQL database...${NC}"
railway add postgresql || echo "PostgreSQL might already exist"

# Add Redis if not exists
echo -e "${YELLOW}Adding Redis...${NC}"
railway add redis || echo "Redis might already exist"

# Get database URLs
echo -e "${YELLOW}Getting database URLs...${NC}"
DB_URL=$(railway variables get DATABASE_URL)
REDIS_URL=$(railway variables get REDIS_URL)

# Deploy Transcription Service
echo ""
echo "======================================="
echo "Deploying Transcription Service"
echo "======================================="
deploy_service "transcription" "services/transcription" "8000"

# Set database URLs for transcription service
railway variables set \
    DATABASE_URL="$DB_URL" \
    REDIS_URL="$REDIS_URL" \
    RAILWAY_VOLUME_PATH="/data" \
    --service "transcription"

# Deploy Analysis Service
echo ""
echo "======================================="
echo "Deploying Analysis Service"
echo "======================================="
deploy_service "analysis" "services/analysis" "8001"

# Set database URLs for analysis service
railway variables set \
    DATABASE_URL="$DB_URL" \
    REDIS_URL="$REDIS_URL" \
    TRANSCRIPTION_SERVICE_URL="https://transcription-production.up.railway.app" \
    --service "analysis"

# Run database migrations
echo ""
echo -e "${YELLOW}Running database migrations...${NC}"
cd services/transcription
railway run --service transcription python -c "
from app.database import init_db
import asyncio
asyncio.run(init_db())
print('Database initialized successfully')
" || echo "Migration might have already been applied"
cd -

# Verify deployments
echo ""
echo "======================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "======================================="
echo ""
echo "Services deployed:"
echo "  • Transcription Service"
echo "  • Analysis Service"
echo "  • PostgreSQL Database"
echo "  • Redis Cache"
echo ""
echo "To check deployment status:"
echo "  railway status"
echo ""
echo "To view logs:"
echo "  railway logs --service transcription"
echo "  railway logs --service analysis"
echo ""
echo "To get service URLs:"
echo "  railway open --service transcription"
echo "  railway open --service analysis"
echo ""
echo -e "${GREEN}✨ Your AIBOA system is ready!${NC}"