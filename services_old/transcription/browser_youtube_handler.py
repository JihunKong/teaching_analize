#!/usr/bin/env python3
"""
Browser-based YouTube Handler
서버 환경에서 Selenium/Chrome을 통한 YouTube 스크립트 추출
동시 처리 지원 및 캐싱 시스템 포함
"""

import logging
import asyncio
import hashlib
import time
from typing import Optional, Dict, Tuple
from functools import lru_cache
from selenium_youtube_scraper import SeleniumYouTubeScraper

logger = logging.getLogger(__name__)

# 동시 실행 제한 (3명 동시 사용 가능)
MAX_CONCURRENT = 3
concurrency_semaphore = asyncio.Semaphore(MAX_CONCURRENT)

# 메모리 캐시 (TTL 1시간)
cache: Dict[str, Tuple[str, float]] = {}  # video_id: (transcript, timestamp)
CACHE_TTL = 3600  # 1시간

class BrowserYouTubeHandler:
    """브라우저 기반 YouTube 핸들러 - 동시 처리 지원"""
    
    def __init__(self):
        self.scraper = None
        logger.info(f"🚀 BrowserYouTubeHandler 초기화 - 최대 {MAX_CONCURRENT}명 동시 처리")
    
    def _get_video_id(self, video_url: str) -> Optional[str]:
        """비디오 ID 추출 및 캐시 키 생성"""
        return self.extract_video_id(video_url)
    
    def _check_cache(self, video_id: str) -> Optional[str]:
        """캐시에서 결과 확인"""
        if video_id in cache:
            transcript, timestamp = cache[video_id]
            if time.time() - timestamp < CACHE_TTL:
                logger.info(f"✨ 캐시에서 반환: {video_id}")
                return transcript
            else:
                # TTL 만료된 아이템 삭제
                del cache[video_id]
        return None
    
    def _store_cache(self, video_id: str, transcript: str):
        """결과를 캐시에 저장"""
        cache[video_id] = (transcript, time.time())
        logger.info(f"💾 캐시에 저장: {video_id} ({len(transcript)}자)")
    
    async def extract_transcript(self, video_url: str) -> Optional[str]:
        """YouTube URL에서 스크립트 추출 - 동시 처리 및 캐싱 지원"""
        video_id = self._get_video_id(video_url)
        if not video_id:
            logger.error("❌ 유효하지 않은 YouTube URL")
            return None
        
        # 1. 캐시 확인
        cached_result = self._check_cache(video_id)
        if cached_result:
            return cached_result
        
        # 2. 동시 실행 제한 적용
        async with concurrency_semaphore:
            logger.info(f"🎬 브라우저 추출 시작: {video_url} (동시 실행 {MAX_CONCURRENT - concurrency_semaphore._value + 1}/{MAX_CONCURRENT})")
            
            try:
                # 각 요청마다 독립적인 WebDriver 인스턴스
                with SeleniumYouTubeScraper(headless=True) as scraper:
                    transcript = scraper.scrape_youtube_transcript(video_url)
                    
                    if transcript:
                        logger.info(f"✅ 추출 성공: {len(transcript)}자")
                        # 3. 결과 캐싱
                        self._store_cache(video_id, transcript)
                        return transcript
                    else:
                        logger.error("❌ 전사 추출 실패")
                        return None
                        
            except Exception as e:
                logger.error(f"❌ 브라우저 추출 오류: {e}")
                return None
            finally:
                logger.info(f"📊 동시 실행 종료 - 대기 중: {concurrency_semaphore._value}/{MAX_CONCURRENT}")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """캐시 통계 반환"""
        current_time = time.time()
        valid_items = sum(1 for _, (_, timestamp) in cache.items() 
                         if current_time - timestamp < CACHE_TTL)
        
        return {
            "total_cached": len(cache),
            "valid_cached": valid_items,
            "concurrent_limit": MAX_CONCURRENT,
            "current_running": MAX_CONCURRENT - concurrency_semaphore._value
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """YouTube URL에서 비디오 ID 추출"""
        import re
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None


# 전역 핸들러 인스턴스
browser_handler = BrowserYouTubeHandler()


async def extract_youtube_transcript_browser(video_url: str) -> Optional[str]:
    """YouTube 스크립트 추출 편의 함수 (브라우저 방식)"""
    return await browser_handler.extract_transcript(video_url)


def get_handler_stats() -> Dict[str, int]:
    """핸들러 통계 조회"""
    return browser_handler.get_cache_stats()


# 테스트
if __name__ == "__main__":
    async def test_concurrent_handler():
        """동시 처리 테스트"""
        handler = BrowserYouTubeHandler()
        video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
        
        print(f"🎬 Testing concurrent browser handler for: {video_url}")
        
        # 3개의 동시 요청 테스트
        tasks = []
        for i in range(3):
            task = asyncio.create_task(handler.extract_transcript(video_url))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        for i, transcript in enumerate(results):
            if transcript:
                print(f"✅ Task {i+1} Success! Extracted {len(transcript)} characters")
            else:
                print(f"❌ Task {i+1} Failed to extract transcript")
        
        # 캐시 통계 출력
        stats = handler.get_cache_stats()
        print(f"📊 Cache Stats: {stats}")
    
    asyncio.run(test_concurrent_handler())