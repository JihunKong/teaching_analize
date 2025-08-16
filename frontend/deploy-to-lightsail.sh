#!/bin/bash

# AIBOA AWS Lightsail Deployment Script
# Usage: ./deploy-to-lightsail.sh

set -e  # Exit on any error

# Configuration
SERVER_IP="3.38.107.23"
PEM_KEY="./teaching_analize.pem"
SERVER_USER="ubuntu"
PROJECT_NAME="aiboa"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting AIBOA deployment to AWS Lightsail${NC}"
echo -e "${BLUE}Server: ${SERVER_IP}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"

# Check if PEM key exists
if [[ ! -f "$PEM_KEY" ]]; then
    echo -e "${RED}❌ Error: PEM key file not found: $PEM_KEY${NC}"
    exit 1
fi

# Check if .env file exists
if [[ ! -f "aws-lightsail/.env" ]]; then
    echo -e "${RED}❌ Error: .env file not found. Please create aws-lightsail/.env with your API keys.${NC}"
    echo -e "${YELLOW}📝 You can copy from aws-lightsail/.env.example and update the values.${NC}"
    exit 1
fi

# Set correct permissions for PEM key
chmod 600 "$PEM_KEY"

echo -e "${YELLOW}🔐 Testing server connection...${NC}"
if ! ssh -i "$PEM_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "echo 'Connection successful'"; then
    echo -e "${RED}❌ Cannot connect to server. Please check:${NC}"
    echo -e "${RED}   - Server IP: $SERVER_IP${NC}"
    echo -e "${RED}   - PEM key: $PEM_KEY${NC}"
    echo -e "${RED}   - Security groups allow SSH (port 22)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Server connection successful${NC}"

# Step 1: Server preparation and Docker installation
echo -e "${YELLOW}🔧 Step 1: Preparing server and installing Docker...${NC}"
ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
    set -e
    
    echo "🔄 Updating system packages..."
    sudo apt update -y
    
    echo "🐳 Installing Docker..."
    if ! command -v docker &> /dev/null; then
        sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        sudo apt update -y
        sudo apt install -y docker-ce docker-ce-cli containerd.io
        sudo usermod -aG docker ubuntu
    else
        echo "Docker is already installed"
    fi
    
    echo "🔧 Installing Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    else
        echo "Docker Compose is already installed"
    fi
    
    echo "📁 Creating project directory..."
    mkdir -p ~/aiboa
    
    echo "🔄 Starting Docker service..."
    sudo systemctl start docker
    sudo systemctl enable docker
    
    echo "✅ Server preparation completed"
ENDSSH

echo -e "${GREEN}✅ Step 1 completed: Docker installation${NC}"

# Step 2: File transfer
echo -e "${YELLOW}📁 Step 2: Transferring project files...${NC}"

# Create temporary exclude file for rsync
cat > /tmp/rsync_exclude << EOF
node_modules
.git
.next
build
dist
*.log
.DS_Store
.env*
*.pem
old/
backup_*/
__pycache__/
*.pyc
.pytest_cache/
EOF

echo "📤 Syncing project files (this may take a few minutes)..."
rsync -avz --progress \
    --exclude-from=/tmp/rsync_exclude \
    -e "ssh -i $PEM_KEY -o StrictHostKeyChecking=no" \
    ./ "$SERVER_USER@$SERVER_IP":~/aiboa/

# Clean up temporary file
rm /tmp/rsync_exclude

echo "📤 Transferring .env file..."
scp -i "$PEM_KEY" -o StrictHostKeyChecking=no \
    aws-lightsail/.env "$SERVER_USER@$SERVER_IP":~/aiboa/aws-lightsail/

echo -e "${GREEN}✅ Step 2 completed: File transfer${NC}"

# Step 3: SSL certificates generation
echo -e "${YELLOW}🔒 Step 3: Generating SSL certificates...${NC}"
ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_IP" << ENDSSH
    cd ~/aiboa/aws-lightsail/nginx
    chmod +x generate-ssl-cert.sh
    ./generate-ssl-cert.sh
ENDSSH

echo -e "${GREEN}✅ Step 3 completed: SSL certificates${NC}"

# Step 4: Docker services deployment
echo -e "${YELLOW}🚀 Step 4: Deploying AIBOA services...${NC}"
ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_IP" << ENDSSH
    set -e
    cd ~/aiboa/aws-lightsail
    
    echo "🔽 Stopping existing services (if any)..."
    docker-compose down --remove-orphans || true
    
    echo "🧹 Cleaning up old images and containers..."
    docker system prune -f || true
    
    echo "🏗️  Building and starting services..."
    docker-compose up -d --build
    
    echo "⏳ Waiting for services to start..."
    sleep 30
    
    echo "📊 Service status:"
    docker-compose ps
    
    echo "🔍 Quick health check:"
    docker-compose logs --tail=10
ENDSSH

echo -e "${GREEN}✅ Step 4 completed: Service deployment${NC}"

# Step 5: Health checks and validation
echo -e "${YELLOW}🔍 Step 5: Running health checks...${NC}"

echo "🏥 Testing service endpoints..."

# Test services
services=(
    "Nginx:80"
    "Frontend:3000"
    "Transcription:8000"
    "Analysis:8001"
)

for service_info in "${services[@]}"; do
    IFS=':' read -r service_name port <<< "$service_info"
    echo -n "Testing $service_name (port $port)... "
    
    if curl -f -s --max-time 10 "http://$SERVER_IP:$port/health" > /dev/null 2>&1 || \
       curl -f -s --max-time 10 "http://$SERVER_IP:$port/" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Service may still be starting${NC}"
    fi
done

# Final status check
echo -e "${YELLOW}📋 Final deployment status:${NC}"
ssh -i "$PEM_KEY" "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
    cd ~/aiboa/aws-lightsail
    echo "🐳 Docker containers:"
    docker-compose ps
    
    echo -e "\n💾 Disk usage:"
    df -h
    
    echo -e "\n🖥️  Memory usage:"
    free -h
    
    echo -e "\n🔥 Recent logs:"
    docker-compose logs --tail=5 --timestamps
ENDSSH

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 AIBOA deployment completed successfully!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📍 Access your application:${NC}"
echo -e "${GREEN}🌐 Main Application: http://$SERVER_IP${NC}"
echo -e "${GREEN}🎯 Frontend: http://$SERVER_IP:3000${NC}"
echo -e "${GREEN}🎙️  Transcription API: http://$SERVER_IP:8000${NC}"
echo -e "${GREEN}📊 Analysis API: http://$SERVER_IP:8001${NC}"
echo ""
echo -e "${YELLOW}🔧 Management commands:${NC}"
echo -e "${BLUE}ssh -i $PEM_KEY $SERVER_USER@$SERVER_IP${NC}"
echo -e "${BLUE}cd ~/aiboa/aws-lightsail${NC}"
echo -e "${BLUE}docker-compose logs -f [service-name]${NC}"
echo -e "${BLUE}docker-compose restart [service-name]${NC}"
echo -e "${BLUE}docker-compose ps${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "${BLUE}1. Test YouTube transcription functionality${NC}"
echo -e "${BLUE}2. Set up domain and SSL certificates (optional)${NC}"
echo -e "${BLUE}3. Configure monitoring and backups${NC}"
echo ""
echo -e "${GREEN}✨ Happy analyzing! 🎓${NC}"
