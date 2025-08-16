'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { analysisService, AnalysisRequest, AnalysisResult, StatisticsResponse } from '@/lib/api'
import { 
  frameworkAnalysisService,
  frameworkValidation,
} from '@/lib/analysis-api'
import {
  BaseAnalysisRequest,
  BaseAnalysisResult,
  CBILAnalysisResult,
  AnalysisFramework,
  AVAILABLE_FRAMEWORKS,
} from '@/types/analysis'

// Query keys
export const analysisKeys = {
  all: ['analysis'] as const,
  result: (id: string) => [...analysisKeys.all, 'result', id] as const,
  statistics: () => [...analysisKeys.all, 'statistics'] as const,
  health: () => [...analysisKeys.all, 'health'] as const,
  frameworks: () => [...analysisKeys.all, 'frameworks'] as const,
  framework: (id: string) => [...analysisKeys.all, 'framework', id] as const,
  history: () => [...analysisKeys.all, 'history'] as const,
}

// Hook for analyzing text
export function useAnalyzeText() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request: AnalysisRequest) => analysisService.analyzeText(request),
    onSuccess: (data) => {
      // Cache the analysis result
      queryClient.setQueryData(analysisKeys.result(data.analysis_id), data)
      // Invalidate statistics to refresh counts
      queryClient.invalidateQueries({ queryKey: analysisKeys.statistics() })
    },
    onError: (error) => {
      console.error('Text analysis failed:', error)
    },
  })
}

// Hook for getting analysis result
export function useAnalysisResult(analysisId: string | undefined) {
  return useQuery({
    queryKey: analysisKeys.result(analysisId || ''),
    queryFn: () => analysisService.getAnalysis(analysisId!),
    enabled: !!analysisId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  })
}

// Hook for getting statistics
export function useStatistics() {
  return useQuery({
    queryKey: analysisKeys.statistics(),
    queryFn: analysisService.getStatistics,
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 2,
  })
}

// Hook for analysis service health
export function useAnalysisHealth() {
  return useQuery({
    queryKey: analysisKeys.health(),
    queryFn: analysisService.healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
    retry: 1,
  })
}

// Custom hook for CBIL score interpretation
export function useCBILInterpretation(scores: Record<string, number> | undefined) {
  if (!scores) return null

  const interpretation = {
    dominantLevel: '',
    dominantScore: 0,
    levelDistribution: {
      basic: 0, // levels 1-2
      intermediate: 0, // levels 3-4
      advanced: 0, // levels 5-7
    },
    recommendations: [] as string[],
  }

  // Find dominant level
  Object.entries(scores).forEach(([level, score]) => {
    if (score > interpretation.dominantScore) {
      interpretation.dominantLevel = level
      interpretation.dominantScore = score
    }
  })

  // Calculate level distribution
  interpretation.levelDistribution.basic = (scores['1'] || 0) + (scores['2'] || 0)
  interpretation.levelDistribution.intermediate = (scores['3'] || 0) + (scores['4'] || 0)
  interpretation.levelDistribution.advanced = 
    (scores['5'] || 0) + (scores['6'] || 0) + (scores['7'] || 0)

  // Generate recommendations
  if (interpretation.levelDistribution.basic > 0.6) {
    interpretation.recommendations.push('고차원적 사고를 요구하는 질문을 더 포함하세요')
  }
  if (interpretation.levelDistribution.advanced < 0.2) {
    interpretation.recommendations.push('창의적이고 평가적 사고를 유도하는 활동을 추가하세요')
  }
  if (scores['7'] === 0) {
    interpretation.recommendations.push('창의적 적용 단계의 질문을 포함하세요')
  }

  return interpretation
}

// Hook for managing multiple analyses (legacy)
export function useLegacyAnalysisHistory() {
  const queryClient = useQueryClient()

  const getAllAnalyses = (): AnalysisResult[] => {
    const queryCache = queryClient.getQueryCache()
    const analyses: AnalysisResult[] = []

    queryCache
      .findAll({ queryKey: analysisKeys.all })
      .forEach((query) => {
        if (query.queryKey.includes('result') && query.state.data) {
          analyses.push(query.state.data as AnalysisResult)
        }
      })

    return analyses.sort((a, b) => 
      // Sort by analysis_id timestamp if available, otherwise maintain insertion order
      b.analysis_id.localeCompare(a.analysis_id)
    )
  }

  const getAnalysis = (analysisId: string) => {
    return queryClient.getQueryData<AnalysisResult>(analysisKeys.result(analysisId))
  }

  const clearAnalysisCache = () => {
    queryClient.removeQueries({ queryKey: analysisKeys.all })
  }

  return {
    getAllAnalyses,
    getAnalysis,
    clearAnalysisCache,
  }
}

// Hook for comparing multiple analyses
export function useAnalysisComparison(analysisIds: string[]) {
  const queryClient = useQueryClient()

  const getComparisons = () => {
    const analyses = analysisIds
      .map(id => queryClient.getQueryData<AnalysisResult>(analysisKeys.result(id)))
      .filter(Boolean) as AnalysisResult[]

    if (analyses.length < 2) return null

    const comparison = {
      analyses,
      averageScores: {} as Record<string, number>,
      trends: [] as Array<{ level: string; trend: 'up' | 'down' | 'stable' }>,
    }

    // Calculate average CBIL scores across all analyses
    const levels = ['1', '2', '3', '4', '5', '6', '7']
    levels.forEach(level => {
      const scores = analyses.map(a => a.cbil_scores[level] || 0)
      comparison.averageScores[level] = scores.reduce((sum, score) => sum + score, 0) / scores.length
    })

    // Analyze trends (simplified - could be more sophisticated)
    if (analyses.length >= 2) {
      const first = analyses[0]
      const last = analyses[analyses.length - 1]

      levels.forEach(level => {
        const firstScore = first.cbil_scores[level] || 0
        const lastScore = last.cbil_scores[level] || 0
        const diff = lastScore - firstScore

        comparison.trends.push({
          level,
          trend: Math.abs(diff) < 0.05 ? 'stable' : diff > 0 ? 'up' : 'down',
        })
      })
    }

    return comparison
  }

  return { getComparisons }
}

// FRAMEWORK-AWARE HOOKS (New System)

// Hook for getting available analysis frameworks
export function useAnalysisFrameworks() {
  return useQuery({
    queryKey: analysisKeys.frameworks(),
    queryFn: frameworkAnalysisService.getFrameworks,
    staleTime: 10 * 60 * 1000, // 10 minutes - frameworks don't change often
    refetchOnWindowFocus: false,
  })
}

// Hook for getting specific framework details
export function useAnalysisFramework(frameworkId: string | undefined) {
  return useQuery({
    queryKey: analysisKeys.framework(frameworkId || ''),
    queryFn: () => frameworkAnalysisService.getFramework(frameworkId!),
    enabled: !!frameworkId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Hook for framework-aware analysis
export function useFrameworkAnalysis() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (request: BaseAnalysisRequest) => {
      // Validate request before sending
      if (!frameworkValidation.validateRequest(request)) {
        throw new Error('Invalid analysis request')
      }
      
      return frameworkAnalysisService.analyzeWithFramework(request)
    },
    onSuccess: (data) => {
      // Cache the analysis result
      queryClient.setQueryData(analysisKeys.result(data.id), data)
      // Invalidate statistics and history
      queryClient.invalidateQueries({ queryKey: analysisKeys.statistics() })
      queryClient.invalidateQueries({ queryKey: analysisKeys.history() })
    },
    onError: (error) => {
      console.error('Framework analysis failed:', error)
    },
  })
}

// Hook for getting analysis history
export function useAnalysisHistory() {
  return useQuery({
    queryKey: analysisKeys.history(),
    queryFn: () => frameworkAnalysisService.getAnalysisHistory(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Hook for framework-specific CBIL analysis
export function useCBILAnalysis() {
  const frameworkAnalysis = useFrameworkAnalysis()

  const analyzeCBIL = (text: string, metadata?: any) => {
    return frameworkAnalysis.mutate({
      framework: 'cbil',
      text,
      metadata,
    })
  }

  return {
    ...frameworkAnalysis,
    analyzeCBIL,
  }
}

// Hook for workflow management (transcript -> analysis)
export function useTranscriptToAnalysis() {
  const frameworkAnalysis = useFrameworkAnalysis()

  const analyzeTranscript = async (
    transcriptText: string,
    frameworkId: string,
    metadata?: {
      source_type: 'file_upload' | 'youtube'
      source_id: string
      duration?: number
      language?: string
    }
  ) => {
    const request: BaseAnalysisRequest = {
      framework: frameworkId,
      text: transcriptText,
      metadata: metadata ? {
        ...metadata,
        source_type: metadata.source_type,
        source_id: metadata.source_id,
      } : undefined,
    }

    return frameworkAnalysis.mutate(request)
  }

  return {
    ...frameworkAnalysis,
    analyzeTranscript,
  }
}

// Hook for framework validation and requirements
export function useFrameworkValidation(frameworkId: string) {
  const requirements = frameworkValidation.getFrameworkRequirements(frameworkId)
  const isValid = frameworkValidation.validateFramework(frameworkId)

  const validateText = (text: string): { isValid: boolean; errors: string[] } => {
    const errors: string[] = []

    if (!text || text.trim().length === 0) {
      errors.push('텍스트를 입력해주세요')
    }

    if (requirements.minTextLength && text.length < requirements.minTextLength) {
      errors.push(`최소 ${requirements.minTextLength}자 이상 입력해주세요`)
    }

    if (requirements.maxTextLength && text.length > requirements.maxTextLength) {
      errors.push(`최대 ${requirements.maxTextLength}자 이하로 입력해주세요`)
    }

    return {
      isValid: errors.length === 0,
      errors,
    }
  }

  return {
    requirements,
    isValidFramework: isValid,
    validateText,
  }
}