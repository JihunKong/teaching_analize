const { spawn } = require('child_process');

async function testYtDlp() {
    console.log('🔧 Testing yt-dlp for YouTube caption extraction...');
    
    const videoUrl = 'https://www.youtube.com/watch?v=-OLCt6WScEY';
    
    // Test 1: Check if yt-dlp is available
    console.log('\n📋 Test 1: Checking yt-dlp availability...');
    
    return new Promise((resolve, reject) => {
        const ytdlp = spawn('yt-dlp', ['--version'], { stdio: 'pipe' });
        
        let output = '';
        let errorOutput = '';
        
        ytdlp.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        ytdlp.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });
        
        ytdlp.on('close', async (code) => {
            if (code === 0) {
                console.log(`✅ yt-dlp is available, version: ${output.trim()}`);
                await testCaptionExtraction(videoUrl);
                resolve();
            } else {
                console.log('❌ yt-dlp is not available');
                console.log('Error:', errorOutput);
                
                // Try to install yt-dlp
                console.log('\n📦 Attempting to install yt-dlp...');
                await installYtDlp();
                resolve();
            }
        });
        
        ytdlp.on('error', (error) => {
            console.log('❌ yt-dlp command failed:', error.message);
            reject(error);
        });
    });
}

async function installYtDlp() {
    console.log('Installing yt-dlp via pip...');
    
    return new Promise((resolve, reject) => {
        const pip = spawn('pip3', ['install', 'yt-dlp'], { stdio: 'inherit' });
        
        pip.on('close', (code) => {
            if (code === 0) {
                console.log('✅ yt-dlp installed successfully');
                testCaptionExtraction('https://www.youtube.com/watch?v=-OLCt6WScEY').then(resolve);
            } else {
                console.log('❌ Failed to install yt-dlp');
                resolve();
            }
        });
        
        pip.on('error', (error) => {
            console.log('❌ pip install failed:', error.message);
            resolve();
        });
    });
}

async function testCaptionExtraction(videoUrl) {
    console.log('\n📋 Test 2: Extracting captions with yt-dlp...');
    
    // Test different yt-dlp methods
    const tests = [
        {
            name: 'List available subtitles',
            args: ['--list-subs', videoUrl]
        },
        {
            name: 'Extract auto-generated Korean subtitles',
            args: ['--write-auto-subs', '--sub-langs', 'ko', '--skip-download', '--sub-format', 'vtt', '-o', '/Users/jihunkong/teaching_analize/frontend/pages/%(title)s.%(ext)s', videoUrl]
        },
        {
            name: 'Extract manual Korean subtitles',
            args: ['--write-subs', '--sub-langs', 'ko', '--skip-download', '--sub-format', 'vtt', '-o', '/Users/jihunkong/teaching_analize/frontend/pages/%(title)s.%(ext)s', videoUrl]
        },
        {
            name: 'Extract all available subtitles',
            args: ['--write-subs', '--write-auto-subs', '--all-subs', '--skip-download', '--sub-format', 'vtt', '-o', '/Users/jihunkong/teaching_analize/frontend/pages/%(title)s.%(ext)s', videoUrl]
        }
    ];
    
    for (const test of tests) {
        console.log(`\n🧪 ${test.name}...`);
        
        await new Promise((resolve) => {
            const ytdlp = spawn('yt-dlp', test.args, { stdio: 'pipe' });
            
            let output = '';
            let errorOutput = '';
            
            ytdlp.stdout.on('data', (data) => {
                output += data.toString();
            });
            
            ytdlp.stderr.on('data', (data) => {
                errorOutput += data.toString();
            });
            
            ytdlp.on('close', (code) => {
                if (code === 0) {
                    console.log(`✅ Success!`);
                    console.log(output.trim());
                } else {
                    console.log(`❌ Failed (exit code: ${code})`);
                    if (errorOutput) {
                        console.log('Error output:');
                        console.log(errorOutput.trim());
                    }
                }
                resolve();
            });
            
            setTimeout(() => {
                ytdlp.kill();
                console.log('⏰ Test timed out after 30 seconds');
                resolve();
            }, 30000);
        });
    }
}

// Also test youtube-transcript-api if available
async function testYouTubeTranscriptAPI() {
    console.log('\n🐍 Testing youtube-transcript-api (Python)...');
    
    const pythonScript = `
import sys
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    
    video_id = '-OLCt6WScEY'
    print(f"Attempting to get transcript for video: {video_id}")
    
    # Try to get available transcript languages
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("Available transcripts:")
        for transcript in transcript_list:
            print(f"  - {transcript.language} ({transcript.language_code}) - Auto-generated: {transcript.is_generated}")
        
        # Try to get Korean transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            print(f"\\nSuccessfully extracted Korean transcript with {len(transcript)} segments")
            
            # Save to file
            import json
            with open('/Users/jihunkong/teaching_analize/frontend/pages/transcript_python.json', 'w', encoding='utf-8') as f:
                json.dump(transcript, f, ensure_ascii=False, indent=2)
            print("Transcript saved to: transcript_python.json")
            
            # Show first few segments
            print("\\nFirst 5 segments:")
            for i, segment in enumerate(transcript[:5]):
                print(f"  {i+1}. [{segment['start']:.1f}s] {segment['text']}")
                
        except Exception as e:
            print(f"Failed to get Korean transcript: {e}")
            
    except Exception as e:
        print(f"Failed to list transcripts: {e}")
        
except ImportError:
    print("youtube-transcript-api not available")
    print("Installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'youtube-transcript-api'])
    print("Installed! Please run the test again.")
    
except Exception as e:
    print(f"Error: {e}")
`;
    
    return new Promise((resolve) => {
        const python = spawn('python3', ['-c', pythonScript], { stdio: 'pipe' });
        
        let output = '';
        let errorOutput = '';
        
        python.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });
        
        python.on('close', (code) => {
            console.log(`Python script completed with exit code: ${code}`);
            if (output) {
                console.log('Output:', output);
            }
            if (errorOutput) {
                console.log('Error output:', errorOutput);
            }
            resolve();
        });
        
        setTimeout(() => {
            python.kill();
            console.log('⏰ Python script timed out');
            resolve();
        }, 30000);
    });
}

async function main() {
    console.log('🚀 Starting comprehensive YouTube caption extraction test...');
    
    try {
        await testYtDlp();
        await testYouTubeTranscriptAPI();
        
        console.log('\n📊 Test Summary:');
        console.log('✅ Browser-based extraction: Failed (YouTube blocks API access)');
        console.log('🔧 yt-dlp: Testing completed');
        console.log('🐍 Python youtube-transcript-api: Testing completed');
        
        console.log('\n💡 Recommendations:');
        console.log('1. Use yt-dlp for reliable caption extraction');
        console.log('2. Use youtube-transcript-api as Python alternative');
        console.log('3. Implement fallback to Whisper STT for videos without captions');
        console.log('4. Consider using these tools in Railway environment instead of browser automation');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

main().catch(console.error);