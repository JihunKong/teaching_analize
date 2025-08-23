'use client'

import { useState } from 'react'

interface TranscriptionJob {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  message: string
  result?: {
    transcript: string
    character_count: number
    word_count: number
    video_id: string
    method_used: string
  }
}

export default function TranscriptionPage() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [language, setLanguage] = useState('ko')
  const [job, setJob] = useState<TranscriptionJob | null>(null)
  const [loading, setLoading] = useState(false)

  const submitTranscription = async () => {
    if (!youtubeUrl.trim()) {
      alert('YouTube URL을 입력해주세요.')
      return
    }

    setLoading(true)
    
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.API_BASE_URL || ''
      
      const response = await fetch(`${API_BASE}/api/transcribe/youtube`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          youtube_url: youtubeUrl,
          language,
          export_format: 'json'
        }),
      })

      const data = await response.json()
      
      if (response.ok) {
        setJob({
          job_id: data.job_id,
          status: data.status,
          message: data.message
        })
        
        // Start polling for status
        pollJobStatus(data.job_id)
      } else {
        throw new Error(data.detail || 'Transcription failed')
      }
    } catch (error) {
      console.error('Error submitting transcription:', error)
      alert('전사 요청 중 오류가 발생했습니다: ' + (error as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const pollJobStatus = async (jobId: string) => {
    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.API_BASE_URL || ''
    
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/transcribe/${jobId}`)
        const data = await response.json()
        
        setJob(data)
        
        if (data.status === 'completed') {
          // Auto-navigate to analysis tab after successful transcription
          if (data.result && data.result.transcript) {
            // Store transcript in sessionStorage for analysis page
            sessionStorage.setItem('transcriptData', JSON.stringify({
              transcript: data.result.transcript,
              video_id: data.result.video_id,
              character_count: data.result.character_count,
              word_count: data.result.word_count,
              method_used: data.result.method_used,
              auto_analyze: true
            }))
            
            // Navigate to analysis page
            setTimeout(() => {
              window.location.href = '/analysis'
            }, 2000) // Show success for 2 seconds then navigate
          }
          return // Stop polling
        }
        
        if (data.status === 'failed') {
          return // Stop polling
        }
        
        // Continue polling every 2 seconds
        setTimeout(checkStatus, 2000)
      } catch (error) {
        console.error('Error checking job status:', error)
      }
    }
    
    // Start the polling
    setTimeout(checkStatus, 2000)
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
      case 'processing': return '처리 중'
      case 'completed': return '완료'
      case 'failed': return '실패'
      default: return status
    }
  }

  return (
    <div className="container">
      <div className="page-title">YouTube 전사</div>
      <div className="page-subtitle">YouTube 영상을 텍스트로 변환합니다</div>
      
      <div className="grid">
        <div className="form-group">
          <label className="form-label">YouTube URL</label>
          <input
            type="url"
            className="form-input"
            placeholder="https://www.youtube.com/watch?v=..."
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            disabled={loading}
          />
          <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
            예: https://www.youtube.com/watch?v=-OLCt6WScEY&list=PLugIxwJYmOhl_8KO3GHx9gp6VKMmbsTfw
          </small>
        </div>
        
        <div className="form-group">
          <label className="form-label">언어</label>
          <select
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            disabled={loading}
          >
            <option value="ko">한국어</option>
            <option value="en">영어</option>
            <option value="ja">일본어</option>
            <option value="zh">중국어</option>
          </select>
        </div>
        
        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button
            className="btn btn-large"
            onClick={submitTranscription}
            disabled={loading || !youtubeUrl.trim()}
          >
            {loading ? '처리 중...' : '전사 시작'}
          </button>
        </div>
      </div>
      
      {job && (
        <div className="container" style={{ marginTop: '30px' }}>
          <h3>전사 진행 상황</h3>
          
          <div style={{ 
            padding: '20px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '10px',
            marginBottom: '20px'
          }}>
            <p><strong>작업 ID:</strong> {job.job_id}</p>
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
            <p><strong>메시지:</strong> {job.message}</p>
          </div>
          
          {job.status === 'processing' && (
            <div className="loading">
              <div className="spinner"></div>
              <p>YouTube에서 전사를 추출하고 있습니다...</p>
            </div>
          )}
          
          {job.status === 'completed' && job.result && (
            <div style={{ marginTop: '20px' }}>
              <div className="status status-success" style={{ marginBottom: '20px' }}>
                <strong>✅ 전사 완료!</strong> 잠시 후 분석 탭으로 자동 이동합니다...
                <div className="loading" style={{ marginTop: '10px' }}>
                  <div className="spinner"></div>
                  <small>분석 페이지로 이동 중...</small>
                </div>
              </div>
              
              <div className="grid grid-2" style={{ marginBottom: '20px' }}>
                <div className="card">
                  <h4>📊 통계</h4>
                  <p><strong>문자 수:</strong> {job.result.character_count.toLocaleString()}</p>
                  <p><strong>단어 수:</strong> {job.result.word_count.toLocaleString()}</p>
                  <p><strong>추출 방법:</strong> {job.result.method_used}</p>
                </div>
                
                <div className="card">
                  <h4>🎬 영상 정보</h4>
                  <p><strong>비디오 ID:</strong> {job.result.video_id}</p>
                  <p><strong>언어:</strong> {language.toUpperCase()}</p>
                </div>
              </div>
              
              <div className="card">
                <h4>📝 전사 결과</h4>
                <textarea
                  className="form-textarea"
                  value={job.result.transcript}
                  readOnly
                  style={{ 
                    minHeight: '300px',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem'
                  }}
                />
                
                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                  <a 
                    href="/analysis"
                    className="btn"
                    style={{ marginRight: '10px' }}
                  >
                    🧠 분석하기
                  </a>
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      navigator.clipboard.writeText(job.result!.transcript)
                      alert('전사 텍스트가 클립보드에 복사되었습니다.')
                    }}
                  >
                    📋 복사하기
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {job.status === 'failed' && (
            <div className="status status-error">
              <strong>전사 실패:</strong> {job.message}
              <br />
              <small>다른 YouTube URL로 다시 시도해보세요.</small>
            </div>
          )}
        </div>
      )}
      
      <div className="container" style={{ marginTop: '30px' }}>
        <h3>📋 사용 안내</h3>
        <div className="grid grid-2">
          <div>
            <h4>✅ 지원되는 영상</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li>자막이 있는 YouTube 영상</li>
              <li>공개 또는 제한공개 영상</li>
              <li>한국어, 영어, 일본어, 중국어</li>
            </ul>
          </div>
          
          <div>
            <h4>⚠️ 주의사항</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li>개인정보가 포함된 영상 주의</li>
              <li>긴 영상은 처리 시간이 오래 걸림</li>
              <li>자막이 없으면 전사 불가</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}