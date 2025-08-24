#!/usr/bin/env python3
"""
Rotating Proxy YouTube Extractor
다양한 User-Agent와 IP 변경으로 차단 우회
"""

import requests
import random
import time
import logging
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

class RotatingExtractor:
    """프록시 회전 및 User-Agent 변경을 통한 추출"""
    
    def __init__(self):
        self.user_agents = [
            # 모바일 브라우저
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/110.0',
            
            # 데스크톱 브라우저 (다양한 OS)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox 브라우저
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
            
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        ]
        
        # 무료 공개 프록시 (실제로는 더 안정적인 프록시 서비스 필요)
        self.free_proxies = [
            # 주의: 실제 환경에서는 안정적인 프록시 서비스 사용 권장
        ]
    
    def get_random_headers(self) -> dict:
        """랜덤 헤더 생성"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def extract_with_delay(self, video_id: str, max_attempts: int = 3) -> Optional[str]:
        """지연과 재시도를 통한 추출"""
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"Attempt {attempt + 1}/{max_attempts} for video {video_id}")
                
                # 랜덤 지연
                delay = random.uniform(1, 3)
                time.sleep(delay)
                
                # 세션 재생성 (다른 User-Agent)
                session = requests.Session()
                session.headers.update(self.get_random_headers())
                
                # YouTube Transcript API에 커스텀 세션 적용
                import youtube_transcript_api._api
                
                # 원본 _get_session_with_pool 백업
                original_get_session = youtube_transcript_api._api._get_session_with_pool
                
                # 커스텀 세션으로 교체
                def custom_get_session():
                    return session
                
                youtube_transcript_api._api._get_session_with_pool = custom_get_session
                
                try:
                    # 전사 시도
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
                    
                    if transcript_list:
                        full_text = ' '.join([item['text'] for item in transcript_list])
                        logger.info(f"✅ Success on attempt {attempt + 1}")
                        return full_text
                    
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    
                finally:
                    # 원본 함수 복원
                    youtube_transcript_api._api._get_session_with_pool = original_get_session
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} error: {e}")
            
            # 실패 시 더 긴 지연
            if attempt < max_attempts - 1:
                wait_time = random.uniform(3, 8)
                logger.info(f"Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
        
        logger.error(f"All {max_attempts} attempts failed for video {video_id}")
        return None


# 테스트
if __name__ == "__main__":
    extractor = RotatingExtractor()
    
    video_id = "-OLCt6WScEY"
    print(f"🔄 Testing rotating extraction for: {video_id}")
    
    result = extractor.extract_with_delay(video_id)
    
    if result:
        print(f"✅ Success! Length: {len(result)} characters")
        print(f"📝 Preview: {result[:200]}...")
    else:
        print("❌ All attempts failed")