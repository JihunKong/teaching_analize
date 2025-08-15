"""
Enhanced yt-dlp subtitle extraction with multiple fallback methods
"""
import os
import re
import logging
import tempfile
import json
from typing import Optional, Dict, List
import yt_dlp

logger = logging.getLogger(__name__)


def normalize_youtube_url(url: str) -> str:
    """
    Normalize various YouTube URL formats
    Handles URLs copied from right-click menu
    
    Args:
        url: YouTube URL in any format
        
    Returns:
        Normalized YouTube URL
    """
    # Clean up URL - remove any extra parameters or tracking
    url = url.strip()
    
    # Handle various YouTube URL formats
    # Right-click copied URLs might have extra parameters
    if 'youtube.com' in url or 'youtu.be' in url:
        # Extract video ID
        video_id_patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
            r'(?:youtube\.com\/watch.*[?&]v=)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in video_id_patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                # Return clean YouTube URL
                return f"https://www.youtube.com/watch?v={video_id}"
    
    return url


def extract_subtitles_only(url: str, language: str = "ko") -> Optional[Dict]:
    """
    Extract only subtitles from YouTube video using yt-dlp
    Uses various methods to bypass restrictions
    
    Args:
        url: YouTube video URL (can be from right-click copy)
        language: Preferred subtitle language
        
    Returns:
        Dictionary with subtitle text and metadata
    """
    # Normalize URL first
    url = normalize_youtube_url(url)
    logger.info(f"Extracting subtitles from: {url}")
    
    # Create temp directory for subtitle files
    temp_dir = tempfile.mkdtemp()
    
    # Try different yt-dlp configurations
    configs = [
        {
            # Config 1: Basic subtitle extraction
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language, 'en', 'ko', 'auto'],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        },
        {
            # Config 2: With user agent and IPv4
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['all'],  # Get all available
            'force_ipv4': True,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'quiet': False,
            'extract_flat': False,
        },
        {
            # Config 3: With cookies and referer
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [language],
            'force_ipv4': True,
            'no_check_certificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
            'referer': 'https://www.youtube.com/',
            'cookiefile': '/tmp/yt_cookies.txt',
            'quiet': False,
        },
        {
            # Config 4: Minimal options
            'skip_download': True,
            'writesubtitles': True,
            'quiet': False,
            'force_ipv4': True,
        }
    ]
    
    for i, config in enumerate(configs):
        try:
            logger.info(f"Trying config {i+1}/{len(configs)}")
            
            # Add output template for subtitle files
            config['outtmpl'] = os.path.join(temp_dir, '%(title)s.%(ext)s')
            config['subtitlesformat'] = 'vtt/srt/best'
            
            with yt_dlp.YoutubeDL(config) as ydl:
                # Extract info without downloading video
                info = ydl.extract_info(url, download=False)
                
                # Check for available subtitles
                subtitles = info.get('subtitles', {})
                auto_captions = info.get('automatic_captions', {})
                
                # Combine all available subtitles
                all_subs = {**subtitles, **auto_captions}
                
                if not all_subs:
                    logger.warning(f"No subtitles found with config {i+1}")
                    continue
                
                # Find best subtitle match
                subtitle_url = None
                subtitle_lang = None
                is_auto = False
                
                # Priority: requested language > English > Korean > any
                for lang in [language, 'en', 'ko'] + list(all_subs.keys()):
                    if lang in subtitles:
                        subtitle_data = subtitles[lang]
                        subtitle_lang = lang
                        is_auto = False
                        break
                    elif lang in auto_captions:
                        subtitle_data = auto_captions[lang]
                        subtitle_lang = lang
                        is_auto = True
                        break
                
                if subtitle_lang and subtitle_data:
                    # Download subtitle content
                    import requests
                    
                    # Find best format
                    for sub in subtitle_data:
                        if sub.get('ext') in ['vtt', 'srv3', 'srt', 'json3']:
                            try:
                                response = requests.get(sub['url'], timeout=10)
                                if response.status_code == 200:
                                    subtitle_text = parse_subtitle_content(
                                        response.text, 
                                        sub.get('ext', 'vtt')
                                    )
                                    
                                    # Clean up temp directory
                                    import shutil
                                    shutil.rmtree(temp_dir, ignore_errors=True)
                                    
                                    return {
                                        'text': subtitle_text,
                                        'language': subtitle_lang,
                                        'is_auto_generated': is_auto,
                                        'video_id': info.get('id', ''),
                                        'title': info.get('title', ''),
                                        'duration': info.get('duration', 0),
                                        'source': 'yt-dlp_subtitles',
                                        'config_used': i + 1
                                    }
                            except Exception as e:
                                logger.error(f"Failed to download subtitle: {e}")
                                continue
                
        except Exception as e:
            logger.error(f"Config {i+1} failed: {str(e)}")
            continue
    
    # Clean up temp directory
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    logger.error("All subtitle extraction methods failed")
    return None


def parse_subtitle_content(content: str, format: str) -> str:
    """
    Parse subtitle content from various formats to plain text
    
    Args:
        content: Raw subtitle content
        format: Subtitle format (vtt, srt, json3, etc.)
        
    Returns:
        Plain text extracted from subtitles
    """
    lines = []
    
    if format == 'json3':
        # Parse JSON3 format (YouTube's format)
        try:
            import json
            data = json.loads(content)
            events = data.get('events', [])
            for event in events:
                if 'segs' in event:
                    for seg in event['segs']:
                        text = seg.get('utf8', '')
                        if text and text.strip():
                            lines.append(text.strip())
        except:
            pass
    
    elif format == 'vtt':
        # Parse WebVTT format
        for line in content.split('\n'):
            # Skip headers, timestamps, and formatting
            if (not line.startswith('WEBVTT') and 
                '-->' not in line and 
                not line.startswith('NOTE') and
                line.strip() and
                not line.strip().isdigit()):
                # Remove HTML tags
                clean_line = re.sub('<[^<]+?>', '', line)
                if clean_line.strip():
                    lines.append(clean_line.strip())
    
    elif format in ['srt', 'srv3']:
        # Parse SRT format
        blocks = content.split('\n\n')
        for block in blocks:
            block_lines = block.split('\n')
            for line in block_lines:
                # Skip numbers and timestamps
                if (not re.match(r'^\d+$', line) and 
                    '-->' not in line and 
                    line.strip()):
                    lines.append(line.strip())
    
    else:
        # Unknown format - try to extract text
        for line in content.split('\n'):
            if (line.strip() and 
                '-->' not in line and
                not line.strip().isdigit()):
                lines.append(line.strip())
    
    # Join lines and clean up
    text = ' '.join(lines)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def test_subtitle_extraction():
    """Test function for subtitle extraction"""
    test_urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # English
        "https://www.youtube.com/watch?v=UQpjPgMRypQ",  # Korean
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        result = extract_subtitles_only(url, "en")
        if result:
            print(f"Success! Language: {result['language']}, Auto: {result['is_auto_generated']}")
            print(f"Text preview: {result['text'][:200]}...")
        else:
            print("Failed to extract subtitles")


if __name__ == "__main__":
    test_subtitle_extraction()