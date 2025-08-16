// Report Templates Export
export { default as ComprehensiveReportTemplate } from './ComprehensiveReportTemplate'
export { default as SummaryReportTemplate } from './SummaryReportTemplate'
export { default as ActionPlanTemplate } from './ActionPlanTemplate'
export { FrameworkReportTemplates, CBILReportTemplate, QTAReportTemplate, SEIReportTemplate } from './FrameworkReportTemplates'

// Report types and interfaces
export interface ReportTemplateProps {
  analysisResult: any
  metadata: {
    teacher?: string
    subject?: string
    grade?: string
    duration?: string
    analysisTime: string
  }
  showCharts?: boolean
  className?: string
}

// Report template registry
export const ReportTemplates = {
  comprehensive: 'ComprehensiveReportTemplate',
  summary: 'SummaryReportTemplate',
  actionPlan: 'ActionPlanTemplate',
  // Framework-specific templates
  cbil: 'CBILReportTemplate',
  qta: 'QTAReportTemplate',
  sei: 'SEIReportTemplate',
  loa: 'GenericFrameworkTemplate',
  cea: 'GenericFrameworkTemplate',
  cma: 'GenericFrameworkTemplate',
  asa: 'GenericFrameworkTemplate',
  dia: 'GenericFrameworkTemplate',
  tia: 'GenericFrameworkTemplate',
  cta: 'GenericFrameworkTemplate',
  cra: 'GenericFrameworkTemplate',
  ita: 'GenericFrameworkTemplate',
  rwc: 'GenericFrameworkTemplate'
}

// Template utilities
export const reportTemplateUtils = {
  getTemplateName: (templateId: string): string => {
    const templateNames: Record<string, string> = {
      comprehensive: '종합 분석 보고서',
      summary: '요약 보고서',
      actionPlan: '실행 계획서',
      cbil: 'CBIL 분석 보고서',
      qta: '질문 유형 분석 보고서',
      sei: '학습자 참여도 보고서',
      loa: '학습목표 연계성 보고서',
      cea: '의사소통 효과성 보고서',
      cma: '교실 관리 보고서',
      asa: '평가 전략 보고서',
      dia: '수업 차별화 보고서',
      tia: '기술 통합 보고서',
      cta: '비판적 사고력 보고서',
      cra: '문화 반응성 보고서',
      ita: '포용적 교수법 보고서',
      rwc: '실생활 연계성 보고서'
    }
    return templateNames[templateId] || templateId
  },

  getTemplateDescription: (templateId: string): string => {
    const descriptions: Record<string, string> = {
      comprehensive: '모든 분석 프레임워크 결과를 종합한 상세 보고서',
      summary: '핵심 내용을 요약한 간략 보고서',
      actionPlan: '분석 결과 기반 구체적 실행 계획',
      cbil: '인지적 부담 수준 분석 전문 보고서',
      qta: '교사 질문 패턴 분석 전문 보고서',
      sei: '학습자 참여도 측정 전문 보고서'
    }
    return descriptions[templateId] || '전문 분석 보고서'
  },

  getRecommendedUseCase: (templateId: string): string => {
    const useCases: Record<string, string> = {
      comprehensive: '전체적인 교육 품질 평가가 필요한 경우',
      summary: '빠른 진단과 핵심 개선점 파악이 필요한 경우',
      actionPlan: '구체적인 개선 실행 방안이 필요한 경우',
      cbil: '학습자의 인지 부하 관리 개선이 필요한 경우',
      qta: '질문 기법 향상이 필요한 경우',
      sei: '학습자 참여도 증진이 필요한 경우'
    }
    return useCases[templateId] || '특정 영역 집중 개선이 필요한 경우'
  },

  getSupportedFormats: (templateId: string): string[] => {
    // All templates support HTML and PDF
    const baseFormats = ['html', 'pdf']
    
    // Some templates might support additional formats
    const additionalFormats: Record<string, string[]> = {
      actionPlan: ['docx'], // Action plans might need Word format for editing
      summary: ['pptx'], // Summary might be useful for presentations
    }
    
    return [...baseFormats, ...(additionalFormats[templateId] || [])]
  },

  getEstimatedGenerationTime: (templateId: string, dataSize: 'small' | 'medium' | 'large'): number => {
    // Time in seconds
    const baseTimes: Record<string, number> = {
      comprehensive: 10,
      summary: 3,
      actionPlan: 5,
      cbil: 2,
      qta: 2,
      sei: 2
    }
    
    const multipliers = {
      small: 1,
      medium: 1.5,
      large: 2.5
    }
    
    return (baseTimes[templateId] || 2) * multipliers[dataSize]
  }
}

export default ReportTemplates