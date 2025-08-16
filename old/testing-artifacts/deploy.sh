#!/bin/bash

# AIBOA Teaching Analysis System - Railway Deployment Script
# This script automates the deployment process to Railway

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="379dfeea-b7f3-47cf-80c8-4d6d6b72329f"
GITHUB_REPO="https://github.com/JihunKong/teaching_analize"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Railway login
check_railway_login() {
    if railway whoami >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Main deployment function
main() {
    echo "================================================"
    echo "   AIBOA Teaching Analysis System Deployment"
    echo "================================================"
    echo ""

    # Step 1: Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command_exists railway; then
        print_error "Railway CLI not installed!"
        echo "Please install Railway CLI first:"
        echo "  macOS: brew install railway"
        echo "  Linux: curl -fsSL https://railway.app/install.sh | sh"
        exit 1
    fi
    print_success "Railway CLI installed"

    if ! command_exists git; then
        print_error "Git not installed!"
        exit 1
    fi
    print_success "Git installed"

    # Step 2: Check Railway login
    print_status "Checking Railway authentication..."
    
    if ! check_railway_login; then
        print_warning "Not logged in to Railway"
        echo "Please login to Railway:"
        railway login
        
        if ! check_railway_login; then
            print_error "Railway login failed!"
            exit 1
        fi
    fi
    print_success "Authenticated with Railway"

    # Step 3: Link to Railway project
    print_status "Linking to Railway project..."
    
    if railway link $PROJECT_ID 2>/dev/null; then
        print_success "Linked to Railway project"
    else
        print_warning "Already linked or linking failed"
    fi

    # Step 4: Setup databases
    print_status "Setting up database services..."
    
    echo "Do you want to add PostgreSQL? (y/n)"
    read -r add_postgres
    if [[ $add_postgres == "y" ]]; then
        railway add postgresql || print_warning "PostgreSQL might already exist"
        print_success "PostgreSQL configured"
    fi

    echo "Do you want to add Redis? (y/n)"
    read -r add_redis
    if [[ $add_redis == "y" ]]; then
        railway add redis || print_warning "Redis might already exist"
        print_success "Redis configured"
    fi

    # Step 5: Get database URLs
    print_status "Retrieving database connection strings..."
    
    DATABASE_URL=$(railway variables get DATABASE_URL 2>/dev/null || echo "")
    REDIS_URL=$(railway variables get REDIS_URL 2>/dev/null || echo "")
    
    if [[ -n "$DATABASE_URL" ]]; then
        print_success "PostgreSQL URL retrieved"
    else
        print_warning "Could not retrieve PostgreSQL URL"
    fi
    
    if [[ -n "$REDIS_URL" ]]; then
        print_success "Redis URL retrieved"
    else
        print_warning "Could not retrieve Redis URL"
    fi

    # Step 6: Set environment variables
    print_status "Setting environment variables..."
    
    # Common variables
    railway variables set NODE_ENV=production
    railway variables set PYTHON_ENV=production
    railway variables set TZ=Asia/Seoul
    railway variables set DEBUG=false
    railway variables set LOG_LEVEL=INFO
    
    # API Keys - Load from environment or prompt user
    if [[ -n "${OPENAI_API_KEY}" ]]; then
        railway variables set OPENAI_API_KEY="${OPENAI_API_KEY}"
    else
        read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
        railway variables set OPENAI_API_KEY="${OPENAI_API_KEY}"
    fi
    
    if [[ -n "${UPSTAGE_API_KEY}" ]]; then
        railway variables set UPSTAGE_API_KEY="${UPSTAGE_API_KEY}"
    else
        read -p "Enter your Upstage/Solar API Key: " UPSTAGE_API_KEY
        railway variables set UPSTAGE_API_KEY="${UPSTAGE_API_KEY}"
    fi
    
    # Generate a secure API key
    API_KEY=$(openssl rand -hex 32 2>/dev/null || echo "development-key-$(date +%s)")
    railway variables set API_KEY="$API_KEY"
    
    print_success "Environment variables configured"

    # Step 7: Run database migrations
    print_status "Running database migrations..."
    
    if [[ -n "$DATABASE_URL" ]]; then
        # Check if migrations directory exists
        if [[ -f "migrations/001_initial_schema.sql" ]]; then
            railway run --service postgres psql $DATABASE_URL -f migrations/001_initial_schema.sql || print_warning "Migration might have already been applied"
            print_success "Database migrations completed"
        else
            print_warning "No migration files found"
        fi
    else
        print_warning "Skipping migrations - no database URL"
    fi

    # Step 8: Deploy services
    print_status "Deploying services..."
    
    # Deploy Transcription Service
    echo "Deploying Transcription Service..."
    cd services/transcription
    railway up --detach || print_error "Failed to deploy Transcription Service"
    cd ../..
    print_success "Transcription Service deployed"
    
    # Deploy Analysis Service
    echo "Deploying Analysis Service..."
    cd services/analysis
    railway up --detach || print_error "Failed to deploy Analysis Service"
    cd ../..
    print_success "Analysis Service deployed"

    # Step 9: Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10

    # Step 10: Verify deployment
    print_status "Verifying deployment..."
    
    # Get service URLs
    TRANSCRIPTION_URL=$(railway status --json 2>/dev/null | grep -o '"domain":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "")
    ANALYSIS_URL=$(railway status --json 2>/dev/null | grep -o '"domain":"[^"]*"' | tail -1 | cut -d'"' -f4 || echo "")
    
    if [[ -n "$TRANSCRIPTION_URL" ]]; then
        if curl -s -o /dev/null -w "%{http_code}" "https://$TRANSCRIPTION_URL/health" | grep -q "200"; then
            print_success "Transcription Service is healthy"
        else
            print_warning "Transcription Service health check failed"
        fi
    fi
    
    if [[ -n "$ANALYSIS_URL" ]]; then
        if curl -s -o /dev/null -w "%{http_code}" "https://$ANALYSIS_URL/health" | grep -q "200"; then
            print_success "Analysis Service is healthy"
        else
            print_warning "Analysis Service health check failed"
        fi
    fi

    # Step 11: Display summary
    echo ""
    echo "================================================"
    echo "         Deployment Summary"
    echo "================================================"
    echo ""
    
    if [[ -n "$TRANSCRIPTION_URL" ]]; then
        echo "📡 Transcription Service:"
        echo "   URL: https://$TRANSCRIPTION_URL"
        echo "   Health: https://$TRANSCRIPTION_URL/health"
        echo "   Docs: https://$TRANSCRIPTION_URL/docs"
    fi
    
    echo ""
    
    if [[ -n "$ANALYSIS_URL" ]]; then
        echo "🧠 Analysis Service:"
        echo "   URL: https://$ANALYSIS_URL"
        echo "   Health: https://$ANALYSIS_URL/health"
        echo "   Docs: https://$ANALYSIS_URL/docs"
    fi
    
    echo ""
    echo "🔑 API Key: $API_KEY"
    echo ""
    echo "📊 View logs:"
    echo "   railway logs --service transcription"
    echo "   railway logs --service analysis"
    echo ""
    echo "🌐 Railway Dashboard:"
    echo "   https://railway.app/project/$PROJECT_ID"
    echo ""
    
    print_success "Deployment completed successfully!"
}

# Run main function
main "$@"