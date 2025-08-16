#!/bin/bash

# Railway 강제 배포 스크립트
# 서비스가 없으면 생성하고, 있으면 업데이트

set -e

echo "🚀 Railway 서비스 강제 배포"
echo "============================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 프로젝트 root로 이동
cd /Users/jihunkong/teaching_analize

# 1. 먼저 기본 배포 시도 (서비스 이름 없이)
echo -e "${YELLOW}방법 1: 기본 배포 시도${NC}"
railway up --detach 2>&1 | tee deploy_output.txt || {
    echo -e "${YELLOW}기본 배포 실패, 다른 방법 시도...${NC}"
}

# 2. 출력 분석
if grep -q "Multiple services found" deploy_output.txt; then
    echo -e "${YELLOW}여러 서비스 발견됨. 개별 배포 시도...${NC}"
    
    # Transcription 서비스 배포 시도
    echo -e "${BLUE}Transcription 서비스 배포 시도...${NC}"
    cd services/transcription
    
    # 여러 이름으로 시도
    for service_name in "transcription" "transcription-service" "web" "teaching-analize-transcription"; do
        echo "시도: $service_name"
        railway up --service "$service_name" --detach 2>&1 || {
            echo "실패: $service_name"
            continue
        }
        echo -e "${GREEN}✓ 성공: $service_name${NC}"
        break
    done
    
    # Analysis 서비스 배포 시도
    echo -e "${BLUE}Analysis 서비스 배포 시도...${NC}"
    cd ../analysis
    
    for service_name in "analysis" "analysis-service" "worker" "teaching-analize-analysis"; do
        echo "시도: $service_name"
        railway up --service "$service_name" --detach 2>&1 || {
            echo "실패: $service_name"
            continue
        }
        echo -e "${GREEN}✓ 성공: $service_name${NC}"
        break
    done
    
elif grep -q "No service linked" deploy_output.txt; then
    echo -e "${RED}서비스가 연결되지 않음${NC}"
    echo "Railway Dashboard에서 서비스를 먼저 생성해야 합니다."
    echo ""
    echo "Dashboard에서 할 일:"
    echo "1. + New → GitHub Repo 클릭"
    echo "2. Repository 선택: JihunKong/teaching_analize"
    echo "3. 서비스 생성 후 Settings에서:"
    echo "   - Transcription: Root Directory = services/transcription"
    echo "   - Analysis: Root Directory = services/analysis"
    
elif grep -q "Uploading" deploy_output.txt; then
    echo -e "${GREEN}✓ 배포가 시작되었습니다!${NC}"
fi

# 3. 현재 상태 확인
echo ""
echo -e "${YELLOW}현재 배포 상태:${NC}"
railway status

# 4. 로그 확인 시도
echo ""
echo -e "${YELLOW}서비스 로그 확인 시도:${NC}"

# 가능한 서비스 이름들로 로그 확인
for service in "transcription" "analysis" "web" "worker"; do
    echo -n "Checking $service... "
    railway logs --service "$service" 2>&1 | head -1 | grep -q "error" && echo "❌" || echo "✓"
done

echo ""
echo "========================================="
echo -e "${BLUE}다음 단계:${NC}"
echo ""
echo "1. Dashboard 확인:"
echo "   https://railway.app/project/379dfeea-b7f3-47cf-80c8-4d6d6b72329f"
echo ""
echo "2. 서비스가 없다면 Dashboard에서 생성:"
echo "   - + New → GitHub Repo"
echo "   - Root Directory 설정 필수!"
echo ""
echo "3. 서비스가 있다면 다시 실행:"
echo "   ./force_deploy.sh"
echo ""

# 클린업
rm -f deploy_output.txt