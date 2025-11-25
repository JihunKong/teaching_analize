# AIBOA Frontend E2E Testing Suite

## 📋 Overview

This comprehensive Playwright E2E testing suite provides automated testing for the AIBOA teaching analysis frontend. It includes tests for all major functionality, Docker containerization, and CI/CD integration.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Docker and Docker Compose
- npm or yarn

### Installation

1. **Install Playwright and dependencies:**
   ```bash
   ./scripts/install-playwright.sh
   ```

2. **Install npm dependencies:**
   ```bash
   npm install
   ```

3. **Run tests locally:**
   ```bash
   npm run test
   ```

4. **Run tests with Docker:**
   ```bash
   npm run test:docker
   ```

## 🏗️ Architecture

### Directory Structure
```
tests/
├── e2e/                    # E2E test files
│   ├── transcription.spec.ts
│   ├── analysis.spec.ts
│   └── reports.spec.ts
├── fixtures/               # Test data fixtures
│   └── test-data.ts
├── mocks/                  # WireMock configurations
│   ├── transcription/
│   ├── analysis/
│   └── reports/
├── nginx/                  # Nginx test configuration
├── page-objects/           # Page Object Model classes
│   ├── BasePage.ts
│   ├── TranscriptionPage.ts
│   ├── AnalysisPage.ts
│   └── ReportsPage.ts
└── utils/                  # Test utilities
    ├── test-helpers.ts
    └── api-mocks.ts
```

### Key Components

- **Page Object Model**: Maintainable test structure with reusable page interactions
- **Mock API Services**: WireMock-based API mocking for consistent testing
- **Docker Infrastructure**: Containerized testing environment
- **CI/CD Integration**: GitHub Actions workflow with comprehensive reporting

## 📝 Test Coverage

### Transcription Page Tests
- ✅ Page loading and UI elements
- ✅ Form validation and interaction
- ✅ YouTube URL validation
- ✅ Language selection
- ✅ Transcription process flow
- ✅ Job status polling
- ✅ Results display and interaction
- ✅ Copy to clipboard functionality
- ✅ Auto-navigation to analysis
- ✅ Error handling
- ✅ Responsive design

### Analysis Page Tests
- ✅ Page loading and framework loading
- ✅ Parallel vs single analysis modes
- ✅ Text input and validation
- ✅ Framework selection
- ✅ Analysis submission and polling
- ✅ Results display
- ✅ Report generation
- ✅ Transcription integration
- ✅ Error handling
- ✅ Mobile compatibility

### Reports Page Tests
- ✅ Page loading and templates
- ✅ Comprehensive report generation
- ✅ Summary report generation
- ✅ JSON download functionality
- ✅ New window handling
- ✅ Navigation links
- ✅ Accessibility features
- ✅ Performance testing
- ✅ Error boundaries

## 🐳 Docker Setup

### Services Architecture
```
┌─────────────────┐    ┌──────────────┐
│   Frontend      │    │    Nginx     │
│   (Next.js)     │◄───┤   (Proxy)    │
│   Port: 3000    │    │   Port: 80   │
└─────────────────┘    └──────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐    ┌────────▼────────┐    ┌──────▼──────┐
│ Mock-Transc.  │    │  Mock-Analysis  │    │ Mock-Reports│
│ Port: 8000    │    │  Port: 8001     │    │ Port: 8002  │
└───────────────┘    └─────────────────┘    └─────────────┘
```

### Running with Docker

1. **Full test suite:**
   ```bash
   docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
   ```

2. **Using the test runner script:**
   ```bash
   ./scripts/run-e2e-tests.sh
   ```

3. **With custom options:**
   ```bash
   ./scripts/run-e2e-tests.sh --headed --grep transcription
   ```

## 🛠️ Configuration

### Playwright Configuration (`playwright.config.ts`)
- **Browsers**: Chromium, Firefox, WebKit
- **Viewports**: Desktop and mobile
- **Retries**: 2 retries on CI, 1 locally
- **Timeouts**: 60s test timeout, 30s navigation
- **Reports**: HTML, JSON, JUnit
- **Artifacts**: Screenshots, videos, traces

### Test Data (`tests/fixtures/test-data.ts`)
- Sample URLs (valid/invalid)
- Mock transcripts (various lengths)
- Framework definitions
- Analysis results
- Performance thresholds

## 📊 Reporting

### Local Testing
- **HTML Report**: `test-results/html-report/index.html`
- **Screenshots**: `test-results/screenshots/`
- **Videos**: `test-results/videos/`
- **Traces**: `test-results/traces/`

### CI/CD Reports
- **GitHub Actions**: Integrated test results
- **JUnit Reports**: For external systems
- **Performance Analysis**: Slow test detection
- **PR Comments**: Automated result summaries

## 🔧 Available Scripts

```bash
# Local testing
npm run test                 # Run all tests
npm run test:headed         # Run with browser UI
npm run test:debug          # Run in debug mode
npm run test:ui             # Run with Playwright UI

# Docker testing
npm run test:docker         # Full Docker test suite

# Specific test patterns
npx playwright test --grep transcription
npx playwright test --grep analysis
npx playwright test --grep reports
```

## 🐛 Debugging

### Local Debugging
1. **Debug mode:**
   ```bash
   npm run test:debug
   ```

2. **Headed mode:**
   ```bash
   npm run test:headed
   ```

3. **Playwright UI:**
   ```bash
   npm run test:ui
   ```

### Docker Debugging
1. **Check service logs:**
   ```bash
   docker-compose -f docker-compose.test.yml logs frontend
   ```

2. **Manual container inspection:**
   ```bash
   docker-compose -f docker-compose.test.yml run --rm e2e-tests bash
   ```

### Common Issues
- **Port conflicts**: Ensure ports 3000, 8000-8002, 80 are available
- **Docker memory**: Increase Docker memory allocation if tests fail
- **Browser deps**: Run `./scripts/install-playwright.sh` if browsers fail

## 🚀 CI/CD Integration

### GitHub Actions Workflow (`.github/workflows/e2e-tests.yml`)
- **Triggers**: Push, PR, schedule, manual
- **Matrix Strategy**: Multiple browsers and shards
- **Artifact Collection**: Results, reports, failure screenshots
- **Performance Monitoring**: Slow test detection
- **PR Comments**: Automated result summaries

### Workflow Features
- **Smart Change Detection**: Only runs when relevant files change
- **Parallel Execution**: Tests run in parallel shards
- **Comprehensive Reporting**: Multiple report formats
- **Failure Analysis**: Detailed logs and artifacts
- **Performance Tracking**: Duration and threshold monitoring

## 📈 Performance Monitoring

### Thresholds
- **Page Load**: < 5 seconds
- **API Response**: < 30 seconds  
- **Test Execution**: < 60 seconds
- **Transcription**: < 5 minutes
- **Analysis**: < 3 minutes

### Monitoring
- Automatic slow test detection
- Performance trend analysis
- Resource usage tracking
- Failure pattern analysis

## 🔒 Security

### Best Practices
- Non-root container execution
- Secure mock data (no real credentials)
- Network isolation in Docker
- Proper cleanup after tests
- No sensitive data in logs

### Mock Data
All test data is synthetic and safe:
- Sample YouTube URLs (non-functional)
- Generated Korean text for analysis
- Mock API responses
- Test-only user data

## 🤝 Contributing

### Adding New Tests
1. Create test file in `tests/e2e/`
2. Use existing page objects or create new ones
3. Add test data to `tests/fixtures/test-data.ts`
4. Update mock configurations if needed
5. Ensure tests pass locally and in Docker

### Page Object Guidelines
- Inherit from `BasePage`
- Use descriptive locators
- Include proper waiting mechanisms
- Add comprehensive error handling
- Document public methods

### Mock API Guidelines
- Use WireMock JSON configurations
- Support different scenarios (success, failure, slow)
- Match real API response formats
- Include proper delay simulation

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [WireMock Documentation](http://wiremock.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 📞 Support

For questions or issues:
1. Check this documentation
2. Review existing test examples
3. Check GitHub Actions logs
4. Create an issue with test results and logs

---

**Last Updated**: August 2025
**Playwright Version**: 1.40.0
**Node.js Version**: 18+