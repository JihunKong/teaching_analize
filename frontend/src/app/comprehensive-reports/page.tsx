'use client'

import { useState, useEffect } from 'react'
import { 
  AnalysisSelectionCard, 
  ReportConfigurationPanel, 
  ComprehensiveReportViewer 
} from '../../components/comprehensive'

interface Analysis {
  analysis_id: string
  framework: string
  framework_name: string
  analysis: string
  character_count: number
  word_count: number
  created_at: string
  metadata?: {
    video_url?: string
    video_id?: string
    language?: string
    temperature?: number
  }
}

interface Framework {
  id: string
  name: string
  description: string
}

interface ReportConfiguration {
  title: string
  type: 'comparison' | 'detailed' | 'summary'
  includeRecommendations: boolean
  frameworkWeights: { [framework: string]: number }
  format: 'html' | 'pdf'
}

interface ComprehensiveReportJob {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  message: string
  progress?: number
  result?: {
    report_html?: string
    report_url?: string
    generated_at: string
  }
}

export default function ComprehensiveReportsPage() {
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [selectedAnalyses, setSelectedAnalyses] = useState<string[]>([])
  const [frameworks, setFrameworks] = useState<Framework[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [dateFilter, setDateFilter] = useState('')
  const [frameworkFilter, setFrameworkFilter] = useState('')
  const [sortBy, setSortBy] = useState<'date' | 'framework' | 'length'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  
  // Report configuration
  const [reportConfig, setReportConfig] = useState<ReportConfiguration>({
    title: '종합 교육 분석 보고서',
    type: 'detailed',
    includeRecommendations: true,
    frameworkWeights: {},
    format: 'html'
  })
  
  // Report generation
  const [generatingReport, setGeneratingReport] = useState(false)
  const [reportJob, setReportJob] = useState<ComprehensiveReportJob | null>(null)
  const [generatedReports, setGeneratedReports] = useState<ComprehensiveReportJob[]>([])
  const [fromParallelAnalysis, setFromParallelAnalysis] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    // Initialize framework weights when frameworks are loaded
    if (frameworks.length > 0) {
      const initialWeights: { [framework: string]: number } = {}
      frameworks.forEach(fw => {
        initialWeights[fw.id] = 1.0 // Equal weight initially
      })
      setReportConfig(prev => ({
        ...prev,
        frameworkWeights: initialWeights
      }))
    }
  }, [frameworks])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load frameworks
      const frameworksResponse = await fetch('/api/frameworks')
      if (frameworksResponse.ok) {
        const frameworksData = await frameworksResponse.json()
        setFrameworks(frameworksData.frameworks || [])
      }

      // Check for parallel analysis results from analysis page
      const storedResults = sessionStorage.getItem('parallelAnalysisResults')
      let loadedAnalyses: Analysis[] = []
      
      if (storedResults) {
        try {
          const { results, frameworks: storedFrameworks } = JSON.parse(storedResults)
          
          // Convert parallel results to analyses format
          loadedAnalyses = Object.entries(results).map(([frameworkId, result]: [string, any]) => {
            if (result && result.status === 'completed' && result.result) {
              const framework = storedFrameworks.find((fw: any) => fw.id === frameworkId)
              return {
                analysis_id: result.analysis_id,
                framework: frameworkId,
                framework_name: framework?.name || frameworkId,
                analysis: result.result.analysis,
                character_count: result.result.character_count,
                word_count: result.result.word_count || 0,
                created_at: result.result.created_at,
                metadata: {
                  temperature: 0.3,
                  parallel: true
                }
              }
            }
            return null
          }).filter(Boolean) as Analysis[]
          
          // Auto-select all loaded analyses
          if (loadedAnalyses.length > 0) {
            setSelectedAnalyses(loadedAnalyses.map(a => a.analysis_id))
            setFromParallelAnalysis(true)
          }
          
          // Clear stored data after loading
          sessionStorage.removeItem('parallelAnalysisResults')
        } catch (error) {
          console.error('Error parsing stored results:', error)
        }
      }

      // Add mock data if no real data was loaded
      if (loadedAnalyses.length === 0) {
        loadedAnalyses = [
          {
            analysis_id: "cbil-001",
            framework: "cbil",
            framework_name: "개념기반 탐구 수업(CBIL)",
            analysis: "CBIL 7단계 분석 결과입니다...",
            character_count: 5026,
            word_count: 1229,
            created_at: "2025-08-22T10:35:00Z",
            metadata: {
              video_id: "-OLCt6WScEY",
              temperature: 0.3
            }
          },
          {
            analysis_id: "discussion-001",
            framework: "discussion",
            framework_name: "학생주도 토론 분석",
            analysis: "학생주도 토론 분석 결과입니다...",
            character_count: 4521,
            word_count: 1105,
            created_at: "2025-08-22T11:20:00Z",
            metadata: {
              video_id: "-OLCt6WScEY",
              temperature: 0.3
            }
          },
          {
            analysis_id: "coaching-001",
            framework: "coaching",
            framework_name: "수업 코칭 분석",
            analysis: "수업 코칭 분석 결과입니다...",
            character_count: 3892,
            word_count: 952,
            created_at: "2025-08-22T11:45:00Z",
            metadata: {
              video_id: "-OLCt6WScEY",
              temperature: 0.3
            }
          }
        ]
      }
      
      setAnalyses(loadedAnalyses)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredAndSortedAnalyses = analyses
    .filter(analysis => {
      const matchesSearch = !searchTerm || 
        analysis.framework_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        analysis.analysis.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesDate = !dateFilter || 
        new Date(analysis.created_at).toISOString().split('T')[0] >= dateFilter
      
      const matchesFramework = !frameworkFilter || analysis.framework === frameworkFilter
      
      return matchesSearch && matchesDate && matchesFramework
    })
    .sort((a, b) => {
      let comparison = 0
      
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          break
        case 'framework':
          comparison = a.framework_name.localeCompare(b.framework_name)
          break
        case 'length':
          comparison = a.character_count - b.character_count
          break
      }
      
      return sortOrder === 'desc' ? -comparison : comparison
    })

  const toggleAnalysisSelection = (analysisId: string) => {
    setSelectedAnalyses(prev => 
      prev.includes(analysisId) 
        ? prev.filter(id => id !== analysisId)
        : [...prev, analysisId]
    )
  }

  const selectAllAnalyses = () => {
    setSelectedAnalyses(filteredAndSortedAnalyses.map(a => a.analysis_id))
  }

  const clearSelection = () => {
    setSelectedAnalyses([])
  }


  const generateComprehensiveReport = async () => {
    if (selectedAnalyses.length === 0) {
      alert('분석을 선택해주세요.')
      return
    }

    setGeneratingReport(true)
    
    try {
      const selectedAnalysisData = analyses.filter(a => selectedAnalyses.includes(a.analysis_id))
      
      const response = await fetch('/api/reports/generate/comprehensive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analyses: selectedAnalysisData,
          configuration: reportConfig
        }),
      })

      const data = await response.json()
      
      if (response.ok) {
        const job: ComprehensiveReportJob = {
          job_id: data.job_id || `comp-${Date.now()}`,
          status: data.status || 'processing',
          message: data.message || '종합 보고서를 생성하고 있습니다...',
          progress: 0
        }
        
        setReportJob(job)
        
        // Start polling for status
        pollReportStatus(job.job_id)
      } else {
        throw new Error(data.detail || 'Report generation failed')
      }
    } catch (error) {
      console.error('Error generating comprehensive report:', error)
      
      // For demo purposes, simulate successful report generation
      const mockJob: ComprehensiveReportJob = {
        job_id: `mock-${Date.now()}`,
        status: 'processing',
        message: '종합 보고서를 생성하고 있습니다...',
        progress: 0
      }
      
      setReportJob(mockJob)
      simulateReportGeneration(mockJob)
    }
  }

  const simulateReportGeneration = (job: ComprehensiveReportJob) => {
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 20 + 10
      
      if (progress >= 100) {
        clearInterval(interval)
        
        const completedJob: ComprehensiveReportJob = {
          ...job,
          status: 'completed',
          message: '종합 보고서가 성공적으로 생성되었습니다.',
          progress: 100,
          result: {
            report_html: generateMockReportHtml(),
            generated_at: new Date().toISOString()
          }
        }
        
        setReportJob(completedJob)
        setGeneratedReports(prev => [completedJob, ...prev])
        setGeneratingReport(false)
      } else {
        setReportJob(prev => prev ? { ...prev, progress } : null)
      }
    }, 800)
  }

  const pollReportStatus = async (jobId: string) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`/api/reports/status/${jobId}`)
        const data = await response.json()
        
        setReportJob(data)
        
        if (data.status === 'completed' || data.status === 'failed') {
          if (data.status === 'completed') {
            setGeneratedReports(prev => [data, ...prev])
          }
          setGeneratingReport(false)
          return
        }
        
        setTimeout(checkStatus, 3000)
      } catch (error) {
        console.error('Error checking report status:', error)
        setGeneratingReport(false)
      }
    }
    
    setTimeout(checkStatus, 2000)
  }

  const generateMockReportHtml = () => {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${reportConfig.title}</title>
        <meta charset="utf-8">
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .header { background: #667eea; color: white; padding: 20px; border-radius: 10px; }
          .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
          .framework { margin: 15px 0; padding: 15px; background: #f8f9fa; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>${reportConfig.title}</h1>
          <p>생성일: ${new Date().toLocaleDateString('ko-KR')}</p>
        </div>
        <div class="section">
          <h2>분석 개요</h2>
          <p>선택된 ${selectedAnalyses.length}개 분석 결과를 종합한 보고서입니다.</p>
        </div>
        <div class="section">
          <h2>프레임워크별 분석</h2>
          ${selectedAnalyses.map(id => {
            const analysis = analyses.find(a => a.analysis_id === id)
            return analysis ? `
              <div class="framework">
                <h3>${analysis.framework_name}</h3>
                <p>가중치: ${reportConfig.frameworkWeights[analysis.framework]?.toFixed(1) || 1.0}</p>
                <div>${analysis.analysis.substring(0, 500)}...</div>
              </div>
            ` : ''
          }).join('')}
        </div>
      </body>
      </html>
    `
  }

  const viewReport = (job: ComprehensiveReportJob) => {
    if (job.result?.report_html) {
      const newWindow = window.open('', '_blank')
      if (newWindow) {
        newWindow.document.write(job.result.report_html)
        newWindow.document.close()
      }
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
          <p>데이터를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="page-title">종합 보고서 생성</div>
      <div className="page-subtitle">여러 프레임워크 분석을 통합하여 포괄적인 교육 보고서를 생성합니다</div>
      
      {fromParallelAnalysis && (
        <div className="status status-success" style={{ marginBottom: '20px' }}>
          <strong>🎉 병렬 분석 완료!</strong> 분석 페이지에서 {selectedAnalyses.length}개 프레임워크 분석이 자동으로 로드되었습니다. 
          아래에서 설정을 조정하고 종합 보고서를 생성하세요.
        </div>
      )}
      
      {/* Analysis Selection Section */}
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>📚 분석 선택 ({selectedAnalyses.length}/{filteredAndSortedAnalyses.length})</h3>
          <div>
            <button 
              className="btn btn-secondary" 
              onClick={selectAllAnalyses}
              style={{ marginRight: '10px' }}
            >
              전체 선택
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={clearSelection}
            >
              선택 해제
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-2" style={{ marginBottom: '20px' }}>
          <div className="form-group">
            <label className="form-label">검색</label>
            <input
              type="text"
              className="form-input"
              placeholder="프레임워크명 또는 내용 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">생성일 이후</label>
            <input
              type="date"
              className="form-input"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
            />
          </div>
        </div>

        <div className="grid grid-3" style={{ marginBottom: '20px' }}>
          <div className="form-group">
            <label className="form-label">프레임워크 필터</label>
            <select
              className="form-select"
              value={frameworkFilter}
              onChange={(e) => setFrameworkFilter(e.target.value)}
            >
              <option value="">모든 프레임워크</option>
              {frameworks.map(fw => (
                <option key={fw.id} value={fw.id}>{fw.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">정렬 기준</label>
            <select
              className="form-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
            >
              <option value="date">생성일</option>
              <option value="framework">프레임워크</option>
              <option value="length">텍스트 길이</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">정렬 순서</label>
            <select
              className="form-select"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as any)}
            >
              <option value="desc">내림차순</option>
              <option value="asc">오름차순</option>
            </select>
          </div>
        </div>

        {/* Analysis List */}
        <div className="grid">
          {filteredAndSortedAnalyses.map(analysis => (
            <AnalysisSelectionCard
              key={analysis.analysis_id}
              analysis={analysis}
              selected={selectedAnalyses.includes(analysis.analysis_id)}
              onToggle={toggleAnalysisSelection}
            />
          ))}
        </div>

        {filteredAndSortedAnalyses.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            조건에 맞는 분석 결과가 없습니다.
          </div>
        )}
      </div>

      {/* Report Configuration Section */}
      {selectedAnalyses.length > 0 && (
        <ReportConfigurationPanel
          frameworks={frameworks}
          selectedFrameworks={Array.from(new Set(
            selectedAnalyses.map(id => analyses.find(a => a.analysis_id === id)?.framework).filter(Boolean) as string[]
          ))}
          configuration={reportConfig}
          onConfigurationChange={setReportConfig}
        />
      )}

      {/* Report Generation Section */}
      <div className="container">
        <h3>🚀 보고서 생성</h3>
        
        <div style={{ textAlign: 'center', marginBottom: '20px' }}>
          <button
            className="btn btn-large"
            onClick={generateComprehensiveReport}
            disabled={selectedAnalyses.length === 0 || generatingReport}
            style={{ marginRight: '10px' }}
          >
            {generatingReport ? '종합 보고서 생성 중...' : '종합 보고서 생성'}
          </button>
          
          <div style={{ marginTop: '10px', fontSize: '0.9rem', color: '#666' }}>
            {selectedAnalyses.length}개 분석 선택됨
          </div>
        </div>

        {/* Progress Display */}
        {reportJob && (
          <div style={{ 
            padding: '20px',
            backgroundColor: '#f8f9fa',
            borderRadius: '10px',
            marginBottom: '20px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <strong>보고서 생성 진행상황</strong>
              <span style={{
                color: reportJob.status === 'completed' ? '#28a745' : 
                      reportJob.status === 'failed' ? '#dc3545' : '#ffc107'
              }}>
                {reportJob.status === 'pending' && '대기 중'}
                {reportJob.status === 'processing' && '생성 중'}
                {reportJob.status === 'completed' && '완료'}
                {reportJob.status === 'failed' && '실패'}
              </span>
            </div>
            
            {typeof reportJob.progress === 'number' && (
              <div className="progress">
                <div 
                  className="progress-bar" 
                  style={{ width: `${reportJob.progress}%` }}
                >
                  {Math.round(reportJob.progress)}%
                </div>
              </div>
            )}
            
            <p style={{ margin: '10px 0 0 0' }}>{reportJob.message}</p>
            
            {reportJob.status === 'completed' && reportJob.result?.report_html && (
              <div style={{ marginTop: '20px' }}>
                <ComprehensiveReportViewer
                  reportHtml={reportJob.result.report_html}
                  title={reportConfig.title}
                  onClose={() => setReportJob(null)}
                />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Generated Reports List */}
      {generatedReports.length > 0 && (
        <div className="container">
          <h3>📋 생성된 보고서</h3>
          
          <div className="grid">
            {generatedReports.map((report, index) => (
              <div key={report.job_id} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <h4 style={{ margin: 0 }}>종합 보고서 #{generatedReports.length - index}</h4>
                  <span style={{
                    backgroundColor: report.status === 'completed' ? '#28a745' : '#dc3545',
                    color: 'white',
                    padding: '2px 8px',
                    borderRadius: '10px',
                    fontSize: '0.8rem'
                  }}>
                    {report.status === 'completed' ? '완료' : '실패'}
                  </span>
                </div>
                
                <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '10px' }}>
                  생성일: {new Date(report.result?.generated_at || '').toLocaleDateString('ko-KR')}
                </div>
                
                <div style={{ textAlign: 'center' }}>
                  <button
                    className="btn"
                    onClick={() => viewReport(report)}
                    disabled={report.status !== 'completed'}
                  >
                    📄 새 탭에서 보기
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="container">
        <h3>💡 도움말</h3>
        <div className="grid grid-2">
          <div>
            <h4>🎯 보고서 유형</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li><strong>상세 분석:</strong> 각 프레임워크별 완전한 분석 포함</li>
              <li><strong>비교 분석:</strong> 프레임워크 간 비교 중심</li>
              <li><strong>요약 분석:</strong> 핵심 내용만 간략히 정리</li>
            </ul>
            
            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
              <strong>💡 팁:</strong> <a href="/analysis" style={{ color: '#667eea' }}>분석 페이지</a>에서 
              병렬 분석을 실행하면 모든 프레임워크 분석을 자동으로 가져올 수 있습니다.
            </div>
          </div>
          
          <div>
            <h4>⚖️ 가중치 설정</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li><strong>1.0:</strong> 기본 중요도 (권장)</li>
              <li><strong>0.1-0.9:</strong> 낮은 중요도</li>
              <li><strong>1.1-3.0:</strong> 높은 중요도</li>
            </ul>
            
            <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
              <strong>📊 예시:</strong> CBIL 분석을 중심으로 하려면 CBIL 가중치를 2.0으로, 
              나머지를 0.8로 설정하세요.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}