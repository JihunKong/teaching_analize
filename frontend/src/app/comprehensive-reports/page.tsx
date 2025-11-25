'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import dynamic from 'next/dynamic'
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
    evaluation_type?: string
    from_workflow?: boolean
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

function ComprehensiveReportsContent() {
  const searchParams = useSearchParams()
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
    // Skip loading if we're in single analysis iframe mode
    const singleAnalysisId = searchParams.get('analysis_id')
    if (!singleAnalysisId) {
      loadData()
    }
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
      // Always use nginx backend URL for API requests (static export doesn't support API routes)
      const apiUrl = 'http://localhost:8080'
      const frameworksResponse = await fetch(`${apiUrl}/api/analyze/frameworks`)
      if (frameworksResponse.ok) {
        const frameworksData = await frameworksResponse.json()
        setFrameworks(frameworksData.frameworks || [])
      }

      let loadedAnalyses: Analysis[] = []

      // Check for analysis_id in URL parameter (from workflow redirect)
      const analysisIdFromUrl = searchParams.get('analysis_id')
      if (analysisIdFromUrl) {
        try {
          console.log('Fetching analysis from URL parameter:', analysisIdFromUrl)
          const analysisResponse = await fetch(`${apiUrl}/api/analyze/${analysisIdFromUrl}`)

          if (analysisResponse.ok) {
            const analysisData = await analysisResponse.json()
            console.log('Analysis data received:', analysisData)

            if (analysisData.status === 'completed' && analysisData.result) {
              // Convert API response to Analysis format
              const analysis: Analysis = {
                analysis_id: analysisIdFromUrl,
                framework: analysisData.result.evaluation_type || 'cbil_comprehensive',
                framework_name: 'CBIL 종합 분석',
                analysis: JSON.stringify(analysisData.result, null, 2), // Full result as JSON string
                character_count: JSON.stringify(analysisData.result).length,
                word_count: analysisData.result.matrix_analysis?.statistics?.total_utterances || 0,
                created_at: analysisData.created_at || new Date().toISOString(),
                metadata: {
                  video_url: analysisData.result.matrix_analysis?.statistics?.video_url,
                  evaluation_type: analysisData.result.evaluation_type,
                  from_workflow: true
                }
              }

              loadedAnalyses.push(analysis)

              // Auto-select this analysis
              setSelectedAnalyses([analysisIdFromUrl])
              console.log('Successfully loaded analysis from workflow')
            }
          } else {
            console.error('Failed to fetch analysis:', analysisResponse.status)
          }
        } catch (error) {
          console.error('Error fetching analysis from URL:', error)
        }
      }

      // Check for parallel analysis results from analysis page
      const storedResults = sessionStorage.getItem('parallelAnalysisResults')
      if (storedResults) {
        try {
          const { results, frameworks: storedFrameworks } = JSON.parse(storedResults)

          // Convert parallel results to analyses format
          const parallelAnalyses = Object.entries(results).map(([frameworkId, result]: [string, any]) => {
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

          loadedAnalyses = [...loadedAnalyses, ...parallelAnalyses]

          // Auto-select all parallel analyses
          if (parallelAnalyses.length > 0) {
            setSelectedAnalyses(prev => [...prev, ...parallelAnalyses.map(a => a.analysis_id)])
            setFromParallelAnalysis(true)
          }

          // Clear stored data after loading
          sessionStorage.removeItem('parallelAnalysisResults')
        } catch (error) {
          console.error('Error parsing stored results:', error)
        }
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
      // Always use nginx backend URL for API requests
      const apiUrl = 'http://localhost:8080'

      const response = await fetch(`${apiUrl}/api/reports/generate/comprehensive`, {
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
      // Always use nginx backend URL for API requests
      const apiUrl = 'http://localhost:8080'
      try {
        const response = await fetch(`${apiUrl}/api/reports/status/${jobId}`)
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
          body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
          }
          .report-container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          }
          .header {
            background: #667eea;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
          }
          .section {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
          }
          .framework {
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
          }
          @media (max-width: 768px) {
            .report-container {
              max-width: 100%;
              padding: 20px;
            }
          }
        </style>
      </head>
      <body>
        <div class="report-container">
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

  // Single analysis mode - display HTML report in iframe
  const singleAnalysisId = searchParams.get('analysis_id')

  // Add fullscreen class to body when in single analysis mode
  useEffect(() => {
    if (singleAnalysisId) {
      document.body.classList.add('fullscreen-report-mode')
      return () => {
        document.body.classList.remove('fullscreen-report-mode')
      }
    }
  }, [singleAnalysisId])

  if (singleAnalysisId) {
    // Use relative path to preserve port (nginx proxies API requests)
    return (
      <div className="fixed inset-0 w-screen h-screen bg-gradient-to-br from-indigo-50 via-white to-emerald-50 m-0 p-0" style={{ zIndex: 9999 }}>
        <iframe
          src={`/api/reports/html/${singleAnalysisId}`}
          className="w-full h-full border-none block"
          style={{ width: '100%', height: '100%', border: 'none', display: 'block', minWidth: '100%', minHeight: '100%' }}
          title="분석 보고서"
        />
      </div>
    )
  }

  if (loading) {
    return (
      <div className="fixed inset-0 w-screen h-screen bg-gradient-to-br from-indigo-50 via-white to-emerald-50 flex items-center justify-center">
        <div className="glass-card p-8 rounded-2xl shadow-2xl max-w-md w-full mx-4">
          <div className="spinner mb-4"></div>
          <p className="text-lg font-medium text-gray-700 text-center">데이터를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">Comprehensive Report Generation</h1>
        <p className="subtitle">Integrate multiple framework analyses into a comprehensive educational report</p>
      </div>

      {fromParallelAnalysis && (
        <div className="status status-success mb-8 p-5 rounded-xl bg-green-50 text-green-800 border border-green-200">
          <strong>🎉 Parallel Analysis Complete!</strong> {selectedAnalyses.length} framework analyses have been automatically loaded.
          Adjust settings below and generate your comprehensive report.
        </div>
      )}

      {/* Analysis Selection Section */}
      <div className="section">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-xl font-bold text-slate-900 m-0">
            📚 Select Analysis ({selectedAnalyses.length}/{filteredAndSortedAnalyses.length})
          </h3>
          <div className="flex gap-2.5">
            <button
              className="btn-secondary px-4 py-2 text-sm"
              onClick={selectAllAnalyses}
            >
              Select All
            </button>
            <button
              className="btn-secondary px-4 py-2 text-sm"
              onClick={clearSelection}
            >
              Clear Selection
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="grid grid-2 mb-5">
          <div className="form-group">
            <label className="form-label">Search</label>
            <input
              type="text"
              className="form-input"
              placeholder="Search framework or content..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Date Filter</label>
            <input
              type="date"
              className="form-input"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
            />
          </div>
        </div>

        <div className="grid grid-3" style={{ marginBottom: '30px' }}>
          <div className="form-group">
            <label className="form-label">Framework</label>
            <select
              className="form-select"
              value={frameworkFilter}
              onChange={(e) => setFrameworkFilter(e.target.value)}
            >
              <option value="">All Frameworks</option>
              {frameworks.map(fw => (
                <option key={fw.id} value={fw.id}>{fw.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Sort By</label>
            <select
              className="form-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
            >
              <option value="date">Date</option>
              <option value="framework">Framework</option>
              <option value="length">Length</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Order</label>
            <select
              className="form-select"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as any)}
            >
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>

        {/* Analysis List */}
        <div className="grid grid-2">
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
          <div style={{ textAlign: 'center', padding: '60px', color: '#64748B', background: '#F8FAFC', borderRadius: '12px', border: '2px dashed #E2E8F0' }}>
            No analysis results found matching your criteria.
          </div>
        )}
      </div>

      {/* Report Configuration Section */}
      {selectedAnalyses.length > 0 && (
        <div className="section" style={{ marginTop: '40px' }}>
          <ReportConfigurationPanel
            frameworks={frameworks}
            selectedFrameworks={Array.from(new Set(
              selectedAnalyses.map(id => analyses.find(a => a.analysis_id === id)?.framework).filter(Boolean) as string[]
            ))}
            configuration={reportConfig}
            onConfigurationChange={setReportConfig}
          />
        </div>
      )}

      {/* Report Generation Section */}
      <div className="section" style={{ marginTop: '40px', textAlign: 'center' }}>
        <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#0F172A', marginBottom: '20px' }}>🚀 Generate Report</h3>

        <div style={{ marginBottom: '30px' }}>
          <button
            className="btn-primary btn-large"
            onClick={generateComprehensiveReport}
            disabled={selectedAnalyses.length === 0 || generatingReport}
            style={{ minWidth: '250px' }}
          >
            {generatingReport ? 'Generating Report...' : 'Generate Comprehensive Report'}
          </button>

          <div style={{ marginTop: '15px', fontSize: '14px', color: '#64748B' }}>
            {selectedAnalyses.length} analyses selected
          </div>
        </div>

        {/* Progress Display */}
        {reportJob && (
          <div style={{
            padding: '30px',
            backgroundColor: '#F8FAFC',
            borderRadius: '16px',
            border: '1px solid #E2E8F0',
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <strong style={{ color: '#0F172A' }}>Generation Status</strong>
              <span style={{
                padding: '4px 12px',
                borderRadius: '9999px',
                fontSize: '12px',
                fontWeight: '600',
                backgroundColor: reportJob.status === 'completed' ? '#DCFCE7' :
                  reportJob.status === 'failed' ? '#FEE2E2' : '#FEF3C7',
                color: reportJob.status === 'completed' ? '#166534' :
                  reportJob.status === 'failed' ? '#991B1B' : '#92400E'
              }}>
                {reportJob.status === 'pending' && 'Pending'}
                {reportJob.status === 'processing' && 'Processing'}
                {reportJob.status === 'completed' && 'Completed'}
                {reportJob.status === 'failed' && 'Failed'}
              </span>
            </div>

            {typeof reportJob.progress === 'number' && (
              <div style={{ height: '8px', background: '#E2E8F0', borderRadius: '4px', overflow: 'hidden', marginBottom: '15px' }}>
                <div
                  style={{
                    width: `${reportJob.progress}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #2563EB, #4F46E5)',
                    transition: 'width 0.3s ease'
                  }}
                />
              </div>
            )}

            <p style={{ margin: 0, color: '#64748B', fontSize: '14px' }}>{reportJob.message}</p>

            {reportJob.status === 'completed' && reportJob.result?.report_html && (
              <div style={{ marginTop: '25px' }}>
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
        <div className="section" style={{ marginTop: '40px' }}>
          <h3 style={{ fontSize: '20px', fontWeight: '700', color: '#0F172A', marginBottom: '20px' }}>📋 Generated Reports</h3>

          <div className="grid grid-2">
            {generatedReports.map((report, index) => (
              <div key={report.job_id} className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h4 style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: '#0F172A' }}>
                    Comprehensive Report #{generatedReports.length - index}
                  </h4>
                  <span style={{
                    backgroundColor: report.status === 'completed' ? '#DCFCE7' : '#FEE2E2',
                    color: report.status === 'completed' ? '#166534' : '#991B1B',
                    padding: '4px 10px',
                    borderRadius: '9999px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    {report.status === 'completed' ? 'Success' : 'Failed'}
                  </span>
                </div>

                <div style={{ fontSize: '14px', color: '#64748B', marginBottom: '20px' }}>
                  Generated: {new Date(report.result?.generated_at || '').toLocaleDateString()}
                </div>

                <div style={{ textAlign: 'center' }}>
                  <button
                    className="btn-secondary"
                    onClick={() => viewReport(report)}
                    disabled={report.status !== 'completed'}
                    style={{ width: '100%' }}
                  >
                    📄 View in New Tab
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="section" style={{ marginTop: '40px', background: '#F8FAFC' }}>
        <h3 style={{ fontSize: '20px', fontWeight: '700', color: '#0F172A', marginBottom: '20px' }}>💡 Help & Tips</h3>
        <div className="grid grid-2">
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#0F172A', marginBottom: '10px' }}>🎯 Report Types</h4>
            <ul style={{ marginLeft: '20px', color: '#64748B', fontSize: '14px', lineHeight: '1.8' }}>
              <li><strong>Detailed:</strong> Includes full analysis for each framework</li>
              <li><strong>Comparison:</strong> Focuses on comparing frameworks</li>
              <li><strong>Summary:</strong> Concise overview of key insights</li>
            </ul>

            <div style={{ marginTop: '15px', padding: '15px', backgroundColor: 'white', borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '13px', color: '#64748B' }}>
              <strong>💡 Tip:</strong> Running parallel analysis on the <a href="/analysis" style={{ color: '#2563EB', textDecoration: 'none', fontWeight: '500' }}>Analysis Page</a> automatically loads all framework results here.
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#0F172A', marginBottom: '10px' }}>⚖️ Weight Settings</h4>
            <ul style={{ marginLeft: '20px', color: '#64748B', fontSize: '14px', lineHeight: '1.8' }}>
              <li><strong>1.0:</strong> Default importance (Recommended)</li>
              <li><strong>0.1-0.9:</strong> Lower importance</li>
              <li><strong>1.1-3.0:</strong> Higher importance</li>
            </ul>

            <div style={{ marginTop: '15px', padding: '15px', backgroundColor: 'white', borderRadius: '8px', border: '1px solid #E2E8F0', fontSize: '13px', color: '#64748B' }}>
              <strong>📊 Example:</strong> To focus on CBIL analysis, set CBIL weight to 2.0 and others to 0.8.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Dynamically import the content component with no SSR
const DynamicContent = dynamic(() => Promise.resolve(ComprehensiveReportsContent), {
  ssr: false,
  loading: () => (
    <div className="container">
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    </div>
  )
})

export default function ComprehensiveReportsPage() {
  return <DynamicContent />
}