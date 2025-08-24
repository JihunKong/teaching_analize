#!/usr/bin/env python3
"""
Web-based OAuth handler for the MVP
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from youtube_oauth import YouTubeOAuth
import logging
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

class OAuthWebHandler:
    """Handle OAuth flow in web interface"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.oauth = YouTubeOAuth()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup OAuth routes"""
        
        @self.app.get("/auth/login", response_class=HTMLResponse)
        async def login():
            """Start OAuth flow"""
            if not self.oauth.client_config:
                return HTMLResponse("""
                <html><body>
                    <h2>❌ OAuth 설정 오류</h2>
                    <p>credentials.json 파일이 필요합니다.</p>
                    <p><a href="/">메인으로 돌아가기</a></p>
                </body></html>
                """)
            
            # Check if already authenticated
            token = self.oauth.get_valid_token()
            if token:
                return HTMLResponse("""
                <html><body>
                    <h2>✅ 이미 인증되었습니다</h2>
                    <p><a href="/">메인으로 돌아가기</a></p>
                    <script>
                        setTimeout(() => window.location.href = '/', 2000);
                    </script>
                </body></html>
                """)
            
            # Generate auth URL
            auth_url = self.oauth.get_auth_url()
            
            return HTMLResponse(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>YouTube OAuth 인증</title>
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                        max-width: 600px; 
                        margin: 50px auto; 
                        padding: 20px;
                        text-align: center;
                    }}
                    .btn {{ 
                        background: #1976d2; 
                        color: white; 
                        padding: 15px 30px; 
                        text-decoration: none; 
                        border-radius: 8px;
                        display: inline-block;
                        margin: 20px;
                        font-size: 16px;
                    }}
                    .btn:hover {{ background: #1565c0; }}
                </style>
            </head>
            <body>
                <h1>🔐 YouTube OAuth 인증</h1>
                <p>YouTube 전사 기능을 사용하려면 Google 계정 인증이 필요합니다.</p>
                
                <a href="{auth_url}" class="btn" target="_blank">
                    🚀 Google 계정으로 인증하기
                </a>
                
                <div style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 8px;">
                    <h3>📋 인증 절차</h3>
                    <ol style="text-align: left;">
                        <li>위 버튼을 클릭하여 Google 인증 페이지로 이동</li>
                        <li>본인의 Google 계정으로 로그인</li>
                        <li>YouTube 접근 권한 허용</li>
                        <li>자동으로 이 페이지로 돌아옵니다</li>
                    </ol>
                </div>
                
                <p style="margin-top: 20px;">
                    <a href="/">← 메인으로 돌아가기</a>
                </p>
            </body>
            </html>
            """)
        
        @self.app.get("/auth/callback")
        async def oauth_callback(request: Request):
            """Handle OAuth callback"""
            query_params = dict(request.query_params)
            
            if 'error' in query_params:
                error = query_params['error']
                return HTMLResponse(f"""
                <html><body>
                    <h2>❌ 인증 오류</h2>
                    <p>오류: {error}</p>
                    <p><a href="/auth/login">다시 시도</a></p>
                </body></html>
                """)
            
            if 'code' not in query_params:
                return HTMLResponse("""
                <html><body>
                    <h2>❌ 인증 코드 없음</h2>
                    <p><a href="/auth/login">다시 시도</a></p>
                </body></html>
                """)
            
            auth_code = query_params['code']
            
            try:
                # Exchange code for token
                token_info = self.oauth.exchange_code_for_token(auth_code)
                
                if token_info and 'access_token' in token_info:
                    return HTMLResponse("""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>인증 완료</title>
                        <style>
                            body { 
                                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                                max-width: 600px; 
                                margin: 50px auto; 
                                padding: 20px;
                                text-align: center;
                            }
                        </style>
                    </head>
                    <body>
                        <h1>✅ 인증 완료!</h1>
                        <p>YouTube 전사 기능을 사용할 수 있습니다.</p>
                        <p>2초 후 자동으로 메인 페이지로 이동합니다...</p>
                        
                        <script>
                            setTimeout(() => {
                                window.location.href = '/';
                            }, 2000);
                        </script>
                    </body>
                    </html>
                    """)
                else:
                    return HTMLResponse("""
                    <html><body>
                        <h2>❌ 토큰 교환 실패</h2>
                        <p><a href="/auth/login">다시 시도</a></p>
                    </body></html>
                    """)
                    
            except Exception as e:
                logger.error(f"OAuth callback error: {e}")
                return HTMLResponse(f"""
                <html><body>
                    <h2>❌ 인증 처리 오류</h2>
                    <p>오류: {str(e)}</p>
                    <p><a href="/auth/login">다시 시도</a></p>
                </body></html>
                """)
        
        @self.app.get("/auth/status")
        async def auth_status():
            """Check authentication status"""
            token = self.oauth.get_valid_token()
            
            return {
                "authenticated": bool(token),
                "has_credentials": bool(self.oauth.client_config),
                "message": "인증됨" if token else "인증 필요"
            }
        
        @self.app.post("/auth/logout")
        async def logout():
            """Logout - remove saved token"""
            import os
            
            try:
                if os.path.exists(self.oauth.token_file):
                    os.remove(self.oauth.token_file)
                return {"success": True, "message": "로그아웃 완료"}
            except Exception as e:
                return {"success": False, "error": str(e)}