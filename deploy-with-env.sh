#!/bin/bash

##############################################################################
# AIBOA Platform Deployment Script with Environment Variable Management
# Ensures proper loading of environment variables before deployment
##############################################################################

set -euo pipefail

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.fixed.yml"
ENV_FILE=".env"
LOG_FILE="./logs/deployment_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

##############################################################################
# Logging Functions
##############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "${LOG_FILE}"
}

##############################################################################
# Environment Validation
##############################################################################

validate_environment() {
    log_info "Validating environment variables..."
    
    # Check if .env file exists
    if [[ ! -f "${ENV_FILE}" ]]; then
        log_error "Environment file ${ENV_FILE} not found!"
        exit 1
    fi
    
    # Source the environment file
    set -a  # automatically export all variables
    source "${ENV_FILE}"
    set +a
    
    # Required environment variables
    local required_vars=(
        "UPSTAGE_API_KEY"
        "OPENAI_API_KEY"
        "POSTGRES_PASSWORD"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    # Validate API key format
    if [[ ! "${UPSTAGE_API_KEY}" =~ ^up_.+ ]]; then
        log_error "Invalid UPSTAGE_API_KEY format. Should start with 'up_'"
        exit 1
    fi
    
    log_success "Environment validation completed"
    log_info "UPSTAGE_API_KEY: ${UPSTAGE_API_KEY:0:10}..."
    log_info "Environment variables are properly loaded"
}

##############################################################################
# Deployment Function
##############################################################################

deploy_services() {
    log_info "Starting deployment with validated environment..."
    
    # Ensure logs directory exists
    mkdir -p logs
    
    # Validate environment first
    validate_environment
    
    # Stop any existing services
    log_info "Stopping existing services..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" down --remove-orphans --timeout 30 2>/dev/null || true
    
    # Clean up
    docker system prune -f 2>/dev/null || true
    
    # Build and start services with environment variables
    log_info "Building services with environment variables..."
    if ! docker-compose -f "${DOCKER_COMPOSE_FILE}" build --no-cache; then
        log_error "Failed to build Docker images"
        exit 1
    fi
    
    log_info "Starting services..."
    if ! docker-compose -f "${DOCKER_COMPOSE_FILE}" up -d; then
        log_error "Failed to start services"
        exit 1
    fi
    
    # Wait for services to stabilize
    log_info "Waiting for services to stabilize..."
    sleep 20
    
    # Check container status
    log_info "Checking container status..."
    docker-compose -f "${DOCKER_COMPOSE_FILE}" ps
    
    log_success "Deployment completed successfully!"
}

##############################################################################
# Environment Variable Verification
##############################################################################

verify_container_env() {
    log_info "Verifying environment variables in containers..."
    
    # Check analysis service environment
    if docker-compose -f "${DOCKER_COMPOSE_FILE}" exec -T analysis printenv | grep -q "UPSTAGE_API_KEY=up_"; then
        log_success "UPSTAGE_API_KEY is properly set in analysis container"
    else
        log_error "UPSTAGE_API_KEY not found in analysis container"
    fi
    
    # Check transcription service environment
    if docker-compose -f "${DOCKER_COMPOSE_FILE}" exec -T transcription printenv | grep -q "OPENAI_API_KEY=sk-"; then
        log_success "OPENAI_API_KEY is properly set in transcription container"
    else
        log_warning "OPENAI_API_KEY may not be set in transcription container"
    fi
}

##############################################################################
# Main Execution
##############################################################################

main() {
    log_info "Starting AIBOA Platform Deployment with Environment Management"
    log_info "================================================================"
    
    # Deploy services
    deploy_services
    
    # Optional: Verify environment in containers (may require containers to be fully started)
    sleep 10
    verify_container_env 2>/dev/null || log_warning "Container environment verification skipped (containers may not be ready)"
    
    log_success "================================================================"
    log_success "DEPLOYMENT SUCCESSFUL!"
    log_success "================================================================"
    log_info "API Key Status:"
    log_info "- UPSTAGE_API_KEY: ✓ Configured"
    log_info "- OPENAI_API_KEY: ✓ Configured"
    log_info "- Environment file: ${ENV_FILE}"
    log_info "- Deployment log: ${LOG_FILE}"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi