#!/bin/bash

# AIBOA Automated Deployment Script
# Builds frontend locally and deploys to AWS Lightsail

set -e  # Exit on any error

# Configuration
SERVER_HOST="43.203.128.246"
SERVER_USER="ubuntu"
PEM_KEY="./teaching_analize.pem"
PROJECT_DIR="/home/ubuntu/aiboa"
LOCAL_DIR="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if PEM key exists
    if [ ! -f "$PEM_KEY" ]; then
        error "PEM key not found: $PEM_KEY"
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        error "Node.js is not installed"
        exit 1
    fi
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        error "npm is not installed"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Build frontend
build_frontend() {
    log "Building frontend..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log "Installing frontend dependencies..."
        npm install
    fi
    
    # Build for production
    log "Building Next.js app..."
    npm run build
    
    # Export static files
    log "Exporting static files..."
    npm run export 2>/dev/null || log "Export command not available, using build output"
    
    cd ..
    success "Frontend build completed"
}

# Prepare deployment package
prepare_deployment() {
    log "Preparing deployment package..."
    
    # Create temporary deployment directory
    TEMP_DIR="/tmp/aiboa_deploy_$(date +%s)"
    mkdir -p "$TEMP_DIR"
    
    # Copy necessary files
    cp -r frontend/out "$TEMP_DIR/" 2>/dev/null || cp -r frontend/.next "$TEMP_DIR/out"
    cp nginx.production.conf "$TEMP_DIR/"
    cp docker-compose.integrated.yml "$TEMP_DIR/"
    cp -r services "$TEMP_DIR/" 2>/dev/null || log "Services directory not found locally"
    
    # Copy environment template
    if [ -f ".env.example" ]; then
        cp .env.example "$TEMP_DIR/"
    fi
    
    success "Deployment package prepared in $TEMP_DIR"
}

# Deploy to server
deploy_to_server() {
    log "Deploying to server..."
    
    # Create project directory on server
    ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_HOST" "mkdir -p $PROJECT_DIR"
    
    # Copy deployment package to server
    log "Copying files to server..."
    scp -i "$PEM_KEY" -r "$TEMP_DIR"/* "$SERVER_USER@$SERVER_HOST:$PROJECT_DIR/"
    
    # Set proper permissions
    ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_HOST" "chmod +x $PROJECT_DIR/*.sh"
    
    success "Files copied to server"
}

# Update git repository on server
update_git_repo() {
    log "Updating git repository on server..."
    
    ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_HOST" << 'EOF'
        cd /home/ubuntu/aiboa
        
        # Pull latest changes
        if [ -d ".git" ]; then
            echo "Pulling latest changes..."
            git pull origin main 2>/dev/null || git pull origin master
        else
            echo "Git repository not initialized. Skipping git update."
        fi
EOF
    
    success "Git repository updated"
}

# Deploy services
deploy_services() {
    log "Deploying services on server..."
    
    ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_HOST" << 'EOF'
        cd /home/ubuntu/aiboa
        
        # Stop existing services
        echo "Stopping existing services..."
        sudo docker-compose -f docker-compose.integrated.yml down 2>/dev/null || true
        
        # Remove old nginx container if exists
        sudo docker rm -f aiboa_nginx 2>/dev/null || true
        
        # Check if .env file exists
        if [ ! -f ".env" ]; then
            echo "Creating .env file from template..."
            if [ -f ".env.example" ]; then
                cp .env.example .env
                echo "Please update .env file with production values"
            else
                echo "No .env template found. Please create .env file manually."
            fi
        fi
        
        # Build and start services
        echo "Building and starting services..."
        sudo docker-compose -f docker-compose.integrated.yml build --no-cache
        sudo docker-compose -f docker-compose.integrated.yml up -d
        
        # Wait for services to start
        echo "Waiting for services to start..."
        sleep 30
        
        # Check service status
        echo "Checking service status..."
        sudo docker-compose -f docker-compose.integrated.yml ps
        
        # Test health endpoints
        echo "Testing health endpoints..."
        curl -f http://localhost/health 2>/dev/null && echo "✓ nginx healthy" || echo "✗ nginx not responding"
        curl -f http://localhost:8002/health 2>/dev/null && echo "✓ auth service healthy" || echo "✗ auth service not responding"
        curl -f http://localhost:8000/health 2>/dev/null && echo "✓ transcription service healthy" || echo "✗ transcription service not responding"
        curl -f http://localhost:8001/health 2>/dev/null && echo "✓ analysis service healthy" || echo "✗ analysis service not responding"
EOF
    
    success "Services deployed"
}

# Cleanup
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        log "Cleaning up temporary files..."
        rm -rf "$TEMP_DIR"
        success "Cleanup completed"
    fi
}

# Main deployment function
main() {
    log "Starting AIBOA deployment to $SERVER_HOST"
    
    # Check prerequisites
    check_prerequisites
    
    # Build frontend
    build_frontend
    
    # Prepare deployment
    prepare_deployment
    
    # Deploy to server
    deploy_to_server
    
    # Update git repo (if exists)
    update_git_repo
    
    # Deploy services
    deploy_services
    
    # Cleanup
    cleanup
    
    success "🎉 Deployment completed successfully!"
    log "Access your application at: http://$SERVER_HOST"
    log "Admin panel: http://$SERVER_HOST/admin"
    log "Login page: http://$SERVER_HOST/login"
}

# Error handling
trap cleanup EXIT

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --no-build     Skip frontend build (use existing build)"
    echo "  --services-only Deploy services only (skip frontend)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full deployment"
    echo "  $0 --no-build         # Deploy without building"
    echo "  $0 --services-only    # Deploy only backend services"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --no-build)
            SKIP_BUILD=true
            shift
            ;;
        --services-only)
            SERVICES_ONLY=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Execute main function
main "$@"