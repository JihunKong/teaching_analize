'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import PipelineProgress from '@/components/PipelineProgress'

export default function PipelinePage() {
  const router = useRouter()
  const [videoUrl, setVideoUrl] = useState('')
  const [framework, setFramework] = useState('cbil_comprehensive')
  const [workflowId, setWorkflowId] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const apiUrl = typeof window !== 'undefined' ? window.location.origin : 'http://localhost'
      const response = await fetch(`${apiUrl}/api/workflow/full-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: videoUrl,
          framework,
          language: 'ko',
          use_diarization: true,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to start workflow')
      }

      const data = await response.json()
      setWorkflowId(data.workflow_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      setIsSubmitting(false)
    }
  }

  const handleComplete = (data: any) => {
    console.log('handleComplete called with data:', data)
    // Navigate to report page
    // Support both analysis_id (new) and analysis_job_id (old) for compatibility
    const analysisId = data?.analysis_id || data?.analysis_job_id
    if (analysisId) {
      console.log('Redirecting to comprehensive-reports with analysis_id:', analysisId)
      router.push(`/comprehensive-reports?analysis_id=${analysisId}`)
    } else {
      console.error('No analysis_id found in completion data:', data)
      setError('보고서 ID를 찾을 수 없습니다. 관리자에게 문의하세요.')
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--color-white)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Brutalist Geometric Background Elements */}
      <div className="geo-square" style={{
        top: '10%',
        right: '5%',
        width: '200px',
        height: '200px',
        opacity: 0.03
      }}></div>
      <div className="geo-circle" style={{
        bottom: '15%',
        left: '8%',
        width: '150px',
        height: '150px',
        opacity: 0.05
      }}></div>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: 'var(--space-6) var(--space-4)',
        position: 'relative',
        zIndex: 1
      }}>
        {/* Brutalist Header */}
        <div style={{ marginBottom: 'var(--space-6)' }}>
          <h1 className="brutalist-title" style={{
            marginBottom: 'var(--space-3)',
            borderBottom: 'var(--border-massive) solid var(--color-black)',
            paddingBottom: 'var(--space-3)'
          }}>
            통합 분석 파이프라인
          </h1>
          <p style={{
            fontSize: 'var(--text-xl)',
            color: 'var(--color-gray-700)',
            fontWeight: 'var(--font-medium)',
            letterSpacing: 'var(--tracking-normal)'
          }}>
            YouTube 영상 → 전사 → 분석 → 보고서 생성
          </p>
        </div>

        {/* Brutalist Form */}
        {!workflowId ? (
          <div style={{
            background: 'var(--color-white)',
            border: 'var(--border-thick) solid var(--color-black)',
            borderRadius: '0',
            padding: 'var(--space-6)',
            marginBottom: 'var(--space-6)',
            boxShadow: '12px 12px 0 var(--color-black)'
          }}>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 'var(--space-4)' }}>
                <label
                  htmlFor="videoUrl"
                  style={{
                    display: 'block',
                    fontSize: 'var(--text-lg)',
                    fontWeight: 'var(--font-black)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--tracking-wide)',
                    marginBottom: 'var(--space-2)',
                    color: 'var(--color-black)'
                  }}
                >
                  YouTube URL
                </label>
                <input
                  id="videoUrl"
                  type="url"
                  required
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  style={{
                    width: '100%',
                    padding: 'var(--space-3)',
                    border: 'var(--border-medium) solid var(--color-black)',
                    borderRadius: '0',
                    fontSize: 'var(--text-base)',
                    fontFamily: 'var(--font-mono)',
                    background: 'var(--color-white)',
                    transition: 'all 0.2s ease'
                  }}
                  onFocus={(e) => {
                    e.target.style.outline = 'none'
                    e.target.style.boxShadow = '6px 6px 0 var(--color-black)'
                  }}
                  onBlur={(e) => {
                    e.target.style.boxShadow = 'none'
                  }}
                />
              </div>

              <div style={{ marginBottom: 'var(--space-4)' }}>
                <label
                  htmlFor="framework"
                  style={{
                    display: 'block',
                    fontSize: 'var(--text-lg)',
                    fontWeight: 'var(--font-black)',
                    textTransform: 'uppercase',
                    letterSpacing: 'var(--tracking-wide)',
                    marginBottom: 'var(--space-2)',
                    color: 'var(--color-black)'
                  }}
                >
                  분석 프레임워크
                </label>
                <select
                  id="framework"
                  value={framework}
                  onChange={(e) => setFramework(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 'var(--space-3)',
                    border: 'var(--border-medium) solid var(--color-black)',
                    borderRadius: '0',
                    fontSize: 'var(--text-base)',
                    fontWeight: 'var(--font-semibold)',
                    background: 'var(--color-white)',
                    cursor: 'pointer'
                  }}
                >
                  <option value="cbil_comprehensive">CBIL 종합 분석</option>
                  <option value="diagnostic">진단 보고서 분석</option>
                  <option value="bloom">Bloom's Taxonomy</option>
                  <option value="webb">Webb's DOK</option>
                </select>
              </div>

              {error && (
                <div style={{
                  padding: 'var(--space-3)',
                  marginBottom: 'var(--space-4)',
                  background: 'var(--color-black)',
                  color: 'var(--color-white)',
                  border: 'var(--border-medium) solid var(--color-black)',
                  fontWeight: 'var(--font-bold)',
                  letterSpacing: 'var(--tracking-normal)'
                }}>
                  ⚠ {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                style={{
                  width: '100%',
                  padding: 'var(--space-4)',
                  background: 'var(--color-black)',
                  color: 'var(--color-white)',
                  border: 'var(--border-thick) solid var(--color-black)',
                  borderRadius: '0',
                  fontSize: 'var(--text-xl)',
                  fontWeight: 'var(--font-black)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--tracking-wide)',
                  cursor: isSubmitting ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s ease',
                  opacity: isSubmitting ? 0.6 : 1
                }}
                onMouseEnter={(e) => {
                  if (!isSubmitting) {
                    e.currentTarget.style.transform = 'translate(4px, 4px)'
                    e.currentTarget.style.boxShadow = 'none'
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translate(0, 0)'
                  e.currentTarget.style.boxShadow = '8px 8px 0 var(--color-gray-400)'
                }}
              >
                {isSubmitting ? '⏳ 시작하는 중...' : '▶ 분석 시작하기'}
              </button>
            </form>
          </div>
        ) : (
          /* Progress Display */
          <PipelineProgress workflowId={workflowId} onComplete={handleComplete} />
        )}

        {/* Brutalist Feature Grid */}
        <div className="bento-grid" style={{ marginTop: 'var(--space-6)' }}>
          <div className="bento-card bento-card--large" style={{
            background: 'var(--color-white)',
            border: 'var(--border-thick) solid var(--color-black)',
            borderRadius: '0',
            padding: 'var(--space-5)',
            transition: 'all 0.3s ease'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              background: 'var(--color-black)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 'var(--space-3)',
              fontSize: 'var(--text-3xl)'
            }}>
              01
            </div>
            <h3 style={{
              fontSize: 'var(--text-2xl)',
              fontWeight: 'var(--font-black)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--tracking-normal)',
              marginBottom: 'var(--space-2)',
              color: 'var(--color-black)'
            }}>
              자동 전사
            </h3>
            <p style={{
              fontSize: 'var(--text-base)',
              color: 'var(--color-gray-700)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              Selenium을 통한 YouTube 자막 자동 추출 (스크립트 보기 기능 활용)
            </p>
          </div>

          <div className="bento-card" style={{
            background: 'var(--color-black)',
            color: 'var(--color-white)',
            border: 'var(--border-thick) solid var(--color-black)',
            borderRadius: '0',
            padding: 'var(--space-5)',
            transition: 'all 0.3s ease'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              background: 'var(--color-white)',
              color: 'var(--color-black)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 'var(--space-3)',
              fontSize: 'var(--text-3xl)',
              fontWeight: 'var(--font-black)'
            }}>
              02
            </div>
            <h3 style={{
              fontSize: 'var(--text-2xl)',
              fontWeight: 'var(--font-black)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--tracking-normal)',
              marginBottom: 'var(--space-2)'
            }}>
              AI 분석
            </h3>
            <p style={{
              fontSize: 'var(--text-base)',
              color: 'var(--color-gray-300)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              Claude AI를 활용한 심층 교수학습 패턴 분석
            </p>
          </div>

          <div className="bento-card" style={{
            background: 'var(--color-white)',
            border: 'var(--border-thick) solid var(--color-black)',
            borderRadius: '0',
            padding: 'var(--space-5)',
            transition: 'all 0.3s ease'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              background: 'var(--color-black)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 'var(--space-3)',
              fontSize: 'var(--text-3xl)'
            }}>
              03
            </div>
            <h3 style={{
              fontSize: 'var(--text-2xl)',
              fontWeight: 'var(--font-black)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--tracking-normal)',
              marginBottom: 'var(--space-2)',
              color: 'var(--color-black)'
            }}>
              시각화 보고서
            </h3>
            <p style={{
              fontSize: 'var(--text-base)',
              color: 'var(--color-gray-700)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              Chart.js 기반 인터랙티브 차트 및 진단 보고서 레이아웃
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
