// Comprehensive Analysis Framework Types
// 13개 분석 프레임워크를 위한 TypeScript 인터페이스 정의

import { BaseAnalysisRequest, BaseAnalysisResult, VisualizationConfig } from './analysis'

// =============================================================================
// FRAMEWORK REGISTRY & COMMON TYPES
// =============================================================================

export interface ComprehensiveFramework {
  id: string
  name_ko: string
  name_en: string
  description: string
  purpose: string
  categories: string[]
  version: string
  enabled: boolean
  icon: string
  color: string
  temperature: number // LLM temperature for consistency
  analysis_levels: number // Number of analysis categories
}

export const COMPREHENSIVE_FRAMEWORKS: ComprehensiveFramework[] = [
  {
    id: 'cbil',
    name_ko: '인지적 부담 기반 교육언어 분석',
    name_en: 'Cognitive Burden of Instructional Language Analysis',
    description: '교육 언어의 인지적 복잡성 7단계 분류',
    purpose: '발화별 인지부하 수준 측정',
    categories: ['인지분석', '언어분석'],
    version: '1.0.0',
    enabled: true,
    icon: 'BarChart3',
    color: '#3b82f6',
    temperature: 0.3,
    analysis_levels: 7
  },
  {
    id: 'qta',
    name_ko: '질문 유형 분석',
    name_en: 'Question Type Analysis',
    description: '교사 질문의 유형과 패턴을 분석하여 학습자 참여도 향상 방안 제시',
    purpose: '질문 형태, 인지 수준, 응답 유도 방식 분석',
    categories: ['질문분석', '상호작용', '참여도'],
    version: '1.0.0',
    enabled: true,
    icon: 'MessageCircleQuestion',
    color: '#8b5cf6',
    temperature: 0.3,
    analysis_levels: 7
  },
  {
    id: 'sei',
    name_ko: '학습자 참여도 지표 분석',
    name_en: 'Student Engagement Indicators Analysis',
    description: '학습자의 능동적 참여 정도와 참여 유형을 측정하여 수업 개선점 도출',
    purpose: '발언 기회, 상호작용 패턴, 응답 품질 분석',
    categories: ['참여도', '상호작용', '학습자중심'],
    version: '1.0.0',
    enabled: true,
    icon: 'Users',
    color: '#10b981',
    temperature: 0.3,
    analysis_levels: 6
  },
  {
    id: 'loa',
    name_ko: '학습목표 연계성 분석',
    name_en: 'Learning Objectives Alignment Analysis',
    description: '수업 내용과 활동이 학습목표와 얼마나 잘 연계되어 있는지 분석',
    purpose: '목표-내용 일치도, 평가 연계성, 성취기준 달성도 분석',
    categories: ['목표분석', '교육과정', '연계성'],
    version: '1.0.0',
    enabled: true,
    icon: 'Target',
    color: '#f59e0b',
    temperature: 0.3,
    analysis_levels: 5
  },
  {
    id: 'cea',
    name_ko: '의사소통 효과성 분석',
    name_en: 'Communication Effectiveness Analysis',
    description: '교사의 의사소통 방식이 학습자의 이해와 참여에 미치는 효과 분석',
    purpose: '언어 명확성, 피드백 품질, 상호작용 패턴 분석',
    categories: ['의사소통', '피드백', '명확성'],
    version: '1.0.0',
    enabled: true,
    icon: 'MessageSquare',
    color: '#ef4444',
    temperature: 0.3,
    analysis_levels: 7
  },
  {
    id: 'cma',
    name_ko: '교실 관리 분석',
    name_en: 'Classroom Management Analysis',
    description: '교실 환경 조성과 학습 분위기 관리 능력 분석',
    purpose: '수업 진행 관리, 행동 지도, 시간 관리, 환경 조성 분석',
    categories: ['교실관리', '환경조성', '시간관리'],
    version: '1.0.0',
    enabled: true,
    icon: 'Layout',
    color: '#06b6d4',
    temperature: 0.3,
    analysis_levels: 6
  },
  {
    id: 'asa',
    name_ko: '평가 전략 분석',
    name_en: 'Assessment Strategy Analysis',
    description: '수업 중 평가 활동의 유형과 효과성 분석',
    purpose: '진단평가, 형성평가, 총괄평가, 피드백 제공 분석',
    categories: ['평가', '피드백', '진단'],
    version: '1.0.0',
    enabled: true,
    icon: 'ClipboardCheck',
    color: '#84cc16',
    temperature: 0.3,
    analysis_levels: 5
  },
  {
    id: 'dia',
    name_ko: '수업 차별화 분석',
    name_en: 'Differentiation in Instruction Analysis',
    description: '학습자 개별 차이를 고려한 수업 설계와 실행 정도 분석',
    purpose: '내용 차별화, 과정 차별화, 결과물 차별화, 학습 환경 분석',
    categories: ['차별화', '개별화', '맞춤형'],
    version: '1.0.0',
    enabled: true,
    icon: 'Settings',
    color: '#ec4899',
    temperature: 0.3,
    analysis_levels: 4
  },
  {
    id: 'tia',
    name_ko: '기술 통합 분석',
    name_en: 'Technology Integration Analysis',
    description: '교육 기술의 활용 수준과 효과성 분석 (SAMR 모델 기반)',
    purpose: '기술 도구 사용, 통합 수준, 학습 향상 효과 분석',
    categories: ['기술통합', 'SAMR', '디지털교육'],
    version: '1.0.0',
    enabled: true,
    icon: 'Monitor',
    color: '#6366f1',
    temperature: 0.3,
    analysis_levels: 5
  },
  {
    id: 'cta',
    name_ko: '비판적 사고력 분석',
    name_en: 'Critical Thinking Analysis',
    description: '비판적 사고 능력 함양을 위한 수업 요소 분석',
    purpose: '사고 과정, 논리적 추론, 증거 평가, 다양한 관점 분석',
    categories: ['비판적사고', '논리', '추론'],
    version: '1.0.0',
    enabled: true,
    icon: 'Brain',
    color: '#7c3aed',
    temperature: 0.3,
    analysis_levels: 6
  },
  {
    id: 'cra',
    name_ko: '문화 반응성 분석',
    name_en: 'Cultural Responsiveness Analysis',
    description: '다양한 문화적 배경을 가진 학습자들을 고려한 수업 실행 분석',
    purpose: '문화적 인식, 포용성, 다양성 존중, 형평성 분석',
    categories: ['문화다양성', '포용성', '형평성'],
    version: '1.0.0',
    enabled: true,
    icon: 'Globe',
    color: '#059669',
    temperature: 0.3,
    analysis_levels: 5
  },
  {
    id: 'ita',
    name_ko: '포용적 교수법 분석',
    name_en: 'Inclusive Teaching Analysis',
    description: '모든 학습자가 참여할 수 있는 포용적 수업 환경 조성 정도 분석',
    purpose: '접근성, 다양성 지원, 장벽 제거, 공평한 기회 제공 분석',
    categories: ['포용성', '접근성', '다양성지원'],
    version: '1.0.0',
    enabled: true,
    icon: 'Heart',
    color: '#dc2626',
    temperature: 0.3,
    analysis_levels: 4
  },
  {
    id: 'rwc',
    name_ko: '실생활 연계성 분석',
    name_en: 'Real-World Connections Analysis',
    description: '학습 내용과 실제 생활의 연계성 정도 분석',
    purpose: '실생활 예시, 현실 문제 해결, 사회적 맥락, 미래 적용성 분석',
    categories: ['실생활연계', '사회적맥락', '실용성'],
    version: '1.0.0',
    enabled: true,
    icon: 'Link',
    color: '#0891b2',
    temperature: 0.3,
    analysis_levels: 5
  }
]

// =============================================================================
// ANALYSIS REQUEST & RESULT INTERFACES
// =============================================================================

export interface ComprehensiveAnalysisRequest {
  frameworks: string[] // Selected framework IDs
  text: string
  parallel_execution: boolean
  temperature: number
  include_cross_analysis: boolean
  metadata?: Record<string, any>
}

export interface CrossFrameworkInsight {
  frameworks_involved: string[]
  insight_type: 'correlation' | 'contradiction' | 'reinforcement' | 'gap'
  description: string
  significance: 'high' | 'medium' | 'low'
  recommendations: string[]
}

export interface OverallSummary {
  total_frameworks: number
  analysis_coverage: number // 0-100 percentage
  dominant_patterns: string[]
  key_strengths: string[]
  priority_improvements: string[]
  overall_score: number // 0-100
}

export interface PrioritizedRecommendation {
  recommendation: string
  priority: 'high' | 'medium' | 'low'
  frameworks_source: string[]
  implementation_difficulty: 'easy' | 'moderate' | 'challenging'
  expected_impact: 'high' | 'medium' | 'low'
}

export interface ComprehensiveAnalysisResult {
  id: string
  request_id: string
  frameworks_analyzed: string[]
  individual_results: Record<string, FrameworkSpecificResult>
  cross_framework_insights: CrossFrameworkInsight[]
  overall_summary: OverallSummary
  recommendations: PrioritizedRecommendation[]
  analysis_metadata: {
    total_analysis_time: number
    parallel_execution: boolean
    temperature_used: number
    text_length: number
    created_at: string
  }
}

// =============================================================================
// FRAMEWORK-SPECIFIC RESULT INTERFACES
// =============================================================================

export type FrameworkSpecificResult = 
  | CBILAnalysisResult 
  | QTAAnalysisResult 
  | SEIAnalysisResult 
  | LOAAnalysisResult 
  | CEAAnalysisResult 
  | CMAAnalysisResult 
  | ASAAnalysisResult 
  | DIAAnalysisResult 
  | TIAAnalysisResult 
  | CTAAnalysisResult 
  | CRAAnalysisResult 
  | ITAAnalysisResult 
  | RWCAnalysisResult

// 1. CBIL (Cognitive Burden of Instructional Language)
export interface CBILAnalysisResult extends BaseAnalysisResult {
  framework: 'cbil'
  cbil_levels: {
    simple_confirmation: number
    fact_recall: number
    concept_explanation: number
    analytical_thinking: number
    comprehensive_understanding: number
    evaluative_judgment: number
    creative_application: number
  }
  cognitive_load_score: number
  complexity_distribution: Record<string, number>
  recommendations: string[]
}

// 2. QTA (Question Type Analysis)
export interface QTAAnalysisResult extends BaseAnalysisResult {
  framework: 'qta'
  question_distribution: {
    closed: number
    open: number
    checking: number
    leading: number
    inquiry: number
    creative: number
    metacognitive: number
  }
  question_density: number
  cognitive_level_average: number
  engagement_score: number
  patterns: {
    sequence_analysis: string[]
    wait_time_indicators: number
    follow_up_rate: number
  }
  recommendations: string[]
}

// 3. SEI (Student Engagement Indicators)
export interface SEIAnalysisResult extends BaseAnalysisResult {
  framework: 'sei'
  engagement_levels: {
    passive_listening: number
    simple_response: number
    question_participation: number
    discussion_participation: number
    collaborative_activity: number
    leading_presentation: number
  }
  interaction_metrics: {
    teacher_talk_ratio: number
    student_response_ratio: number
    wait_time_average: number
    interruption_count: number
  }
  engagement_trend: 'increasing' | 'stable' | 'decreasing'
  participation_equity: number
  recommendations: string[]
}

// 4. LOA (Learning Objectives Alignment)
export interface LOAAnalysisResult extends BaseAnalysisResult {
  framework: 'loa'
  alignment_scores: {
    no_objective: number
    objective_mentioned: number
    content_aligned: number
    activity_aligned: number
    assessment_aligned: number
  }
  objective_clarity: number
  content_relevance: number
  coherence_score: number
  achievement_indicators: string[]
  gap_analysis: {
    missing_connections: string[]
    improvement_areas: string[]
  }
  recommendations: string[]
}

// 5. CEA (Communication Effectiveness Analysis)
export interface CEAAnalysisResult extends BaseAnalysisResult {
  framework: 'cea'
  communication_levels: {
    unclear: number
    simple_delivery: number
    clear_explanation: number
    interactive: number
    feedback_giving: number
    encouragement: number
    personalized: number
  }
  effectiveness_metrics: {
    clarity_score: number
    interaction_quality: number
    feedback_frequency: number
    emotional_support: number
  }
  communication_style: 'authoritative' | 'facilitative' | 'supportive' | 'mixed'
  improvement_areas: string[]
  recommendations: string[]
}

// 6. CMA (Classroom Management Analysis)
export interface CMAAnalysisResult extends BaseAnalysisResult {
  framework: 'cma'
  management_levels: {
    chaotic: number
    basic_control: number
    systematic_flow: number
    active_management: number
    preventive_management: number
    community_building: number
  }
  management_aspects: {
    behavior_guidance: number
    time_management: number
    space_utilization: number
    routine_establishment: number
  }
  intervention_types: string[]
  effectiveness_score: number
  recommendations: string[]
}

// 7. ASA (Assessment Strategy Analysis)
export interface ASAAnalysisResult extends BaseAnalysisResult {
  framework: 'asa'
  assessment_types: {
    no_assessment: number
    simple_check: number
    formative_assessment: number
    diverse_assessment: number
    comprehensive_assessment: number
  }
  assessment_methods: {
    oral_questions: number
    written_tasks: number
    peer_assessment: number
    self_assessment: number
    portfolio: number
  }
  feedback_quality: number
  assessment_frequency: number
  recommendations: string[]
}

// 8. DIA (Differentiation in Instruction Analysis)
export interface DIAAnalysisResult extends BaseAnalysisResult {
  framework: 'dia'
  differentiation_levels: {
    one_size_fits_all: number
    partial_differentiation: number
    systematic_differentiation: number
    individualized: number
  }
  differentiation_aspects: {
    content: number
    process: number
    product: number
    environment: number
  }
  learner_consideration: {
    ability_levels: boolean
    learning_styles: boolean
    interests: boolean
    background: boolean
  }
  adaptation_strategies: string[]
  recommendations: string[]
}

// 9. TIA (Technology Integration Analysis)
export interface TIAAnalysisResult extends BaseAnalysisResult {
  framework: 'tia'
  samr_levels: {
    no_technology: number
    substitution: number
    augmentation: number
    modification: number
    redefinition: number
  }
  technology_types: {
    presentation_tools: number
    interactive_media: number
    collaboration_platforms: number
    assessment_tools: number
    content_creation: number
  }
  integration_effectiveness: number
  digital_literacy_support: number
  recommendations: string[]
}

// 10. CTA (Critical Thinking Analysis)
export interface CTAAnalysisResult extends BaseAnalysisResult {
  framework: 'cta'
  thinking_levels: {
    information_reception: number
    basic_questioning: number
    evidence_seeking: number
    perspective_comparison: number
    logic_analysis: number
    creative_resolution: number
  }
  critical_thinking_skills: {
    analysis: number
    evaluation: number
    inference: number
    interpretation: number
    explanation: number
  }
  reasoning_patterns: string[]
  thinking_depth: number
  recommendations: string[]
}

// 11. CRA (Cultural Responsiveness Analysis)
export interface CRAAnalysisResult extends BaseAnalysisResult {
  framework: 'cra'
  responsiveness_levels: {
    cultural_ignorance: number
    surface_awareness: number
    cultural_respect: number
    cultural_integration: number
    culturally_sustaining: number
  }
  cultural_aspects: {
    language_diversity: number
    cultural_references: number
    inclusive_examples: number
    equity_practices: number
  }
  inclusivity_indicators: string[]
  cultural_sensitivity: number
  recommendations: string[]
}

// 12. ITA (Inclusive Teaching Analysis)
export interface ITAAnalysisResult extends BaseAnalysisResult {
  framework: 'ita'
  inclusion_levels: {
    exclusive: number
    segregative: number
    integrative: number
    inclusive: number
  }
  inclusion_practices: {
    universal_design: number
    accessibility: number
    participation_equity: number
    diverse_strengths: number
  }
  support_strategies: string[]
  barrier_removal: string[]
  recommendations: string[]
}

// 13. RWC (Real-World Connections Analysis)
export interface RWCAnalysisResult extends BaseAnalysisResult {
  framework: 'rwc'
  connection_levels: {
    abstract_learning: number
    example_giving: number
    problem_connection: number
    practical_application: number
    social_engagement: number
  }
  connection_types: {
    personal_relevance: number
    social_issues: number
    career_connections: number
    community_impact: number
  }
  authenticity_score: number
  future_application: string[]
  recommendations: string[]
}

// =============================================================================
// VISUALIZATION CONFIGURATIONS
// =============================================================================

export interface FrameworkVisualization {
  framework_id: string
  charts: VisualizationConfig[]
  dashboard_layout: 'single' | 'grid' | 'tabs'
  color_scheme: string[]
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

export const comprehensiveFrameworkUtils = {
  getFramework: (id: string): ComprehensiveFramework | undefined => {
    return COMPREHENSIVE_FRAMEWORKS.find(f => f.id === id)
  },

  getEnabledFrameworks: (): ComprehensiveFramework[] => {
    return COMPREHENSIVE_FRAMEWORKS.filter(f => f.enabled)
  },

  getFrameworksByCategory: (category: string): ComprehensiveFramework[] => {
    return COMPREHENSIVE_FRAMEWORKS.filter(f => 
      f.categories.includes(category)
    )
  },

  isFrameworkEnabled: (id: string): boolean => {
    const framework = COMPREHENSIVE_FRAMEWORKS.find(f => f.id === id)
    return framework?.enabled ?? false
  },

  getFrameworkColor: (id: string): string => {
    const framework = COMPREHENSIVE_FRAMEWORKS.find(f => f.id === id)
    return framework?.color ?? '#6b7280'
  },

  validateFrameworkResult: (framework: string, result: any): boolean => {
    // Type validation logic for each framework result
    if (!result || typeof result !== 'object') return false
    if (result.framework !== framework) return false
    
    // Framework-specific validation can be added here
    return true
  },

  calculateOverallScore: (results: Record<string, FrameworkSpecificResult>): number => {
    // Calculate weighted overall score across all frameworks
    const scores: number[] = []
    
    Object.values(results).forEach(result => {
      // Extract relevant scores from each framework
      if ('overall_score' in result) {
        scores.push((result as any).overall_score)
      } else if ('effectiveness_score' in result) {
        scores.push((result as any).effectiveness_score)
      } else if ('coherence_score' in result) {
        scores.push((result as any).coherence_score)
      }
      // Add more score extraction logic as needed
    })
    
    return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0
  },

  generateCrossFrameworkInsights: (
    results: Record<string, FrameworkSpecificResult>
  ): CrossFrameworkInsight[] => {
    // Generate insights by comparing results across frameworks
    const insights: CrossFrameworkInsight[] = []
    
    // Example: High CBIL complexity with low SEI engagement
    const cbil = results['cbil'] as CBILAnalysisResult
    const sei = results['sei'] as SEIAnalysisResult
    
    if (cbil && sei) {
      const highComplexity = cbil.cognitive_load_score > 70
      const lowEngagement = sei.engagement_trend === 'decreasing'
      
      if (highComplexity && lowEngagement) {
        insights.push({
          frameworks_involved: ['cbil', 'sei'],
          insight_type: 'correlation',
          description: '높은 인지적 부담이 학습자 참여도 저하와 상관관계를 보입니다.',
          significance: 'high',
          recommendations: [
            '복잡한 내용을 단계별로 나누어 제시하세요',
            '학습자 이해도를 자주 확인하세요'
          ]
        })
      }
    }
    
    return insights
  }
}

// =============================================================================
// CONSTANTS FOR ANALYSIS PROMPTS
// =============================================================================

export const FRAMEWORK_ANALYSIS_PROMPTS = {
  qta: `당신은 교육학 전문가로서 교사의 질문 패턴을 분석합니다.

다음 발화에서 질문을 찾아 7가지 유형으로 분류하세요:
1. 폐쇄형 (단답형)
2. 개방형 (다양한 답변)  
3. 확인형 (이해도 점검)
4. 유도형 (특정 답변 유도)
5. 탐구형 (깊이 있는 사고)
6. 창의형 (창의적 사고)
7. 메타인지형 (학습 과정 성찰)

분석할 텍스트: "{text}"

JSON 형식으로 응답하세요.`,

  sei: `교실 상호작용 전문가로서 학습자 참여도를 분석하세요.

다음 6단계로 참여 수준을 분류하세요:
1. 수동적 청취 - 일방향 강의
2. 단순 응답 - 짧은 답변
3. 질문 참여 - 학생의 질문
4. 토론 참여 - 의견 교환
5. 협력 활동 - 그룹 작업
6. 주도적 발표 - 학생 주도

분석할 텍스트: "{text}"

JSON 응답하세요.`,

  // Add prompts for other frameworks...
  // (prompts would be similar to what's defined in the main specification document)
}