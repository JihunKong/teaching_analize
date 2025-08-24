import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object for Transcription page (/transcription)
 * Handles YouTube URL input, language selection, and transcription processing
 */
export class TranscriptionPage extends BasePage {
  // Form elements
  readonly youtubeUrlInput: Locator;
  readonly languageSelector: Locator;
  readonly submitButton: Locator;

  // Job status elements
  readonly jobStatusSection: Locator;
  readonly jobId: Locator;
  readonly jobStatus: Locator;
  readonly jobMessage: Locator;

  // Results elements
  readonly transcriptResults: Locator;
  readonly transcriptTextarea: Locator;
  readonly statisticsSection: Locator;
  readonly videoInfoSection: Locator;
  readonly characterCount: Locator;
  readonly wordCount: Locator;
  readonly videoId: Locator;
  readonly methodUsed: Locator;

  // Action buttons
  readonly analyzeButton: Locator;
  readonly copyButton: Locator;

  // Guidance sections
  readonly supportedVideosSection: Locator;
  readonly cautionsSection: Locator;

  constructor(page: Page) {
    super(page);

    // Form elements
    this.youtubeUrlInput = page.locator('input[type="url"]');
    this.languageSelector = page.locator('select.form-select');
    this.submitButton = page.locator('button.btn-large');

    // Job status elements
    this.jobStatusSection = page.locator('h3:has-text("전사 진행 상황")').locator('..');
    this.jobId = page.locator('text="작업 ID:"').locator('..');
    this.jobStatus = page.locator('text="상태:"').locator('..');
    this.jobMessage = page.locator('text="메시지:"').locator('..');

    // Results elements
    this.transcriptResults = page.locator('.card:has(h4:has-text("📝 전사 결과"))');
    this.transcriptTextarea = page.locator('.form-textarea[readonly]');
    this.statisticsSection = page.locator('.card:has(h4:has-text("📊 통계"))');
    this.videoInfoSection = page.locator('.card:has(h4:has-text("🎬 영상 정보"))');
    this.characterCount = page.locator('text="문자 수:"');
    this.wordCount = page.locator('text="단어 수:"');
    this.videoId = page.locator('text="비디오 ID:"');
    this.methodUsed = page.locator('text="추출 방법:"');

    // Action buttons
    this.analyzeButton = page.locator('a.btn:has-text("🧠 분석하기")');
    this.copyButton = page.locator('button.btn-secondary:has-text("📋 복사하기")');

    // Guidance sections
    this.supportedVideosSection = page.locator('h4:has-text("✅ 지원되는 영상")');
    this.cautionsSection = page.locator('h4:has-text("⚠️ 주의사항")');
  }

  /**
   * Navigate to transcription page
   */
  async goto() {
    await super.goto('/transcription');
  }

  /**
   * Enter YouTube URL
   */
  async enterYouTubeURL(url: string) {
    await this.fillField(this.youtubeUrlInput, url, { clear: true });
  }

  /**
   * Select language for transcription
   */
  async selectLanguage(language: 'ko' | 'en' | 'ja' | 'zh') {
    await this.selectOption(this.languageSelector, language);
  }

  /**
   * Get currently selected language
   */
  async getSelectedLanguage(): Promise<string> {
    return await this.languageSelector.inputValue();
  }

  /**
   * Click submit transcription button
   */
  async submitTranscription() {
    await this.handleAlert(); // Handle any alerts that might appear
    await this.clickButton(this.submitButton);
  }

  /**
   * Check if submit button is enabled
   */
  async isSubmitButtonEnabled(): Promise<boolean> {
    return await this.submitButton.isEnabled();
  }

  /**
   * Get submit button text
   */
  async getSubmitButtonText(): Promise<string> {
    return await this.getTextContent(this.submitButton);
  }

  /**
   * Wait for job status to appear
   */
  async waitForJobStatus() {
    await this.waitForElement(this.jobStatusSection, 15000);
  }

  /**
   * Get job ID
   */
  async getJobId(): Promise<string> {
    const text = await this.getTextContent(this.jobId);
    return text.replace('작업 ID:', '').trim();
  }

  /**
   * Get current job status
   */
  async getJobStatus(): Promise<string> {
    await this.waitForElement(this.jobStatus);
    const statusElement = this.jobStatus.locator('span[style*="color"]');
    return await this.getTextContent(statusElement);
  }

  /**
   * Get job message
   */
  async getJobMessage(): Promise<string> {
    const text = await this.getTextContent(this.jobMessage);
    return text.replace('메시지:', '').trim();
  }

  /**
   * Wait for transcription to complete
   */
  async waitForTranscriptionComplete(timeout: number = 120000) {
    await expect(this.jobStatus.locator('span:has-text("완료")')).toBeVisible({ timeout });
  }

  /**
   * Wait for processing to start
   */
  async waitForProcessingStart() {
    await expect(this.jobStatus.locator('span:has-text("처리 중")')).toBeVisible({ timeout: 15000 });
  }

  /**
   * Check if transcription failed
   */
  async isTranscriptionFailed(): Promise<boolean> {
    try {
      await this.jobStatus.locator('span:has-text("실패")').waitFor({ timeout: 2000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get transcript text
   */
  async getTranscriptText(): Promise<string> {
    await this.waitForElement(this.transcriptTextarea);
    return await this.transcriptTextarea.inputValue();
  }

  /**
   * Get character count from statistics
   */
  async getCharacterCount(): Promise<number> {
    const text = await this.getTextContent(this.characterCount);
    const match = text.match(/문자 수:\s*([\d,]+)/);
    return match ? parseInt(match[1].replace(/,/g, '')) : 0;
  }

  /**
   * Get word count from statistics
   */
  async getWordCount(): Promise<number> {
    const text = await this.getTextContent(this.wordCount);
    const match = text.match(/단어 수:\s*([\d,]+)/);
    return match ? parseInt(match[1].replace(/,/g, '')) : 0;
  }

  /**
   * Get video ID from results
   */
  async getVideoId(): Promise<string> {
    const text = await this.getTextContent(this.videoId);
    return text.replace('비디오 ID:', '').trim();
  }

  /**
   * Get extraction method used
   */
  async getMethodUsed(): Promise<string> {
    const text = await this.getTextContent(this.methodUsed);
    return text.replace('추출 방법:', '').trim();
  }

  /**
   * Click analyze button
   */
  async clickAnalyzeButton() {
    await this.clickButton(this.analyzeButton, { waitForNavigation: true });
  }

  /**
   * Click copy button and verify clipboard
   */
  async clickCopyButton() {
    // Setup clipboard permission
    await this.page.context().grantPermissions(['clipboard-write', 'clipboard-read']);
    
    await this.clickButton(this.copyButton);
    
    // Handle the alert that appears after copying
    await this.handleAlert();
    
    // Wait a bit for clipboard operation
    await this.page.waitForTimeout(1000);
  }

  /**
   * Verify transcript was copied to clipboard
   */
  async verifyTranscriptCopied(): Promise<boolean> {
    const clipboardContent = await this.getClipboardContent();
    const transcriptText = await this.getTranscriptText();
    return clipboardContent === transcriptText;
  }

  /**
   * Check if results section is visible
   */
  async isResultsSectionVisible(): Promise<boolean> {
    return await this.transcriptResults.isVisible();
  }

  /**
   * Check if statistics section is visible
   */
  async isStatisticsSectionVisible(): Promise<boolean> {
    return await this.statisticsSection.isVisible();
  }

  /**
   * Check if video info section is visible
   */
  async isVideoInfoSectionVisible(): Promise<boolean> {
    return await this.videoInfoSection.isVisible();
  }

  /**
   * Verify page elements are present
   */
  async verifyPageElements() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.pageTitle).toHaveText('YouTube 전사');
    await expect(this.pageSubtitle).toContainText('YouTube 영상을 텍스트로 변환합니다');
    
    // Form elements
    await expect(this.youtubeUrlInput).toBeVisible();
    await expect(this.languageSelector).toBeVisible();
    await expect(this.submitButton).toBeVisible();
    
    // Guidance sections
    await expect(this.supportedVideosSection).toBeVisible();
    await expect(this.cautionsSection).toBeVisible();
  }

  /**
   * Validate YouTube URL format (client-side validation)
   */
  async validateYouTubeURL(url: string): Promise<boolean> {
    const youtubeRegex = /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/;
    return youtubeRegex.test(url);
  }

  /**
   * Wait for auto-navigation to analysis page
   */
  async waitForAutoNavigation() {
    // Wait for the navigation message to appear first
    await expect(this.page.locator('text="분석 페이지로 이동 중..."')).toBeVisible({ timeout: 5000 });
    
    // Wait for actual navigation
    await this.page.waitForURL('**/analysis', { timeout: 10000 });
  }

  /**
   * Poll job status until completion or failure
   */
  async pollJobStatus(maxRetries: number = 60): Promise<'completed' | 'failed' | 'timeout'> {
    for (let i = 0; i < maxRetries; i++) {
      const status = await this.getJobStatus();
      
      if (status === '완료') {
        return 'completed';
      } else if (status === '실패') {
        return 'failed';
      }
      
      // Wait 2 seconds before next check (matches frontend polling)
      await this.page.waitForTimeout(2000);
    }
    
    return 'timeout';
  }
}