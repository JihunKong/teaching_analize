#!/bin/bash

# AWS Lightsail Deployment Script
# Deploys updates without requiring SSH access

set -e

# Configuration
LIGHTSAIL_IP="3.38.107.23"
HTML_SOURCE="authenticated-dashboard.html"
HTML_TARGET="index.html"
ADMIN_KEY="${ADMIN_UPDATE_KEY:-temp-admin-key-123}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 AIBOA Lightsail Deployment Script${NC}"
echo "========================================"

# Function to test service health
test_service_health() {
    local port=$1
    local endpoint=${2:-"/health"}
    local service_name=$3
    
    echo -n "Testing $service_name (port $port)... "
    local status=$(curl -s -o /dev/null -w "%{http_code}" "http://$LIGHTSAIL_IP:$port$endpoint" 2>/dev/null || echo "000")
    
    if [ "$status" = "200" ]; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unhealthy (status: $status)${NC}"
        return 1
    fi
}

# Function to check SSH connectivity
check_ssh() {
    echo -n "Checking SSH connectivity... "
    if timeout 10 ssh -i teaching_analize.pem -o ConnectTimeout=5 -o BatchMode=yes ubuntu@$LIGHTSAIL_IP "echo 'SSH OK'" 2>/dev/null; then
        echo -e "${GREEN}✅ SSH Available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ SSH Timeout${NC}"
        return 1
    fi
}

# Function to try alternative SSH ports
try_alt_ssh_ports() {
    echo "Trying alternative SSH ports..."
    for port in 2222 2200 22222 2022; do
        echo -n "  Testing port $port... "
        if timeout 5 ssh -i teaching_analize.pem -p $port -o ConnectTimeout=3 -o BatchMode=yes ubuntu@$LIGHTSAIL_IP "echo 'Connected'" 2>/dev/null; then
            echo -e "${GREEN}✅ Working${NC}"
            SSH_PORT=$port
            return 0
        else
            echo -e "${RED}❌ Failed${NC}"
        fi
    done
    return 1
}

# Function to deploy via HTTP update endpoint
deploy_via_http() {
    echo "Attempting HTTP deployment..."
    
    if [ ! -f "$HTML_SOURCE" ]; then
        echo -e "${RED}❌ Source file $HTML_SOURCE not found${NC}"
        return 1
    fi
    
    # Method 1: Try admin update endpoint
    echo -n "  Trying admin update endpoint... "
    if curl -f -X POST "http://$LIGHTSAIL_IP/admin/update-content" \
        -H "X-Admin-Key: $ADMIN_KEY" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@$HTML_SOURCE" \
        -F "target=$HTML_TARGET" 2>/dev/null; then
        echo -e "${GREEN}✅ Success${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
    
    # Method 2: Try simple file upload endpoint
    echo -n "  Trying simple upload endpoint... "
    if curl -f -X PUT "http://$LIGHTSAIL_IP/upload/$HTML_TARGET" \
        -H "Authorization: Bearer $ADMIN_KEY" \
        --data-binary "@$HTML_SOURCE" 2>/dev/null; then
        echo -e "${GREEN}✅ Success${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed${NC}"
    fi
    
    return 1
}

# Function to verify deployment
verify_deployment() {
    echo ""
    echo "🔍 Verifying deployment..."
    echo "=========================="
    
    # Test all services
    local all_healthy=true
    
    test_service_health 80 "/" "Web Server" || all_healthy=false
    test_service_health 8002 "/health" "Auth Service" || all_healthy=false
    test_service_health 8000 "/health" "Transcription Service" || all_healthy=false
    test_service_health 8001 "/health" "Analysis Service" || all_healthy=false
    
    # Check if updated HTML is deployed
    echo -n "Checking HTML update... "
    if curl -s "http://$LIGHTSAIL_IP/" | grep -q "favicon" && curl -s "http://$LIGHTSAIL_IP/" | grep -q "workflow-form"; then
        echo -e "${GREEN}✅ Updated HTML deployed${NC}"
    else
        echo -e "${RED}❌ HTML not updated${NC}"
        all_healthy=false
    fi
    
    if [ "$all_healthy" = "true" ]; then
        echo ""
        echo -e "${GREEN}🎉 Deployment successful! All services are healthy.${NC}"
        echo ""
        echo "🌐 Application URLs:"
        echo "   Main App: http://$LIGHTSAIL_IP/"
        echo "   Auth API: http://$LIGHTSAIL_IP:8002/health"
        echo ""
        return 0
    else
        echo ""
        echo -e "${RED}⚠️ Deployment completed with some issues. Check the logs above.${NC}"
        return 1
    fi
}

# Main deployment flow
main() {
    echo "Starting deployment process..."
    echo ""
    
    # Step 1: Check current service health
    echo "📊 Current Service Status:"
    echo "========================="
    test_service_health 80 "/" "Web Server"
    test_service_health 8002 "/health" "Auth Service"  
    test_service_health 8000 "/health" "Transcription Service"
    test_service_health 8001 "/health" "Analysis Service"
    echo ""
    
    # Step 2: Check SSH availability
    SSH_AVAILABLE=false
    if check_ssh; then
        SSH_AVAILABLE=true
    elif try_alt_ssh_ports; then
        SSH_AVAILABLE=true
    fi
    echo ""
    
    # Step 3: Deploy HTML update
    echo "📄 Deploying HTML Update:"
    echo "========================="
    if deploy_via_http; then
        echo -e "${GREEN}✅ HTML deployed via HTTP${NC}"
    else
        echo -e "${RED}❌ HTTP deployment failed${NC}"
        echo "Manual deployment required via Lightsail console"
    fi
    echo ""
    
    # Step 4: Verify deployment
    verify_deployment
    
    echo ""
    echo -e "${BLUE}🏁 Deployment process completed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Test the application at http://$LIGHTSAIL_IP/"
    echo "2. Monitor logs for any issues"
    echo "3. Set up automated health monitoring"
    
    if [ "$SSH_AVAILABLE" = "false" ]; then
        echo ""
        echo -e "${YELLOW}⚠️ SSH access issues detected. Manual steps:${NC}"
        echo "   1. Go to: https://lightsail.aws.amazon.com/"
        echo "   2. Select your instance and click 'Connect using SSH'"
        echo "   3. Upload the updated HTML file manually"
    fi
}

# Check if running as main script
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi