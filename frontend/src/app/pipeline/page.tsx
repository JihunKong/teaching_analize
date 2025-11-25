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
    // Navigate directly to HTML report API endpoint
    // Support both analysis_id (new) and analysis_job_id (old) for compatibility
    const analysisId = data?.analysis_id || data?.analysis_job_id
    if (analysisId) {
      console.log('Redirecting directly to HTML report:', analysisId)
      // Use window.location for full page redirect to API endpoint
      window.location.href = `/api/reports/html/${analysisId}`
    } else {
      console.error('No analysis_id found in completion data:', data)
      setError('보고서 ID를 찾을 수 없습니다. 관리자에게 문의하세요.')
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.1) 0%, transparent 50%)',
      padding: 'var(--space-8) var(--space-4)'
    }}>
      <div className="container" style={{ maxWidth: '800px' }}>
        {/* Header */}
        <div className="text-center animate-fade-in" style={{ marginBottom: 'var(--space-8)' }}>
          <h1 style={{
            fontSize: 'var(--text-4xl)',
            fontWeight: '800',
            marginBottom: 'var(--space-4)',
            background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Start New Analysis
          </h1>
          <p style={{
            fontSize: 'var(--text-lg)',
            color: 'var(--color-text-secondary)',
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            Enter your YouTube video URL below to generate a comprehensive educational analysis report.
          </p>
        </div>

        {/* Main Card */}
        {!workflowId ? (
          <div className="glass-card animate-fade-in" style={{ padding: 'var(--space-8)' }}>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: 'var(--space-6)' }}>
                <label
                  htmlFor="videoUrl"
                  style={{
                    display: 'block',
                    fontSize: 'var(--text-sm)',
                    fontWeight: '600',
                    color: 'var(--color-text-primary)',
                    marginBottom: 'var(--space-2)',
                    marginLeft: 'var(--space-1)'
                  }}
                >
                  YouTube Video URL
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    id="videoUrl"
                    type="url"
                    required
                    value={videoUrl}
                    onChange={(e) => setVideoUrl(e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    style={{
                      width: '100%',
                      padding: 'var(--space-4)',
                      paddingLeft: 'var(--space-12)',
                      borderRadius: 'var(--radius-xl)',
                      border: '1px solid var(--color-border)',
                      background: 'rgba(255, 255, 255, 0.5)',
                      fontSize: 'var(--text-base)',
                      color: 'var(--color-text-primary)',
                      outline: 'none',
                      transition: 'all 0.2s ease'
                    }}
                    className="focus:ring-2 focus:ring-primary"
                  />
                  <div style={{
                    position: 'absolute',
                    left: 'var(--space-4)',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: 'var(--text-xl)'
                  }}>
                    📹
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: 'var(--space-8)' }}>
                <label
                  htmlFor="framework"
                  style={{
                    display: 'block',
                    fontSize: 'var(--text-sm)',
                    fontWeight: '600',
                    color: 'var(--color-text-primary)',
                    marginBottom: 'var(--space-2)',
                    marginLeft: 'var(--space-1)'
                  }}
                >
                  Analysis Framework
                </label>
                <div style={{ position: 'relative' }}>
                  <select
                    id="framework"
                    value={framework}
                    onChange={(e) => setFramework(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 'var(--space-4)',
                      paddingLeft: 'var(--space-12)',
                      borderRadius: 'var(--radius-xl)',
                      border: '1px solid var(--color-border)',
                      background: 'rgba(255, 255, 255, 0.5)',
                      fontSize: 'var(--text-base)',
                      color: 'var(--color-text-primary)',
                      outline: 'none',
                      cursor: 'pointer',
                      appearance: 'none'
                    }}
                  >
                    <option value="cbil_comprehensive">CBIL Comprehensive Analysis</option>
                    <option value="bloom">Bloom's Taxonomy</option>
                    <option value="webb">Webb's DOK</option>
                  </select>
                  <div style={{
                    position: 'absolute',
                    left: 'var(--space-4)',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: 'var(--text-xl)'
                  }}>
                    🧠
                  </div>
                  <div style={{
                    position: 'absolute',
                    right: 'var(--space-4)',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    pointerEvents: 'none',
                    color: 'var(--color-text-secondary)'
                  }}>
                    ▼
                  </div>
                </div>
              </div>

              {error && (
                <div style={{
                  padding: 'var(--space-4)',
                  marginBottom: 'var(--space-6)',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: 'var(--radius-lg)',
                  color: '#ef4444',
                  fontSize: 'var(--text-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-3)'
                }}>
                  <span>⚠️</span>
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary btn-large"
                style={{
                  width: '100%',
                  justifyContent: 'center',
                  opacity: isSubmitting ? 0.7 : 1
                }}
              >
                {isSubmitting ? (
                  <>
                    <span className="animate-spin" style={{ marginRight: 'var(--space-2)' }}>⚪</span>
                    Starting Analysis...
                  </>
                ) : (
                  <>
                    Start Analysis <span style={{ marginLeft: 'var(--space-2)' }}>→</span>
                  </>
                )}
              </button>
            </form>
          </div>
        ) : (
          /* Progress Display */
          <div className="animate-fade-in">
            <PipelineProgress workflowId={workflowId} onComplete={handleComplete} />
          </div>
        )}

        {/* Features Grid */}
        <div className="grid grid-3" style={{ marginTop: 'var(--space-12)', gap: 'var(--space-6)' }}>
          <div className="glass-card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
            <div style={{ fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-3)' }}>⚡️</div>
            <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: '700', marginBottom: 'var(--space-2)' }}>Fast</h3>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
              Automated transcription and analysis in minutes.
            </p>
          </div>
          <div className="glass-card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
            <div style={{ fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-3)' }}>🎯</div>
            <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: '700', marginBottom: 'var(--space-2)' }}>Accurate</h3>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
              Powered by advanced AI models for deep insights.
            </p>
          </div>
          <div className="glass-card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
            <div style={{ fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-3)' }}>📊</div>
            <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: '700', marginBottom: 'var(--space-2)' }}>Visual</h3>
            <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
              Clear, interactive charts and actionable reports.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
