#!/bin/bash

##############################################################################
# AIBOA Platform - AWS Lightsail Docker 배포 스크립트
# 프론트엔드와 백엔드를 AWS Lightsail에 Docker로 배포
##############################################################################

set -euo pipefail

# Configuration
LIGHTSAIL_SERVER="3.38.107.23"
PEM_KEY="/Users/jihunkong/teaching_analize/teaching_analize.pem"
PROJECT_NAME="teaching_analize"
DOCKER_COMPOSE_FILE="docker-compose.fixed.yml"
REMOTE_PROJECT_DIR="/home/ubuntu/${PROJECT_NAME}"
GIT_REPO="https://github.com/JihunKong/teaching_analize.git"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
LOG_FILE="./logs/deployment_$(date +%Y%m%d_%H%M%S).log"
mkdir -p ./logs

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "${LOG_FILE}"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "${LOG_FILE}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}" | tee -a "${LOG_FILE}"
}

# Function to execute remote SSH command
ssh_exec() {
    local cmd="$1"
    log "Executing on server: $cmd"
    ssh -i "${PEM_KEY}" -o StrictHostKeyChecking=no ubuntu@"${LIGHTSAIL_SERVER}" "${cmd}"
}

# Function to copy files to server
scp_copy() {
    local source="$1"
    local target="$2"
    log "Copying $source to server:$target"
    scp -i "${PEM_KEY}" -o StrictHostKeyChecking=no -r "${source}" ubuntu@"${LIGHTSAIL_SERVER}":"${target}"
}

main() {
    log "Starting AIBOA Platform deployment to AWS Lightsail"
    log "Server: ${LIGHTSAIL_SERVER}"
    log "Project: ${PROJECT_NAME}"
    
    # Step 1: Test SSH connection
    log "Step 1: Testing SSH connection"
    if ! ssh_exec "echo 'SSH connection successful'"; then
        error "SSH connection failed"
    fi
    success "SSH connection established"
    
    # Step 2: Stop existing containers (if any)
    log "Step 2: Stopping existing Docker containers"
    ssh_exec "cd ${REMOTE_PROJECT_DIR} && docker-compose -f ${DOCKER_COMPOSE_FILE} down || true" || warning "No existing containers to stop"
    
    # Step 3: Clone or update Git repository
    log "Step 3: Setting up Git repository"
    if ssh_exec "[ -d ${REMOTE_PROJECT_DIR} ]"; then
        log "Project directory exists, pulling latest changes"
        ssh_exec "cd ${REMOTE_PROJECT_DIR} && git pull origin main"
    else
        log "Cloning repository"
        ssh_exec "git clone ${GIT_REPO} ${REMOTE_PROJECT_DIR}"
    fi
    
    # Step 4: Clean up Docker system
    log "Step 4: Cleaning Docker system"
    ssh_exec "docker system prune -f"
    
    # Step 5: Build frontend (Next.js export)
    log "Step 5: Building frontend"
    ssh_exec "cd ${REMOTE_PROJECT_DIR}/frontend && npm install --production"
    ssh_exec "cd ${REMOTE_PROJECT_DIR}/frontend && npm run build"
    
    # Step 6: Set file permissions
    log "Step 6: Setting file permissions"
    ssh_exec "chmod +x ${REMOTE_PROJECT_DIR}/*.sh"
    ssh_exec "sudo chown -R ubuntu:ubuntu ${REMOTE_PROJECT_DIR}"
    
    # Step 7: Create required directories
    log "Step 7: Creating required directories"
    ssh_exec "mkdir -p ${REMOTE_PROJECT_DIR}/data ${REMOTE_PROJECT_DIR}/logs"
    
    # Step 8: Build Docker images
    log "Step 8: Building Docker images"
    ssh_exec "cd ${REMOTE_PROJECT_DIR} && docker-compose -f ${DOCKER_COMPOSE_FILE} build --no-cache"
    
    # Step 9: Start services
    log "Step 9: Starting Docker services"
    ssh_exec "cd ${REMOTE_PROJECT_DIR} && docker-compose -f ${DOCKER_COMPOSE_FILE} up -d"
    
    # Step 10: Wait for services to be ready
    log "Step 10: Waiting for services to start (30 seconds)"
    sleep 30
    
    # Step 11: Check service status
    log "Step 11: Checking service status"
    ssh_exec "cd ${REMOTE_PROJECT_DIR} && docker-compose -f ${DOCKER_COMPOSE_FILE} ps"
    
    # Step 12: Test endpoints
    log "Step 12: Testing endpoints"
    if ssh_exec "curl -f -s http://localhost/health > /dev/null"; then
        success "Health check passed"
    else
        warning "Health check failed - checking individual services"
        ssh_exec "cd ${REMOTE_PROJECT_DIR} && docker-compose -f ${DOCKER_COMPOSE_FILE} logs --tail=20 nginx"
    fi
    
    # Step 13: Show final status
    log "Step 13: Final deployment status"
    ssh_exec "cd ${REMOTE_PROJECT_DIR} && docker-compose -f ${DOCKER_COMPOSE_FILE} ps"
    ssh_exec "docker system df"
    
    success "Deployment completed successfully!"
    log "Application should be accessible at: http://${LIGHTSAIL_SERVER}"
    log "Frontend: http://${LIGHTSAIL_SERVER}"
    log "API Health: http://${LIGHTSAIL_SERVER}/health"
    log "Log file: ${LOG_FILE}"
    
    # Optional: Show logs
    echo
    echo "To view logs:"
    echo "ssh -i ${PEM_KEY} ubuntu@${LIGHTSAIL_SERVER} 'cd ${REMOTE_PROJECT_DIR} && docker-compose -f ${DOCKER_COMPOSE_FILE} logs -f'"
}

# Error handling
trap 'error "Deployment failed at line $LINENO"' ERR

# Check prerequisites
if [[ ! -f "${PEM_KEY}" ]]; then
    error "PEM key not found: ${PEM_KEY}"
fi

if [[ ! -f "${DOCKER_COMPOSE_FILE}" ]]; then
    error "Docker compose file not found: ${DOCKER_COMPOSE_FILE}"
fi

# Run main function
main "$@"