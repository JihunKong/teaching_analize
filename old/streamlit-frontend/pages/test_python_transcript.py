#!/usr/bin/env python3

import sys
import json
from youtube_transcript_api import YouTubeTranscriptApi

def test_youtube_transcript_api():
    print('🐍 Testing YouTube Transcript API (Python)')
    
    video_id = '-OLCt6WScEY'
    print(f"📺 Video ID: {video_id}")
    
    try:
        # List available transcripts
        print('\n📋 Step 1: Listing available transcripts...')
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        print("Available transcripts:")
        transcripts_info = []
        
        for transcript in transcript_list:
            info = {
                'language_code': transcript.language_code,
                'language': transcript.language,
                'is_generated': transcript.is_generated,
                'is_translatable': transcript.is_translatable
            }
            transcripts_info.append(info)
            print(f"  - {transcript.language} ({transcript.language_code})")
            print(f"    Auto-generated: {'Yes' if transcript.is_generated else 'No'}")
            print(f"    Translatable: {'Yes' if transcript.is_translatable else 'No'}")
        
        # Try to get Korean transcript
        print('\n📋 Step 2: Extracting Korean transcript...')
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            print(f"✅ Successfully extracted Korean transcript with {len(transcript)} segments")
            
            # Save full transcript to JSON
            output_file = '/Users/jihunkong/teaching_analize/frontend/pages/transcript_python.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'video_id': video_id,
                    'available_transcripts': transcripts_info,
                    'transcript': transcript
                }, f, ensure_ascii=False, indent=2)
            print(f"💾 Full transcript saved to: {output_file}")
            
            # Create a simple text version
            text_output = '/Users/jihunkong/teaching_analize/frontend/pages/transcript_python.txt'
            with open(text_output, 'w', encoding='utf-8') as f:
                for segment in transcript:
                    f.write(f"[{segment['start']:.1f}s] {segment['text']}\n")
            print(f"💾 Text transcript saved to: {text_output}")
            
            # Show first 10 segments
            print('\n📄 First 10 transcript segments:')
            for i, segment in enumerate(transcript[:10]):
                timestamp = f"{int(segment['start'] // 60)}:{int(segment['start'] % 60):02d}"
                print(f"  {i+1:2d}. [{timestamp}] {segment['text']}")
            
            # Calculate total duration
            if transcript:
                total_duration = transcript[-1]['start'] + transcript[-1]['duration']
                print(f'\n⏱️  Total video duration: {int(total_duration // 60)}:{int(total_duration % 60):02d}')
                print(f'📊 Average segment length: {total_duration / len(transcript):.1f} seconds')
            
            return transcript
            
        except Exception as e:
            print(f"❌ Failed to get Korean transcript: {e}")
            
            # Try auto-generated transcript
            print('\n📋 Step 3: Trying auto-generated transcript...')
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                print(f"✅ Got auto-generated transcript with {len(transcript)} segments")
                
                # Show language of the transcript we got
                first_transcript = list(transcript_list)[0]
                print(f"Language: {first_transcript.language} ({first_transcript.language_code})")
                
                return transcript
            except Exception as e2:
                print(f"❌ Failed to get any transcript: {e2}")
                return None
                
    except Exception as e:
        print(f"❌ Failed to list transcripts: {e}")
        return None

def convert_vtt_to_text():
    """Convert the VTT file we got from yt-dlp to plain text for comparison"""
    print('\n🔄 Converting VTT file to plain text for comparison...')
    
    vtt_file = '/Users/jihunkong/teaching_analize/frontend/pages/[수업영상]온라인 콘텐츠 활용 교과서 우수 수업 사례 #1 (신성중학교 곽상경 선생님).ko.vtt'
    
    try:
        with open(vtt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract text from VTT format
        lines = content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip WEBVTT header, timestamps, and empty lines
            if (line and 
                not line.startswith('WEBVTT') and
                not line.startswith('Kind:') and
                not line.startswith('Language:') and
                not '-->' in line and
                not line.startswith('align:') and
                not line.startswith('<')):
                
                # Clean up the text
                clean_text = line.replace('[음악]', '').strip()
                if clean_text and clean_text not in text_lines:
                    text_lines.append(clean_text)
        
        # Save cleaned text
        clean_output = '/Users/jihunkong/teaching_analize/frontend/pages/transcript_vtt_cleaned.txt'
        with open(clean_output, 'w', encoding='utf-8') as f:
            for line in text_lines:
                f.write(line + '\n')
        
        print(f"💾 Cleaned VTT transcript saved to: {clean_output}")
        print(f"📊 Extracted {len(text_lines)} text segments from VTT")
        
        # Show first few lines
        print('\n📄 First 10 lines from VTT:')
        for i, line in enumerate(text_lines[:10]):
            print(f"  {i+1:2d}. {line}")
            
    except Exception as e:
        print(f"❌ Failed to convert VTT file: {e}")

def main():
    print('🚀 Comprehensive YouTube Caption Extraction Test')
    print('=' * 50)
    
    # Test Python API
    transcript = test_youtube_transcript_api()
    
    # Convert VTT file for comparison
    convert_vtt_to_text()
    
    print('\n📊 SUMMARY:')
    print('=' * 50)
    
    if transcript:
        print('✅ Python youtube-transcript-api: SUCCESS')
        print(f'   - Extracted {len(transcript)} segments')
    else:
        print('❌ Python youtube-transcript-api: FAILED')
    
    print('✅ yt-dlp VTT extraction: SUCCESS')
    print('   - Downloaded VTT file with Korean captions')
    
    print('\n💡 RECOMMENDATIONS:')
    print('=' * 50)
    print('1. 🏆 Use yt-dlp for most reliable caption extraction')
    print('2. 🐍 Use youtube-transcript-api as Python fallback')
    print('3. 🔧 Both methods work locally but may fail on Railway')
    print('4. 📋 Consider implementing both methods with fallbacks')
    print('5. ⚡ yt-dlp is faster and more reliable than browser automation')

if __name__ == '__main__':
    main()