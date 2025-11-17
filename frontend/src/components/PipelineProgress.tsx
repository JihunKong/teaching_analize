'use client'

import { useEffect, useState, useRef } from 'react'

export interface WorkflowStep {
  id: string
  name: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
  message?: string
  progress?: number
}

interface PipelineProgressProps {
  workflowId: string | null
  onComplete?: (data: any) => void
}

export default function PipelineProgress({ workflowId, onComplete }: PipelineProgressProps) {
  const [steps, setSteps] = useState<WorkflowStep[]>([
    { id: 'transcription', name: '영상 전사', status: 'pending' },
    { id: 'analysis', name: 'AI 분석', status: 'pending' },
    { id: 'report', name: '보고서 생성', status: 'pending' }
  ])
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!workflowId) return

    const MAX_POLL_TIME = 10 * 60 * 1000 // 10 minutes
    const startTime = Date.now()
    let pollCount = 0

    const pollStatus = async () => {
      // Check timeout
      const elapsed = Date.now() - startTime
      pollCount++

      if (elapsed > MAX_POLL_TIME) {
        console.error(`Polling timeout after ${Math.floor(elapsed / 1000)}s (${pollCount} attempts)`)
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
          intervalRef.current = null
        }
        setSteps(prevSteps => {
          const currentStep = prevSteps.find(s => s.status === 'in_progress')
          if (currentStep) {
            return prevSteps.map(s =>
              s.id === currentStep.id
                ? { ...s, status: 'error', message: '작업 시간 초과 (10분). 페이지를 새로고침하거나 다시 시도해주세요.' }
                : s
            )
          }
          return prevSteps
        })
        return
      }

      try {
        const apiUrl = typeof window !== 'undefined' ? window.location.origin : 'http://localhost'
        const response = await fetch(`${apiUrl}/api/workflow/status/${workflowId}`)
        const data = await response.json()

        console.log('Workflow status:', data) // Debug log

        // Check for completion first (backend returns status: "success")
        if (data.status === 'success' || data.current_step === 'completed') {
          console.log('Workflow completed! Stopping polling.')
          // Mark all steps as completed
          setSteps(prevSteps => prevSteps.map(step => ({
            ...step,
            status: 'completed' as const
          })))
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
          if (onComplete) {
            onComplete(data.data)
          }
          return
        }

        // Check for error
        if (data.status === 'error' || data.status === 'failed') {
          console.log('Workflow failed. Stopping polling.')
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
          setSteps(prevSteps => {
            const errorStepIndex = prevSteps.findIndex(s => s.id === data.current_step)
            if (errorStepIndex >= 0) {
              const updated = [...prevSteps]
              updated[errorStepIndex] = {
                ...updated[errorStepIndex],
                status: 'error',
                message: data.message || '작업 중 오류가 발생했습니다'
              }
              return updated
            }
            return prevSteps
          })
          return
        }

        // Update steps based on current progress
        if (data.current_step) {
          setSteps(prevSteps => prevSteps.map(step => {
            if (step.id === data.current_step) {
              return { ...step, status: 'in_progress' as const, message: data.message }
            } else if (data.completed_steps?.includes(step.id)) {
              return { ...step, status: 'completed' as const }
            }
            return step
          }))
        }
      } catch (error) {
        console.error('Failed to fetch workflow status:', error)
      }
    }

    // Poll every 3 seconds
    intervalRef.current = setInterval(pollStatus, 3000)
    pollStatus() // Initial call

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [workflowId, onComplete])

  return (
    <div style={{
      background: 'var(--color-white)',
      border: 'var(--border-thick) solid var(--color-black)',
      borderRadius: '0',
      padding: 'var(--space-6)',
      boxShadow: '8px 8px 0 var(--color-black)',
      marginBottom: 'var(--space-4)'
    }}>
      {/* Brutalist Header */}
      <div style={{
        marginBottom: 'var(--space-5)',
        paddingBottom: 'var(--space-4)',
        borderBottom: 'var(--border-medium) solid var(--color-black)'
      }}>
        <h2 style={{
          fontSize: 'var(--text-3xl)',
          fontWeight: 'var(--font-black)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--tracking-wide)',
          color: 'var(--color-black)',
          marginBottom: 'var(--space-2)'
        }}>
          ▶ 분석 진행 중
        </h2>
        <p style={{
          fontSize: 'var(--text-base)',
          color: 'var(--color-gray-600)',
          fontFamily: 'var(--font-mono)'
        }}>
          YouTube 영상 → 전사 → 분석 → 보고서 생성
        </p>
      </div>

      {/* Brutalist Pipeline Steps */}
      <div style={{ marginBottom: 'var(--space-5)' }}>
        {steps.map((step, index) => (
          <div key={step.id} style={{
            marginBottom: index < steps.length - 1 ? 'var(--space-4)' : '0',
            position: 'relative'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 'var(--space-4)'
            }}>
              {/* Brutalist Step Icon */}
              <div style={{
                width: '64px',
                height: '64px',
                border: 'var(--border-medium) solid var(--color-black)',
                borderRadius: '0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                background: step.status === 'completed' ? 'var(--color-black)' :
                           step.status === 'in_progress' ? 'var(--color-white)' :
                           step.status === 'error' ? 'var(--color-gray-900)' :
                           'var(--color-gray-100)',
                color: step.status === 'completed' ? 'var(--color-white)' :
                       step.status === 'in_progress' ? 'var(--color-black)' :
                       step.status === 'error' ? 'var(--color-white)' :
                       'var(--color-gray-500)',
                boxShadow: step.status === 'in_progress' ? '4px 4px 0 var(--color-black)' : 'none',
                position: 'relative'
              }}>
                {step.status === 'completed' ? (
                  <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="square" strokeLinejoin="miter" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                ) : step.status === 'in_progress' ? (
                  <div style={{
                    width: '28px',
                    height: '28px',
                    border: '4px solid var(--color-black)',
                    borderTop: '4px solid transparent',
                    borderRadius: '0',
                    animation: 'brutalist-spin 1s linear infinite'
                  }} />
                ) : step.status === 'error' ? (
                  <svg width="32" height="32" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="square" strokeLinejoin="miter" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                ) : (
                  <span style={{
                    fontSize: 'var(--text-2xl)',
                    fontWeight: 'var(--font-black)',
                    fontFamily: 'var(--font-mono)'
                  }}>
                    {index + 1}
                  </span>
                )}
              </div>

              {/* Step Content */}
              <div style={{ flex: 1, paddingTop: 'var(--space-2)' }}>
                <div style={{
                  fontSize: 'var(--text-xl)',
                  fontWeight: 'var(--font-bold)',
                  textTransform: 'uppercase',
                  letterSpacing: 'var(--tracking-normal)',
                  color: step.status === 'completed' ? 'var(--color-black)' :
                         step.status === 'in_progress' ? 'var(--color-black)' :
                         step.status === 'error' ? 'var(--color-gray-900)' :
                         'var(--color-gray-400)',
                  marginBottom: 'var(--space-2)'
                }}>
                  {step.name}
                </div>
                {step.message && (
                  <div style={{
                    fontSize: 'var(--text-sm)',
                    padding: 'var(--space-2)',
                    background: step.status === 'error' ? 'var(--color-black)' :
                               step.status === 'in_progress' ? 'var(--color-white)' :
                               'var(--color-gray-100)',
                    color: step.status === 'error' ? 'var(--color-white)' :
                           'var(--color-gray-700)',
                    border: step.status === 'error' ? 'none' :
                           'var(--border-thin) solid var(--color-gray-300)',
                    borderRadius: '0',
                    fontFamily: 'var(--font-primary)'
                  }}>
                    {step.message}
                  </div>
                )}
              </div>
            </div>

            {/* Brutalist Connector */}
            {index < steps.length - 1 && (
              <div style={{
                position: 'absolute',
                left: '31px',
                top: '72px',
                width: '2px',
                height: '32px',
                background: step.status === 'completed' ? 'var(--color-black)' :
                           step.status === 'in_progress' ? 'var(--color-gray-400)' :
                           'var(--color-gray-200)'
              }} />
            )}
          </div>
        ))}
      </div>

      {/* Brutalist Footer */}
      <div style={{
        paddingTop: 'var(--space-4)',
        borderTop: 'var(--border-thin) solid var(--color-gray-200)'
      }}>
        <div style={{
          fontSize: 'var(--text-sm)',
          fontWeight: 'var(--font-semibold)',
          color: 'var(--color-gray-700)',
          marginBottom: 'var(--space-3)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--tracking-wide)'
        }}>
          ⏱ 예상 소요 시간: 3-5분
        </div>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--space-2)'
        }}>
          <div style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--color-gray-600)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              background: 'var(--color-black)',
              borderRadius: '0'
            }}></div>
            <span>자동 전사: Selenium을 통한 YouTube 자막 추출</span>
          </div>
          <div style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--color-gray-600)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              background: 'var(--color-gray-700)',
              borderRadius: '0'
            }}></div>
            <span>AI 분석: Claude AI를 활용한 심층 교수학습 패턴 분석</span>
          </div>
          <div style={{
            fontSize: 'var(--text-xs)',
            color: 'var(--color-gray-600)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              background: 'var(--color-gray-500)',
              borderRadius: '0'
            }}></div>
            <span>시각화 보고서: Chart.js 기반 인터랙티브 차트 생성</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes brutalist-spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
