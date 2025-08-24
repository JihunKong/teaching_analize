import { useState, useCallback, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReportGenerator, { ReportOptions, ReportData, reportUtils } from '../lib/report-generator'
import { 
  ComprehensiveAnalysisResult, 
  FrameworkSpecificResult,
  comprehensiveFrameworkUtils 
} from '../types/comprehensive-analysis'

export interface GeneratedReport {
  id: string
  title: string
  html: string
  metadata: ReportData['metadata']
  createdAt: string
  type: 'comprehensive' | 'summary' | 'individual'
  frameworkIds: string[]
  options: ReportOptions
}

export interface ReportGenerationState {
  isGenerating: boolean
  progress: number
  error: string | null
  currentStep: string
}

export interface UseReportGenerationReturn {
  // State
  generatedReports: GeneratedReport[]
  isLoading: boolean
  error: string | null
  generationState: ReportGenerationState

  // Actions
  generateComprehensiveReport: (
    analysisResult: ComprehensiveAnalysisResult,
    metadata: ReportData['metadata'],
    options?: Partial<ReportOptions>
  ) => Promise<GeneratedReport>
  
  generateFrameworkReport: (
    frameworkId: string,
    result: FrameworkSpecificResult,
    metadata: ReportData['metadata'],
    options?: Partial<ReportOptions>
  ) => Promise<GeneratedReport>
  
  generateSummaryReport: (
    analysisResult: ComprehensiveAnalysisResult,
    metadata: ReportData['metadata'],
    options?: Partial<ReportOptions>
  ) => Promise<GeneratedReport>
  
  // Report management
  deleteReport: (reportId: string) => void
  downloadReport: (reportId: string, format?: 'html' | 'pdf') => void
  previewReport: (reportId: string) => void
  getReportById: (reportId: string) => GeneratedReport | undefined
  
  // Utilities
  exportToPDF: (html: string, filename: string) => Promise<void>
  printReport: (reportId: string) => void
  shareReport: (reportId: string) => Promise<string>
}

const REPORTS_STORAGE_KEY = 'aiboa_generated_reports'
const MAX_CACHED_REPORTS = 50

export const useReportGeneration = (): UseReportGenerationReturn => {
  const queryClient = useQueryClient()
  
  const [generationState, setGenerationState] = useState<ReportGenerationState>({
    isGenerating: false,
    progress: 0,
    error: null,
    currentStep: ''
  })

  // Load cached reports
  const { data: generatedReports = [], isLoading } = useQuery({
    queryKey: ['generated-reports'],
    queryFn: () => {
      try {
        const cached = localStorage.getItem(REPORTS_STORAGE_KEY)
        return cached ? JSON.parse(cached) : []
      } catch (error) {
        console.error('Failed to load cached reports:', error)
        return []
      }
    },
    staleTime: 0,
    refetchOnWindowFocus: false
  })

  // Save reports to cache
  const saveReportsToCache = useCallback((reports: GeneratedReport[]) => {
    try {
      // Keep only the most recent reports
      const reportsToSave = reports
        .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
        .slice(0, MAX_CACHED_REPORTS)
      
      localStorage.setItem(REPORTS_STORAGE_KEY, JSON.stringify(reportsToSave))
      queryClient.setQueryData(['generated-reports'], reportsToSave)
    } catch (error) {
      console.error('Failed to cache reports:', error)
    }
  }, [queryClient])

  // Generate comprehensive report
  const generateComprehensiveReport = useCallback(async (
    analysisResult: ComprehensiveAnalysisResult,
    metadata: ReportData['metadata'],
    options: Partial<ReportOptions> = {}
  ): Promise<GeneratedReport> => {
    setGenerationState({
      isGenerating: true,
      progress: 0,
      error: null,
      currentStep: '보고서 생성 준비 중...'
    })

    try {
      setGenerationState(prev => ({ ...prev, progress: 20, currentStep: '분석 데이터 처리 중...' }))
      
      const reportOptions: ReportOptions = {
        includeCharts: true,
        includeCrossAnalysis: true,
        includeRecommendations: true,
        language: 'ko',
        theme: 'light',
        format: 'comprehensive',
        ...options
      }

      const reportData: ReportData = {
        title: `종합 분석 보고서`,
        subtitle: `${analysisResult.frameworks_analyzed.length}개 프레임워크 통합 분석`,
        date: new Date().toLocaleDateString('ko-KR'),
        metadata: {
          ...metadata,
          analysisTime: `${analysisResult.analysis_metadata?.total_analysis_time || 0}초`
        },
        results: analysisResult
      }

      setGenerationState(prev => ({ ...prev, progress: 50, currentStep: 'HTML 보고서 생성 중...' }))

      const generator = new ReportGenerator(reportOptions)
      const html = generator.generateReport(reportData)

      setGenerationState(prev => ({ ...prev, progress: 80, currentStep: '보고서 저장 중...' }))

      const report: GeneratedReport = {
        id: `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        title: reportData.title,
        html,
        metadata,
        createdAt: new Date().toISOString(),
        type: 'comprehensive',
        frameworkIds: analysisResult.frameworks_analyzed,
        options: reportOptions
      }

      // Save to cache
      const updatedReports = [report, ...generatedReports]
      saveReportsToCache(updatedReports)

      setGenerationState(prev => ({ ...prev, progress: 100, currentStep: '완료' }))
      
      // Reset state after a brief delay
      setTimeout(() => {
        setGenerationState({
          isGenerating: false,
          progress: 0,
          error: null,
          currentStep: ''
        })
      }, 1000)

      return report
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '보고서 생성 중 오류가 발생했습니다'
      setGenerationState({
        isGenerating: false,
        progress: 0,
        error: errorMessage,
        currentStep: '오류 발생'
      })
      throw error
    }
  }, [generatedReports, saveReportsToCache])

  // Generate framework-specific report
  const generateFrameworkReport = useCallback(async (
    frameworkId: string,
    result: FrameworkSpecificResult,
    metadata: ReportData['metadata'],
    options: Partial<ReportOptions> = {}
  ): Promise<GeneratedReport> => {
    setGenerationState({
      isGenerating: true,
      progress: 0,
      error: null,
      currentStep: '개별 프레임워크 보고서 생성 중...'
    })

    try {
      const framework = comprehensiveFrameworkUtils.getFramework(frameworkId)
      if (!framework) {
        throw new Error(`프레임워크 ${frameworkId}를 찾을 수 없습니다`)
      }

      setGenerationState(prev => ({ ...prev, progress: 30, currentStep: 'HTML 보고서 생성 중...' }))

      const reportOptions: ReportOptions = {
        includeCharts: true,
        includeCrossAnalysis: false,
        includeRecommendations: true,
        language: 'ko',
        theme: 'light',
        format: 'individual',
        frameworks: [frameworkId],
        ...options
      }

      const generator = new ReportGenerator(reportOptions)
      const html = generator.generateFrameworkReport(frameworkId, result, metadata)

      setGenerationState(prev => ({ ...prev, progress: 80, currentStep: '보고서 저장 중...' }))

      const report: GeneratedReport = {
        id: `report_${frameworkId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        title: `${framework.name_ko} 분석 보고서`,
        html,
        metadata,
        createdAt: new Date().toISOString(),
        type: 'individual',
        frameworkIds: [frameworkId],
        options: reportOptions
      }

      const updatedReports = [report, ...generatedReports]
      saveReportsToCache(updatedReports)

      setGenerationState(prev => ({ ...prev, progress: 100, currentStep: '완료' }))
      
      setTimeout(() => {
        setGenerationState({
          isGenerating: false,
          progress: 0,
          error: null,
          currentStep: ''
        })
      }, 1000)

      return report
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '보고서 생성 중 오류가 발생했습니다'
      setGenerationState({
        isGenerating: false,
        progress: 0,
        error: errorMessage,
        currentStep: '오류 발생'
      })
      throw error
    }
  }, [generatedReports, saveReportsToCache])

  // Generate summary report
  const generateSummaryReport = useCallback(async (
    analysisResult: ComprehensiveAnalysisResult,
    metadata: ReportData['metadata'],
    options: Partial<ReportOptions> = {}
  ): Promise<GeneratedReport> => {
    const reportOptions: ReportOptions = {
      ...options,
      format: 'summary',
      includeCrossAnalysis: false,
      includeCharts: false,
      includeRecommendations: options.includeRecommendations ?? true,
      language: options.language ?? 'ko',
      theme: options.theme ?? 'light',
      frameworks: options.frameworks ?? ['cbil', 'qta', 'sei']
    }

    return generateComprehensiveReport(analysisResult, metadata, reportOptions)
  }, [generateComprehensiveReport])

  // Delete report
  const deleteReportMutation = useMutation({
    mutationFn: async (reportId: string) => {
      const updatedReports = generatedReports.filter((report: GeneratedReport) => report.id !== reportId)
      saveReportsToCache(updatedReports)
      return updatedReports
    },
    onSuccess: (updatedReports) => {
      queryClient.setQueryData(['generated-reports'], updatedReports)
    }
  })

  const deleteReport = useCallback((reportId: string) => {
    deleteReportMutation.mutate(reportId)
  }, [deleteReportMutation])

  // Download report
  const downloadReport = useCallback(async (reportId: string, format: 'html' | 'pdf' = 'html') => {
    const report = generatedReports.find((r: GeneratedReport) => r.id === reportId)
    if (!report) {
      throw new Error('보고서를 찾을 수 없습니다')
    }

    if (format === 'html') {
      const filename = reportUtils.generateFileName(report.title, 'html')
      reportUtils.downloadReport(report.html, filename)
    } else {
      // PDF export
      await exportToPDF(report.html, reportUtils.generateFileName(report.title, 'pdf'))
    }
  }, [generatedReports])

  // Export to PDF
  const exportToPDF = useCallback(async (html: string, filename: string) => {
    try {
      // Dynamic import to avoid bundle size issues
      const html2pdf = await import('html2pdf.js')
      
      const element = document.createElement('div')
      element.innerHTML = html
      element.style.width = '210mm'
      element.style.minHeight = '297mm'
      
      const options = {
        margin: [10, 10, 10, 10],
        filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { 
          scale: 2,
          useCORS: true,
          letterRendering: true
        },
        jsPDF: { 
          unit: 'mm', 
          format: 'a4', 
          orientation: 'portrait' 
        }
      }

      await html2pdf.default().from(element).set(options).save()
    } catch (error) {
      console.error('PDF 내보내기 오류:', error)
      throw new Error('PDF 내보내기 중 오류가 발생했습니다')
    }
  }, [])

  // Preview report
  const previewReport = useCallback((reportId: string) => {
    const report = generatedReports.find((r: GeneratedReport) => r.id === reportId)
    if (!report) {
      throw new Error('보고서를 찾을 수 없습니다')
    }

    const newWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes')
    if (newWindow) {
      newWindow.document.write(report.html)
      newWindow.document.close()
    }
  }, [generatedReports])

  // Get report by ID
  const getReportById = useCallback((reportId: string) => {
    return generatedReports.find((report: GeneratedReport) => report.id === reportId)
  }, [generatedReports])

  // Print report
  const printReport = useCallback((reportId: string) => {
    const report = generatedReports.find((r: GeneratedReport) => r.id === reportId)
    if (!report) {
      throw new Error('보고서를 찾을 수 없습니다')
    }

    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(report.html)
      printWindow.document.close()
      printWindow.focus()
      printWindow.print()
    }
  }, [generatedReports])

  // Share report (generate shareable link)
  const shareReport = useCallback(async (reportId: string): Promise<string> => {
    const report = generatedReports.find((r: GeneratedReport) => r.id === reportId)
    if (!report) {
      throw new Error('보고서를 찾을 수 없습니다')
    }

    // Create a data URL for sharing
    const dataUrl = reportUtils.convertToDataUrl(report.html)
    
    // In a real implementation, you might upload to a server and return a public URL
    // For now, we'll return the data URL
    return dataUrl
  }, [generatedReports])

  const memoizedReturn = useMemo(() => ({
    // State
    generatedReports,
    isLoading,
    error: generationState.error,
    generationState,

    // Actions
    generateComprehensiveReport,
    generateFrameworkReport,
    generateSummaryReport,

    // Report management
    deleteReport,
    downloadReport,
    previewReport,
    getReportById,

    // Utilities
    exportToPDF,
    printReport,
    shareReport
  }), [
    generatedReports,
    isLoading,
    generationState,
    generateComprehensiveReport,
    generateFrameworkReport,
    generateSummaryReport,
    deleteReport,
    downloadReport,
    previewReport,
    getReportById,
    exportToPDF,
    printReport,
    shareReport
  ])

  return memoizedReturn
}

export default useReportGeneration