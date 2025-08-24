import { chromium, FullConfig } from '@playwright/test';

/**
 * Global setup for Playwright tests
 * Initializes test environment and prepares shared resources
 */
async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global test setup...');

  // Launch browser for setup tasks
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Get base URL from config
    const baseURL = config.projects[0]?.use?.baseURL || process.env.BASE_URL || 'http://localhost:3000';
    console.log(`🌐 Base URL: ${baseURL}`);

    // Wait for application to be ready
    console.log('⏳ Waiting for application to be ready...');
    let retries = 30;
    while (retries > 0) {
      try {
        const response = await page.goto(`${baseURL}/`, { 
          waitUntil: 'networkidle',
          timeout: 10000 
        });
        
        if (response && response.ok()) {
          console.log('✅ Application is ready');
          break;
        }
      } catch (error) {
        console.log(`⏳ Retrying... (${30 - retries + 1}/30)`);
        retries--;
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }

    if (retries === 0) {
      throw new Error('❌ Application failed to start within timeout');
    }

    // Check if all required pages are accessible
    const pages = ['/transcription', '/analysis', '/reports'];
    for (const pagePath of pages) {
      console.log(`🔍 Checking page: ${pagePath}`);
      const response = await page.goto(`${baseURL}${pagePath}`, { 
        waitUntil: 'networkidle',
        timeout: 15000 
      });
      
      if (!response || !response.ok()) {
        console.warn(`⚠️  Warning: Page ${pagePath} may not be fully ready`);
      } else {
        console.log(`✅ Page ${pagePath} is accessible`);
      }
    }

    // Setup test data or authentication if needed
    console.log('🔧 Setting up test data...');
    
    // Store any global state for tests
    process.env.TEST_SETUP_COMPLETE = 'true';
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await context.close();
    await browser.close();
  }

  console.log('✅ Global setup completed successfully');
}

export default globalSetup;