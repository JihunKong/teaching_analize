#!/bin/bash

# AIBOA API Keys Setup Script
# This script helps you configure API keys interactively

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔑 AIBOA API Keys Setup${NC}"
echo -e "${BLUE}═════════════════════════${NC}"
echo ""

# Check if .env file exists
ENV_FILE="aws-lightsail/.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo -e "${RED}❌ Error: $ENV_FILE not found${NC}"
    echo -e "${YELLOW}Please run the deployment script first to generate the template.${NC}"
    exit 1
fi

echo -e "${YELLOW}📝 This script will help you update your API keys in $ENV_FILE${NC}"
echo -e "${YELLOW}Press Enter to keep current value, or type new value to update${NC}"
echo ""

# Function to update env var
update_env_var() {
    local var_name=$1
    local description=$2
    local current_value=$(grep "^$var_name=" "$ENV_FILE" | cut -d '=' -f2-)
    
    echo -e "${BLUE}$description${NC}"
    echo -e "${YELLOW}Current value: ${current_value}${NC}"
    echo -n "New value (press Enter to keep current): "
    read new_value
    
    if [[ -n "$new_value" ]]; then
        # Escape special characters for sed
        escaped_value=$(printf '%s\n' "$new_value" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -i.bak "s|^$var_name=.*|$var_name=$new_value|" "$ENV_FILE"
        echo -e "${GREEN}✅ Updated $var_name${NC}"
    else
        echo -e "${BLUE}⏭️  Keeping current value${NC}"
    fi
    echo ""
}

# Update each API key
update_env_var "OPENAI_API_KEY" "🤖 OpenAI API Key (for Whisper transcription)"
update_env_var "SOLAR_API_KEY" "☀️ Solar API Key (for Korean CBIL analysis)"
update_env_var "YOUTUBE_API_KEY" "📺 YouTube API Key (for YouTube transcription)"
update_env_var "UPSTAGE_API_KEY" "🚀 Upstage API Key (optional, for additional analysis)"

# Update database password
echo -e "${BLUE}🔒 Database Configuration${NC}"
update_env_var "POSTGRES_PASSWORD" "Database Password (PostgreSQL)"

echo -e "${GREEN}✅ API keys setup completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Summary of configured keys:${NC}"
grep -E "^(OPENAI_API_KEY|SOLAR_API_KEY|YOUTUBE_API_KEY|UPSTAGE_API_KEY|POSTGRES_PASSWORD)=" "$ENV_FILE" | while read line; do
    key=$(echo "$line" | cut -d '=' -f1)
    value=$(echo "$line" | cut -d '=' -f2-)
    
    if [[ "$value" == *"YOUR_"* ]] || [[ "$value" == *"your_"* ]]; then
        echo -e "${RED}⚠️  $key: Not configured${NC}"
    else
        # Show first 10 chars and last 4 chars
        masked_value=$(echo "$value" | sed 's/\(.\{10\}\).*\(.\{4\}\)/\1...\2/')
        echo -e "${GREEN}✅ $key: $masked_value${NC}"
    fi
done

echo ""
echo -e "${BLUE}🚀 Next steps:${NC}"
echo -e "${YELLOW}1. Review the configuration in $ENV_FILE${NC}"
echo -e "${YELLOW}2. Run: ./deploy-to-lightsail.sh${NC}"
echo -e "${YELLOW}3. Test your deployment at: http://3.38.107.23${NC}"
echo ""
echo -e "${GREEN}Happy analyzing! 🎓✨${NC}"