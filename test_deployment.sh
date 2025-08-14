#!/bin/bash

# Test Railway deployment status
echo "=== Railway Deployment Status Check ==="
echo ""

# Check project status
echo "1. Current Railway status:"
railway status

echo ""
echo "2. Checking service endpoints:"

# Test transcription service (teaching_analize)
echo "   - Teaching Analize Service (Port 8001):"
response=$(curl -s -o /dev/null -w "%{http_code}" https://teachinganalize-production.up.railway.app/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo "     ✅ Service is running"
else
    echo "     ❌ Service not responding (HTTP $response)"
fi

# Test analysis service (amused-friendship)  
echo "   - Amused Friendship Service (Port 8001):"
response=$(curl -s -o /dev/null -w "%{http_code}" https://amused-friendship-production.up.railway.app/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo "     ✅ Service is running"
else
    echo "     ❌ Service not responding (HTTP $response)"
fi

echo ""
echo "3. Testing root endpoints:"

# Test root domains
echo "   - https://teachinganalize-production.up.railway.app/"
curl -s https://teachinganalize-production.up.railway.app/ | head -n 5

echo ""
echo "   - https://amused-friendship-production.up.railway.app/"
curl -s https://amused-friendship-production.up.railway.app/ | head -n 5

echo ""
echo "=== End of status check ==="