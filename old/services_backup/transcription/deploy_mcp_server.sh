#!/bin/bash

# Deploy MCP YouTube Transcript Server
# This script sets up and deploys the MCP server for YouTube transcript extraction

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Deploying MCP YouTube Transcript Server"
echo "Project root: $PROJECT_ROOT"
echo "Script directory: $SCRIPT_DIR"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs/mcp"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose is available
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Neither docker-compose nor 'docker compose' is available"
    exit 1
fi

echo "✅ Found compose command: $COMPOSE_CMD"

# Load environment variables if .env file exists
if [ -f "$SCRIPT_DIR/.env.mcp" ]; then
    echo "📄 Loading environment variables from .env.mcp"
    set -a
    source "$SCRIPT_DIR/.env.mcp"
    set +a
else
    echo "⚠️ No .env.mcp file found. Creating template..."
    cat > "$SCRIPT_DIR/.env.mcp" << 'EOF'
# Webshare Proxy Configuration (for YouTube bot detection bypass)
# Sign up at https://www.webshare.io/ for residential proxies
WEBSHARE_PROXY_USERNAME=
WEBSHARE_PROXY_PASSWORD=
WEBSHARE_PROXY_ENDPOINT=

# Alternative HTTP Proxy Configuration
HTTP_PROXY=
HTTPS_PROXY=

# Rate Limiting
MAX_REQUESTS_PER_HOUR=60

# Server Configuration
MCP_SERVER_PORT=8888
EOF
    echo "📝 Created .env.mcp template. Please fill in your proxy credentials."
fi

# Pull the latest MCP YouTube Transcript image
echo "📦 Pulling MCP YouTube Transcript Docker image..."
docker pull jkawamoto/mcp-youtube-transcript:latest

# Stop existing containers if running
echo "🛑 Stopping existing MCP containers..."
$COMPOSE_CMD -f "$SCRIPT_DIR/docker-compose.mcp.yml" down --remove-orphans || true

# Start the MCP server
echo "🎬 Starting MCP YouTube Transcript server..."
$COMPOSE_CMD -f "$SCRIPT_DIR/docker-compose.mcp.yml" up -d

# Wait for service to be ready
echo "⏳ Waiting for MCP server to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f http://localhost:8888/health >/dev/null 2>&1; then
        echo "✅ MCP server is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Attempt $attempt/$max_attempts - waiting for MCP server..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ MCP server failed to start after $max_attempts attempts"
    echo "📋 Checking logs..."
    $COMPOSE_CMD -f "$SCRIPT_DIR/docker-compose.mcp.yml" logs
    exit 1
fi

# Test the MCP server
echo "🧪 Testing MCP server functionality..."
python3 "$SCRIPT_DIR/test_mcp_integration.py"

echo "🎉 MCP YouTube Transcript server deployed successfully!"
echo ""
echo "📊 Server Status:"
echo "   URL: http://localhost:8888"
echo "   Health: http://localhost:8888/health"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: $COMPOSE_CMD -f $SCRIPT_DIR/docker-compose.mcp.yml logs -f"
echo "   Stop server: $COMPOSE_CMD -f $SCRIPT_DIR/docker-compose.mcp.yml down"
echo "   Restart: $COMPOSE_CMD -f $SCRIPT_DIR/docker-compose.mcp.yml restart"
echo ""
echo "💡 Next Steps:"
echo "   1. Configure proxy settings in .env.mcp if needed"
echo "   2. Test with: python3 $SCRIPT_DIR/mcp_youtube_client.py <youtube_url>"
echo "   3. Integrate with your application using MCPYouTubeClient"