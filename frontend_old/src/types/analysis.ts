// Analysis Framework Types
// Designed to support multiple analysis tools/frameworks

export interface AnalysisFramework {
  id: string
  name: string
  description: string
  version: string
  enabled: boolean
  icon?: string
  color?: string
  categories?: string[]
}

// CBIL Analysis Framework (current implementation)
export interface CBILFramework extends AnalysisFramework {
  id: 'cbil'
  levels: CBILLevel[]
}

export interface CBILLevel {
  level: number
  name: string
  description: string
  weight: number
  examples?: string[]
}

// Base analysis request/result interfaces
export interface BaseAnalysisRequest {
  framework: string // Framework ID
  text: string
  metadata?: AnalysisMetadata
}

export interface BaseAnalysisResult {
  id: string
  framework: string
  text_preview: string
  created_at: string
  metadata?: AnalysisMetadata
}

// CBIL-specific analysis types
export interface CBILAnalysisRequest extends BaseAnalysisRequest {
  framework: 'cbil'
}

export interface CBILAnalysisResult extends BaseAnalysisResult {
  framework: 'cbil'
  cbil_scores: Record<string, number>
  overall_score: number
  level_distribution: {
    low_level: number    // levels 1-3
    mid_level: number    // levels 4-5
    high_level: number   // levels 6-7
  }
  recommendations: string[]
  dominant_level: {
    level: number
    name: string
    percentage: number
  }
}

// Future analysis frameworks can extend these base types
export interface CustomAnalysisRequest extends BaseAnalysisRequest {
  framework: string // Will be specific framework ID
  parameters?: Record<string, any>
}

export interface CustomAnalysisResult extends BaseAnalysisResult {
  framework: string
  results: Record<string, any>
  visualizations?: VisualizationConfig[]
}

// Metadata for analysis context
export interface AnalysisMetadata {
  source_type?: 'file_upload' | 'youtube' | 'direct_text'
  source_id?: string // transcription job ID or direct input ID
  language?: string
  duration?: number
  subject?: string
  grade_level?: string
  teacher?: string
  school?: string
  tags?: string[]
}

// Visualization configuration for flexible chart rendering
export interface VisualizationConfig {
  type: 'bar' | 'pie' | 'line' | 'radar' | 'heatmap'
  title: string
  data: any[]
  config: Record<string, any>
}

// Analysis comparison types
export interface AnalysisComparison {
  frameworks: string[]
  analyses: BaseAnalysisResult[]
  comparisons: ComparisonMetric[]
}

export interface ComparisonMetric {
  name: string
  description: string
  values: Record<string, number>
  trend: 'positive' | 'negative' | 'neutral'
}

// Framework registry for extensibility
export interface FrameworkRegistry {
  frameworks: AnalysisFramework[]
  active_framework: string
  default_parameters: Record<string, any>
}

// Built-in frameworks (extensible list)
export const AVAILABLE_FRAMEWORKS: AnalysisFramework[] = [
  {
    id: 'cbil',
    name: 'CBIL 분석',
    description: '인지적 부담 기반 교육언어 분석 (Cognitive Burden of Instructional Language)',
    version: '1.0.0',
    enabled: true,
    icon: 'BarChart3',
    color: '#3b82f6',
    categories: ['교육', '인지분석', '언어분석'],
  },
  // Future frameworks will be added here
  // {
  //   id: 'bloom',
  //   name: 'Bloom\'s Taxonomy',
  //   description: '블룸의 교육목표 분류학 기반 분석',
  //   version: '1.0.0',
  //   enabled: false, // Coming soon
  //   icon: 'Pyramid',
  //   color: '#10b981',
  //   categories: ['교육', '목표분석'],
  // },
  // {
  //   id: 'questioning',
  //   name: '질문 유형 분석',
  //   description: '교사의 질문 패턴 및 유형 분석',
  //   version: '1.0.0',
  //   enabled: false, // Coming soon
  //   icon: 'MessageCircleQuestion',
  //   color: '#8b5cf6',
  //   categories: ['교육', '질문분석', '상호작용'],
  // },
]

// Helper functions for analysis framework management
export const analysisFrameworkUtils = {
  getFramework: (id: string): AnalysisFramework | undefined => {
    return AVAILABLE_FRAMEWORKS.find(f => f.id === id)
  },

  getEnabledFrameworks: (): AnalysisFramework[] => {
    return AVAILABLE_FRAMEWORKS.filter(f => f.enabled)
  },

  getFrameworksByCategory: (category: string): AnalysisFramework[] => {
    return AVAILABLE_FRAMEWORKS.filter(f => 
      f.categories?.includes(category)
    )
  },

  isFrameworkEnabled: (id: string): boolean => {
    const framework = AVAILABLE_FRAMEWORKS.find(f => f.id === id)
    return framework?.enabled ?? false
  },
}

// CBIL-specific constants and utilities
export const CBIL_LEVELS: CBILLevel[] = [
  {
    level: 1,
    name: '단순 확인',
    description: 'Simple confirmation',
    weight: 0.1,
    examples: ['맞니?', '이해했니?', '알겠지?'],
  },
  {
    level: 2,
    name: '사실 회상',
    description: 'Fact recall',
    weight: 0.2,
    examples: ['언제였지?', '누가 했을까?', '어디에 있을까?'],
  },
  {
    level: 3,
    name: '개념 설명',
    description: 'Concept explanation',
    weight: 0.3,
    examples: ['이것은 무엇인가요?', '어떻게 작동하나요?'],
  },
  {
    level: 4,
    name: '분석적 사고',
    description: 'Analytical thinking',
    weight: 0.5,
    examples: ['왜 그런 일이 일어났을까요?', '어떤 차이가 있나요?'],
  },
  {
    level: 5,
    name: '종합적 이해',
    description: 'Comprehensive understanding',
    weight: 0.7,
    examples: ['전체적으로 어떤 의미인가요?', '패턴을 찾아보세요'],
  },
  {
    level: 6,
    name: '평가적 판단',
    description: 'Evaluative judgment',
    weight: 0.85,
    examples: ['어떤 것이 더 좋다고 생각하나요?', '판단해보세요'],
  },
  {
    level: 7,
    name: '창의적 적용',
    description: 'Creative application',
    weight: 1.0,
    examples: ['새로운 방법을 생각해보세요', '다른 상황에 적용한다면?'],
  },
]