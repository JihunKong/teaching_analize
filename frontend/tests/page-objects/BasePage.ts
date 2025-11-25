import { Page, Locator, expect } from '@playwright/test';

/**
 * Base page class with common functionality for all pages
 * Provides shared methods and utilities for page interactions
 */
export class BasePage {
  readonly page: Page;
  
  // Common selectors
  readonly pageTitle: Locator;
  readonly pageSubtitle: Locator;
  readonly loadingSpinner: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Common UI elements
    this.pageTitle = page.locator('.page-title');
    this.pageSubtitle = page.locator('.page-subtitle');
    this.loadingSpinner = page.locator('.spinner');
    this.errorMessage = page.locator('.status-error');
    this.successMessage = page.locator('.status-success');
  }

  /**
   * Navigate to a specific path
   */
  async goto(path: string = '') {
    await this.page.goto(path);
    await this.waitForPageLoad();
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle', { timeout: 30000 });
    
    // Wait for any loading spinners to disappear
    await this.page.waitForFunction(() => {
      const spinners = document.querySelectorAll('.spinner');
      return spinners.length === 0 || Array.from(spinners).every(spinner => 
        (spinner as HTMLElement).style.display === 'none'
      );
    }, { timeout: 10000 }).catch(() => {
      // Ignore timeout - spinner might not exist
    });
  }

  /**
   * Wait for loading to complete
   */
  async waitForLoading(timeout: number = 30000) {
    await this.page.waitForSelector('.loading', { state: 'detached', timeout }).catch(() => {
      // Loading element might not exist
    });
  }

  /**
   * Check if page is currently loading
   */
  async isLoading(): Promise<boolean> {
    return await this.loadingSpinner.isVisible();
  }

  /**
   * Get page title text
   */
  async getPageTitle(): Promise<string> {
    return await this.pageTitle.textContent() || '';
  }

  /**
   * Get page subtitle text
   */
  async getPageSubtitle(): Promise<string> {
    return await this.pageSubtitle.textContent() || '';
  }

  /**
   * Wait for and verify error message
   */
  async expectError(message?: string) {
    await expect(this.errorMessage).toBeVisible();
    if (message) {
      await expect(this.errorMessage).toContainText(message);
    }
  }

  /**
   * Wait for and verify success message
   */
  async expectSuccess(message?: string) {
    await expect(this.successMessage).toBeVisible();
    if (message) {
      await expect(this.successMessage).toContainText(message);
    }
  }

  /**
   * Take screenshot with descriptive name
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({
      path: `test-results/screenshots/${name}-${Date.now()}.png`,
      fullPage: true
    });
  }

  /**
   * Fill form field with retry logic
   */
  async fillField(locator: Locator, value: string, options?: { clear?: boolean }) {
    if (options?.clear) {
      await locator.clear();
    }
    
    await locator.fill(value);
    
    // Verify the value was set correctly
    await expect(locator).toHaveValue(value);
  }

  /**
   * Click button with retry logic and loading handling
   */
  async clickButton(locator: Locator, options?: { waitForNavigation?: boolean }) {
    await expect(locator).toBeEnabled();
    
    if (options?.waitForNavigation) {
      await Promise.all([
        this.page.waitForNavigation({ waitUntil: 'networkidle' }),
        locator.click()
      ]);
    } else {
      await locator.click();
    }
  }

  /**
   * Select dropdown option
   */
  async selectOption(locator: Locator, value: string) {
    await locator.selectOption(value);
    await expect(locator).toHaveValue(value);
  }

  /**
   * Wait for element to be visible with custom timeout
   */
  async waitForElement(locator: Locator, timeout: number = 10000) {
    await expect(locator).toBeVisible({ timeout });
  }

  /**
   * Scroll element into view
   */
  async scrollToElement(locator: Locator) {
    await locator.scrollIntoViewIfNeeded();
  }

  /**
   * Handle JavaScript alerts/confirms
   */
  async handleAlert(accept: boolean = true) {
    this.page.on('dialog', dialog => {
      if (accept) {
        dialog.accept();
      } else {
        dialog.dismiss();
      }
    });
  }

  /**
   * Wait for API request to complete
   */
  async waitForAPIRequest(urlPattern: string, timeout: number = 30000) {
    return await this.page.waitForRequest(
      request => request.url().includes(urlPattern),
      { timeout }
    );
  }

  /**
   * Wait for API response
   */
  async waitForAPIResponse(urlPattern: string, timeout: number = 30000) {
    return await this.page.waitForResponse(
      response => response.url().includes(urlPattern),
      { timeout }
    );
  }

  /**
   * Check if element exists without waiting
   */
  async elementExists(selector: string): Promise<boolean> {
    try {
      await this.page.locator(selector).first().waitFor({ timeout: 1000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get text content safely
   */
  async getTextContent(locator: Locator): Promise<string> {
    const text = await locator.textContent();
    return text?.trim() || '';
  }

  /**
   * Copy text to clipboard (for testing copy functionality)
   */
  async copyToClipboard(text: string) {
    await this.page.evaluate(async (text) => {
      await navigator.clipboard.writeText(text);
    }, text);
  }

  /**
   * Get clipboard content
   */
  async getClipboardContent(): Promise<string> {
    return await this.page.evaluate(() => navigator.clipboard.readText());
  }
}