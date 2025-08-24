'use client'

import { useState, useEffect } from 'react'

interface Framework {
  id: string
  name: string
  description: string
}

interface AnalysisJob {
  analysis_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  message: string
  framework: string
  result?: {
    analysis_id: string
    framework: string
    framework_name: string
    analysis: string
    character_count: number
    word_count: number
    created_at: string
  }
}

interface ParallelAnalysisResults {
  [framework: string]: AnalysisJob
}

export default function AnalysisPage() {
  const [text, setText] = useState('')
  const [framework, setFramework] = useState('cbil')
  const [frameworks, setFrameworks] = useState<Framework[]>([])
  const [job, setJob] = useState<AnalysisJob | null>(null)
  const [loading, setLoading] = useState(false)
  const [parallelAnalysis, setParallelAnalysis] = useState(false)
  const [parallelResults, setParallelResults] = useState<ParallelAnalysisResults>({})
  const [expandedResults, setExpandedResults] = useState<{[key: string]: boolean}>({})
  const [transcriptData, setTranscriptData] = useState<any>(null)

  useEffect(() => {
    loadFrameworks()
    
    // Check for auto-analysis from transcription page
    const storedTranscript = sessionStorage.getItem('transcriptData')
    if (storedTranscript) {
      const data = JSON.parse(storedTranscript)
      setTranscriptData(data)
      setText(data.transcript)
      
      if (data.auto_analyze) {
        // Auto-start parallel analysis after transcription
        setTimeout(() => {
          startParallelAnalysis(data.transcript)
        }, 1000)
        
        // Clear the stored data
        sessionStorage.removeItem('transcriptData')
      }
    }
  }, [])

  const loadFrameworks = async () => {
    try {
      const response = await fetch('/api/frameworks')
      const data = await response.json()
      
      if (response.ok && data.frameworks) {
        setFrameworks(data.frameworks)
      }
    } catch (error) {
      console.error('Error loading frameworks:', error)
    }
  }

  const submitAnalysis = async () => {
    if (!text.trim()) {
      alert('분석할 텍스트를 입력해주세요.')
      return
    }

    if (parallelAnalysis) {
      startParallelAnalysis(text)
    } else {
      setLoading(true)
      
      try {
        const response = await fetch('/api/analyze/text', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text,
            framework,
            metadata: { temperature: 0.3 }  // Set temperature for consistent analysis
          }),
        })

        const data = await response.json()
        
        if (response.ok) {
          setJob({
            analysis_id: data.analysis_id,
            status: data.status,
            message: data.message,
            framework: data.framework
          })
          
          // Start polling for status
          pollJobStatus(data.analysis_id)
        } else {
          throw new Error(data.detail || 'Analysis failed')
        }
      } catch (error) {
        console.error('Error submitting analysis:', error)
        alert('분석 요청 중 오류가 발생했습니다: ' + (error as Error).message)
      } finally {
        setLoading(false)
      }
    }
  }

  const startParallelAnalysis = async (analysisText: string) => {
    if (!analysisText.trim()) {
      alert('분석할 텍스트를 입력해주세요.')
      return
    }

    setLoading(true)
    setParallelResults({})
    
    // Start all analyses in parallel with temperature 0.3 for consistency
    const analysisPromises = frameworks.map(async (fw) => {
      try {
        const response = await fetch('/api/analyze/text', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text: analysisText,
            framework: fw.id,
            metadata: { temperature: 0.3, parallel: true }  // Temperature 0.3 for consistent results
          }),
        })

        const data = await response.json()
        
        if (response.ok) {
          const job = {
            analysis_id: data.analysis_id,
            status: data.status,
            message: data.message,
            framework: data.framework
          }
          
          // Start polling for this specific job
          pollParallelJobStatus(data.analysis_id, fw.id)
          
          return { framework: fw.id, job }
        } else {
          throw new Error(data.detail || 'Analysis failed')
        }
      } catch (error) {
        console.error(`Error submitting ${fw.name} analysis:`, error)
        return {
          framework: fw.id,
          job: {
            analysis_id: `error-${fw.id}`,
            status: 'failed' as const,
            message: `Failed to start: ${(error as Error).message}`,
            framework: fw.id
          }
        }
      }
    })
    
    // Initialize parallel results
    const results = await Promise.all(analysisPromises)
    const newResults: ParallelAnalysisResults = {}
    
    results.forEach(({ framework, job }) => {
      newResults[framework] = job
    })
    
    setParallelResults(newResults)
    setLoading(false)
  }

  const pollJobStatus = async (jobId: string) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`/api/analyze/${jobId}`)
        const data = await response.json()
        
        setJob(data)
        
        if (data.status === 'completed' || data.status === 'failed') {
          return // Stop polling
        }
        
        // Continue polling every 3 seconds
        setTimeout(checkStatus, 3000)
      } catch (error) {
        console.error('Error checking job status:', error)
      }
    }
    
    // Start the polling
    setTimeout(checkStatus, 3000)
  }

  const pollParallelJobStatus = async (jobId: string, framework: string) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`/api/analyze/${jobId}`)
        const data = await response.json()
        
        // Update specific framework result
        setParallelResults(prev => ({
          ...prev,
          [framework]: data
        }))
        
        if (data.status === 'completed' || data.status === 'failed') {
          return // Stop polling
        }
        
        // Continue polling every 3 seconds
        setTimeout(checkStatus, 3000)
      } catch (error) {
        console.error(`Error checking job status for ${framework}:`, error)
      }
    }
    
    // Start the polling
    setTimeout(checkStatus, 3000)
  }

  const toggleResult = (framework: string) => {
    setExpandedResults(prev => ({
      ...prev,
      [framework]: !prev[framework]
    }))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#28a745'
      case 'failed': return '#dc3545'
      case 'processing': return '#ffc107'
      default: return '#6c757d'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기 중'
      case 'processing': return '분석 중'
      case 'completed': return '완료'
      case 'failed': return '실패'
      default: return status
    }
  }

  const generateReport = async () => {
    if (!job?.result) return
    
    try {
      const response = await fetch('/api/reports/generate/html', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_result: job.result,
          template: 'comprehensive',
          title: `${job.result.framework_name} 분석 보고서`
        }),
      })

      if (response.ok) {
        const htmlContent = await response.text()
        
        // Open HTML report in new window
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(htmlContent)
          newWindow.document.close()
        }
      } else {
        throw new Error('Report generation failed')
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('보고서 생성 중 오류가 발생했습니다.')
    }
  }

  return (
    <div className="container">
      <div className="page-title">교육 분석</div>
      <div className="page-subtitle">다양한 프레임워크로 교사 발화를 분석합니다</div>
      
      {transcriptData && (
        <div className="status status-info" style={{ marginBottom: '20px' }}>
          <strong>🎬 전사 완료!</strong> 영상 ID: {transcriptData.video_id} | 
          문자수: {transcriptData.character_count?.toLocaleString()} | 
          추출 방법: {transcriptData.method_used}
        </div>
      )}
      
      <div className="grid">
        <div className="form-group">
          <label className="form-label">
            <input
              type="checkbox"
              checked={parallelAnalysis}
              onChange={(e) => setParallelAnalysis(e.target.checked)}
              style={{ marginRight: '8px' }}
            />
            병렬 분석 모드 (모든 프레임워크 동시 실행, Temperature 0.3)
          </label>
          {parallelAnalysis ? (
            <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
              모든 분석 프레임워크를 동시에 실행하여 일관성 있는 결과를 제공합니다.
            </small>
          ) : (
            <>
              <label className="form-label" style={{ marginTop: '15px' }}>분석 프레임워크</label>
              <select
                className="form-select"
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                disabled={loading}
              >
                {frameworks.map((fw) => (
                  <option key={fw.id} value={fw.id}>
                    {fw.name}
                  </option>
                ))}
              </select>
              {frameworks.find(fw => fw.id === framework) && (
                <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
                  {frameworks.find(fw => fw.id === framework)?.description}
                </small>
              )}
            </>
          )}
        </div>
        
        <div className="form-group">
          <label className="form-label">분석할 텍스트</label>
          <textarea
            className="form-textarea"
            placeholder="수업 전사 텍스트를 입력하거나 붙여넣으세요..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={loading}
            style={{ minHeight: '200px' }}
          />
          <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
            {text.length.toLocaleString()} 문자, 약 {text.split(' ').length.toLocaleString()} 단어
          </small>
        </div>
        
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button
            className="btn btn-large"
            onClick={submitAnalysis}
            disabled={loading || !text.trim()}
          >
            {loading ? (parallelAnalysis ? '병렬 분석 중...' : '분석 중...') : (parallelAnalysis ? '모든 프레임워크 분석 시작' : '분석 시작')}
          </button>
        </div>
      </div>
      
      {job && (
        <div className="container" style={{ marginTop: '30px' }}>
          <h3>분석 진행 상황</h3>
          
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '10px',
            marginBottom: '20px'
          }}>
            <p><strong>분석 ID:</strong> {job.analysis_id}</p>
            <p>
              <strong>상태:</strong> 
              <span style={{ 
                color: getStatusColor(job.status), 
                fontWeight: 'bold',
                marginLeft: '10px'
              }}>
                {getStatusText(job.status)}
              </span>
            </p>
            <p><strong>프레임워크:</strong> {job.framework}</p>
            <p><strong>메시지:</strong> {job.message}</p>
          </div>
          
          {job.status === 'processing' && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Solar2 Pro AI가 텍스트를 분석하고 있습니다...</p>
            </div>
          )}
          
          {job.status === 'completed' && job.result && (
            <div style={{ marginTop: '20px' }}>
              <div className="grid grid-2" style={{ marginBottom: '20px' }}>
                <div className="card">
                  <h4>📊 분석 정보</h4>
                  <p><strong>프레임워크:</strong> {job.result.framework_name}</p>
                  <p><strong>생성일:</strong> {new Date(job.result.created_at).toLocaleDateString('ko-KR')}</p>
                  <p><strong>분석 문자 수:</strong> {job.result.character_count.toLocaleString()}</p>
                </div>
                
                <div className="card">
                  <h4>⚙️ 분석 설정</h4>
                  <p><strong>모델:</strong> Solar2 Pro</p>
                  <p><strong>온도:</strong> 0.1 (일관성 중시)</p>
                  <p><strong>언어:</strong> 한국어</p>
                </div>
              </div>
              
              <div className="card">
                <h4>📝 분석 결과</h4>
                <div style={{ 
                  backgroundColor: '#f8f9fa',
                  border: '1px solid #dee2e6',
                  borderRadius: '5px',
                  padding: '20px',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'Georgia, serif',
                  fontSize: '1rem',
                  lineHeight: '1.8',
                  marginBottom: '20px'
                }}>
                  {job.result.analysis}
                </div>
                
                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                  <button
                    className="btn"
                    onClick={generateReport}
                    style={{ marginRight: '10px' }}
                  >
                    📄 HTML 보고서 생성
                  </button>
                  <a 
                    href="/reports"
                    className="btn btn-secondary"
                  >
                    📊 보고서 목록
                  </a>
                </div>
              </div>
            </div>
          )}
          
          {job.status === 'failed' && (
            <div className="status status-error">
              <strong>분석 실패:</strong> {job.message}
              <br />
              <small>텍스트 내용을 확인하고 다시 시도해보세요.</small>
            </div>
          )}
        </div>
      )}

      {/* Parallel Analysis Results */}
      {Object.keys(parallelResults).length > 0 && (
        <div className="container" style={{ marginTop: '30px' }}>
          <h3>🧠 병렬 분석 결과 ({Object.keys(parallelResults).length}개 프레임워크)</h3>
          <div style={{ marginBottom: '20px' }}>
            <small style={{ color: '#666' }}>
              Temperature 0.3으로 일관성 있는 분석을 제공합니다. 각 결과를 클릭하여 자세히 확인하세요.
            </small>
          </div>
          
          {frameworks.map((fw) => {
            const result = parallelResults[fw.id]
            if (!result) return null
            
            const isExpanded = expandedResults[fw.id]
            const statusColor = getStatusColor(result.status)
            
            return (
              <div key={fw.id} className="card" style={{ marginBottom: '15px' }}>
                <div 
                  style={{ 
                    cursor: 'pointer',
                    padding: '15px',
                    borderBottom: isExpanded ? '1px solid #dee2e6' : 'none'
                  }}
                  onClick={() => toggleResult(fw.id)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h4 style={{ margin: '0 0 5px 0' }}>
                        {fw.name}
                        <span style={{ 
                          color: statusColor, 
                          fontWeight: 'bold', 
                          marginLeft: '10px',
                          fontSize: '0.9rem'
                        }}>
                          {getStatusText(result.status)}
                        </span>
                      </h4>
                      <small style={{ color: '#666' }}>{fw.description}</small>
                    </div>
                    <div style={{ fontSize: '1.2rem' }}>
                      {isExpanded ? '▼' : '▶'}
                    </div>
                  </div>
                </div>
                
                {isExpanded && (
                  <div style={{ padding: '15px' }}>
                    {result.status === 'processing' && (
                      <div className="loading">
                        <div className="spinner"></div>
                        <p>분석 중...</p>
                      </div>
                    )}
                    
                    {result.status === 'completed' && result.result && (
                      <div>
                        <div className="grid grid-2" style={{ marginBottom: '15px' }}>
                          <div>
                            <p><strong>📊 문자 수:</strong> {result.result.character_count?.toLocaleString()}</p>
                            <p><strong>📅 생성일:</strong> {new Date(result.result.created_at).toLocaleDateString('ko-KR')}</p>
                          </div>
                          <div>
                            <p><strong>🔧 모델:</strong> Solar2 Pro</p>
                            <p><strong>🌡️ 온도:</strong> 0.3 (일관성 중시)</p>
                          </div>
                        </div>
                        
                        <div style={{ 
                          backgroundColor: '#f8f9fa',
                          border: '1px solid #dee2e6',
                          borderRadius: '5px',
                          padding: '15px',
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'Georgia, serif',
                          fontSize: '0.95rem',
                          lineHeight: '1.7',
                          maxHeight: '300px',
                          overflowY: 'auto'
                        }}>
                          {result.result.analysis}
                        </div>
                      </div>
                    )}
                    
                    {result.status === 'failed' && (
                      <div className="status status-error">
                        <strong>분석 실패:</strong> {result.message}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
          
          <div style={{ textAlign: 'center', marginTop: '30px' }}>
            <button
              className="btn"
              onClick={() => {
                // Generate comprehensive report for all completed analyses
                const completedResults = frameworks
                  .map(fw => parallelResults[fw.id])
                  .filter(result => result && result.status === 'completed' && result.result)
                
                if (completedResults.length > 0) {
                  alert(`${completedResults.length}개 프레임워크 분석 완료! 종합 보고서 생성 기능 개발 중입니다.`)
                } else {
                  alert('완료된 분석이 없습니다.')
                }
              }}
              style={{ marginRight: '10px' }}
            >
              📄 종합 보고서 생성
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => {
                const completedCount = Object.values(parallelResults)
                  .filter(result => result.status === 'completed').length
                const failedCount = Object.values(parallelResults)
                  .filter(result => result.status === 'failed').length
                const processingCount = Object.values(parallelResults)
                  .filter(result => result.status === 'processing').length
                
                alert(`분석 현황:\n✅ 완료: ${completedCount}개\n❌ 실패: ${failedCount}개\n⏳ 진행 중: ${processingCount}개`)
              }}
            >
              📊 분석 현황
            </button>
          </div>
        </div>
      )}
      
      <div className="container" style={{ marginTop: '30px' }}>
        <h3>📋 분석 프레임워크 안내</h3>
        <div className="grid grid-3">
          <div className="card">
            <h4>🎯 CBIL (7단계)</h4>
            <p>개념기반 탐구학습의 7단계 실행 여부를 평가하고 점수를 부여합니다.</p>
            <ul style={{ marginLeft: '20px', color: '#666', fontSize: '0.9rem' }}>
              <li>Engage (흥미 유도)</li>
              <li>Focus (탐구 방향 설정)</li>
              <li>Investigate (자료 탐색)</li>
              <li>Organize (개념 구조화)</li>
              <li>Generalize (일반화)</li>
              <li>Transfer (전이)</li>
              <li>Reflect (성찰)</li>
            </ul>
          </div>
          
          <div className="card">
            <h4>💬 학생주도 토론</h4>
            <p>학생 주도 질문과 대화, 토론 수업의 질문 유형과 대화 패턴을 분석합니다.</p>
            <ul style={{ marginLeft: '20px', color: '#666', fontSize: '0.9rem' }}>
              <li>질문 유형 (사실적, 해석적, 평가적)</li>
              <li>후속 질문 (명료화, 초점화, 정교화)</li>
              <li>수업 대화 유형</li>
            </ul>
          </div>
          
          <div className="card">
            <h4>📚 수업 코칭</h4>
            <p>수업 설계와 실행을 15개 항목으로 분석하고 구체적인 코칭을 제공합니다.</p>
            <ul style={{ marginLeft: '20px', color: '#666', fontSize: '0.9rem' }}>
              <li>학습 목표의 명확성</li>
              <li>도입의 효과</li>
              <li>학습 내용의 적절성</li>
              <li>피드백의 효과성</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}