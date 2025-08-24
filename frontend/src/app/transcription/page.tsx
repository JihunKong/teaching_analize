'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { LanguageMetrics, WordFrequency } from '../../components/transcription'
import YouTubeVerification from '../../components/YouTubeVerification'
import { isValidYouTubeUrl } from '../../utils/youtube'

// Constants
const POLLING_INTERVAL = 2000
const AUTO_REDIRECT_DELAY = 5000
const MAX_POLL_ATTEMPTS = 150 // 5분 최대 대기

// TranscriptionResults component with tabs
interface TranscriptionResultsProps {
  transcript: string
  characterCount: number
  wordCount: number
  onAnalyze: () => void
  onCopy: () => void
}

const TranscriptionResults: React.FC<TranscriptionResultsProps> = ({
  transcript,
  characterCount,
  wordCount,
  onAnalyze,
  onCopy
}) => {
  const [activeTab, setActiveTab] = useState<'transcript' | 'language' | 'words'>('transcript')

  const tabStyle = (isActive: boolean) => ({
    padding: '10px 20px',
    border: 'none',
    backgroundColor: isActive ? '#667eea' : '#f8f9fa',
    color: isActive ? 'white' : '#333',
    borderRadius: '8px 8px 0 0',
    cursor: 'pointer',
    fontWeight: isActive ? 'bold' : 'normal',
    fontSize: '14px',
    marginRight: '5px',
    transition: 'all 0.2s ease'
  })

  return (
    <div className="card">
      <h4>📊 전사 결과 및 분석</h4>
      
      {/* Tab Navigation */}
      <div style={{ 
        marginBottom: '20px', 
        borderBottom: '2px solid #e9ecef',
        display: 'flex'
      }}>
        <button
          onClick={() => setActiveTab('transcript')}
          style={tabStyle(activeTab === 'transcript')}
        >
          📝 전사 텍스트
        </button>
        <button
          onClick={() => setActiveTab('language')}
          style={tabStyle(activeTab === 'language')}
        >
          📊 언어 분석
        </button>
        <button
          onClick={() => setActiveTab('words')}
          style={tabStyle(activeTab === 'words')}
        >
          🔤 단어 분석
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'transcript' && (
        <div>
          <textarea
            className="form-textarea"
            value={transcript}
            readOnly
            style={{ 
              minHeight: '350px',
              fontFamily: 'system-ui, -apple-system, sans-serif',
              fontSize: '1rem',
              lineHeight: '1.6',
              width: '100%',
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '15px'
            }}
            aria-label="전사된 텍스트"
          />
          
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              className="btn"
              onClick={onAnalyze}
              style={{ marginRight: '10px' }}
            >
              🧠 분석하기
            </button>
            <button
              className="btn btn-secondary"
              onClick={onCopy}
            >
              📋 복사하기
            </button>
          </div>
        </div>
      )}

      {activeTab === 'language' && (
        <div>
          <LanguageMetrics
            transcript={transcript}
            characterCount={characterCount}
            wordCount={wordCount}
          />
        </div>
      )}

      {activeTab === 'words' && (
        <div>
          <WordFrequency
            transcript={transcript}
            maxWords={25}
          />
        </div>
      )}
    </div>
  )
}

interface TranscriptionJob {
  job_id: string
  status: 'pending' | 'processing' | 'progress' | 'completed' | 'success' | 'failed'
  message: string
  result?: {
    transcript: string
    character_count: number
    word_count: number
    video_id: string
    method_used: string
  }
}

interface ToastMessage {
  type: 'success' | 'error' | 'info'
  message: string
}

export default function TranscriptionPage() {
  const router = useRouter()
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [language, setLanguage] = useState('ko')
  const [job, setJob] = useState<TranscriptionJob | null>(null)
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [autoRedirectCountdown, setAutoRedirectCountdown] = useState<number | null>(null)
  const [userCancelledAutoRedirect, setUserCancelledAutoRedirect] = useState(false)
  const [isVerified, setIsVerified] = useState(false)
  const [verifiedVideoId, setVerifiedVideoId] = useState('')
  
  const pollAttemptsRef = useRef(0)
  const pollTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const redirectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Toast 메시지 표시 함수
  const showToast = useCallback((type: ToastMessage['type'], message: string) => {
    setToast({ type, message })
    setTimeout(() => setToast(null), 5000)
  }, [])

  // 안전한 sessionStorage 사용
  const saveToSessionStorage = useCallback((key: string, data: any) => {
    try {
      if (typeof window !== 'undefined' && window.sessionStorage) {
        sessionStorage.setItem(key, JSON.stringify(data))
        return true
      }
    } catch (error) {
      console.error('Failed to save to sessionStorage:', error)
      showToast('error', '데이터 저장에 실패했습니다.')
    }
    return false
  }, [showToast])

  // 클립보드 복사 (브라우저 호환성 고려)
  const copyToClipboard = useCallback(async (text: string) => {
    try {
      // Modern clipboard API 시도
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(text)
        showToast('success', '전사 텍스트가 클립보드에 복사되었습니다.')
        return
      }

      // Fallback: textarea를 이용한 복사
      const textArea = document.createElement('textarea')
      textArea.value = text
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      const successful = document.execCommand('copy')
      document.body.removeChild(textArea)
      
      if (successful) {
        showToast('success', '전사 텍스트가 클립보드에 복사되었습니다.')
      } else {
        throw new Error('Copy command failed')
      }
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
      showToast('error', '클립보드 복사에 실패했습니다. 텍스트를 직접 선택하여 복사해주세요.')
    }
  }, [showToast])

  // 자동 리다이렉트 관리
  const startAutoRedirect = useCallback(() => {
    if (userCancelledAutoRedirect) return

    setAutoRedirectCountdown(AUTO_REDIRECT_DELAY / 1000)
    
    const countdownInterval = setInterval(() => {
      setAutoRedirectCountdown(prev => {
        if (prev === null || prev <= 1) {
          clearInterval(countdownInterval)
          if (!userCancelledAutoRedirect) {
            router.push('/analysis')
          }
          return null
        }
        return prev - 1
      })
    }, 1000)

    redirectTimeoutRef.current = setTimeout(() => {
      if (!userCancelledAutoRedirect) {
        router.push('/analysis')
      }
    }, AUTO_REDIRECT_DELAY)
  }, [router, userCancelledAutoRedirect])

  // 자동 리다이렉트 취소
  const cancelAutoRedirect = useCallback(() => {
    setUserCancelledAutoRedirect(true)
    setAutoRedirectCountdown(null)
    if (redirectTimeoutRef.current) {
      clearTimeout(redirectTimeoutRef.current)
      redirectTimeoutRef.current = null
    }
    showToast('info', '자동 이동이 취소되었습니다.')
  }, [showToast])

  // Handle YouTube verification confirmation
  const handleVerificationConfirm = useCallback((videoId: string, url: string) => {
    setVerifiedVideoId(videoId)
    setYoutubeUrl(url)
    setIsVerified(true)
    showToast('success', '영상이 확인되었습니다. 전사를 시작할 수 있습니다.')
  }, [showToast])

  // Reset verification state
  const resetVerification = useCallback(() => {
    setIsVerified(false)
    setVerifiedVideoId('')
    setYoutubeUrl('')
    setJob(null)
  }, [])

  // 수동 분석 페이지 이동
  const goToAnalysis = useCallback(() => {
    if (job?.result) {
      const success = saveToSessionStorage('transcriptData', {
        transcript: job.result.transcript,
        video_id: job.result.video_id,
        character_count: job.result.character_count,
        word_count: job.result.word_count,
        method_used: job.result.method_used,
        auto_analyze: false
      })
      
      if (success) {
        router.push('/analysis')
      }
    }
  }, [job, router, saveToSessionStorage])

  // 전사 요청 제출
  const submitTranscription = async () => {
    if (!isVerified || !youtubeUrl.trim()) {
      showToast('error', '먼저 YouTube 영상을 확인해주세요.')
      return
    }

    if (!isValidYouTubeUrl(youtubeUrl.trim())) {
      showToast('error', '올바른 YouTube URL을 입력해주세요.')
      return
    }

    setLoading(true)
    setJob(null)
    setUserCancelledAutoRedirect(false)
    
    try {
      const response = await fetch('/api/transcribe/youtube', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          youtube_url: youtubeUrl.trim(),
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
        
        showToast('success', '전사 요청이 시작되었습니다.')
        pollAttemptsRef.current = 0
        pollJobStatus(data.job_id)
      } else {
        throw new Error(data.detail || 'Transcription failed')
      }
    } catch (error) {
      console.error('Error submitting transcription:', error)
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.'
      showToast('error', `전사 요청 중 오류가 발생했습니다: ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }

  // 작업 상태 폴링
  const pollJobStatus = useCallback(async (jobId: string) => {
    const checkStatus = async () => {
      try {
        pollAttemptsRef.current += 1

        if (pollAttemptsRef.current > MAX_POLL_ATTEMPTS) {
          showToast('error', '작업 확인 시간이 초과되었습니다. 페이지를 새로고침해주세요.')
          return
        }

        const response = await fetch(`/api/transcribe/${jobId}`)
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        setJob(data)
        
        if (data.status === 'completed' || data.status === 'success') {
          showToast('success', '전사가 완료되었습니다!')
          
          if (data.result?.transcript) {
            saveToSessionStorage('transcriptData', {
              transcript: data.result.transcript,
              video_id: data.result.video_id,
              character_count: data.result.character_count,
              word_count: data.result.word_count,
              method_used: data.result.method_used,
              auto_analyze: false
            })
          }
          return
        }
        
        if (data.status === 'failed') {
          showToast('error', `전사 실패: ${data.message}`)
          return
        }
        
        // 계속 폴링
        pollTimeoutRef.current = setTimeout(checkStatus, POLLING_INTERVAL)
      } catch (error) {
        console.error('Error checking job status:', error)
        pollAttemptsRef.current += 1
        
        if (pollAttemptsRef.current <= MAX_POLL_ATTEMPTS) {
          pollTimeoutRef.current = setTimeout(checkStatus, POLLING_INTERVAL)
        } else {
          showToast('error', '작업 상태 확인에 실패했습니다.')
        }
      }
    }
    
    pollTimeoutRef.current = setTimeout(checkStatus, POLLING_INTERVAL)
  }, [saveToSessionStorage, showToast, startAutoRedirect])

  // 컴포넌트 언마운트 시 타이머 정리
  useEffect(() => {
    return () => {
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current)
      }
      if (redirectTimeoutRef.current) {
        clearTimeout(redirectTimeoutRef.current)
      }
    }
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'success': return '#28a745'
      case 'failed': return '#dc3545'
      case 'processing':
      case 'progress': return '#ffc107'
      default: return '#6c757d'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return '대기 중'
      case 'processing': 
      case 'progress': return '처리 중'
      case 'completed':
      case 'success': return '완료'
      case 'failed': return '실패'
      default: return status
    }
  }

  return (
    <div className="container">
      {/* Toast Messages */}
      {toast && (
        <div 
          className={`toast toast-${toast.type}`}
          role="alert"
          aria-live="assertive"
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 1000,
            padding: '15px 20px',
            borderRadius: '5px',
            color: 'white',
            fontWeight: 'bold',
            backgroundColor: toast.type === 'success' ? '#28a745' : 
                           toast.type === 'error' ? '#dc3545' : '#17a2b8'
          }}
        >
          {toast.message}
        </div>
      )}

      <div className="page-title">YouTube 전사</div>
      <div className="page-subtitle">YouTube 영상을 텍스트로 변환합니다</div>
      
      {/* YouTube Verification Section */}
      {!isVerified && !job && (
        <YouTubeVerification 
          onConfirm={handleVerificationConfirm}
          className="verification-container"
        />
      )}
      
      {/* Verified Video and Transcription Controls */}
      {isVerified && !job && (
        <div className="verified-section">
          <div className="status status-success" style={{ marginBottom: '20px' }}>
            <strong>✅ 영상 확인 완료!</strong>
            <p style={{ marginTop: '5px', fontWeight: 'normal' }}>
              Video ID: <strong>{verifiedVideoId}</strong>
            </p>
          </div>
          
          <div className="grid">
            <div className="form-group">
              <label className="form-label" htmlFor="language-select">
                전사 언어 선택
              </label>
              <select
                id="language-select"
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
            
            <div style={{ textAlign: 'center', marginTop: '20px', display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <button
                className="btn btn-large"
                onClick={submitTranscription}
                disabled={loading}
                aria-describedby={loading ? 'loading-status' : undefined}
                style={{ minWidth: '150px' }}
              >
                {loading ? '처리 중...' : '🎯 전사 시작'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={resetVerification}
                disabled={loading}
                style={{ minWidth: '120px' }}
              >
                다시 선택
              </button>
              {loading && (
                <div id="loading-status" className="sr-only" aria-live="polite">
                  전사 요청을 처리 중입니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      
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
          
          {(job.status === 'processing' || job.status === 'progress') && (
            <div className="loading" role="status" aria-live="polite">
              <div className="spinner"></div>
              <p>YouTube에서 전사를 추출하고 있습니다...</p>
            </div>
          )}
          
          {(job.status === 'completed' || job.status === 'success') && job.result && (
            <div style={{ marginTop: '20px' }}>
              <div className="status status-success" style={{ marginBottom: '20px' }}>
                <strong>✅ 전사 완료!</strong>
                {autoRedirectCountdown !== null && (
                  <div style={{ marginTop: '10px' }}>
                    <p>
                      {autoRedirectCountdown}초 후 분석 페이지로 자동 이동합니다.
                    </p>
                    <button
                      className="btn btn-secondary btn-small"
                      onClick={cancelAutoRedirect}
                      style={{ marginTop: '5px' }}
                    >
                      자동 이동 취소
                    </button>
                  </div>
                )}
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
              
              <TranscriptionResults 
                transcript={job.result.transcript}
                characterCount={job.result.character_count}
                wordCount={job.result.word_count}
                onAnalyze={goToAnalysis}
                onCopy={() => copyToClipboard(job.result!.transcript)}
              />
            </div>
          )}
          
          {job.status === 'failed' && (
            <div className="status status-error" role="alert">
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
            <h4>🎯 전사 과정</h4>
            <ol style={{ marginLeft: '20px', color: '#666' }}>
              <li><strong>URL 입력:</strong> YouTube URL을 입력</li>
              <li><strong>영상 확인:</strong> 미리보기로 영상 검증</li>
              <li><strong>확인 완료:</strong> 올바른 영상인지 확인</li>
              <li><strong>전사 시작:</strong> 언어 선택 후 전사 진행</li>
            </ol>
          </div>
          
          <div>
            <h4>✅ 지원 사항</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li>YouTube 영상 (자막 유무 무관)</li>
              <li>공개 또는 제한공개 영상</li>
              <li>한국어, 영어, 일본어, 중국어</li>
              <li>모든 표준 YouTube URL 형식</li>
            </ul>
          </div>
        </div>
        
        <div className="grid grid-2" style={{ marginTop: '20px' }}>
          <div>
            <h4>⚠️ 주의사항</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li>개인정보가 포함된 영상 주의</li>
              <li>긴 영상은 처리 시간이 오래 걸림</li>
              <li>네트워크 상황에 따라 처리 시간 변동 가능</li>
            </ul>
          </div>
          
          <div>
            <h4>💡 팁</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li>URL 입력 후 Enter키로 빠른 미리보기</li>
              <li>미리보기에서 영상 내용 미리 확인</li>
              <li>잘못된 영상이면 "다시 입력" 버튼 활용</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}