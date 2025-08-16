# 🚀 AIBOA AWS Lightsail 배포 가이드

## 📋 배포 전 체크리스트

### 1. API 키 준비하기
아래 API 키들을 준비해주세요:

```bash
# OpenAI API Key (Whisper 전사용)
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_OPENAI_KEY

# Solar API Key (한국어 CBIL 분석용)
SOLAR_API_KEY=YOUR_ACTUAL_SOLAR_KEY

# YouTube API Key (새로 발급 필요)
YOUTUBE_API_KEY=YOUR_NEW_YOUTUBE_API_KEY

# Upstage API Key (선택사항)
UPSTAGE_API_KEY=YOUR_UPSTAGE_KEY
```

### 2. .env 파일 업데이트
```bash
# 1. .env 파일 편집
nano aws-lightsail/.env

# 2. 실제 API 키들로 교체
# YOUR_ACTUAL_* 부분을 실제 키로 변경하세요
```

## 🔧 배포 실행

### 자동 배포 (권장)
```bash
# 한 번에 모든 배포 과정 실행
./deploy-to-lightsail.sh
```

### 수동 배포 (문제 해결 시)

#### 1. 서버 접속 확인
```bash
ssh -i teaching_analize.pem ubuntu@3.38.107.23
```

#### 2. Docker 설치 (서버에서 실행)
```bash
# 시스템 업데이트
sudo apt update -y

# Docker 설치
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# 재로그인 (그룹 변경 적용)
exit
ssh -i teaching_analize.pem ubuntu@3.38.107.23
```

#### 3. 프로젝트 파일 전송 (로컬에서 실행)
```bash
# 파일 동기화
rsync -avz --exclude 'node_modules' --exclude '.git' \
  -e "ssh -i teaching_analize.pem" \
  ./ ubuntu@3.38.107.23:~/aiboa/

# .env 파일 전송
scp -i teaching_analize.pem aws-lightsail/.env \
  ubuntu@3.38.107.23:~/aiboa/aws-lightsail/
```

#### 4. 서비스 실행 (서버에서 실행)
```bash
cd ~/aiboa/aws-lightsail

# SSL 인증서 생성
cd nginx && ./generate-ssl-cert.sh && cd ..

# 서비스 시작
docker-compose up -d --build

# 상태 확인
docker-compose ps
docker-compose logs
```

## ✅ 배포 확인

### 서비스 접속 테스트
```bash
# 메인 애플리케이션
curl http://3.38.107.23

# Frontend (React)
curl http://3.38.107.23:3000

# Transcription API
curl http://3.38.107.23:8000/health

# Analysis API
curl http://3.38.107.23:8001/health
```

### 브라우저에서 확인
- **메인 애플리케이션**: http://3.38.107.23
- **React Frontend**: http://3.38.107.23:3000  
- **API 문서**: http://3.38.107.23:8000/docs

## 🔧 관리 명령어

### 서버 접속
```bash
ssh -i teaching_analize.pem ubuntu@3.38.107.23
cd ~/aiboa/aws-lightsail
```

### 서비스 관리
```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f
docker-compose logs -f frontend
docker-compose logs -f transcription
docker-compose logs -f analysis

# 서비스 재시작
docker-compose restart
docker-compose restart frontend

# 서비스 중지/시작
docker-compose down
docker-compose up -d

# 새 버전 배포
docker-compose down
docker-compose up -d --build
```

### 시스템 모니터링
```bash
# 디스크 사용량
df -h

# 메모리 사용량
free -h

# Docker 컨테이너 상태
docker stats

# 시스템 로그
sudo journalctl -f
```

## 🔍 문제 해결

### 1. 서비스 시작 실패
```bash
# 로그 확인
docker-compose logs [service-name]

# 컨테이너 상태 확인
docker-compose ps

# 포트 확인
sudo netstat -tulpn | grep LISTEN
```

### 2. API 키 오류
```bash
# .env 파일 확인
cat ~/aiboa/aws-lightsail/.env

# 환경 변수 확인 (컨테이너 내부)
docker-compose exec frontend env | grep API
docker-compose exec transcription env | grep API
```

### 3. YouTube 접근 테스트
```bash
# 서버에서 YouTube 접근 테스트
curl -I "https://www.youtube.com"

# Python으로 YouTube 접근 테스트
docker-compose exec transcription python3 -c "
import requests
response = requests.get('https://www.youtube.com')
print(f'Status: {response.status_code}')
"
```

### 4. 포트 문제
```bash
# 방화벽 확인 (Ubuntu)
sudo ufw status

# AWS Lightsail 보안 그룹에서 포트 열기:
# - HTTP: 80
# - HTTPS: 443  
# - Frontend: 3000
# - Transcription: 8000
# - Analysis: 8001
```

## 📊 성능 최적화

### 리소스 모니터링
```bash
# 실시간 리소스 사용량
htop

# Docker 컨테이너별 리소스 사용량
docker stats

# 디스크 I/O 모니터링  
iotop
```

### 로그 정리
```bash
# Docker 로그 정리
docker system prune -f

# 시스템 로그 정리
sudo journalctl --vacuum-time=7d
```

## 🔒 보안 강화

### 방화벽 설정
```bash
# UFW 방화벽 활성화
sudo ufw enable

# 필요한 포트만 열기
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp
```

### SSL 인증서 (Let's Encrypt)
```bash
# Certbot 설치
sudo apt install certbot

# 도메인이 있을 경우
sudo certbot certonly --standalone -d your-domain.com
```

## 📚 추가 리소스

- [Docker Compose 문서](https://docs.docker.com/compose/)
- [AWS Lightsail 가이드](https://lightsail.aws.amazon.com/ls/docs/)
- [Next.js 배포 가이드](https://nextjs.org/docs/deployment)

---

⭐ **팁**: 정기적으로 시스템을 업데이트하고 백업을 생성하세요!

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 이미지 업데이트
docker-compose pull && docker-compose up -d
```