import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

/**
 * Page Object for Reports page (/reports)
 * Handles report generation, templates, and data export functionality
 */
export class ReportsPage extends BasePage {
  // Report template buttons
  readonly comprehensiveReportButton: Locator;
  readonly summaryReportButton: Locator;
  readonly downloadJsonButton: Locator;

  // Template cards
  readonly comprehensiveTemplateCard: Locator;
  readonly summaryTemplateCard: Locator;
  readonly jsonExportCard: Locator;

  // Feature sections
  readonly reportFeaturesSection: Locator;
  readonly visualAnalysisCard: Locator;
  readonly mobileOptimizationCard: Locator;
  readonly beautifulDesignCard: Locator;

  // Usage sections
  readonly usageMethodsSection: Locator;
  readonly personalUsageSection: Locator;
  readonly institutionalUsageSection: Locator;

  // Information notice
  readonly informationNotice: Locator;
  readonly transcriptionLink: Locator;
  readonly analysisLink: Locator;

  constructor(page: Page) {
    super(page);

    // Report template buttons
    this.comprehensiveReportButton = page.locator('button:has-text("📄 종합 보고서 보기")');
    this.summaryReportButton = page.locator('button:has-text("📋 요약 보고서 보기")');
    this.downloadJsonButton = page.locator('button:has-text("📥 JSON 다운로드")');

    // Template cards
    this.comprehensiveTemplateCard = page.locator('.card:has(h4:has-text("📄 종합 보고서"))');
    this.summaryTemplateCard = page.locator('.card:has(h4:has-text("📋 요약 보고서"))');
    this.jsonExportCard = page.locator('.card:has(h4:has-text("🔄 JSON 형식"))');

    // Feature sections
    this.reportFeaturesSection = page.locator('h3:has-text("🎨 보고서 특징")').locator('..');
    this.visualAnalysisCard = this.reportFeaturesSection.locator('.card:has(h4:has-text("📊 시각적 분석"))');
    this.mobileOptimizationCard = this.reportFeaturesSection.locator('.card:has(h4:has-text("📱 모바일 최적화"))');
    this.beautifulDesignCard = this.reportFeaturesSection.locator('.card:has(h4:has-text("🎨 아름다운 디자인"))');

    // Usage sections
    this.usageMethodsSection = page.locator('h3:has-text("📈 활용 방법")').locator('..');
    this.personalUsageSection = this.usageMethodsSection.locator('div:has(h4:has-text("🎯 개인 활용"))');
    this.institutionalUsageSection = this.usageMethodsSection.locator('div:has(h4:has-text("🏫 기관 활용"))');

    // Information notice
    this.informationNotice = page.locator('.status-info:has-text("💡 안내:")');
    this.transcriptionLink = this.informationNotice.locator('a[href="/transcription"]');
    this.analysisLink = this.informationNotice.locator('a[href="/analysis"]');
  }

  /**
   * Navigate to reports page
   */
  async goto() {
    await super.goto('/reports');
  }

  /**
   * Click comprehensive report button and handle new window
   */
  async clickComprehensiveReport(): Promise<Page | null> {
    const newPagePromise = this.page.context().waitForEvent('page');
    
    try {
      await this.clickButton(this.comprehensiveReportButton);
      const newPage = await newPagePromise;
      await newPage.waitForLoadState('networkidle');
      return newPage;
    } catch (error) {
      console.error('Failed to open comprehensive report:', error);
      return null;
    }
  }

  /**
   * Click summary report button and handle new window
   */
  async clickSummaryReport(): Promise<Page | null> {
    const newPagePromise = this.page.context().waitForEvent('page');
    
    try {
      await this.clickButton(this.summaryReportButton);
      const newPage = await newPagePromise;
      await newPage.waitForLoadState('networkidle');
      return newPage;
    } catch (error) {
      console.error('Failed to open summary report:', error);
      return null;
    }
  }

  /**
   * Click JSON download button and verify download
   */
  async clickDownloadJson(): Promise<boolean> {
    try {
      // Set up download handling
      const downloadPromise = this.page.waitForEvent('download');
      
      await this.clickButton(this.downloadJsonButton);
      
      const download = await downloadPromise;
      const filename = download.suggestedFilename();
      
      // Verify filename format
      const expectedPattern = /^analysis-sample-cbil-001\.json$/;
      const isValidFilename = expectedPattern.test(filename);
      
      if (isValidFilename) {
        // Save download to verify content
        const downloadPath = `test-results/downloads/${filename}`;
        await download.saveAs(downloadPath);
        
        // Verify file was downloaded
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Failed to download JSON:', error);
      return false;
    }
  }

  /**
   * Verify downloaded JSON content
   */
  async verifyJsonDownloadContent(filePath: string): Promise<boolean> {
    try {
      const fs = require('fs').promises;
      const content = await fs.readFile(filePath, 'utf-8');
      const jsonData = JSON.parse(content);
      
      // Verify required fields exist
      const requiredFields = [
        'analysis_id',
        'framework',
        'framework_name',
        'analysis',
        'character_count',
        'word_count',
        'created_at'
      ];
      
      for (const field of requiredFields) {
        if (!(field in jsonData)) {
          console.error(`Missing required field: ${field}`);
          return false;
        }
      }
      
      // Verify sample data values
      if (jsonData.analysis_id !== 'sample-cbil-001') {
        console.error('Incorrect analysis_id in downloaded JSON');
        return false;
      }
      
      if (jsonData.framework !== 'cbil') {
        console.error('Incorrect framework in downloaded JSON');
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Failed to verify JSON content:', error);
      return false;
    }
  }

  /**
   * Verify comprehensive report window content
   */
  async verifyComprehensiveReportContent(reportPage: Page): Promise<boolean> {
    try {
      await reportPage.waitForLoadState('networkidle');
      
      // Check for key elements in the report
      const title = await reportPage.locator('title').textContent();
      if (!title?.includes('개념기반 탐구 수업(CBIL) 분석')) {
        console.error('Report title is incorrect');
        return false;
      }
      
      // Check for analysis content
      const hasAnalysisContent = await reportPage.locator('text=CBIL 7단계 분석').isVisible();
      if (!hasAnalysisContent) {
        console.error('Analysis content not found in report');
        return false;
      }
      
      // Check for charts or visualizations (comprehensive report should have them)
      const hasCharts = await reportPage.locator('canvas, svg').count() > 0;
      if (!hasCharts) {
        console.warn('No charts found in comprehensive report');
      }
      
      return true;
    } catch (error) {
      console.error('Failed to verify comprehensive report content:', error);
      return false;
    }
  }

  /**
   * Verify summary report window content
   */
  async verifySummaryReportContent(reportPage: Page): Promise<boolean> {
    try {
      await reportPage.waitForLoadState('networkidle');
      
      // Check for key elements in the report
      const title = await reportPage.locator('title').textContent();
      if (!title?.includes('개념기반 탐구 수업(CBIL) 분석')) {
        console.error('Report title is incorrect');
        return false;
      }
      
      // Check for analysis content
      const hasAnalysisContent = await reportPage.locator('text=CBIL 7단계 분석').isVisible();
      if (!hasAnalysisContent) {
        console.error('Analysis content not found in report');
        return false;
      }
      
      // Summary report should be more concise
      const bodyText = await reportPage.locator('body').textContent();
      const wordCount = bodyText?.split(' ').length || 0;
      
      // Summary should be shorter than comprehensive
      console.log(`Summary report word count: ${wordCount}`);
      
      return true;
    } catch (error) {
      console.error('Failed to verify summary report content:', error);
      return false;
    }
  }

  /**
   * Click transcription link in information notice
   */
  async clickTranscriptionLink() {
    await this.clickButton(this.transcriptionLink, { waitForNavigation: true });
  }

  /**
   * Click analysis link in information notice
   */
  async clickAnalysisLink() {
    await this.clickButton(this.analysisLink, { waitForNavigation: true });
  }

  /**
   * Get template card descriptions
   */
  async getTemplateDescriptions(): Promise<{comprehensive: string, summary: string, json: string}> {
    const comprehensive = await this.getTextContent(this.comprehensiveTemplateCard.locator('p'));
    const summary = await this.getTextContent(this.summaryTemplateCard.locator('p'));
    const json = await this.getTextContent(this.jsonExportCard.locator('p'));
    
    return { comprehensive, summary, json };
  }

  /**
   * Get feature card information
   */
  async getFeatureInformation(): Promise<Array<{title: string, description: string, features: string[]}>> {
    const featureCards = [this.visualAnalysisCard, this.mobileOptimizationCard, this.beautifulDesignCard];
    const features = [];
    
    for (const card of featureCards) {
      const title = await this.getTextContent(card.locator('h4'));
      const description = await this.getTextContent(card.locator('p'));
      
      const featureItems = await card.locator('ul li').all();
      const featureList = [];
      for (const item of featureItems) {
        featureList.push(await this.getTextContent(item));
      }
      
      features.push({ title, description, features: featureList });
    }
    
    return features;
  }

  /**
   * Get usage method information
   */
  async getUsageMethodInformation(): Promise<{personal: string[], institutional: string[]}> {
    const personalItems = await this.personalUsageSection.locator('ul li').all();
    const institutionalItems = await this.institutionalUsageSection.locator('ul li').all();
    
    const personal = [];
    for (const item of personalItems) {
      personal.push(await this.getTextContent(item));
    }
    
    const institutional = [];
    for (const item of institutionalItems) {
      institutional.push(await this.getTextContent(item));
    }
    
    return { personal, institutional };
  }

  /**
   * Verify all template buttons are functional
   */
  async verifyTemplateButtonsFunctionality(): Promise<{comprehensive: boolean, summary: boolean, json: boolean}> {
    // Test comprehensive report
    const comprehensiveWorks = await this.testReportGeneration('comprehensive');
    
    // Test summary report
    const summaryWorks = await this.testReportGeneration('summary');
    
    // Test JSON download
    const jsonWorks = await this.clickDownloadJson();
    
    return {
      comprehensive: comprehensiveWorks,
      summary: summaryWorks,
      json: jsonWorks
    };
  }

  /**
   * Test report generation functionality
   */
  private async testReportGeneration(type: 'comprehensive' | 'summary'): Promise<boolean> {
    try {
      let reportPage: Page | null = null;
      
      if (type === 'comprehensive') {
        reportPage = await this.clickComprehensiveReport();
      } else {
        reportPage = await this.clickSummaryReport();
      }
      
      if (!reportPage) {
        return false;
      }
      
      // Verify content
      const isValid = type === 'comprehensive' 
        ? await this.verifyComprehensiveReportContent(reportPage)
        : await this.verifySummaryReportContent(reportPage);
      
      // Close the report page
      await reportPage.close();
      
      return isValid;
    } catch (error) {
      console.error(`Failed to test ${type} report generation:`, error);
      return false;
    }
  }

  /**
   * Verify page elements are present
   */
  async verifyPageElements() {
    await expect(this.pageTitle).toBeVisible();
    await expect(this.pageTitle).toHaveText('분석 보고서');
    await expect(this.pageSubtitle).toContainText('아름다운 HTML 보고서로 분석 결과를 확인하세요');
    
    // Template cards
    await expect(this.comprehensiveTemplateCard).toBeVisible();
    await expect(this.summaryTemplateCard).toBeVisible();
    await expect(this.jsonExportCard).toBeVisible();
    
    // Feature sections
    await expect(this.reportFeaturesSection).toBeVisible();
    await expect(this.visualAnalysisCard).toBeVisible();
    await expect(this.mobileOptimizationCard).toBeVisible();
    await expect(this.beautifulDesignCard).toBeVisible();
    
    // Usage sections
    await expect(this.usageMethodsSection).toBeVisible();
    await expect(this.personalUsageSection).toBeVisible();
    await expect(this.institutionalUsageSection).toBeVisible();
    
    // Information notice
    await expect(this.informationNotice).toBeVisible();
    await expect(this.transcriptionLink).toBeVisible();
    await expect(this.analysisLink).toBeVisible();
  }

  /**
   * Wait for reports to load (if they require backend data)
   */
  async waitForReportsLoad() {
    // Wait for any loading states to complete
    await this.waitForLoading();
    
    // Ensure all buttons are enabled
    await expect(this.comprehensiveReportButton).toBeEnabled();
    await expect(this.summaryReportButton).toBeEnabled();
    await expect(this.downloadJsonButton).toBeEnabled();
  }

  /**
   * Verify navigation links work correctly
   */
  async verifyNavigationLinks(): Promise<{transcription: boolean, analysis: boolean}> {
    try {
      // Test transcription link
      const currentUrl = this.page.url();
      await this.clickTranscriptionLink();
      await this.page.waitForURL('**/transcription');
      const transcriptionWorks = this.page.url().includes('/transcription');
      
      // Navigate back
      await this.page.goBack();
      await this.page.waitForURL(currentUrl);
      
      // Test analysis link
      await this.clickAnalysisLink();
      await this.page.waitForURL('**/analysis');
      const analysisWorks = this.page.url().includes('/analysis');
      
      // Navigate back
      await this.page.goBack();
      await this.page.waitForURL(currentUrl);
      
      return {
        transcription: transcriptionWorks,
        analysis: analysisWorks
      };
    } catch (error) {
      console.error('Failed to verify navigation links:', error);
      return { transcription: false, analysis: false };
    }
  }
}