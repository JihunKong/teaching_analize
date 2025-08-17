#!/usr/bin/env python3
"""
YouTube OAuth 2.0 Authentication for Transcript Access
"""

import os
import json
import logging
import webbrowser
from typing import Optional, Dict, Any
from urllib.parse import urlencode, parse_qs, urlparse
import requests
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class YouTubeOAuth:
    """YouTube OAuth 2.0 authentication handler"""
    
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = credentials_file
        self.token_file = "youtube_token.json"
        
        # OAuth endpoints
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        
        # YouTube API
        self.api_base = "https://www.googleapis.com/youtube/v3"
        
        # Load client credentials
        self.client_config = self.load_credentials()
        
    def load_credentials(self) -> Dict[str, Any]:
        """Load OAuth client credentials"""
        try:
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)
                
            # Handle both formats
            if 'web' in creds:
                return creds['web']
            elif 'installed' in creds:
                return creds['installed']
            else:
                return creds
                
        except FileNotFoundError:
            logger.error(f"Credentials file not found: {self.credentials_file}")
            logger.info("Please download credentials.json from Google Cloud Console")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid credentials file: {e}")
            return {}
    
    def get_auth_url(self) -> str:
        """Generate OAuth authorization URL"""
        if not self.client_config:
            raise ValueError("No client credentials loaded")
        
        params = {
            'client_id': self.client_config['client_id'],
            'response_type': 'code',
            'scope': 'https://www.googleapis.com/auth/youtube.readonly',
            'redirect_uri': self.client_config['redirect_uris'][0],
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_data = {
            'client_id': self.client_config['client_id'],
            'client_secret': self.client_config['client_secret'],
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.client_config['redirect_uris'][0]
        }
        
        response = requests.post(self.token_url, data=token_data)
        
        if response.status_code == 200:
            token_info = response.json()
            
            # Add expiry time
            if 'expires_in' in token_info:
                expires_at = datetime.now() + timedelta(seconds=token_info['expires_in'])
                token_info['expires_at'] = expires_at.isoformat()
            
            # Save token
            self.save_token(token_info)
            return token_info
        else:
            logger.error(f"Token exchange failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return {}
    
    def save_token(self, token_info: Dict[str, Any]) -> None:
        """Save token to file"""
        with open(self.token_file, 'w') as f:
            json.dump(token_info, f, indent=2)
        logger.info(f"Token saved to {self.token_file}")
    
    def load_token(self) -> Optional[Dict[str, Any]]:
        """Load saved token"""
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token"""
        refresh_data = {
            'client_id': self.client_config['client_id'],
            'client_secret': self.client_config['client_secret'],
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(self.token_url, data=refresh_data)
        
        if response.status_code == 200:
            new_token = response.json()
            
            # Preserve refresh token if not provided
            if 'refresh_token' not in new_token:
                new_token['refresh_token'] = refresh_token
            
            # Add expiry time
            if 'expires_in' in new_token:
                expires_at = datetime.now() + timedelta(seconds=new_token['expires_in'])
                new_token['expires_at'] = expires_at.isoformat()
            
            self.save_token(new_token)
            return new_token
        else:
            logger.error(f"Token refresh failed: {response.status_code}")
            return None
    
    def get_valid_token(self) -> Optional[str]:
        """Get a valid access token (refresh if needed)"""
        token_info = self.load_token()
        
        if not token_info:
            logger.warning("No saved token found. Authorization needed.")
            return None
        
        # Check if token is expired
        if 'expires_at' in token_info:
            expires_at = datetime.fromisoformat(token_info['expires_at'])
            if datetime.now() >= expires_at - timedelta(minutes=5):  # 5 min buffer
                logger.info("Token expired, refreshing...")
                
                if 'refresh_token' in token_info:
                    new_token = self.refresh_token(token_info['refresh_token'])
                    if new_token:
                        return new_token['access_token']
                
                logger.error("Failed to refresh token")
                return None
        
        return token_info.get('access_token')
    
    def authorize_interactive(self) -> bool:
        """Interactive authorization flow"""
        if not self.client_config:
            logger.error("No client credentials available")
            return False
        
        # Generate auth URL
        auth_url = self.get_auth_url()
        
        print("🔐 YouTube OAuth 인증이 필요합니다.")
        print(f"📋 다음 URL에서 인증을 완료하세요:")
        print(f"🌐 {auth_url}")
        print()
        
        # Try to open browser automatically
        try:
            webbrowser.open(auth_url)
            print("✅ 브라우저가 자동으로 열렸습니다.")
        except:
            print("⚠️ 브라우저를 수동으로 열어 위 URL을 방문하세요.")
        
        print()
        print("📝 인증 완료 후 리디렉션 URL에서 'code=' 파라미터의 값을 복사하세요.")
        print("예: http://localhost:8000/auth/callback?code=4/XXXXXXXXX")
        print()
        
        # Get authorization code from user
        auth_code = input("🔑 Authorization code를 입력하세요: ").strip()
        
        if not auth_code:
            logger.error("Authorization code not provided")
            return False
        
        # Exchange for token
        token_info = self.exchange_code_for_token(auth_code)
        
        if token_info and 'access_token' in token_info:
            print("✅ 인증 성공! 토큰이 저장되었습니다.")
            return True
        else:
            print("❌ 인증 실패")
            return False
    
    def get_video_captions(self, video_id: str) -> Optional[str]:
        """Get video captions using authenticated API"""
        access_token = self.get_valid_token()
        
        if not access_token:
            logger.error("No valid access token available")
            return None
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        try:
            # First, list available captions
            captions_url = f"{self.api_base}/captions"
            params = {
                'part': 'snippet',
                'videoId': video_id
            }
            
            response = requests.get(captions_url, headers=headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to list captions: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            captions_data = response.json()
            caption_tracks = captions_data.get('items', [])
            
            if not caption_tracks:
                logger.warning(f"No captions found for video {video_id}")
                return None
            
            logger.info(f"Found {len(caption_tracks)} caption tracks")
            
            # Find Korean or best available caption
            target_caption = None
            
            for caption in caption_tracks:
                snippet = caption['snippet']
                lang = snippet['language']
                logger.info(f"Available caption: {lang} ({'auto' if snippet.get('trackKind') == 'asr' else 'manual'})")
                
                if lang == 'ko':
                    target_caption = caption
                    break
            
            # Fallback to first available
            if not target_caption:
                target_caption = caption_tracks[0]
                logger.info(f"Using first available caption: {target_caption['snippet']['language']}")
            
            # Download caption content
            caption_id = target_caption['id']
            download_url = f"{self.api_base}/captions/{caption_id}"
            download_params = {'tfmt': 'srt'}
            
            download_response = requests.get(
                download_url, 
                headers=headers, 
                params=download_params
            )
            
            if download_response.status_code == 200:
                srt_content = download_response.text
                
                # Convert SRT to plain text
                text = self.srt_to_text(srt_content)
                logger.info(f"Successfully downloaded caption: {len(text)} characters")
                return text
            else:
                logger.error(f"Failed to download caption: {download_response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting video captions: {e}")
            return None
    
    def srt_to_text(self, srt_content: str) -> str:
        """Convert SRT subtitle format to plain text"""
        lines = srt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip sequence numbers, timestamps, and empty lines
            if (line.isdigit() or 
                '-->' in line or 
                not line):
                continue
            
            # Remove HTML tags and formatting
            import re
            line = re.sub(r'<[^>]+>', '', line)
            line = re.sub(r'\[.*?\]', '', line)
            
            if line:
                text_lines.append(line)
        
        return ' '.join(text_lines)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        import re
        
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def get_transcript_from_url(self, video_url: str) -> Optional[str]:
        """Get transcript from YouTube URL"""
        video_id = self.extract_video_id(video_url)
        
        if not video_id:
            logger.error(f"Could not extract video ID from: {video_url}")
            return None
        
        return self.get_video_captions(video_id)

# Test/Demo function
if __name__ == "__main__":
    oauth = YouTubeOAuth()
    
    print("🎬 YouTube OAuth 전사 시스템")
    print("=" * 40)
    
    # Check if we have valid credentials
    if not oauth.client_config:
        print("❌ credentials.json 파일이 필요합니다.")
        print("📋 Google Cloud Console에서 OAuth 클라이언트 ID를 생성하고")
        print("   credentials.json 파일을 다운로드하세요.")
        exit(1)
    
    # Check if we have a valid token
    token = oauth.get_valid_token()
    
    if not token:
        print("🔐 OAuth 인증이 필요합니다.")
        success = oauth.authorize_interactive()
        
        if not success:
            print("❌ 인증 실패")
            exit(1)
    else:
        print("✅ 유효한 토큰이 있습니다.")
    
    # Test with the teaching video
    video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
    print(f"📺 테스트 비디오: {video_url}")
    
    transcript = oauth.get_transcript_from_url(video_url)
    
    if transcript:
        print(f"✅ 전사 성공! 길이: {len(transcript)} 문자")
        print(f"📝 내용 미리보기: {transcript[:200]}...")
    else:
        print("❌ 전사 실패")