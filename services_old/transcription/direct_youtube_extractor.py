#!/usr/bin/env python3
"""
Direct YouTube Audio Stream Extractor
YouTube 내부 API를 직접 호출하여 오디오 스트림 URL 추출
"""

import re
import json
import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import unquote

logger = logging.getLogger(__name__)

class DirectYouTubeExtractor:
    """YouTube 내부 API를 사용한 직접 추출"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # 실제 브라우저처럼 보이는 헤더
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """YouTube URL에서 비디오 ID 추출"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        return None
    
    def get_video_page(self, video_id: str) -> Optional[str]:
        """YouTube 비디오 페이지 HTML 가져오기"""
        try:
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            response = self.session.get(video_url, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Failed to get video page: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting video page: {e}")
            return None
    
    def extract_player_response(self, html: str) -> Optional[Dict]:
        """HTML에서 ytInitialPlayerResponse 추출"""
        try:
            # ytInitialPlayerResponse 찾기
            pattern = r'var ytInitialPlayerResponse = ({.*?});'
            match = re.search(pattern, html)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            
            # 대안 패턴
            pattern = r'ytInitialPlayerResponse":\s*({.*?})(?:,")'
            match = re.search(pattern, html)
            
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
                
            logger.warning("Could not find ytInitialPlayerResponse")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting player response: {e}")
            return None
    
    def extract_captions_from_player_response(self, player_response: Dict) -> Optional[str]:
        """Player response에서 자막 정보 추출"""
        try:
            # 자막 트랙 찾기
            captions = player_response.get('captions', {})
            
            if not captions:
                logger.info("No captions found in player response")
                return None
            
            renderer = captions.get('playerCaptionsTracklistRenderer', {})
            caption_tracks = renderer.get('captionTracks', [])
            
            if not caption_tracks:
                logger.info("No caption tracks found")
                return None
            
            logger.info(f"Found {len(caption_tracks)} caption tracks")
            
            # 한국어 자막 우선 찾기
            target_track = None
            for track in caption_tracks:
                lang_code = track.get('languageCode', '').lower()
                if lang_code == 'ko':
                    target_track = track
                    logger.info("Found Korean caption track")
                    break
            
            # 한국어가 없으면 첫 번째 트랙 사용
            if not target_track and caption_tracks:
                target_track = caption_tracks[0]
                lang = target_track.get('languageCode', 'unknown')
                logger.info(f"Using first available track: {lang}")
            
            if not target_track:
                logger.warning("No usable caption track found")
                return None
            
            # 자막 URL 가져오기
            base_url = target_track.get('baseUrl')
            if not base_url:
                logger.error("No baseUrl in caption track")
                return None
            
            logger.info(f"Caption URL: {base_url[:100]}...")
            
            # 자막 다운로드
            return self.download_captions(base_url)
            
        except Exception as e:
            logger.error(f"Error extracting captions: {e}")
            return None
    
    def download_captions(self, caption_url: str) -> Optional[str]:
        """자막 URL에서 실제 자막 텍스트 다운로드"""
        try:
            response = self.session.get(caption_url, timeout=15)
            
            if response.status_code == 200:
                caption_xml = response.text
                
                # XML에서 텍스트 추출
                text_pattern = r'<text[^>]*>([^<]*)</text>'
                matches = re.findall(text_pattern, caption_xml)
                
                if matches:
                    # HTML 엔티티 디코딩
                    import html
                    decoded_texts = [html.unescape(text.strip()) for text in matches if text.strip()]
                    full_text = ' '.join(decoded_texts)
                    
                    logger.info(f"Extracted {len(full_text)} characters of captions")
                    return full_text
                else:
                    logger.warning("No text found in caption XML")
                    return None
            else:
                logger.error(f"Failed to download captions: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading captions: {e}")
            return None
    
    def extract_transcript(self, video_url: str) -> Optional[str]:
        """YouTube URL에서 전사 추출 (메인 메서드)"""
        video_id = self.extract_video_id(video_url)
        if not video_id:
            logger.error(f"Could not extract video ID from: {video_url}")
            return None
        
        logger.info(f"Extracting transcript for video: {video_id}")
        
        # 1. 비디오 페이지 가져오기
        html = self.get_video_page(video_id)
        if not html:
            return None
        
        # 2. Player response 추출
        player_response = self.extract_player_response(html)
        if not player_response:
            return None
        
        # 3. 자막 추출
        transcript = self.extract_captions_from_player_response(player_response)
        
        return transcript


# 테스트 함수
if __name__ == "__main__":
    extractor = DirectYouTubeExtractor()
    
    # 수업 비디오 테스트
    video_url = "https://www.youtube.com/watch?v=-OLCt6WScEY"
    
    print(f"🎬 Testing direct extraction for: {video_url}")
    
    transcript = extractor.extract_transcript(video_url)
    
    if transcript:
        print(f"✅ Success! Extracted {len(transcript)} characters")
        print(f"📝 Preview: {transcript[:200]}...")
    else:
        print("❌ Failed to extract transcript")