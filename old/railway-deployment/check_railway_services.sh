#!/bin/bash

echo "🔍 Railway 서비스 상태 점검"
echo "=========================="
echo ""

# 프로젝트 정보
echo "📋 프로젝트 정보:"
railway status
echo ""

# 서비스별 확인 시도
echo "🔎 서비스 확인 중..."
echo ""

# 가능한 서비스 이름들 시도
services=(
    "transcription"
    "analysis"
    "transcription-service"
    "analysis-service"
    "teaching-analize"
    "web"
    "worker"
)

for service in "${services[@]}"; do
    echo "Checking service: $service"
    railway logs --service "$service" 2>&1 | head -5
    if [ $? -eq 0 ]; then
        echo "✅ Found service: $service"
        echo "---"
        
        # 환경변수 확인
        echo "Environment variables for $service:"
        railway variables --service "$service" 2>&1 | grep -E "(API_KEY|PORT|DATABASE_URL|REDIS_URL)" | head -10
        echo "---"
    fi
    echo ""
done

echo ""
echo "📝 Railway Dashboard에서 확인할 사항:"
echo "1. 각 서비스의 정확한 이름"
echo "2. 서비스별 Root Directory 설정:"
echo "   - Transcription: services/transcription"
echo "   - Analysis: services/analysis"
echo "3. 환경변수 설정 여부"
echo "4. Build/Deploy 상태"
echo ""
echo "🔗 Dashboard: https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f"