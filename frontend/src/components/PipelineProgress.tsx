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

    const MAX_POLL_TIME = 20 * 60 * 1000 // 20 minutes
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
                ? { ...s, status: 'error', message: '작업 시간 초과 (20분). 페이지를 새로고침하거나 다시 시도해주세요.' }
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
    <div className="glass-card" style={{
      padding: 'var(--space-6)',
      marginBottom: 'var(--space-8)'
    }}>
      {/* Header */}
      <div style={{
        marginBottom: 'var(--space-6)',
        textAlign: 'center'
      }}>
        <h2 style={{
          fontSize: 'var(--text-2xl)',
          fontWeight: '700',
          marginBottom: 'var(--space-2)',
          background: 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          분석 진행 중
        </h2>
        <p style={{
          fontSize: 'var(--text-sm)',
          color: 'var(--color-text-secondary)'
        }}>
          AI가 수업 영상을 정밀하게 분석하고 있습니다
        </p>
      </div>

      {/* Steps */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        position: 'relative',
        marginBottom: 'var(--space-8)',
        maxWidth: '800px',
        margin: '0 auto var(--space-8)'
      }}>
        {/* Progress Bar Background */}
        <div style={{
          position: 'absolute',
          top: '24px',
          left: '0',
          right: '0',
          height: '4px',
          background: 'var(--color-surface-alt)',
          borderRadius: 'var(--radius-full)',
          zIndex: 0
        }} />

        {/* Active Progress Bar */}
        <div style={{
          position: 'absolute',
          top: '24px',
          left: '0',
          height: '4px',
          background: 'linear-gradient(90deg, var(--color-primary) 0%, var(--color-secondary) 100%)',
          borderRadius: 'var(--radius-full)',
          zIndex: 0,
          width: `${(steps.filter(s => s.status === 'completed').length / (steps.length - 1)) * 100}%`,
          transition: 'width 0.5s ease-in-out'
        }} />

        {steps.map((step, index) => (
          <div key={step.id} style={{
            position: 'relative',
            zIndex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '120px'
          }}>
            {/* Step Circle */}
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              background: step.status === 'completed' ? 'var(--color-secondary)' :
                         step.status === 'in_progress' ? 'var(--color-primary)' :
                         step.status === 'error' ? 'var(--color-danger)' :
                         'var(--color-surface)',
              border: step.status === 'pending' ? '2px solid var(--color-surface-alt)' : 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: step.status === 'pending' ? 'var(--color-text-tertiary)' : 'white',
              boxShadow: step.status === 'in_progress' ? '0 0 0 4px rgba(79, 70, 229, 0.2)' : 'var(--shadow-sm)',
              transition: 'all 0.3s ease',
              marginBottom: 'var(--space-3)'
            }}>
              {step.status === 'completed' ? (
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              ) : step.status === 'in_progress' ? (
                <div className="animate-spin" style={{
                  width: '24px',
                  height: '24px',
                  border: '3px solid rgba(255,255,255,0.3)',
                  borderTopColor: 'white',
                  borderRadius: '50%'
                }} />
              ) : step.status === 'error' ? (
                <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <span style={{ fontWeight: '600' }}>{index + 1}</span>
              )}
            </div>

            {/* Step Name */}
            <div style={{
              fontSize: 'var(--text-sm)',
              fontWeight: step.status === 'in_progress' ? '600' : '500',
              color: step.status === 'pending' ? 'var(--color-text-tertiary)' : 'var(--color-text-primary)',
              textAlign: 'center'
            }}>
              {step.name}
            </div>

            {/* Status Message */}
            {step.status === 'in_progress' && step.message && (
              <div style={{
                position: 'absolute',
                top: '80px',
                width: '200px',
                textAlign: 'center',
                fontSize: 'var(--text-xs)',
                color: 'var(--color-primary)',
                background: 'rgba(79, 70, 229, 0.1)',
                padding: '4px 8px',
                borderRadius: 'var(--radius-full)',
                animation: 'fadeIn 0.3s ease'
              }}>
                {step.message}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer Info */}
      <div style={{
        textAlign: 'center',
        paddingTop: 'var(--space-6)',
        borderTop: '1px solid var(--color-surface-alt)'
      }}>
        <div style={{
          fontSize: 'var(--text-sm)',
          color: 'var(--color-text-secondary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 'var(--space-2)'
        }}>
          <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>예상 소요 시간: 5-15분</span>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  )
}
