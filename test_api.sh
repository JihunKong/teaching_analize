#!/bin/bash

# AIBOA API Test Script
# Tests all endpoints of the integrated service

API_URL="https://teachinganalize-production.up.railway.app"
API_KEY="test-api-key"

echo "======================================"
echo "AIBOA API Test Suite"
echo "======================================"
echo ""

# Test root endpoint
echo "1. Testing root endpoint..."
curl -s "${API_URL}/" | python3 -m json.tool | head -10
echo ""

# Test health endpoint
echo "2. Testing health endpoint..."
curl -s "${API_URL}/health" | python3 -m json.tool
echo ""

# Test API status
echo "3. Testing API status..."
curl -s "${API_URL}/api/status" | python3 -m json.tool
echo ""

# Test transcription YouTube endpoint
echo "4. Testing YouTube transcription..."
curl -X POST "${API_URL}/api/transcribe/youtube" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://youtube.com/watch?v=test", "language": "ko"}' \
  -s | python3 -m json.tool
echo ""

# Test analysis text endpoint
echo "5. Testing text analysis..."
curl -X POST "${API_URL}/api/analyze/text" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"text": "오늘 배운 내용을 설명해보세요. 왜 이것이 중요한가요? 다른 개념과 어떻게 연결되나요?"}' \
  -s | python3 -m json.tool
echo ""

# Test statistics endpoint
echo "6. Testing statistics..."
curl -X GET "${API_URL}/api/analyze/statistics" \
  -H "X-API-Key: ${API_KEY}" \
  -s | python3 -m json.tool
echo ""

echo "======================================"
echo "Test Complete!"
echo "======================================" 