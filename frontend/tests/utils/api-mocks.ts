import { Page } from '@playwright/test';
import { 
  mockTranscriptionResults, 
  mockFrameworks, 
  mockAnalysisResults, 
  mockReportData 
} from '../fixtures/test-data';

/**
 * API mock utilities for consistent test mocking
 * Provides reusable mock configurations for different scenarios
 */

export class ApiMocks {
  
  /**
   * Mock successful transcription flow
   */
  static async mockSuccessfulTranscription(
    page: Page, 
    customResult?: Partial<typeof mockTranscriptionResults.successful>
  ): Promise<void> {
    const result = { ...mockTranscriptionResults.successful, ...customResult };
    
    // Mock initial submission
    await page.route('/api/transcribe/youtube', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job_id: result.job_id,
          status: 'pending',
          message: 'Transcription request received'
        })
      });
    });

    // Mock status polling - first processing, then completed
    let pollCount = 0;
    await page.route(`/api/transcribe/${result.job_id}`, async route => {
      pollCount++;
      
      if (pollCount <= 2) {
        // First few polls return processing
        // Add delay before fulfilling
        await new Promise(resolve => setTimeout(resolve, 1000));
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            job_id: result.job_id,
            status: 'processing',
            message: 'Extracting transcript from YouTube...'
          })
        });
      } else {
        // Final poll returns completed
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(result),
          
        });
      }
    });
  }

  /**
   * Mock failed transcription
   */
  static async mockFailedTranscription(
    page: Page,
    errorMessage?: string
  ): Promise<void> {
    const jobId = 'test-failed-job';
    
    await page.route('/api/transcribe/youtube', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job_id: jobId,
          status: 'pending',
          message: 'Transcription started'
        })
      });
    });

    await page.route(`/api/transcribe/${jobId}`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job_id: jobId,
          status: 'failed',
          message: errorMessage || 'Video not found or private'
        }),
        
      });
    });
  }

  /**
   * Mock long-running transcription
   */
  static async mockLongTranscription(page: Page, duration: number = 10000): Promise<void> {
    const jobId = 'test-long-job';
    
    await page.route('/api/transcribe/youtube', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          job_id: jobId,
          status: 'pending',
          message: 'Processing long video'
        })
      });
    });

    let startTime = Date.now();
    await page.route(`/api/transcribe/${jobId}`, async route => {
      const elapsed = Date.now() - startTime;
      
      if (elapsed < duration) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            job_id: jobId,
            status: 'processing',
            message: `Processing... (${Math.round(elapsed / 1000)}s elapsed)`
          }),
          
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            ...mockTranscriptionResults.successful,
            job_id: jobId
          })
        });
      }
    });
  }

  /**
   * Mock frameworks API
   */
  static async mockFrameworks(
    page: Page,
    customFrameworks?: typeof mockFrameworks
  ): Promise<void> {
    const frameworks = customFrameworks || mockFrameworks;
    
    await page.route('/api/frameworks', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ frameworks }),
        
      });
    });
  }

  /**
   * Mock successful single analysis
   */
  static async mockSuccessfulAnalysis(
    page: Page,
    framework: keyof typeof mockAnalysisResults = 'cbil',
    customResult?: any
  ): Promise<void> {
    const result = customResult || mockAnalysisResults[framework];
    const analysisId = `test-${framework}-${Date.now()}`;
    
    // Mock analysis submission
    await page.route('/api/analyze/text', async route => {
      const body = await route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          analysis_id: analysisId,
          status: 'pending',
          message: 'Analysis started',
          framework: body.framework
        }),
        
      });
    });

    // Mock analysis status polling
    let pollCount = 0;
    await page.route(`/api/analyze/${analysisId}`, async route => {
      pollCount++;
      
      if (pollCount <= 2) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            analysis_id: analysisId,
            status: 'processing',
            message: 'Solar2 Pro AI is analyzing...',
            framework
          }),
          
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            analysis_id: analysisId,
            status: 'completed',
            message: 'Analysis completed',
            framework,
            result: {
              ...result,
              analysis_id: analysisId
            }
          }),
          
        });
      }
    });
  }

  /**
   * Mock parallel analysis for all frameworks
   */
  static async mockParallelAnalysis(page: Page): Promise<void> {
    // Mock frameworks first
    await this.mockFrameworks(page);
    
    // Mock analysis submissions for each framework
    await page.route('/api/analyze/text', async route => {
      const body = await route.request().postDataJSON();
      const framework = body.framework;
      const analysisId = `parallel-${framework}-${Date.now()}`;
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          analysis_id: analysisId,
          status: 'pending',
          message: 'Parallel analysis started',
          framework
        }),
        
      });
    });

    // Mock status polling for each framework
    mockFrameworks.forEach((fw, index) => {
      page.route(new RegExp(`/api/analyze/parallel-${fw.id}-\\d+`), async route => {
        const analysisId = route.request().url().split('/').pop()!;
        
        // Stagger completion times
        const delay = (index + 1) * 2000;
        
        setTimeout(async () => {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              analysis_id: analysisId,
              status: 'completed',
              message: 'Analysis completed',
              framework: fw.id,
              result: {
                ...mockAnalysisResults[fw.id as keyof typeof mockAnalysisResults],
                analysis_id: analysisId
              }
            })
          });
        }, delay);
      });
    });
  }

  /**
   * Mock failed analysis
   */
  static async mockFailedAnalysis(
    page: Page,
    errorMessage?: string
  ): Promise<void> {
    const analysisId = 'test-failed-analysis';
    
    await page.route('/api/analyze/text', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          analysis_id: analysisId,
          status: 'pending',
          message: 'Analysis started',
          framework: 'cbil'
        })
      });
    });

    await page.route(`/api/analyze/${analysisId}`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          analysis_id: analysisId,
          status: 'failed',
          message: errorMessage || 'Analysis failed due to processing error'
        }),
        
      });
    });
  }

  /**
   * Mock report generation
   */
  static async mockReportGeneration(
    page: Page,
    reportType: 'comprehensive' | 'summary' = 'comprehensive',
    shouldFail: boolean = false
  ): Promise<void> {
    await page.route('/api/reports/generate/html', async route => {
      const body = await route.request().postDataJSON();
      
      if (shouldFail) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Report generation failed'
          })
        });
        return;
      }

      const isComprehensive = body.template === 'comprehensive';
      const title = body.title || `${reportType} 보고서`;
      
      const htmlContent = `
        <!DOCTYPE html>
        <html lang="ko">
        <head>
          <title>${title}</title>
          <meta charset="utf-8">
          <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .chart-container { width: 100%; height: 300px; background: #f0f0f0; }
            ${isComprehensive ? 'canvas, svg { display: block; margin: 20px 0; }' : ''}
          </style>
        </head>
        <body>
          <h1>${title}</h1>
          <div class="content">
            <h2>CBIL 7단계 분석</h2>
            <p>분석 결과 내용이 여기에 표시됩니다.</p>
            ${isComprehensive ? '<canvas width="400" height="200"></canvas>' : ''}
            ${isComprehensive ? '<svg width="400" height="200"><rect width="100%" height="100%" fill="blue"/></svg>' : ''}
          </div>
          <div class="statistics">
            <p>문자 수: ${mockReportData.sample.character_count}</p>
            <p>단어 수: ${mockReportData.sample.word_count}</p>
          </div>
        </body>
        </html>
      `;

      // Add delay for report generation simulation
      await new Promise(resolve => setTimeout(resolve, reportType === 'comprehensive' ? 1500 : 800));
      
      await route.fulfill({
        status: 200,
        contentType: 'text/html; charset=utf-8',
        body: htmlContent
      });
    });
  }

  /**
   * Mock slow report generation
   */
  static async mockSlowReportGeneration(
    page: Page,
    delay: number = 5000
  ): Promise<void> {
    await page.route('/api/reports/generate/html', async route => {
      await new Promise(resolve => setTimeout(resolve, delay));
      
      await route.fulfill({
        status: 200,
        contentType: 'text/html',
        body: '<html><head><title>Slow Report</title></head><body><h1>Generated after delay</h1></body></html>'
      });
    });
  }

  /**
   * Mock API server errors
   */
  static async mockServerErrors(page: Page): Promise<void> {
    // Mock various server errors
    await page.route('/api/transcribe/youtube', async route => {
      const body = await route.request().postDataJSON();
      if (body.youtube_url?.includes('error')) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal server error' })
        });
      } else {
        await route.continue();
      }
    });

    await page.route('/api/analyze/text', async route => {
      const body = await route.request().postDataJSON();
      if (body.text?.includes('error')) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Analysis service error' })
        });
      } else {
        await route.continue();
      }
    });

    await page.route('/api/frameworks', async route => {
      const headers = route.request().headers();
      if (headers['x-trigger-error']) {
        await route.fulfill({
          status: 503,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Service unavailable' })
        });
      } else {
        await route.continue();
      }
    });
  }

  /**
   * Mock network timeouts
   */
  static async mockNetworkTimeouts(page: Page, endpoints: string[]): Promise<void> {
    for (const endpoint of endpoints) {
      await page.route(endpoint, async route => {
        // Simulate network timeout by never responding
        await new Promise(() => {}); // This will never resolve
      });
    }
  }

  /**
   * Clear all mocks
   */
  static async clearAllMocks(page: Page): Promise<void> {
    await page.unrouteAll();
  }

  /**
   * Mock session storage data for transcription integration
   */
  static async mockTranscriptionSessionData(
    page: Page,
    data: {
      transcript: string;
      video_id: string;
      character_count: number;
      word_count: number;
      method_used: string;
      auto_analyze?: boolean;
    }
  ): Promise<void> {
    await page.addInitScript((transcriptData) => {
      sessionStorage.setItem('transcriptData', JSON.stringify(transcriptData));
    }, data);
  }

  /**
   * Mock clipboard API for copy functionality testing
   */
  static async mockClipboard(page: Page): Promise<void> {
    await page.addInitScript(() => {
      let clipboardData = '';
      
      Object.defineProperty(navigator, 'clipboard', {
        value: {
          writeText: (text: string) => {
            clipboardData = text;
            return Promise.resolve();
          },
          readText: () => Promise.resolve(clipboardData)
        }
      });
    });
  }
}