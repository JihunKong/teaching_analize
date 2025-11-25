/**
 * Test data fixtures for E2E tests
 * Provides reusable test data for consistent testing
 */

export const testUrls = {
  valid: [
    'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'https://youtube.com/watch?v=dQw4w9WgXcQ',
    'https://youtu.be/dQw4w9WgXcQ',
    'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
    'https://www.youtube.com/watch?v=-OLCt6WScEY&list=PLugIxwJYmOhl_8KO3GHx9gp6VKMmbsTfw',
    'https://www.youtube.com/watch?v=abc123DEF456&t=123s'
  ],
  invalid: [
    'not-a-url',
    'https://example.com',
    'https://vimeo.com/123456789',
    'youtube.com/watch?v=123',
    'ftp://youtube.com/watch?v=123',
    'https://www.youtube.com/invalidpath'
  ],
  problematic: [
    'https://www.youtube.com/watch?v=invalid123', // Should fail transcription
    'https://www.youtube.com/watch?v=private456',  // Private video
    'https://www.youtube.com/watch?v=deleted789'   // Deleted video
  ]
};

export const sampleTranscripts = {
  short: '안녕하세요. 오늘은 간단한 수업입니다.',
  medium: `안녕하세요 학생들. 오늘은 수학 시간입니다. 
함수에 대해서 공부해보겠습니다. 
함수란 입력값에 대해 정확히 하나의 출력값을 가지는 관계를 말합니다. 
예를 들어 f(x) = 2x + 1 이라는 함수가 있다면, x가 1일 때 f(1) = 3이 됩니다.`,
  long: `안녕하세요 여러분. 오늘은 수학 시간입니다. 함수에 대해서 공부해보겠습니다. 함수란 입력값에 대해 정확히 하나의 출력값을 가지는 관계를 말합니다. 예를 들어 f(x) = 2x + 1 이라는 함수가 있다면, x가 1일 때 f(1) = 3이 됩니다. 학생 여러분, 이해가 되시나요? 네, 김철수 학생 질문있으면 손을 들어주세요. 좋습니다. 그럼 이제 연습문제를 풀어보겠습니다. 첫 번째 문제는 f(x) = x² + 2x - 3에서 f(2)의 값을 구하는 것입니다. 천천히 계산해보세요. f(2) = 2² + 2×2 - 3 = 4 + 4 - 3 = 5입니다. 잘 하셨습니다. 이제 여러분도 비슷한 문제를 풀어보세요.`.repeat(10),
  empty: '',
  whitespaceOnly: '   \n   \t   ',
  specialCharacters: '특수문자 테스트: !@#$%^&*()[]{}|;:,.<>?',
  korean: '한국어 교육 내용 분석을 위한 샘플 텍스트입니다. 교사와 학생 간의 상호작용을 포함합니다.',
  english: 'This is a sample educational content in English for testing multilingual analysis capabilities.',
  mixed: '한국어와 English가 섞인 mixed content for testing 다국어 분석 기능입니다.'
};

export const mockTranscriptionResults = {
  successful: {
    job_id: 'test-job-success',
    status: 'completed' as const,
    message: 'Transcription completed successfully',
    result: {
      transcript: sampleTranscripts.long,
      character_count: sampleTranscripts.long.length,
      word_count: sampleTranscripts.long.split(' ').length,
      video_id: 'dQw4w9WgXcQ',
      method_used: 'youtube-transcript-api'
    }
  },
  failed: {
    job_id: 'test-job-failed',
    status: 'failed' as const,
    message: 'Failed to extract transcript. Video may be private, deleted, or have no captions available.'
  },
  processing: {
    job_id: 'test-job-processing',
    status: 'processing' as const,
    message: 'Extracting transcript from YouTube video...'
  },
  longProcessing: {
    job_id: 'test-job-long',
    status: 'processing' as const,
    message: 'Processing long video content. This may take several minutes...'
  }
};

export const mockFrameworks = [
  {
    id: 'cbil',
    name: 'CBIL (7단계)',
    description: '개념기반 탐구학습의 7단계 실행 여부를 평가하고 점수를 부여합니다.'
  },
  {
    id: 'dialogue',
    name: '학생주도 토론',
    description: '학생 주도 질문과 대화, 토론 수업의 질문 유형과 대화 패턴을 분석합니다.'
  },
  {
    id: 'coaching',
    name: '수업 코칭',
    description: '수업 설계와 실행을 15개 항목으로 분석하고 구체적인 코칭을 제공합니다.'
  }
];

export const mockAnalysisResults = {
  cbil: {
    analysis_id: 'test-cbil-analysis',
    framework: 'cbil',
    framework_name: 'CBIL (7단계)',
    analysis: `### CBIL 7단계 분석 결과

#### 1. Engage (흥미 유도 및 연결)
교사가 수업 초반에 학생들의 관심을 끌고 기존 지식과 연결하려는 시도가 관찰됩니다.
**점수: 2점**

#### 2. Focus (탐구 방향 설정)
명확히 학습 주제를 제시하였으며, 탐구할 방향을 설정했습니다.
**점수: 2점**

#### 3. Investigate (자료 탐색 및 개념 형성)
구체적인 예시를 제시하여 개념 형성을 도왔습니다.
**점수: 2점**

#### 4. Organize (개념 구조화)
개념을 체계적으로 정리하였습니다.
**점수: 2점**

#### 5. Generalize (일반화 진술)
일반적 개념을 제시하였습니다.
**점수: 1점**

#### 6. Transfer (새로운 맥락에 적용)
연습문제를 통해 전이를 시도했습니다.
**점수: 3점**

#### 7. Reflect (사고 성찰)
학습 과정을 점검하려 했습니다.
**점수: 1점**

### 종합 평가
**총점: 13점 / 21점 (62%)**`,
    character_count: 1456,
    word_count: 487,
    created_at: '2025-08-23T10:30:00Z'
  },
  dialogue: {
    analysis_id: 'test-dialogue-analysis',
    framework: 'dialogue',
    framework_name: '학생주도 토론 분석',
    analysis: `### 학생주도 토론 수업 분석

#### 질문 유형 분석
**사실적 질문:** 높은 비중
**해석적 질문:** 제한적
**평가적 질문:** 거의 없음

#### 후속 질문 분석
**명료화 질문:** 단순한 확인 질문 위주
**초점화 질문:** 제한적
**정교화 질문:** 거의 없음

#### 수업 대화 유형
교사 주도형 대화가 주를 이룸
IRE 패턴이 주요 특징

### 개선 권장사항
1. 개방형 질문 증가
2. 학생 간 상호작용 촉진
3. 사고 확장 질문 활용`,
    character_count: 1234,
    word_count: 412,
    created_at: '2025-08-23T10:30:00Z'
  },
  coaching: {
    analysis_id: 'test-coaching-analysis',
    framework: 'coaching',
    framework_name: '수업 코칭 분석',
    analysis: `### 수업 코칭 분석 보고서

#### 주요 평가 항목
1. **학습 목표의 명확성:** 4/5
2. **도입의 효과성:** 3/5
3. **학습 내용의 적절성:** 5/5
4. **설명의 명확성:** 4/5
5. **예시 활용:** 5/5
6. **학생 참여 유도:** 2/5
7. **질문 기법:** 2/5
8. **피드백의 효과성:** 3/5

### 총 평점: 32/50 (64%)

### 개선 제안
1. 참여형 활동 증가
2. 질문 기법 개선
3. 개별화 지도 강화
4. 동기 유발 강화`,
    character_count: 1567,
    word_count: 523,
    created_at: '2025-08-23T10:30:00Z'
  }
};

export const mockReportData = {
  sample: {
    analysis_id: 'sample-cbil-001',
    framework: 'cbil',
    framework_name: '개념기반 탐구 수업(CBIL) 분석',
    analysis: mockAnalysisResults.cbil.analysis,
    character_count: 5026,
    word_count: 1229,
    created_at: '2025-08-22T10:35:00Z',
    metadata: {
      video_url: 'https://www.youtube.com/watch?v=-OLCt6WScEY',
      video_id: '-OLCt6WScEY',
      language: 'ko'
    }
  }
};

export const testViewports = [
  { name: 'desktop', width: 1920, height: 1080 },
  { name: 'laptop', width: 1366, height: 768 },
  { name: 'tablet', width: 1024, height: 768 },
  { name: 'mobile', width: 375, height: 667 },
  { name: 'small-mobile', width: 320, height: 568 }
];

export const apiEndpoints = {
  transcription: {
    submit: '/api/transcribe/youtube',
    status: (jobId: string) => `/api/transcribe/${jobId}`
  },
  analysis: {
    frameworks: '/api/frameworks',
    submit: '/api/analyze/text',
    status: (analysisId: string) => `/api/analyze/${analysisId}`
  },
  reports: {
    generateHtml: '/api/reports/generate/html'
  }
};

export const testUserAgents = {
  chrome: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
  firefox: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
  safari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
  edge: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
};

export const errorMessages = {
  transcription: {
    invalidUrl: 'Invalid YouTube URL format. Please provide a valid YouTube video URL.',
    serverError: 'Internal server error occurred while processing transcription request',
    videoNotFound: 'Video not found or private',
    noCaption: 'Video has no captions available'
  },
  analysis: {
    emptyText: 'Text content cannot be empty',
    serverError: 'Internal server error occurred during analysis',
    processingError: 'Analysis failed due to text processing error'
  },
  reports: {
    generationError: 'Report generation failed due to template processing error'
  }
};

export const performanceThresholds = {
  pageLoad: 5000,      // 5 seconds max page load
  apiResponse: 30000,  // 30 seconds max API response
  transcription: 300000, // 5 minutes max transcription
  analysis: 180000,    // 3 minutes max analysis
  reportGeneration: 120000 // 2 minutes max report generation
};

export const accessibilityLabels = {
  transcription: {
    urlInput: 'YouTube URL',
    languageSelect: '언어',
    submitButton: '전사 시작'
  },
  analysis: {
    parallelCheckbox: '병렬 분석 모드',
    frameworkSelect: '분석 프레임워크',
    textInput: '분석할 텍스트',
    submitButton: '분석 시작'
  },
  reports: {
    comprehensiveButton: '종합 보고서 보기',
    summaryButton: '요약 보고서 보기',
    jsonButton: 'JSON 다운로드'
  }
};