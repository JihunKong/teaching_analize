#!/usr/bin/env python3
"""
YouTube Debug Tool for Railway Environment
교육 목적으로 Railway에서 YouTube 접근 상태를 진단합니다.
"""

import sys
import os
import subprocess
import requests

def test_basic_connectivity():
    """기본 인터넷 연결 테스트"""
    print("🌐 Testing basic internet connectivity...")
    try:
        response = requests.get("https://www.google.com", timeout=10)
        print(f"✅ Internet connectivity: OK (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ Internet connectivity: FAILED - {e}")
        return False

def test_youtube_access():
    """YouTube 도메인 접근 테스트"""
    print("📺 Testing YouTube domain access...")
    try:
        response = requests.get("https://www.youtube.com", timeout=10)
        print(f"✅ YouTube access: OK (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ YouTube access: FAILED - {e}")
        return False

def test_ytdlp_installation():
    """yt-dlp 설치 상태 확인"""
    print("📦 Testing yt-dlp installation...")
    try:
        import yt_dlp
        print(f"✅ yt-dlp imported successfully: {yt_dlp.version.__version__}")
        return True
    except ImportError as e:
        print(f"❌ yt-dlp import failed: {e}")
        return False

def test_youtube_video_info(url):
    """YouTube 비디오 정보 추출 테스트"""
    print(f"🎥 Testing video info extraction for: {url}")
    try:
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        print(f"✅ Video info extracted:")
        print(f"   - Title: {info.get('title', 'Unknown')}")
        print(f"   - Duration: {info.get('duration', 0)} seconds")
        print(f"   - View count: {info.get('view_count', 0)}")
        
        # 자막 정보 확인
        subtitles = info.get('subtitles', {})
        auto_captions = info.get('automatic_captions', {})
        
        print(f"   - Available subtitles: {list(subtitles.keys())}")
        print(f"   - Auto-captions: {list(auto_captions.keys())}")
        
        return True, info
        
    except Exception as e:
        print(f"❌ Video info extraction failed: {str(e)}")
        return False, str(e)

def test_subtitle_extraction(url, language="ko"):
    """자막 추출 테스트"""
    print(f"📝 Testing subtitle extraction for language: {language}")
    try:
        import yt_dlp
        
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en'],
            'skip_download': True,
            'quiet': False,  # 디버그를 위해 출력 활성화
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        # 자막 데이터 확인
        subtitles = info.get('subtitles', {})
        auto_captions = info.get('automatic_captions', {})
        all_subs = {**subtitles, **auto_captions}
        
        if not all_subs:
            print("❌ No subtitles available")
            return False, "No subtitles"
            
        # 원하는 언어의 자막 다운로드 시도
        for lang in [language, 'en', 'ko'] + list(all_subs.keys()):
            if lang in subtitles:
                subtitle_data = subtitles[lang]
                is_auto = False
                break
            elif lang in auto_captions:
                subtitle_data = auto_captions[lang]
                is_auto = True
                break
        else:
            print("❌ No suitable subtitle language found")
            return False, "No suitable language"
            
        # 자막 콘텐츠 다운로드
        for sub in subtitle_data:
            if sub.get('ext') in ['vtt', 'srv3', 'srt', 'json3']:
                try:
                    response = requests.get(sub['url'], timeout=10)
                    if response.status_code == 200:
                        content = response.text[:500]  # 처음 500자만
                        print(f"✅ Subtitle downloaded:")
                        print(f"   - Language: {lang}")
                        print(f"   - Auto-generated: {is_auto}")
                        print(f"   - Format: {sub.get('ext', 'unknown')}")
                        print(f"   - Content preview: {content[:100]}...")
                        return True, content
                except Exception as e:
                    print(f"❌ Subtitle download failed: {e}")
                    continue
                    
        print("❌ Failed to download subtitle content")
        return False, "Download failed"
        
    except Exception as e:
        print(f"❌ Subtitle extraction failed: {str(e)}")
        return False, str(e)

def get_system_info():
    """시스템 정보 수집"""
    print("💻 System Information:")
    print(f"   - Python version: {sys.version}")
    print(f"   - Platform: {sys.platform}")
    print(f"   - Environment variables:")
    
    relevant_vars = ['PORT', 'RAILWAY_ENVIRONMENT', 'PYTHONPATH']
    for var in relevant_vars:
        value = os.environ.get(var, 'Not set')
        print(f"     - {var}: {value}")

def main():
    """메인 진단 함수"""
    test_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
    
    print("🔍 Railway YouTube 접근 진단 시작...")
    print("=" * 50)
    
    # 시스템 정보
    get_system_info()
    print()
    
    # 기본 연결 테스트
    if not test_basic_connectivity():
        print("❌ 기본 인터넷 연결 실패 - 진단 중단")
        return
    print()
    
    # YouTube 접근 테스트
    if not test_youtube_access():
        print("❌ YouTube 접근 실패 - 도메인 차단 가능성")
    print()
    
    # yt-dlp 설치 확인
    if not test_ytdlp_installation():
        print("❌ yt-dlp 설치 실패 - requirements.txt 확인 필요")
        return
    print()
    
    # 비디오 정보 추출
    success, result = test_youtube_video_info(test_url)
    if not success:
        print(f"❌ 비디오 정보 추출 실패: {result}")
        print("이것이 Railway에서 YouTube 자막 추출이 실패하는 주요 원인일 수 있습니다.")
        return
    print()
    
    # 자막 추출 테스트
    success, result = test_subtitle_extraction(test_url, "ko")
    if success:
        print("✅ 모든 테스트 통과! YouTube 자막 추출이 정상 작동해야 합니다.")
    else:
        print(f"❌ 자막 추출 실패: {result}")
        print("이것이 Railway에서 자막 추출이 실패하는 원인입니다.")
    
    print("=" * 50)
    print("🔍 진단 완료")

if __name__ == "__main__":
    main()