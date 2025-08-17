#!/bin/bash

# Educational Analysis System Deployment Script
# 교육 분석 시스템 서버 배포 스크립트

set -e

LIGHTSAIL_IP="3.38.107.23"
PEM_FILE="/Users/jihunkong/teaching_analize/teaching_analize.pem"
REPO_DIR="/home/ubuntu/aiboa"

echo "🚀 Starting Educational Analysis System Deployment..."

# SSH 연결 함수
ssh_exec() {
    ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no ubuntu@$LIGHTSAIL_IP "$1"
}

# SCP 파일 복사 함수
scp_copy() {
    scp -i "$PEM_FILE" -o StrictHostKeyChecking=no "$1" ubuntu@$LIGHTSAIL_IP:"$2"
}

echo "📡 Connecting to server and updating repository..."

# 1. 저장소 업데이트
ssh_exec "cd $REPO_DIR && git pull origin main"

echo "🔧 Setting up Educational Analysis Service..."

# 2. 교육 분석 서비스 설정
ssh_exec "
cd $REPO_DIR/services/educational-analysis && 
pip3 install -r requirements.txt --user &&
mkdir -p static/charts
"

echo "🔧 Setting up Integration Service..."

# 3. 통합 서비스 설정  
ssh_exec "
cd $REPO_DIR/services/integration &&
pip3 install -r requirements.txt --user
"

echo "🐳 Updating Docker containers..."

# 4. 기존 전사 서비스 재시작 (최신 코드 반영)
ssh_exec "
cd $REPO_DIR/services/transcription &&
docker-compose down &&
docker-compose up -d --build
"

echo "📋 Creating Docker Compose for new services..."

# 5. 새로운 서비스들을 위한 Docker Compose 생성
ssh_exec "cat > $REPO_DIR/docker-compose.educational.yml << 'EOF'
version: '3.8'

services:
  educational-analysis:
    build: 
      context: ./services/educational-analysis
      dockerfile: Dockerfile
    ports:
      - \"8001:8001\"
    environment:
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=\${ANTHROPIC_API_KEY}
      - UPSTAGE_API_KEY=\${UPSTAGE_API_KEY}
    volumes:
      - ./data/analysis:/app/static/charts
    restart: unless-stopped
    
  integration-service:
    build:
      context: ./services/integration  
      dockerfile: Dockerfile
    ports:
      - \"8002:8002\"
    environment:
      - TRANSCRIPTION_SERVICE_URL=http://3.38.107.23:8000
      - ANALYSIS_SERVICE_URL=http://educational-analysis:8001
      - API_KEY=\${API_KEY}
    depends_on:
      - educational-analysis
    restart: unless-stopped
    
volumes:
  analysis_data:
EOF"

echo "🐳 Creating Dockerfiles for new services..."

# 6. 교육 분석 서비스 Dockerfile 생성
ssh_exec "cat > $REPO_DIR/services/educational-analysis/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Korean fonts and plotting
RUN apt-get update && apt-get install -y \\
    fonts-nanum \\
    fonts-nanum-coding \\
    fonts-nanum-extra \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create static directory
RUN mkdir -p static/charts

EXPOSE 8001

CMD [\"python\", \"main.py\"]
EOF"

# 7. 통합 서비스 Dockerfile 생성  
ssh_exec "cat > $REPO_DIR/services/integration/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD [\"python\", \"main.py\"]
EOF"

echo "🔑 Setting up environment variables..."

# 8. 환경 변수 파일 생성 (실제 키는 수동으로 설정 필요)
ssh_exec "cat > $REPO_DIR/.env.educational << 'EOF'
# LLM API Keys (set these manually)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  
UPSTAGE_API_KEY=your_upstage_key_here

# Service Configuration
API_KEY=test-api-key
TRANSCRIPTION_SERVICE_URL=http://3.38.107.23:8000
ANALYSIS_SERVICE_URL=http://3.38.107.23:8001

# Database (for future use)
DATABASE_URL=sqlite:///./educational_analysis.db
EOF"

echo "🚀 Starting new services..."

# 9. 새로운 서비스들 시작
ssh_exec "
cd $REPO_DIR &&
export \$(cat .env.educational | xargs) &&
docker-compose -f docker-compose.educational.yml up -d --build
"

echo "🔍 Checking service status..."

# 10. 서비스 상태 확인
ssh_exec "
echo '=== Docker Containers ===' &&
docker ps &&
echo '' &&
echo '=== Port Status ===' &&
netstat -tlnp | grep -E ':(8000|8001|8002)' || echo 'No services running on ports 8000-8002' &&
echo '' &&
echo '=== Service Health Checks ===' &&
echo 'Transcription Service:' &&
curl -f http://localhost:8000/health 2>/dev/null | python3 -m json.tool || echo 'Service not ready' &&
echo 'Analysis Service:' &&
curl -f http://localhost:8001/health 2>/dev/null | python3 -m json.tool || echo 'Service not ready' &&
echo 'Integration Service:' &&  
curl -f http://localhost:8002/health 2>/dev/null | python3 -m json.tool || echo 'Service not ready'
"

echo "📚 Creating quick test script..."

# 11. 테스트 스크립트 생성
ssh_exec "cat > $REPO_DIR/test-educational-system.sh << 'EOF'
#!/bin/bash

echo \"🧪 Testing Educational Analysis System\"

# Test transcription service
echo \"📝 Testing Transcription Service...\"
curl -s http://localhost:8000/health | python3 -m json.tool

# Test analysis service  
echo \"🎯 Testing Analysis Service...\"
curl -s http://localhost:8001/health | python3 -m json.tool

# Test integration service
echo \"🔗 Testing Integration Service...\"
curl -s http://localhost:8002/health | python3 -m json.tool

# Test connectivity between services
echo \"📡 Testing Service Connectivity...\"
curl -s http://localhost:8002/api/test/services | python3 -m json.tool

echo \"✅ All tests completed!\"
EOF

chmod +x $REPO_DIR/test-educational-system.sh"

echo "📋 Next Steps:"
echo "  1. Set actual API keys in /home/ubuntu/aiboa/.env.educational"
echo "  2. Restart services: cd /home/ubuntu/aiboa && docker-compose -f docker-compose.educational.yml restart"
echo "  3. Run tests: /home/ubuntu/aiboa/test-educational-system.sh"

echo "✅ Deployment completed!"
echo ""
echo "🌐 Service URLs:"
echo "  📝 Transcription: http://$LIGHTSAIL_IP:8000"
echo "  🎯 Analysis:      http://$LIGHTSAIL_IP:8001" 
echo "  🔗 Integration:   http://$LIGHTSAIL_IP:8002"
echo ""
echo "📋 Next Steps:"
echo "  1. Set actual API keys in /home/ubuntu/teaching_analize/.env.educational"
echo "  2. Restart services: cd /home/ubuntu/teaching_analize && docker-compose -f docker-compose.educational.yml restart"
echo "  3. Run tests: /home/ubuntu/teaching_analize/test-educational-system.sh"
echo ""
echo "🔍 To monitor logs:"
echo "  docker-compose -f docker-compose.educational.yml logs -f"