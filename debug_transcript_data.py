#!/usr/bin/env python3
"""
Debug transcript data display with JavaScript console inspection
"""

from playwright.sync_api import sync_playwright
import time

def debug_transcript_data():
    print("🔍 Debugging transcript data display")
    print("=" * 45)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.on("console", lambda msg: print(f"[{msg.type}] {msg.text}"))
        
        try:
            # Load page
            page.goto("http://3.38.107.23:3000")
            page.wait_for_selector("h1")
            print("✅ Page loaded")
            
            # Use Rick Roll again for consistency
            youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            
            # Fill form and start
            page.fill("#youtube-url", youtube_url)
            page.click("#transcribe-btn")
            print("🚀 Transcription started")
            
            # Wait for completion
            time.sleep(10)
            
            # Manually trigger the display function with console logging
            print("🔧 Debugging with JavaScript console...")
            
            result = page.evaluate("""
                // Override the displayTranscriptionResult function with debug logging
                window.originalDisplayTranscriptionResult = displayTranscriptionResult;
                
                window.displayTranscriptionResult = function(data) {
                    console.log('=== DEBUGGING TRANSCRIPT DISPLAY ===');
                    console.log('Full data object:', JSON.stringify(data, null, 2));
                    console.log('data.result:', data.result);
                    console.log('data.result.text:', data.result ? data.result.text : 'No result object');
                    console.log('data.transcript:', data.transcript);
                    
                    // Call original function
                    window.originalDisplayTranscriptionResult(data);
                };
                
                // Try to get the last job status manually
                fetch('/api/transcribe/f2919a49-4b99-49d1-825f-f2ff8690b510', {
                    headers: {
                        'X-API-Key': 'transcription-api-key-prod-2025'
                    }
                }).then(r => r.json()).then(data => {
                    console.log('Manual API call result:', data);
                    displayTranscriptionResult(data);
                }).catch(e => {
                    console.error('Manual API call failed:', e);
                });
                
                return 'Debug setup complete';
            """)
            
            print(f"JavaScript result: {result}")
            
            # Wait for the manual call to complete
            time.sleep(5)
            
            # Check final result
            final_content = page.text_content("#transcription-result") or ""
            print(f"\n📄 Final result length: {len(final_content)} characters")
            print(f"📄 Final result content: {final_content[:200]}...")
            
            # Take screenshot
            page.screenshot(path="debug_transcript.png")
            print("📸 Debug screenshot saved")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
        finally:
            time.sleep(10)  # Keep browser open longer for inspection
            browser.close()

if __name__ == "__main__":
    debug_transcript_data()