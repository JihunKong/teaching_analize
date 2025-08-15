const { chromium } = require('playwright');

async function debugCaptionAccess() {
    const browser = await chromium.launch({ 
        headless: false,  // Keep visible for debugging
        slowMo: 2000
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    
    // Log all network requests
    page.on('request', request => {
        if (request.url().includes('timedtext')) {
            console.log('🔗 Request URL:', request.url());
            console.log('🔗 Request Headers:', request.headers());
        }
    });
    
    page.on('response', async response => {
        if (response.url().includes('timedtext')) {
            console.log('📥 Response URL:', response.url());
            console.log('📥 Response Status:', response.status());
            console.log('📥 Response Headers:', response.headers());
            
            try {
                const content = await response.text();
                console.log('📥 Response Content Length:', content.length);
                console.log('📥 Response Content Preview:', content.substring(0, 200));
                
                if (content.length > 0) {
                    // Save the response content
                    const fs = require('fs').promises;
                    await fs.writeFile(
                        '/Users/jihunkong/teaching_analize/frontend/pages/raw_caption_response.xml',
                        content
                    );
                    console.log('💾 Raw response saved to: raw_caption_response.xml');
                }
            } catch (error) {
                console.log('❌ Error reading response:', error.message);
            }
        }
    });
    
    const videoUrl = 'https://www.youtube.com/watch?v=-OLCt6WScEY&list=PLugIxwJYmOhl_8KO3GHx9gp6VKMmbsTfw';
    console.log('🎬 Loading video page...');
    
    await page.goto(videoUrl, { waitUntil: 'networkidle' });
    await page.waitForSelector('#movie_player', { timeout: 10000 });
    await page.waitForTimeout(5000);
    
    // Extract player response and try to manually access caption URLs
    const playerResponse = await page.evaluate(() => {
        const scripts = document.querySelectorAll('script');
        for (let script of scripts) {
            const content = script.textContent;
            if (content && content.includes('ytInitialPlayerResponse')) {
                const match = content.match(/ytInitialPlayerResponse\s*=\s*({.+?});/);
                if (match) {
                    try {
                        return JSON.parse(match[1]);
                    } catch (e) {
                        return null;
                    }
                }
            }
        }
        return null;
    });
    
    if (playerResponse) {
        const captions = playerResponse?.captions?.playerCaptionsTracklistRenderer?.captionTracks;
        
        if (captions && captions.length > 0) {
            console.log('\n🔍 Found caption tracks, attempting direct access...');
            
            for (const [index, caption] of captions.entries()) {
                console.log(`\n📝 Testing caption track ${index + 1}:`);
                console.log(`   Language: ${caption.languageCode}`);
                console.log(`   URL: ${caption.baseUrl}`);
                
                // Try different methods to access the caption data
                
                // Method 1: Direct fetch with Playwright's request context
                console.log('   Method 1: Playwright request context...');
                try {
                    const response = await context.request.get(caption.baseUrl);
                    console.log(`   Status: ${response.status()}`);
                    const content = await response.text();
                    console.log(`   Content length: ${content.length}`);
                    if (content.length > 0) {
                        console.log(`   Content preview: ${content.substring(0, 100)}`);
                    }
                } catch (error) {
                    console.log(`   Error: ${error.message}`);
                }
                
                // Method 2: Fetch from within the page context
                console.log('   Method 2: Page context fetch...');
                try {
                    const result = await page.evaluate(async (url) => {
                        try {
                            const response = await fetch(url);
                            const text = await response.text();
                            return {
                                status: response.status,
                                headers: Object.fromEntries(response.headers.entries()),
                                content: text,
                                contentLength: text.length
                            };
                        } catch (error) {
                            return { error: error.message };
                        }
                    }, caption.baseUrl);
                    
                    console.log(`   Status: ${result.status}`);
                    console.log(`   Content length: ${result.contentLength}`);
                    console.log(`   Headers:`, result.headers);
                    if (result.content && result.content.length > 0) {
                        console.log(`   Content preview: ${result.content.substring(0, 100)}`);
                        
                        // Save the content
                        const fs = require('fs').promises;
                        await fs.writeFile(
                            `/Users/jihunkong/teaching_analize/frontend/pages/caption_${index + 1}_method2.xml`,
                            result.content
                        );
                        console.log(`   💾 Saved to: caption_${index + 1}_method2.xml`);
                    }
                } catch (error) {
                    console.log(`   Error: ${error.message}`);
                }
                
                // Method 3: Try with additional parameters
                console.log('   Method 3: URL with format parameter...');
                try {
                    const urlWithFormat = caption.baseUrl + '&fmt=srv3';
                    const response = await context.request.get(urlWithFormat);
                    console.log(`   Status: ${response.status()}`);
                    const content = await response.text();
                    console.log(`   Content length: ${content.length}`);
                    if (content.length > 0) {
                        console.log(`   Content preview: ${content.substring(0, 100)}`);
                        
                        const fs = require('fs').promises;
                        await fs.writeFile(
                            `/Users/jihunkong/teaching_analize/frontend/pages/caption_${index + 1}_method3.xml`,
                            content
                        );
                        console.log(`   💾 Saved to: caption_${index + 1}_method3.xml`);
                    }
                } catch (error) {
                    console.log(`   Error: ${error.message}`);
                }
            }
        }
    }
    
    // Try to activate captions on the video player and capture visible text
    console.log('\n🎮 Attempting to activate captions on player...');
    try {
        // Click the caption button
        await page.locator('.ytp-subtitles-button').click();
        await page.waitForTimeout(3000);
        
        // Let the video play a bit to see if captions appear
        const playButton = page.locator('.ytp-play-button');
        if (await playButton.isVisible()) {
            await playButton.click();
            console.log('▶️ Started video playback');
            await page.waitForTimeout(10000); // Let it play for 10 seconds
            
            // Check for visible captions
            const captionElements = await page.locator('.ytp-caption-segment, .caption-visual-line').all();
            if (captionElements.length > 0) {
                console.log(`✅ Found ${captionElements.length} visible caption elements`);
                const texts = await Promise.all(captionElements.map(el => el.textContent()));
                console.log('Visible caption texts:', texts.filter(t => t && t.trim()));
            } else {
                console.log('❌ No visible caption elements found');
            }
            
            // Pause the video
            await page.keyboard.press('Space');
            console.log('⏸️ Paused video');
        }
    } catch (error) {
        console.log(`❌ Player interaction error: ${error.message}`);
    }
    
    console.log('\n🏁 Debug session completed');
    await page.waitForTimeout(5000); // Keep browser open for observation
    await browser.close();
}

debugCaptionAccess().catch(console.error);