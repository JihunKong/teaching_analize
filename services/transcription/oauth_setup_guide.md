# YouTube OAuth 2.0 설정 가이드

## 1. Google Cloud Console 설정

### A. 프로젝트 설정
1. https://console.cloud.google.com 접속
2. 기존 프로젝트 선택 또는 새 프로젝트 생성
3. "API 및 서비스" → "라이브러리" 이동
4. "YouTube Data API v3" 검색 후 활성화

### B. OAuth 2.0 사용자 인증 정보 생성
1. "API 및 서비스" → "사용자 인증 정보" 이동
2. "+ 사용자 인증 정보 만들기" → "OAuth 클라이언트 ID" 선택
3. 애플리케이션 유형: "웹 애플리케이션" 선택
4. 이름: "YouTube Transcript App" 입력
5. 승인된 리디렉션 URI 추가:
   - http://localhost:8000/auth/callback
   - http://localhost:8080/auth/callback

### C. OAuth 동의 화면 설정
1. "OAuth 동의 화면" 탭 이동
2. 사용자 유형: "외부" 선택 (테스트용)
3. 앱 정보 입력:
   - 앱 이름: "YouTube 수업 전사 시스템"
   - 사용자 지원 이메일: 본인 이메일
   - 개발자 연락처 정보: 본인 이메일
4. 범위 추가:
   - https://www.googleapis.com/auth/youtube.readonly
5. 테스트 사용자에 본인 이메일 추가

### D. credentials.json 다운로드
1. 생성된 OAuth 클라이언트 ID 옆의 다운로드 버튼 클릭
2. credentials.json 파일 다운로드
3. 프로젝트 폴더에 저장

## 2. 다음 단계
- OAuth 플로우 구현
- 토큰 저장 및 갱신 로직
- YouTube API 인증된 요청