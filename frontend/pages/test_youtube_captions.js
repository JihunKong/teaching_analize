const { chromium } = require('playwright');

async function testYouTubeCaptions() {
    const browser = await chromium.launch({ 
        headless: false,  // Keep visible to see what's happening
        slowMo: 1000     // Slow down for better observation
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        // Use a realistic user agent
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    
    console.log('🚀 Starting YouTube caption extraction test...');
    
    try {
        // Navigate to the YouTube video
        const url = 'https://www.youtube.com/watch?v=-OLCt6WScEY&list=PLugIxwJYmOhl_8KO3GHx9gp6VKMmbsTfw';
        console.log(`📺 Navigating to: ${url}`);
        
        await page.goto(url, { waitUntil: 'networkidle' });
        
        // Wait for video player to load
        await page.waitForSelector('#movie_player', { timeout: 10000 });
        console.log('✅ Video player loaded');
        
        // Wait a bit more for everything to settle
        await page.waitForTimeout(3000);
        
        // Method 1: Check for caption button in player controls
        console.log('\n🔍 Method 1: Checking caption button in player controls...');
        try {
            const captionButton = await page.locator('.ytp-subtitles-button').first();
            const isVisible = await captionButton.isVisible();
            console.log(`Caption button visible: ${isVisible}`);
            
            if (isVisible) {
                // Click to enable captions
                await captionButton.click();
                console.log('👆 Clicked caption button');
                await page.waitForTimeout(2000);
                
                // Check if captions are now showing
                const captionContainer = await page.locator('.caption-window').first();
                const captionsActive = await captionContainer.isVisible();
                console.log(`Captions now active: ${captionsActive}`);
            }
        } catch (error) {
            console.log(`❌ Caption button method failed: ${error.message}`);
        }
        
        // Method 2: Check caption settings menu
        console.log('\n🔍 Method 2: Checking caption settings menu...');
        try {
            const settingsButton = await page.locator('.ytp-settings-button').first();
            const settingsVisible = await settingsButton.isVisible();
            console.log(`Settings button visible: ${settingsVisible}`);
            
            if (settingsVisible) {
                await settingsButton.click();
                await page.waitForTimeout(1000);
                
                // Look for subtitles/CC option in menu
                const subtitleOption = await page.locator('.ytp-menuitem:has-text("字幕"), .ytp-menuitem:has-text("Subtitles"), .ytp-menuitem:has-text("자막")').first();
                const subtitleOptionVisible = await subtitleOption.isVisible();
                console.log(`Subtitle option in menu visible: ${subtitleOptionVisible}`);
                
                if (subtitleOptionVisible) {
                    await subtitleOption.click();
                    await page.waitForTimeout(1000);
                    
                    // Check available subtitle languages
                    const languageOptions = await page.locator('.ytp-menuitem').allTextContents();
                    console.log('Available subtitle languages:', languageOptions);
                }
                
                // Close menu
                await page.keyboard.press('Escape');
            }
        } catch (error) {
            console.log(`❌ Settings menu method failed: ${error.message}`);
        }
        
        // Method 3: Check for auto-generated captions via keyboard shortcut
        console.log('\n🔍 Method 3: Trying keyboard shortcut to toggle captions...');
        try {
            // Focus on the video player
            await page.locator('#movie_player').click();
            await page.waitForTimeout(500);
            
            // Press 'c' to toggle captions
            await page.keyboard.press('c');
            await page.waitForTimeout(2000);
            
            // Check if captions appeared
            const captionTexts = await page.locator('.caption-window .captions-text .caption-visual-line').allTextContents();
            if (captionTexts.length > 0) {
                console.log('✅ Captions found via keyboard shortcut!');
                console.log('Sample caption text:', captionTexts.slice(0, 3));
            } else {
                console.log('❌ No captions found via keyboard shortcut');
            }
        } catch (error) {
            console.log(`❌ Keyboard shortcut method failed: ${error.message}`);
        }
        
        // Method 4: Check video metadata and network requests
        console.log('\n🔍 Method 4: Checking network requests for caption data...');
        
        // Listen for network responses that might contain caption data
        const captionRequests = [];
        page.on('response', async (response) => {
            const url = response.url();
            if (url.includes('timedtext') || url.includes('caption') || url.includes('subtitle')) {
                captionRequests.push({
                    url: url,
                    status: response.status(),
                    contentType: response.headers()['content-type']
                });
                console.log(`📡 Found caption-related request: ${url} (${response.status()})`);
            }
        });
        
        // Reload page to capture all network requests
        await page.reload({ waitUntil: 'networkidle' });
        await page.waitForTimeout(5000);
        
        console.log(`Found ${captionRequests.length} caption-related network requests`);
        captionRequests.forEach((req, index) => {
            console.log(`  ${index + 1}. ${req.url} (${req.status}) - ${req.contentType}`);
        });
        
        // Method 5: Extract video information from page source
        console.log('\n🔍 Method 5: Extracting video information from page source...');
        try {
            // Get ytInitialPlayerResponse data
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
                console.log('✅ Found ytInitialPlayerResponse data');
                
                // Check for caption tracks
                const captions = playerResponse?.captions?.playerCaptionsTracklistRenderer?.captionTracks;
                if (captions && captions.length > 0) {
                    console.log('🎯 Found caption tracks in player response!');
                    captions.forEach((caption, index) => {
                        console.log(`  ${index + 1}. Language: ${caption.languageCode} (${caption.name?.simpleText})`);
                        console.log(`     URL: ${caption.baseUrl}`);
                        console.log(`     Auto-generated: ${caption.kind === 'asr' ? 'Yes' : 'No'}`);
                    });
                    
                    // Try to fetch caption data from the first track
                    if (captions[0]?.baseUrl) {
                        console.log('\n📥 Attempting to fetch caption data...');
                        try {
                            const captionResponse = await page.request.get(captions[0].baseUrl);
                            if (captionResponse.ok()) {
                                const captionXML = await captionResponse.text();
                                console.log('✅ Successfully fetched caption data!');
                                console.log('Caption format: XML');
                                console.log('Sample caption data (first 500 chars):');
                                console.log(captionXML.substring(0, 500) + '...');
                                
                                // Parse some caption text
                                const textMatches = captionXML.match(/<text[^>]*>([^<]*)<\/text>/g);
                                if (textMatches) {
                                    console.log('\nExtracted caption texts (first 5):');
                                    textMatches.slice(0, 5).forEach((match, i) => {
                                        const text = match.replace(/<[^>]*>/g, '').trim();
                                        if (text) console.log(`  ${i + 1}. "${text}"`);
                                    });
                                }
                            } else {
                                console.log(`❌ Failed to fetch caption data: ${captionResponse.status()}`);
                            }
                        } catch (fetchError) {
                            console.log(`❌ Error fetching caption data: ${fetchError.message}`);
                        }
                    }
                } else {
                    console.log('❌ No caption tracks found in player response');
                }
                
                // Check video metadata
                const videoDetails = playerResponse?.videoDetails;
                if (videoDetails) {
                    console.log('\n📊 Video Details:');
                    console.log(`  Title: ${videoDetails.title}`);
                    console.log(`  Length: ${videoDetails.lengthSeconds} seconds`);
                    console.log(`  Channel: ${videoDetails.author}`);
                    console.log(`  Is Live: ${videoDetails.isLive ? 'Yes' : 'No'}`);
                }
            } else {
                console.log('❌ Could not extract ytInitialPlayerResponse data');
            }
        } catch (error) {
            console.log(`❌ Page source extraction failed: ${error.message}`);
        }
        
        // Method 6: Check current visible captions on the page
        console.log('\n🔍 Method 6: Checking for visible captions on page...');
        try {
            // Try to find any caption elements that might be visible
            const captionSelectors = [
                '.caption-window .captions-text',
                '.ytp-caption-segment',
                '.caption-visual-line',
                '[class*="caption"]',
                '[class*="subtitle"]'
            ];
            
            for (const selector of captionSelectors) {
                const elements = await page.locator(selector).all();
                if (elements.length > 0) {
                    console.log(`✅ Found ${elements.length} elements with selector: ${selector}`);
                    const texts = await page.locator(selector).allTextContents();
                    const nonEmptyTexts = texts.filter(text => text.trim().length > 0);
                    if (nonEmptyTexts.length > 0) {
                        console.log('Sample visible caption texts:');
                        nonEmptyTexts.slice(0, 3).forEach((text, i) => {
                            console.log(`  ${i + 1}. "${text}"`);
                        });
                    }
                } else {
                    console.log(`❌ No elements found with selector: ${selector}`);
                }
            }
        } catch (error) {
            console.log(`❌ Visible caption check failed: ${error.message}`);
        }
        
        // Take a screenshot for reference
        await page.screenshot({ 
            path: '/Users/jihunkong/teaching_analize/frontend/pages/youtube_test_screenshot.png',
            fullPage: false 
        });
        console.log('\n📸 Screenshot saved: youtube_test_screenshot.png');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    } finally {
        await browser.close();
        console.log('\n🏁 Test completed');
    }
}

// Run the test
testYouTubeCaptions().catch(console.error);