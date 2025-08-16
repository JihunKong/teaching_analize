# 🔥 AWS Lightsail 방화벽 설정 가이드

## 1. AWS Lightsail 콘솔 접속

1. https://lightsail.aws.amazon.com 접속
2. AWS 계정으로 로그인
3. 생성된 인스턴스 클릭

## 2. 방화벽 설정 접근

1. 인스턴스 페이지에서 **"Networking"** 탭 클릭
2. **"Firewall"** 섹션으로 스크롤

## 3. 포트 규칙 추가

현재 필요한 포트들:

### 필수 포트 (AIBOA 서비스)
```
Application: Custom
Protocol: TCP
Port range: 8000
Source: 0.0.0.0/0
Description: AIBOA Transcription API
```

```
Application: Custom  
Protocol: TCP
Port range: 8001
Source: 0.0.0.0/0
Description: AIBOA Analysis API
```

```
Application: Custom
Protocol: TCP  
Port range: 3000
Source: 0.0.0.0/0
Description: AIBOA Frontend UI
```

### 선택적 포트 (웹 서버용)
```
Application: HTTP
Protocol: TCP
Port range: 80
Source: 0.0.0.0/0
```

```
Application: HTTPS
Protocol: TCP
Port range: 443  
Source: 0.0.0.0/0
```

## 4. 설정 확인

설정 후 다음 명령어로 확인:

```bash
# 외부에서 접근 테스트
curl http://3.38.107.23:8000/health
curl http://3.38.107.23:8001/health
curl http://3.38.107.23:3000
```

## 5. 문제 해결

### 여전히 접근이 안 되는 경우:
1. 5-10분 대기 (설정 반영 시간)
2. 브라우저 캐시 클리어
3. 다른 네트워크에서 테스트
4. AWS Support 문의

### 보안 고려사항:
- Production 환경에서는 특정 IP만 허용 권장
- API 키 인증이 추가 보안 레이어 제공
- 정기적인 접근 로그 모니터링 필요

## 6. 자동화 스크립트 (AWS CLI 사용 시)

```bash
# AWS CLI를 사용한 방화벽 규칙 자동 추가
aws lightsail put-instance-public-ports \
  --instance-name your-instance-name \
  --port-infos fromPort=8000,toPort=8000,protocol=tcp,cidrs="0.0.0.0/0"

aws lightsail put-instance-public-ports \
  --instance-name your-instance-name \
  --port-infos fromPort=8001,toPort=8001,protocol=tcp,cidrs="0.0.0.0/0"

aws lightsail put-instance-public-ports \
  --instance-name your-instance-name \
  --port-infos fromPort=3000,toPort=3000,protocol=tcp,cidrs="0.0.0.0/0"
```

---

## 🎯 설정 완료 후 확인 사항

✅ **Transcription API**: http://3.38.107.23:8000/docs  
✅ **Analysis API**: http://3.38.107.23:8001/docs  
✅ **Frontend UI**: http://3.38.107.23:3000  
✅ **YouTube 테스트**: 실제 YouTube URL로 전사 테스트  

**이 설정을 완료하면 AIBOA 플랫폼에 완전히 접근할 수 있습니다!** 🚀