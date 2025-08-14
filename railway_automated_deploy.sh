#!/bin/bash

# Railway 자동화 배포 스크립트
# 대화형 프롬프트를 처리하여 서비스 생성 및 배포

set -e

echo "🚀 Railway 자동 배포 시작"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Transcription Service 배포
echo -e "${YELLOW}1. Transcription Service 배포 중...${NC}"
cd services/transcription

# railway up 명령에 서비스 이름 지정하여 새 서비스 생성
echo "transcription" | railway up --detach || {
    echo "Trying with service flag..."
    railway up --service transcription --detach
}

echo -e "${GREEN}✓ Transcription service 배포 시작${NC}"

# 2. Analysis Service 배포
echo -e "${YELLOW}2. Analysis Service 배포 중...${NC}"
cd ../analysis

# railway up 명령에 서비스 이름 지정하여 새 서비스 생성
echo "analysis" | railway up --detach || {
    echo "Trying with service flag..."
    railway up --service analysis --detach
}

echo -e "${GREEN}✓ Analysis service 배포 시작${NC}"

cd ../..

# 3. 환경변수 설정
echo ""
echo -e "${YELLOW}3. 환경변수 설정 중...${NC}"

# Transcription 서비스 환경변수
railway variables set PORT=8000 --service transcription
railway variables set PYTHONUNBUFFERED=1 --service transcription
railway variables set SERVICE_NAME=transcription --service transcription

# Analysis 서비스 환경변수  
railway variables set PORT=8001 --service analysis
railway variables set PYTHONUNBUFFERED=1 --service analysis
railway variables set SERVICE_NAME=analysis --service analysis

echo -e "${GREEN}✓ 환경변수 설정 완료${NC}"

# 4. 상태 확인
echo ""
echo -e "${YELLOW}4. 배포 상태 확인 중...${NC}"
railway status

echo ""
echo "========================================="
echo -e "${GREEN}배포가 시작되었습니다!${NC}"
echo "========================================="
echo ""
echo "확인 사항:"
echo "1. Railway Dashboard에서 빌드 상태 확인"
echo "   https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f"
echo ""
echo "2. 서비스 로그 확인:"
echo "   railway logs --service transcription"
echo "   railway logs --service analysis"
echo ""
echo "3. 환경변수 확인:"
echo "   railway variables --service transcription"
echo "   railway variables --service analysis"