import { useState, useCallback, useRef } from 'react'
import { 
  ComprehensiveAnalysisRequest, 
  ComprehensiveAnalysisResult,
  FrameworkSpecificResult,
  CrossFrameworkInsight,
  OverallSummary,
  PrioritizedRecommendation,
  comprehensiveFrameworkUtils
} from '@/types/comprehensive-analysis'
import { parallelAnalysisApi } from '@/lib/parallel-analysis-api'

interface AnalysisProgress {
  framework: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  startTime?: number
  endTime?: number
  error?: string
}

interface UseParallelAnalysisState {
  isRunning: boolean
  isPaused: boolean
  progress: number
  currentFramework: string | null
  completedFrameworks: string[]
  frameworkProgress: Record<string, AnalysisProgress>
  results: ComprehensiveAnalysisResult | null
  error: Error | null
  estimatedTimeRemaining: number
}

interface UseParallelAnalysisReturn extends UseParallelAnalysisState {
  startAnalysis: (request: ComprehensiveAnalysisRequest) => Promise<void>
  pauseAnalysis: () => void
  resumeAnalysis: () => void
  resetAnalysis: () => void
  retryFailedFrameworks: () => Promise<void>
}

const RETRY_ATTEMPTS = 3
const RETRY_DELAY = 2000 // 2 seconds
const FRAMEWORK_TIMEOUT = 300000 // 5 minutes per framework

export function useParallelAnalysis(): UseParallelAnalysisReturn {
  const [state, setState] = useState<UseParallelAnalysisState>({
    isRunning: false,
    isPaused: false,
    progress: 0,
    currentFramework: null,
    completedFrameworks: [],
    frameworkProgress: {},
    results: null,
    error: null,
    estimatedTimeRemaining: 0
  })

  const analysisControllerRef = useRef<AbortController | null>(null)
  const currentRequestRef = useRef<ComprehensiveAnalysisRequest | null>(null)
  const retryCountRef = useRef<Record<string, number>>({})

  const updateState = useCallback((updates: Partial<UseParallelAnalysisState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }, [])

  const updateFrameworkProgress = useCallback((framework: string, updates: Partial<AnalysisProgress>) => {
    setState(prev => ({
      ...prev,
      frameworkProgress: {
        ...prev.frameworkProgress,
        [framework]: {
          ...prev.frameworkProgress[framework],
          ...updates
        }
      }
    }))
  }, [])

  const calculateOverallProgress = useCallback((frameworkProgress: Record<string, AnalysisProgress>) => {
    const frameworks = Object.keys(frameworkProgress)
    if (frameworks.length === 0) return 0

    const totalProgress = frameworks.reduce((sum, framework) => {
      return sum + (frameworkProgress[framework]?.progress || 0)
    }, 0)

    return totalProgress / frameworks.length
  }, [])

  const calculateEstimatedTime = useCallback((frameworkProgress: Record<string, AnalysisProgress>) => {
    const frameworks = Object.keys(frameworkProgress)
    const now = Date.now()
    
    let totalEstimate = 0
    let activeFrameworks = 0

    frameworks.forEach(framework => {
      const progress = frameworkProgress[framework]
      if (progress.status === 'running' && progress.startTime && progress.progress > 0) {
        const elapsed = now - progress.startTime
        const estimatedTotal = elapsed / (progress.progress / 100)
        const remaining = estimatedTotal - elapsed
        totalEstimate += Math.max(0, remaining)
        activeFrameworks++
      } else if (progress.status === 'pending') {
        totalEstimate += 30000 // 30 seconds default estimate
      }
    })

    return totalEstimate
  }, [])

  const analyzeFramework = async (
    frameworkId: string, 
    request: ComprehensiveAnalysisRequest,
    abortSignal: AbortSignal
  ): Promise<FrameworkSpecificResult> => {
    const retryCount = retryCountRef.current[frameworkId] || 0
    
    try {
      updateFrameworkProgress(frameworkId, {
        framework: frameworkId,
        status: 'running',
        progress: 0,
        startTime: Date.now()
      })

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        if (abortSignal.aborted) {
          clearInterval(progressInterval)
          return
        }

        updateFrameworkProgress(frameworkId, {
          progress: Math.min(90, (Date.now() - (state.frameworkProgress[frameworkId]?.startTime || Date.now())) / 1000 * 3)
        })
      }, 1000)

      const result = await parallelAnalysisApi.analyzeWithFramework(
        frameworkId,
        request.text,
        {
          temperature: request.temperature,
          metadata: request.metadata,
          abortSignal
        }
      )

      clearInterval(progressInterval)

      updateFrameworkProgress(frameworkId, {
        status: 'completed',
        progress: 100,
        endTime: Date.now()
      })

      // Reset retry count on success
      retryCountRef.current[frameworkId] = 0

      return result

    } catch (error) {
      updateFrameworkProgress(frameworkId, {
        status: 'failed',
        progress: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
        endTime: Date.now()
      })

      // Retry logic
      if (retryCount < RETRY_ATTEMPTS && !abortSignal.aborted) {
        console.warn(`Framework ${frameworkId} failed, retrying... (${retryCount + 1}/${RETRY_ATTEMPTS})`)
        retryCountRef.current[frameworkId] = retryCount + 1
        
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (retryCount + 1)))
        
        if (!abortSignal.aborted) {
          return analyzeFramework(frameworkId, request, abortSignal)
        }
      }

      throw error
    }
  }

  const generateCrossFrameworkInsights = (
    results: Record<string, FrameworkSpecificResult>
  ): CrossFrameworkInsight[] => {
    return comprehensiveFrameworkUtils.generateCrossFrameworkInsights(results)
  }

  const generateOverallSummary = (
    results: Record<string, FrameworkSpecificResult>,
    frameworks: string[]
  ): OverallSummary => {
    const overallScore = comprehensiveFrameworkUtils.calculateOverallScore(results)
    
    // Extract patterns and insights
    const dominantPatterns: string[] = []
    const keyStrengths: string[] = []
    const priorityImprovements: string[] = []

    // Analyze patterns across frameworks
    Object.entries(results).forEach(([frameworkId, result]) => {
      // Extract framework-specific insights
      // This would be more sophisticated in a real implementation
      if ('recommendations' in result && result.recommendations) {
        result.recommendations.forEach((rec: string) => {
          if (rec.includes('강점') || rec.includes('우수')) {
            keyStrengths.push(rec)
          } else if (rec.includes('개선') || rec.includes('보완')) {
            priorityImprovements.push(rec)
          }
        })
      }
    })

    return {
      total_frameworks: frameworks.length,
      analysis_coverage: (Object.keys(results).length / frameworks.length) * 100,
      dominant_patterns: dominantPatterns,
      key_strengths: keyStrengths.slice(0, 5), // Top 5
      priority_improvements: priorityImprovements.slice(0, 5), // Top 5
      overall_score: overallScore
    }
  }

  const generatePrioritizedRecommendations = (
    results: Record<string, FrameworkSpecificResult>
  ): PrioritizedRecommendation[] => {
    const recommendations: PrioritizedRecommendation[] = []

    Object.entries(results).forEach(([frameworkId, result]) => {
      if ('recommendations' in result && result.recommendations) {
        result.recommendations.forEach((rec: string, index: number) => {
          recommendations.push({
            recommendation: rec,
            priority: index < 2 ? 'high' : index < 4 ? 'medium' : 'low',
            frameworks_source: [frameworkId],
            implementation_difficulty: 'moderate', // This would be determined by AI
            expected_impact: 'medium' // This would be determined by AI
          })
        })
      }
    })

    // Sort by priority and limit to top recommendations
    return recommendations
      .sort((a, b) => {
        const priorityOrder = { high: 0, medium: 1, low: 2 }
        return priorityOrder[a.priority] - priorityOrder[b.priority]
      })
      .slice(0, 10)
  }

  const startAnalysis = async (request: ComprehensiveAnalysisRequest) => {
    try {
      // Reset state
      const controller = new AbortController()
      analysisControllerRef.current = controller
      currentRequestRef.current = request
      retryCountRef.current = {}

      // Initialize framework progress
      const initialProgress: Record<string, AnalysisProgress> = {}
      request.frameworks.forEach(framework => {
        initialProgress[framework] = {
          framework,
          status: 'pending',
          progress: 0
        }
      })

      updateState({
        isRunning: true,
        isPaused: false,
        progress: 0,
        currentFramework: null,
        completedFrameworks: [],
        frameworkProgress: initialProgress,
        results: null,
        error: null,
        estimatedTimeRemaining: request.frameworks.length * 30000 // 30 sec per framework estimate
      })

      // Start parallel analysis
      const analysisPromises = request.frameworks.map(frameworkId => 
        analyzeFramework(frameworkId, request, controller.signal)
          .then(result => ({ frameworkId, result, success: true }))
          .catch(error => ({ frameworkId, error, success: false }))
      )

      // Track completion
      const analysisResults: Record<string, FrameworkSpecificResult> = {}
      const completedFrameworks: string[] = []

      // Process results as they complete
      const processResults = async () => {
        for (const promise of analysisPromises) {
          if (controller.signal.aborted) break

          try {
            const outcome = await promise
            
            if (outcome.success && 'result' in outcome) {
              analysisResults[outcome.frameworkId] = outcome.result
              completedFrameworks.push(outcome.frameworkId)
              
              updateState({
                completedFrameworks: [...completedFrameworks],
                progress: calculateOverallProgress(state.frameworkProgress)
              })
            }
          } catch (error) {
            console.error(`Framework ${promise} analysis failed:`, error)
          }
        }
      }

      await processResults()

      if (!controller.signal.aborted && Object.keys(analysisResults).length > 0) {
        // Generate comprehensive results
        const crossFrameworkInsights = generateCrossFrameworkInsights(analysisResults)
        const overallSummary = generateOverallSummary(analysisResults, request.frameworks)
        const recommendations = generatePrioritizedRecommendations(analysisResults)

        const comprehensiveResult: ComprehensiveAnalysisResult = {
          id: `analysis_${Date.now()}`,
          request_id: request.metadata?.job_id || `req_${Date.now()}`,
          frameworks_analyzed: Object.keys(analysisResults),
          individual_results: analysisResults,
          cross_framework_insights: crossFrameworkInsights,
          overall_summary: overallSummary,
          recommendations,
          analysis_metadata: {
            total_analysis_time: Date.now() - (Date.now() - 30000), // Approximate
            parallel_execution: request.parallel_execution,
            temperature_used: request.temperature,
            text_length: request.text.length,
            created_at: new Date().toISOString()
          }
        }

        updateState({
          isRunning: false,
          progress: 100,
          results: comprehensiveResult,
          estimatedTimeRemaining: 0
        })
      }

    } catch (error) {
      updateState({
        isRunning: false,
        error: error instanceof Error ? error : new Error('Analysis failed'),
        estimatedTimeRemaining: 0
      })
    }
  }

  const pauseAnalysis = () => {
    updateState({ isPaused: true })
    // In a real implementation, you'd pause individual framework analyses
  }

  const resumeAnalysis = () => {
    updateState({ isPaused: false })
    // In a real implementation, you'd resume paused analyses
  }

  const resetAnalysis = () => {
    if (analysisControllerRef.current) {
      analysisControllerRef.current.abort()
    }
    
    setState({
      isRunning: false,
      isPaused: false,
      progress: 0,
      currentFramework: null,
      completedFrameworks: [],
      frameworkProgress: {},
      results: null,
      error: null,
      estimatedTimeRemaining: 0
    })
    
    retryCountRef.current = {}
  }

  const retryFailedFrameworks = async () => {
    if (!currentRequestRef.current) return

    const failedFrameworks = Object.keys(state.frameworkProgress).filter(
      framework => state.frameworkProgress[framework].status === 'failed'
    )

    if (failedFrameworks.length === 0) return

    // Reset failed frameworks and retry
    failedFrameworks.forEach(framework => {
      retryCountRef.current[framework] = 0
      updateFrameworkProgress(framework, {
        status: 'pending',
        progress: 0,
        error: undefined
      })
    })

    // Restart analysis for failed frameworks only
    const retryRequest: ComprehensiveAnalysisRequest = {
      ...currentRequestRef.current,
      frameworks: failedFrameworks
    }

    await startAnalysis(retryRequest)
  }

  return {
    ...state,
    startAnalysis,
    pauseAnalysis,
    resumeAnalysis,
    resetAnalysis,
    retryFailedFrameworks
  }
}