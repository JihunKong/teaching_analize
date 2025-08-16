#!/usr/bin/env python3

import re
import json
from datetime import timedelta

def parse_vtt_file(vtt_file_path):
    """Parse VTT file and extract clean transcript with timestamps"""
    
    print(f"🎬 Parsing VTT file: {vtt_file_path}")
    
    try:
        with open(vtt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into lines
        lines = content.split('\n')
        
        # Find all timestamp lines and their corresponding text
        segments = []
        current_timestamp = None
        current_text_lines = []
        
        timestamp_pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})'
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line contains a timestamp
            timestamp_match = re.match(timestamp_pattern, line)
            if timestamp_match:
                # If we have a previous segment, save it
                if current_timestamp and current_text_lines:
                    clean_text = clean_vtt_text(' '.join(current_text_lines))
                    if clean_text:
                        segments.append({
                            'start': current_timestamp[0],
                            'end': current_timestamp[1],
                            'text': clean_text
                        })
                
                # Start new segment
                current_timestamp = (timestamp_match.group(1), timestamp_match.group(2))
                current_text_lines = []
                
                # Read the text lines that follow the timestamp
                i += 1
                while i < len(lines):
                    text_line = lines[i].strip()
                    if text_line == '' or re.match(timestamp_pattern, text_line):
                        break
                    if not text_line.startswith('align:') and not text_line.startswith('position:'):
                        current_text_lines.append(text_line)
                    i += 1
                continue
            
            i += 1
        
        # Handle the last segment
        if current_timestamp and current_text_lines:
            clean_text = clean_vtt_text(' '.join(current_text_lines))
            if clean_text:
                segments.append({
                    'start': current_timestamp[0],
                    'end': current_timestamp[1],
                    'text': clean_text
                })
        
        print(f"✅ Parsed {len(segments)} segments from VTT file")
        return segments
        
    except Exception as e:
        print(f"❌ Failed to parse VTT file: {e}")
        return None

def clean_vtt_text(text):
    """Clean VTT text by removing tags and formatting"""
    
    if not text:
        return ""
    
    # Remove [음악] tags
    text = re.sub(r'\[음악\]', '', text)
    
    # Remove VTT timing tags like <00:00:07.440> and <c>
    text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)
    text = re.sub(r'</?c[^>]*>', '', text)
    
    # Remove other HTML-like tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    # Remove common noise words/characters
    text = text.replace('cout', '').strip()
    
    return text.strip()

def timestamp_to_seconds(timestamp_str):
    """Convert timestamp string (HH:MM:SS.mmm) to total seconds"""
    try:
        parts = timestamp_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split('.')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1])
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        return total_seconds
    except:
        return 0

def main():
    vtt_file = '/Users/jihunkong/teaching_analize/frontend/pages/[수업영상]온라인 콘텐츠 활용 교과서 우수 수업 사례 #1 (신성중학교 곽상경 선생님).ko.vtt'
    
    segments = parse_vtt_file(vtt_file)
    
    if not segments:
        print("❌ Failed to parse segments")
        return
    
    # Convert timestamps to seconds and create final transcript
    final_transcript = []
    
    for segment in segments:
        start_seconds = timestamp_to_seconds(segment['start'])
        end_seconds = timestamp_to_seconds(segment['end'])
        
        final_transcript.append({
            'start': start_seconds,
            'end': end_seconds,
            'duration': end_seconds - start_seconds,
            'text': segment['text'],
            'timestamp': segment['start']
        })
    
    # Remove duplicates and very similar segments
    deduplicated = []
    prev_text = ""
    
    for segment in final_transcript:
        if segment['text'] and segment['text'] != prev_text:
            # Check if this is not a substring of previous text
            if not (prev_text and segment['text'] in prev_text):
                deduplicated.append(segment)
                prev_text = segment['text']
    
    print(f"📊 After deduplication: {len(deduplicated)} unique segments")
    
    # Save results
    output_json = '/Users/jihunkong/teaching_analize/frontend/pages/final_transcript.json'
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'video_id': '-OLCt6WScEY',
            'video_title': '온라인 콘텐츠 활용 교과서 우수 수업 사례 #1 (신성중학교 곽상경 선생님)',
            'language': 'ko',
            'total_segments': len(deduplicated),
            'transcript': deduplicated
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Final transcript saved to: {output_json}")
    
    # Create a clean text version
    output_text = '/Users/jihunkong/teaching_analize/frontend/pages/final_transcript.txt'
    with open(output_text, 'w', encoding='utf-8') as f:
        for segment in deduplicated:
            minutes = int(segment['start'] // 60)
            seconds = int(segment['start'] % 60)
            f.write(f"[{minutes:02d}:{seconds:02d}] {segment['text']}\n")
    
    print(f"💾 Clean text transcript saved to: {output_text}")
    
    # Show statistics
    total_duration = deduplicated[-1]['end'] if deduplicated else 0
    total_text = ' '.join([seg['text'] for seg in deduplicated])
    
    print(f"\n📊 TRANSCRIPT STATISTICS:")
    print(f"   📺 Video duration: {int(total_duration // 60)}:{int(total_duration % 60):02d}")
    print(f"   💬 Total segments: {len(deduplicated)}")
    print(f"   📝 Total characters: {len(total_text)}")
    print(f"   📖 Total words: {len(total_text.split())}")
    print(f"   ⏱️  Average segment length: {total_duration / len(deduplicated):.1f} seconds")
    
    # Show first 10 segments
    print(f"\n📄 First 10 segments:")
    for i, segment in enumerate(deduplicated[:10]):
        minutes = int(segment['start'] // 60)
        seconds = int(segment['start'] % 60)
        print(f"   {i+1:2d}. [{minutes:02d}:{seconds:02d}] {segment['text']}")
    
    print(f"\n🎯 SUCCESS! Clean transcript extracted from YouTube video")
    print(f"   ✅ Using yt-dlp method")
    print(f"   ✅ Parsed VTT format successfully")
    print(f"   ✅ Cleaned and deduplicated text")
    print(f"   ✅ Ready for CBIL analysis")

if __name__ == '__main__':
    main()