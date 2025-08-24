import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object for Analysis page (/analysis)
 * Handles text analysis, framework selection, and parallel analysis
 */
export class AnalysisPage extends BasePage {
  // Form elements
  readonly parallelAnalysisCheckbox: Locator;
  readonly frameworkSelector: Locator;
  readonly textInput: Locator;
  readonly submitButton: Locator;
  readonly textStats: Locator;

  // Single analysis status
  readonly analysisStatusSection: Locator;
  readonly analysisId: Locator;
  readonly analysisStatus: Locator;
  readonly analysisFramework: Locator;
  readonly analysisMessage: Locator;

  // Single analysis results
  readonly analysisResults: Locator;
  readonly analysisInfoCard: Locator;
  readonly analysisSettingsCard: Locator;
  readonly analysisContent: Locator;
  readonly generateReportButton: Locator;
  readonly reportsListButton: Locator;

  // Parallel analysis results
  readonly parallelResultsSection: Locator;
  readonly parallelStatusButton: Locator;
  readonly comprehensiveReportButton: Locator;

  // Framework information
  readonly frameworkGuideSection: Locator;
  readonly cbilCard: Locator;
  readonly dialogueCard: Locator;
  readonly coachingCard: Locator;

  // Transcription data notification
  readonly transcriptionNotification: Locator;

  constructor(page: Page) {
    super(page);

    // Form elements
    this.parallelAnalysisCheckbox = page.locator('input[type="checkbox"]');
    this.frameworkSelector = page.locator('select.form-select');
    this.textInput = page.locator('textarea.form-textarea');
    this.submitButton = page.locator('button.btn-large');
    this.textStats = page.locator('small:has-text("문자")');

    // Single analysis status
    this.analysisStatusSection = page.locator('h3:has-text("분석 진행 상황")').locator('..');
    this.analysisId = page.locator('text="분석 ID:"');
    this.analysisStatus = page.locator('text="상태:"').locator('..');
    this.analysisFramework = page.locator('text="프레임워크:"');
    this.analysisMessage = page.locator('text="메시지:"');

    // Single analysis results
    this.analysisResults = page.locator('.card:has(h4:has-text("📝 분석 결과"))');
    this.analysisInfoCard = page.locator('.card:has(h4:has-text("📊 분석 정보"))');
    this.analysisSettingsCard = page.locator('.card:has(h4:has-text("⚙️ 분석 설정"))');
    this.analysisContent = this.analysisResults.locator('div[style*="backgroundColor"]');
    this.generateReportButton = page.locator('button:has-text("📄 HTML 보고서 생성")');
    this.reportsListButton = page.locator('a:has-text("📊 보고서 목록")');

    // Parallel analysis results
    this.parallelResultsSection = page.locator('h3:has-text("🧠 병렬 분석 결과")').locator('..');
    this.parallelStatusButton = page.locator('button:has-text("📊 분석 현황")');
    this.comprehensiveReportButton = page.locator('button:has-text("📄 종합 보고서 생성")');

    // Framework information
    this.frameworkGuideSection = page.locator('h3:has-text("📋 분석 프레임워크 안내")').locator('..');
    this.cbilCard = this.frameworkGuideSection.locator('.card:has(h4:has-text("🎯 CBIL"))');
    this.dialogueCard = this.frameworkGuideSection.locator('.card:has(h4:has-text("💬 학생주도 토론"))');
    this.coachingCard = this.frameworkGuideSection.locator('.card:has(h4:has-text("📚 수업 코칭"))');

    // Transcription data notification
    this.transcriptionNotification = page.locator('.status-info:has-text("🎬 전사 완료!")');
  }

  /**
   * Navigate to analysis page
   */
  async goto() {
    await super.goto('/analysis');
  }

  /**
   * Check if parallel analysis mode is enabled
   */
  async isParallelAnalysisEnabled(): Promise<boolean> {
    return await this.parallelAnalysisCheckbox.isChecked();
  }

  /**
   * Toggle parallel analysis mode
   */
  async toggleParallelAnalysis() {
    await this.parallelAnalysisCheckbox.click();
  }

  /**
   * Enable parallel analysis mode
   */
  async enableParallelAnalysis() {
    if (!(await this.isParallelAnalysisEnabled())) {
      await this.toggleParallelAnalysis();
    }
  }

  /**
   * Disable parallel analysis mode
   */
  async disableParallelAnalysis() {
    if (await this.isParallelAnalysisEnabled()) {
      await this.toggleParallelAnalysis();
    }
  }

  /**
   * Select analysis framework (only available when parallel mode is off)
   */
  async selectFramework(frameworkId: string) {
    await this.selectOption(this.frameworkSelector, frameworkId);
  }

  /**
   * Get currently selected framework
   */
  async getSelectedFramework(): Promise<string> {
    return await this.frameworkSelector.inputValue();
  }

  /**
   * Get available frameworks
   */
  async getAvailableFrameworks(): Promise<Array<{value: string, text: string}>> {
    const options = await this.frameworkSelector.locator('option').all();
    const frameworks = [];
    
    for (const option of options) {
      const value = await option.getAttribute('value') || '';
      const text = await option.textContent() || '';
      frameworks.push({ value, text });
    }
    
    return frameworks;
  }

  /**
   * Enter text for analysis
   */
  async enterAnalysisText(text: string) {
    await this.fillField(this.textInput, text, { clear: true });
  }

  /**
   * Get current text content
   */
  async getAnalysisText(): Promise<string> {
    return await this.textInput.inputValue();
  }

  /**
   * Get text statistics (character and word count)
   */
  async getTextStatistics(): Promise<{ characters: number, words: number }> {
    const statsText = await this.getTextContent(this.textStats);
    const characterMatch = statsText.match(/([\d,]+)\s*문자/);
    const wordMatch = statsText.match(/약\s*([\d,]+)\s*단어/);
    
    return {
      characters: characterMatch ? parseInt(characterMatch[1].replace(/,/g, '')) : 0,
      words: wordMatch ? parseInt(wordMatch[1].replace(/,/g, '')) : 0
    };
  }

  /**
   * Click submit analysis button
   */
  async submitAnalysis() {
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
   * Wait for analysis status section to appear
   */
  async waitForAnalysisStatus() {
    await this.waitForElement(this.analysisStatusSection, 15000);
  }

  /**
   * Get analysis ID
   */
  async getAnalysisId(): Promise<string> {
    const text = await this.getTextContent(this.analysisId);
    return text.replace('분석 ID:', '').trim();
  }

  /**
   * Get current analysis status
   */
  async getAnalysisStatus(): Promise<string> {
    await this.waitForElement(this.analysisStatus);
    const statusElement = this.analysisStatus.locator('span[style*="color"]');
    return await this.getTextContent(statusElement);
  }

  /**
   * Get analysis framework
   */
  async getAnalysisFramework(): Promise<string> {
    const text = await this.getTextContent(this.analysisFramework);
    return text.replace('프레임워크:', '').trim();
  }

  /**
   * Get analysis message
   */
  async getAnalysisMessage(): Promise<string> {
    const text = await this.getTextContent(this.analysisMessage);
    return text.replace('메시지:', '').trim();
  }

  /**
   * Wait for analysis to complete
   */
  async waitForAnalysisComplete(timeout: number = 90000) {
    await expect(this.analysisStatus.locator('span:has-text("완료")')).toBeVisible({ timeout });
  }

  /**
   * Wait for processing to start
   */
  async waitForProcessingStart() {
    await expect(this.analysisStatus.locator('span:has-text("분석 중")')).toBeVisible({ timeout: 15000 });
  }

  /**
   * Check if analysis failed
   */
  async isAnalysisFailed(): Promise<boolean> {
    try {
      await this.analysisStatus.locator('span:has-text("실패")').waitFor({ timeout: 2000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get analysis result content
   */
  async getAnalysisResult(): Promise<string> {
    await this.waitForElement(this.analysisContent);
    return await this.getTextContent(this.analysisContent);
  }

  /**
   * Get analysis info (framework name, created date, character count)
   */
  async getAnalysisInfo(): Promise<{framework: string, date: string, characterCount: string}> {
    await this.waitForElement(this.analysisInfoCard);
    const infoText = await this.getTextContent(this.analysisInfoCard);
    
    const frameworkMatch = infoText.match(/프레임워크:\s*([\s\S]*?)생성일:/);
    const dateMatch = infoText.match(/생성일:\s*([\s\S]*?)분석 문자 수:/);
    const countMatch = infoText.match(/분석 문자 수:\s*([\d,]+)/);
    
    return {
      framework: frameworkMatch ? frameworkMatch[1].trim() : '',
      date: dateMatch ? dateMatch[1].trim() : '',
      characterCount: countMatch ? countMatch[1].trim() : ''
    };
  }

  /**
   * Get analysis settings (model, temperature, language)
   */
  async getAnalysisSettings(): Promise<{model: string, temperature: string, language: string}> {
    await this.waitForElement(this.analysisSettingsCard);
    const settingsText = await this.getTextContent(this.analysisSettingsCard);
    
    const modelMatch = settingsText.match(/모델:\s*([\s\S]*?)온도:/);
    const tempMatch = settingsText.match(/온도:\s*([\s\S]*?)언어:/);
    const langMatch = settingsText.match(/언어:\s*([\s\S]*?)$/);
    
    return {
      model: modelMatch ? modelMatch[1].trim() : '',
      temperature: tempMatch ? tempMatch[1].trim() : '',
      language: langMatch ? langMatch[1].trim() : ''
    };
  }

  /**
   * Click generate HTML report button
   */
  async clickGenerateReport() {
    await this.clickButton(this.generateReportButton);
  }

  /**
   * Click reports list button
   */
  async clickReportsList() {
    await this.clickButton(this.reportsListButton, { waitForNavigation: true });
  }

  /**
   * Check if parallel results section is visible
   */
  async isParallelResultsVisible(): Promise<boolean> {
    return await this.parallelResultsSection.isVisible();
  }

  /**
   * Get parallel analysis results count
   */
  async getParallelResultsCount(): Promise<number> {
    const headerText = await this.getTextContent(this.parallelResultsSection.locator('h3'));
    const match = headerText.match(/\((\d+)개 프레임워크\)/);
    return match ? parseInt(match[1]) : 0;
  }

  /**
   * Get parallel analysis framework results
   */
  async getParallelFrameworkResults(): Promise<Array<{framework: string, status: string}>> {
    const frameworkCards = await this.parallelResultsSection.locator('.card').all();
    const results = [];
    
    for (const card of frameworkCards) {
      const headerText = await this.getTextContent(card.locator('h4'));
      const statusMatch = headerText.match(/(.+?)\s+(완료|실패|분석 중|대기 중)$/);
      
      if (statusMatch) {
        results.push({
          framework: statusMatch[1].trim(),
          status: statusMatch[2]
        });
      }
    }
    
    return results;
  }

  /**
   * Click on a parallel analysis framework result to expand
   */
  async expandParallelResult(frameworkName: string) {
    const card = this.parallelResultsSection.locator('.card', { hasText: frameworkName });
    const header = card.locator('div[style*="cursor"]');
    await header.click();
  }

  /**
   * Click parallel analysis status button
   */
  async clickParallelStatus() {
    await this.handleAlert(); // Handle the alert that shows status
    await this.clickButton(this.parallelStatusButton);
  }

  /**
   * Click comprehensive report generation button
   */
  async clickComprehensiveReport() {
    await this.handleAlert(); // Handle the alert about report generation
    await this.clickButton(this.comprehensiveReportButton);
  }

  /**
   * Check if transcription notification is visible
   */
  async isTranscriptionNotificationVisible(): Promise<boolean> {
    return await this.transcriptionNotification.isVisible();
  }

  /**
   * Get transcription notification details
   */
  async getTranscriptionNotificationDetails(): Promise<{videoId: string, characterCount: string, method: string}> {
    const notificationText = await this.getTextContent(this.transcriptionNotification);
    
    const videoMatch = notificationText.match(/영상 ID:\s*([^\s|]+)/);
    const countMatch = notificationText.match(/문자수:\s*([\d,]+)/);
    const methodMatch = notificationText.match(/추출 방법:\s*(.+)/);
    
    return {
      videoId: videoMatch ? videoMatch[1].trim() : '',
      characterCount: countMatch ? countMatch[1].trim() : '',
      method: methodMatch ? methodMatch[1].trim() : ''
    };
  }

  /**
   * Verify page elements are present
   */
  async verifyPageElements() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.pageTitle).toHaveText('교육 분석');
    await expect(this.pageSubtitle).toContainText('다양한 프레임워크로 교사 발화를 분석합니다');
    
    // Form elements
    await expect(this.parallelAnalysisCheckbox).toBeVisible();
    await expect(this.textInput).toBeVisible();
    await expect(this.submitButton).toBeVisible();
    
    // Framework guide
    await expect(this.frameworkGuideSection).toBeVisible();
    await expect(this.cbilCard).toBeVisible();
    await expect(this.dialogueCard).toBeVisible();
    await expect(this.coachingCard).toBeVisible();
  }

  /**
   * Poll analysis status until completion or failure
   */
  async pollAnalysisStatus(maxRetries: number = 30): Promise<'completed' | 'failed' | 'timeout'> {
    for (let i = 0; i < maxRetries; i++) {
      const status = await this.getAnalysisStatus();
      
      if (status === '완료') {
        return 'completed';
      } else if (status === '실패') {
        return 'failed';
      }
      
      // Wait 3 seconds before next check (matches frontend polling)
      await this.page.waitForTimeout(3000);
    }
    
    return 'timeout';
  }

  /**
   * Wait for new window to open (for report generation)
   */
  async waitForNewWindow(): Promise<Page> {
    const newPagePromise = this.page.context().waitForEvent('page');
    return await newPagePromise;
  }

  /**
   * Verify framework selector is visible/hidden based on parallel mode
   */
  async verifyFrameworkSelectorVisibility() {
    const isParallel = await this.isParallelAnalysisEnabled();
    
    if (isParallel) {
      // Framework selector should be hidden in parallel mode
      await expect(this.frameworkSelector).toBeHidden();
    } else {
      // Framework selector should be visible in single mode
      await expect(this.frameworkSelector).toBeVisible();
    }
  }
}