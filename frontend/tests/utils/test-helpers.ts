import { Page, expect, Browser, BrowserContext } from '@playwright/test';

/**
 * Test helper utilities for Playwright E2E tests
 * Provides common functions for test setup, assertions, and interactions
 */

export class TestHelpers {
  /**
   * Wait for element with custom retry logic
   */
  static async waitForElementWithRetry(
    page: Page, 
    selector: string, 
    maxRetries: number = 5,
    retryDelay: number = 1000
  ): Promise<boolean> {
    for (let i = 0; i < maxRetries; i++) {
      try {
        await page.locator(selector).waitFor({ timeout: 2000 });
        return true;
      } catch (error) {
        if (i === maxRetries - 1) {
          console.error(`Element ${selector} not found after ${maxRetries} retries`);
          return false;
        }
        await page.waitForTimeout(retryDelay);
      }
    }
    return false;
  }

  /**
   * Fill form field with validation
   */
  static async fillAndValidate(page: Page, selector: string, value: string): Promise<void> {
    const element = page.locator(selector);
    await element.clear();
    await element.fill(value);
    
    // Validate the value was set correctly
    const actualValue = await element.inputValue();
    if (actualValue !== value) {
      throw new Error(`Failed to set value. Expected: "${value}", Got: "${actualValue}"`);
    }
  }

  /**
   * Click button with loading state handling
   */
  static async clickButtonWithLoading(
    page: Page, 
    buttonSelector: string,
    loadingSelector?: string
  ): Promise<void> {
    const button = page.locator(buttonSelector);
    await expect(button).toBeEnabled();
    
    await button.click();
    
    // Wait for loading state if provided
    if (loadingSelector) {
      try {
        await page.locator(loadingSelector).waitFor({ timeout: 5000 });
        await page.locator(loadingSelector).waitFor({ state: 'detached', timeout: 30000 });
      } catch (error) {
        // Loading indicator might not appear for fast operations
        console.warn('Loading state not detected or completed quickly');
      }
    }
  }

  /**
   * Handle JavaScript alerts with custom responses
   */
  static setupAlertHandler(page: Page, responses: Record<string, boolean | string> = {}): void {
    page.on('dialog', async dialog => {
      const message = dialog.message().toLowerCase();
      let response = true;
      
      // Check for specific responses
      for (const [key, value] of Object.entries(responses)) {
        if (message.includes(key.toLowerCase())) {
          if (typeof value === 'boolean') {
            response = value;
          } else {
            await dialog.accept(value);
            return;
          }
          break;
        }
      }
      
      if (response) {
        await dialog.accept();
      } else {
        await dialog.dismiss();
      }
    });
  }

  /**
   * Mock API responses for consistent testing
   */
  static async mockApiResponse(
    page: Page,
    urlPattern: string,
    response: any,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
      status?: number;
      delay?: number;
      contentType?: string;
    } = {}
  ): Promise<void> {
    await page.route(urlPattern, async route => {
      const { method = 'GET', status = 200, delay = 0, contentType = 'application/json' } = options;
      
      // Check method if specified
      if (route.request().method() !== method) {
        await route.continue();
        return;
      }
      
      // Add delay if specified
      if (delay > 0) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
      
      await route.fulfill({
        status,
        contentType,
        body: typeof response === 'string' ? response : JSON.stringify(response)
      });
    });
  }

  /**
   * Mock API error responses
   */
  static async mockApiError(
    page: Page,
    urlPattern: string,
    errorCode: number = 500,
    errorMessage: string = 'Internal Server Error'
  ): Promise<void> {
    await page.route(urlPattern, async route => {
      await route.fulfill({
        status: errorCode,
        contentType: 'application/json',
        body: JSON.stringify({ detail: errorMessage })
      });
    });
  }

  /**
   * Capture screenshot with timestamp and test info
   */
  static async captureScreenshot(
    page: Page,
    testName: string,
    step?: string
  ): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${testName}${step ? `-${step}` : ''}-${timestamp}.png`;
    const path = `test-results/screenshots/${filename}`;
    
    await page.screenshot({
      path,
      fullPage: true
    });
    
    return path;
  }

  /**
   * Wait for network idle state
   */
  static async waitForNetworkIdle(page: Page, timeout: number = 30000): Promise<void> {
    await page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Get element text content with fallback
   */
  static async getTextContent(page: Page, selector: string, fallback: string = ''): Promise<string> {
    try {
      const element = page.locator(selector).first();
      const text = await element.textContent();
      return text?.trim() || fallback;
    } catch (error) {
      return fallback;
    }
  }

  /**
   * Check if element exists without throwing
   */
  static async elementExists(page: Page, selector: string): Promise<boolean> {
    try {
      await page.locator(selector).first().waitFor({ timeout: 1000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Scroll element into view
   */
  static async scrollIntoView(page: Page, selector: string): Promise<void> {
    const element = page.locator(selector).first();
    await element.scrollIntoViewIfNeeded();
  }

  /**
   * Wait for multiple elements to be visible
   */
  static async waitForMultipleElements(
    page: Page,
    selectors: string[],
    timeout: number = 10000
  ): Promise<boolean[]> {
    const promises = selectors.map(selector =>
      page.locator(selector).first().isVisible({ timeout }).catch(() => false)
    );
    
    return await Promise.all(promises);
  }

  /**
   * Verify URL matches pattern
   */
  static async verifyUrlPattern(page: Page, pattern: RegExp | string): Promise<boolean> {
    const currentUrl = page.url();
    if (typeof pattern === 'string') {
      return currentUrl.includes(pattern);
    }
    return pattern.test(currentUrl);
  }

  /**
   * Handle file downloads
   */
  static async handleDownload(
    page: Page,
    triggerAction: () => Promise<void>
  ): Promise<{ path: string; filename: string } | null> {
    try {
      const downloadPromise = page.waitForEvent('download', { timeout: 30000 });
      
      await triggerAction();
      
      const download = await downloadPromise;
      const filename = download.suggestedFilename();
      const path = `test-results/downloads/${filename}`;
      
      await download.saveAs(path);
      
      return { path, filename };
    } catch (error) {
      console.error('Download failed:', error);
      return null;
    }
  }

  /**
   * Handle new window/tab opening
   */
  static async handleNewWindow(
    page: Page,
    triggerAction: () => Promise<void>
  ): Promise<Page | null> {
    try {
      const newPagePromise = page.context().waitForEvent('page', { timeout: 10000 });
      
      await triggerAction();
      
      const newPage = await newPagePromise;
      await newPage.waitForLoadState('networkidle', { timeout: 30000 });
      
      return newPage;
    } catch (error) {
      console.error('New window handling failed:', error);
      return null;
    }
  }

  /**
   * Verify accessibility attributes
   */
  static async verifyAccessibility(page: Page, selector: string): Promise<{
    hasRole: boolean;
    hasLabel: boolean;
    isFocusable: boolean;
  }> {
    const element = page.locator(selector).first();
    
    const [role, label, tabIndex] = await Promise.all([
      element.getAttribute('role').catch(() => null),
      Promise.all([
        element.getAttribute('aria-label').catch(() => null),
        element.getAttribute('aria-labelledby').catch(() => null),
        element.locator('label').first().textContent().catch(() => null)
      ]),
      element.getAttribute('tabindex').catch(() => null)
    ]);
    
    const hasLabel = label.some(l => l !== null);
    const isFocusable = tabIndex !== null || 
      await element.evaluate(el => {
        const focusable = ['button', 'input', 'select', 'textarea', 'a'];
        return focusable.includes(el.tagName.toLowerCase());
      }).catch(() => false);

    return {
      hasRole: role !== null,
      hasLabel,
      isFocusable
    };
  }

  /**
   * Performance measurement utilities
   */
  static async measurePerformance<T>(
    operation: () => Promise<T>,
    label: string = 'Operation'
  ): Promise<{ result: T; duration: number }> {
    const startTime = Date.now();
    const result = await operation();
    const duration = Date.now() - startTime;
    
    console.log(`${label} took ${duration}ms`);
    
    return { result, duration };
  }

  /**
   * Retry operation with exponential backoff
   */
  static async retryWithBackoff<T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> {
    let lastError: Error;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (i === maxRetries - 1) {
          throw lastError;
        }
        
        const delay = baseDelay * Math.pow(2, i);
        console.log(`Retry ${i + 1}/${maxRetries} in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    
    throw lastError!;
  }

  /**
   * Generate random test data
   */
  static generateRandomString(length: number = 10): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  /**
   * Generate random Korean text for testing
   */
  static generateRandomKoreanText(sentences: number = 3): string {
    const subjects = ['학생들은', '교사는', '수업에서는', '우리는'];
    const verbs = ['공부했습니다', '배웠습니다', '토론했습니다', '발표했습니다'];
    const objects = ['수학을', '과학을', '국어를', '영어를'];
    
    const result = [];
    for (let i = 0; i < sentences; i++) {
      const subject = subjects[Math.floor(Math.random() * subjects.length)];
      const object = objects[Math.floor(Math.random() * objects.length)];
      const verb = verbs[Math.floor(Math.random() * verbs.length)];
      result.push(`${subject} ${object} ${verb}.`);
    }
    
    return result.join(' ');
  }

  /**
   * Clean up test artifacts
   */
  static async cleanup(page: Page, context: BrowserContext): Promise<void> {
    try {
      // Clear any remaining routes
      await page.unrouteAll();
      
      // Remove event listeners
      page.removeAllListeners();
      
      // Close any additional pages in context
      const pages = context.pages();
      for (const p of pages) {
        if (p !== page && !p.isClosed()) {
          await p.close();
        }
      }
    } catch (error) {
      console.warn('Cleanup warning:', error);
    }
  }
}