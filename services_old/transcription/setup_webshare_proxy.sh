#!/bin/bash

# Setup Webshare Residential Proxy for YouTube Bot Detection Bypass
# This script helps configure Webshare proxy service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🌐 Webshare Residential Proxy Setup"
echo "=================================="

# Check if environment file exists
ENV_FILE="$SCRIPT_DIR/.env.proxy"

if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating proxy environment file..."
    cat > "$ENV_FILE" << 'EOF'
# Webshare Residential Proxy Configuration
# Sign up at: https://www.webshare.io/
# 
# After signing up:
# 1. Go to Dashboard > Proxy > Residential
# 2. Create endpoint (choose rotating or sticky)
# 3. Copy the credentials below

# Webshare Proxy Credentials
WEBSHARE_PROXY_USERNAME=your_username_here
WEBSHARE_PROXY_PASSWORD=your_password_here
WEBSHARE_PROXY_ENDPOINT=hostname:port

# Example values (replace with your actual credentials):
# WEBSHARE_PROXY_USERNAME=username-residential-123
# WEBSHARE_PROXY_PASSWORD=abc123def456
# WEBSHARE_PROXY_ENDPOINT=residential.webshare.io:9999

# Alternative HTTP Proxy (if not using Webshare)
# HTTP_PROXY=http://username:password@proxy.example.com:8080
# HTTPS_PROXY=http://username:password@proxy.example.com:8080

# Rate Limiting
MAX_REQUESTS_PER_HOUR=60
MCP_SERVER_URL=http://localhost:8888
EOF
    echo "✅ Created $ENV_FILE"
    echo ""
    echo "📋 Next steps:"
    echo "1. Sign up for Webshare at: https://www.webshare.io/"
    echo "2. Go to Dashboard > Proxy > Residential"
    echo "3. Create a new endpoint"
    echo "4. Edit $ENV_FILE with your credentials"
    echo "5. Run this script again to test the configuration"
    echo ""
    exit 0
fi

# Load environment variables
echo "📄 Loading environment from $ENV_FILE..."
set -a
source "$ENV_FILE"
set +a

# Validate configuration
if [[ -z "$WEBSHARE_PROXY_USERNAME" || "$WEBSHARE_PROXY_USERNAME" == "your_username_here" ]]; then
    echo "❌ Webshare proxy username not configured"
    echo "   Please edit $ENV_FILE with your Webshare credentials"
    exit 1
fi

if [[ -z "$WEBSHARE_PROXY_PASSWORD" || "$WEBSHARE_PROXY_PASSWORD" == "your_password_here" ]]; then
    echo "❌ Webshare proxy password not configured"
    echo "   Please edit $ENV_FILE with your Webshare credentials"
    exit 1
fi

if [[ -z "$WEBSHARE_PROXY_ENDPOINT" || "$WEBSHARE_PROXY_ENDPOINT" == "hostname:port" ]]; then
    echo "❌ Webshare proxy endpoint not configured"
    echo "   Please edit $ENV_FILE with your Webshare endpoint"
    exit 1
fi

echo "✅ Configuration loaded:"
echo "   Username: $WEBSHARE_PROXY_USERNAME"
echo "   Password: ${WEBSHARE_PROXY_PASSWORD:0:8}..."
echo "   Endpoint: $WEBSHARE_PROXY_ENDPOINT"

# Test proxy configuration
echo ""
echo "🧪 Testing proxy configuration..."

# Extract host and port
IFS=':' read -r PROXY_HOST PROXY_PORT <<< "$WEBSHARE_PROXY_ENDPOINT"

echo "   Host: $PROXY_HOST"
echo "   Port: $PROXY_PORT"

# Test with curl
echo ""
echo "🔍 Testing proxy connectivity..."

PROXY_URL="http://$WEBSHARE_PROXY_USERNAME:$WEBSHARE_PROXY_PASSWORD@$WEBSHARE_PROXY_ENDPOINT"

if curl -s --proxy "$PROXY_URL" --max-time 30 "https://httpbin.org/ip" > /tmp/proxy_test.json; then
    echo "✅ Proxy connection successful!"
    
    # Show IP information
    if command -v jq >/dev/null 2>&1; then
        PROXY_IP=$(jq -r '.origin' /tmp/proxy_test.json 2>/dev/null || echo "unknown")
    else
        PROXY_IP=$(grep -o '"origin": *"[^"]*"' /tmp/proxy_test.json | cut -d'"' -f4 2>/dev/null || echo "unknown")
    fi
    
    echo "   Proxy IP: $PROXY_IP"
    
    # Test YouTube accessibility
    echo ""
    echo "🎬 Testing YouTube accessibility through proxy..."
    
    if curl -s --proxy "$PROXY_URL" --max-time 30 -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" "https://www.youtube.com/" > /dev/null; then
        echo "✅ YouTube accessible through proxy!"
    else
        echo "⚠️ YouTube access test failed"
        echo "   This might be normal - some residential IPs may be rate-limited"
    fi
    
    rm -f /tmp/proxy_test.json
    
else
    echo "❌ Proxy connection failed"
    echo "   Please check your Webshare credentials and endpoint"
    exit 1
fi

# Test with Python proxy manager
echo ""
echo "🐍 Testing Python proxy manager..."

if python3 -c "
import sys
sys.path.append('$SCRIPT_DIR')
from proxy_manager import ProxyManager
manager = ProxyManager()
if manager.has_proxies():
    print('✅ Proxy manager loaded successfully')
    status = manager.get_status_report()
    print(f'   Total proxies: {status[\"total_proxies\"]}')
    if status['total_proxies'] > 0:
        print('🧪 Testing proxy functionality...')
        results = manager.test_all_proxies()
        working = sum(1 for r in results.values() if r)
        print(f'   Working proxies: {working}/{len(results)}')
        if working > 0:
            print('✅ Proxy setup complete!')
        else:
            print('❌ No working proxies found')
            sys.exit(1)
    else:
        print('❌ No proxies configured')
        sys.exit(1)
else:
    print('❌ No proxies found')
    sys.exit(1)
"; then
    echo "✅ Python proxy manager test passed"
else
    echo "❌ Python proxy manager test failed"
    exit 1
fi

# Update MCP environment
echo ""
echo "📝 Updating MCP environment configuration..."

MCP_ENV_FILE="$SCRIPT_DIR/.env.mcp"

if [ ! -f "$MCP_ENV_FILE" ]; then
    cp "$ENV_FILE" "$MCP_ENV_FILE"
    echo "✅ Created MCP environment file: $MCP_ENV_FILE"
else
    # Update existing MCP env file
    grep -v "^WEBSHARE_PROXY_" "$MCP_ENV_FILE" > "$MCP_ENV_FILE.tmp" || true
    echo "" >> "$MCP_ENV_FILE.tmp"
    grep "^WEBSHARE_PROXY_" "$ENV_FILE" >> "$MCP_ENV_FILE.tmp"
    mv "$MCP_ENV_FILE.tmp" "$MCP_ENV_FILE"
    echo "✅ Updated MCP environment file with proxy settings"
fi

echo ""
echo "🎉 Webshare proxy setup complete!"
echo ""
echo "📊 Configuration Summary:"
echo "   Proxy Type: Webshare Residential"
echo "   Endpoint: $WEBSHARE_PROXY_ENDPOINT"
echo "   Status: ✅ Working"
echo ""
echo "🔧 Next Steps:"
echo "1. Restart MCP server to use new proxy settings:"
echo "   ./deploy_mcp_server.sh"
echo ""
echo "2. Test YouTube transcript extraction:"
echo "   python3 mcp_youtube_client.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
echo ""
echo "3. Monitor proxy usage in logs"
echo ""
echo "💰 Webshare Proxy Costs (as of 2025):"
echo "   - Residential: ~$6/month for 20 proxies"
echo "   - Datacenter: ~$2.95/month for 10 proxies"
echo "   - Visit: https://www.webshare.io/pricing"