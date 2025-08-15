#!/bin/bash

# AIBOA Frontend Local Test Script
# This script sets up and tests the frontend locally before Railway deployment

echo "==================================="
echo "AIBOA Frontend Local Test"
echo "==================================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
echo "Setting environment variables..."
export TRANSCRIPTION_API_URL="https://teachinganalize-production.up.railway.app"
export ANALYSIS_API_URL="https://amusedfriendship-production.up.railway.app"
export API_KEY="test-api-key"

# Display configuration
echo ""
echo "Configuration:"
echo "- Transcription API: $TRANSCRIPTION_API_URL"
echo "- Analysis API: $ANALYSIS_API_URL"
echo "- API Key: [CONFIGURED]"
echo ""

# Test API connectivity
echo "Testing API connectivity..."
curl -s -o /dev/null -w "Transcription Service: %{http_code}\n" $TRANSCRIPTION_API_URL/health
curl -s -o /dev/null -w "Analysis Service: %{http_code}\n" $ANALYSIS_API_URL/health

echo ""
echo "==================================="
echo "Starting Streamlit Application..."
echo "==================================="
echo ""
echo "Open your browser to: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run app.py --server.port=8501 --server.address=localhost