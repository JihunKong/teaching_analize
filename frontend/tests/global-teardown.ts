import { FullConfig } from '@playwright/test';
import { promises as fs } from 'fs';
import path from 'path';

/**
 * Global teardown for Playwright tests
 * Cleans up test environment and processes artifacts
 */
async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global test teardown...');

  try {
    // Process test results and artifacts
    const outputDir = 'test-results';
    
    // Generate test summary
    await generateTestSummary(outputDir);
    
    // Clean up temporary files if not in CI
    if (!process.env.CI) {
      console.log('🗑️  Cleaning up temporary test files...');
      await cleanupTempFiles(outputDir);
    }

    // Process screenshots and videos for failed tests
    await processFailureArtifacts(outputDir);

    console.log('✅ Global teardown completed successfully');

  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error to avoid masking test failures
  }
}

async function generateTestSummary(outputDir: string) {
  try {
    const resultsPath = path.join(outputDir, 'results.json');
    
    // Check if results file exists
    try {
      await fs.access(resultsPath);
    } catch {
      console.log('📊 No test results file found, skipping summary generation');
      return;
    }

    const resultsContent = await fs.readFile(resultsPath, 'utf-8');
    const results = JSON.parse(resultsContent);

    const summary = {
      timestamp: new Date().toISOString(),
      totalTests: results.stats?.expected || 0,
      passedTests: results.stats?.passed || 0,
      failedTests: results.stats?.failed || 0,
      skippedTests: results.stats?.skipped || 0,
      flakyTests: results.stats?.flaky || 0,
      duration: results.stats?.duration || 0,
      environment: {
        baseURL: process.env.BASE_URL || 'http://localhost:3000',
        ci: !!process.env.CI,
        nodeVersion: process.version,
      }
    };

    await fs.writeFile(
      path.join(outputDir, 'test-summary.json'),
      JSON.stringify(summary, null, 2)
    );

    console.log('📊 Test Summary:');
    console.log(`   Total: ${summary.totalTests}`);
    console.log(`   Passed: ${summary.passedTests}`);
    console.log(`   Failed: ${summary.failedTests}`);
    console.log(`   Skipped: ${summary.skippedTests}`);
    console.log(`   Duration: ${Math.round(summary.duration / 1000)}s`);

  } catch (error) {
    console.error('❌ Failed to generate test summary:', error);
  }
}

async function cleanupTempFiles(outputDir: string) {
  try {
    // Remove trace files for passed tests to save space
    const traceDir = path.join(outputDir, 'traces');
    try {
      const traceFiles = await fs.readdir(traceDir);
      for (const file of traceFiles) {
        if (file.includes('-retry')) continue; // Keep retry traces
        const filePath = path.join(traceDir, file);
        await fs.unlink(filePath);
      }
    } catch {
      // Trace directory might not exist
    }

  } catch (error) {
    console.error('❌ Failed to cleanup temp files:', error);
  }
}

async function processFailureArtifacts(outputDir: string) {
  try {
    // Create a failures directory for easy access to failed test artifacts
    const failuresDir = path.join(outputDir, 'failures');
    await fs.mkdir(failuresDir, { recursive: true });

    // Copy screenshots and videos from failed tests
    const screenshots = await findFailureArtifacts(outputDir, 'screenshot');
    const videos = await findFailureArtifacts(outputDir, 'video');

    for (const screenshot of screenshots) {
      const destPath = path.join(failuresDir, path.basename(screenshot));
      await fs.copyFile(screenshot, destPath);
    }

    for (const video of videos) {
      const destPath = path.join(failuresDir, path.basename(video));
      await fs.copyFile(video, destPath);
    }

    if (screenshots.length > 0 || videos.length > 0) {
      console.log(`📸 Processed ${screenshots.length} screenshots and ${videos.length} videos from failed tests`);
    }

  } catch (error) {
    console.error('❌ Failed to process failure artifacts:', error);
  }
}

async function findFailureArtifacts(dir: string, type: 'screenshot' | 'video'): Promise<string[]> {
  const artifacts: string[] = [];
  
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        // Recursively search subdirectories
        const subArtifacts = await findFailureArtifacts(fullPath, type);
        artifacts.push(...subArtifacts);
      } else if (entry.isFile()) {
        const extension = type === 'screenshot' ? '.png' : '.webm';
        if (entry.name.endsWith(extension) && entry.name.includes('failed')) {
          artifacts.push(fullPath);
        }
      }
    }
  } catch {
    // Directory might not exist or be inaccessible
  }

  return artifacts;
}

export default globalTeardown;