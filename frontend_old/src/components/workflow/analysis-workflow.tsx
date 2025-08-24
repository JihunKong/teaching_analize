'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { OldFrameworkSelector as FrameworkSelector } from '@/components/analysis/old-framework-selector'
import { TranscriptionResult } from '@/components/transcription/transcription-result'
import { AnalysisResult } from '@/components/analysis/analysis-result'
import { useJobStatusPolling } from '@/hooks/useTranscription'
import { useTranscriptToAnalysis } from '@/hooks/useAnalysis'
import { AnalysisFramework } from '@/types/analysis'
import { 
  UploadIcon, 
  FileTextIcon, 
  BarChart3Icon, 
  CheckCircleIcon,
  ArrowRightIcon,
  PlayIcon,
  PauseIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface AnalysisWorkflowProps {
  initialJobId?: string
  onComplete?: (analysisId: string) => void
}

type WorkflowStep = 'upload' | 'transcription' | 'framework-selection' | 'analysis' | 'results'

interface WorkflowState {
  currentStep: WorkflowStep
  completedSteps: WorkflowStep[]
  jobId?: string
  transcriptionText?: string
  selectedFramework?: AnalysisFramework
  analysisId?: string
}

export function AnalysisWorkflow({ initialJobId, onComplete }: AnalysisWorkflowProps) {
  const [state, setState] = useState<WorkflowState>({
    currentStep: initialJobId ? 'transcription' : 'upload',
    completedSteps: initialJobId ? ['upload'] : [],
    jobId: initialJobId,
  })

  // Poll transcription job status
  const { job: transcriptionJob, isCompleted: isTranscriptionComplete } = useJobStatusPolling(state.jobId)
  
  // Analysis mutation
  const transcriptAnalysis = useTranscriptToAnalysis()

  // Update workflow state based on transcription progress
  useEffect(() => {
    if (isTranscriptionComplete && (transcriptionJob as any)?.result?.text) {
      setState(prev => ({
        ...prev,
        transcriptionText: (transcriptionJob as any).result!.text,
        completedSteps: [...prev.completedSteps, 'transcription'],
        currentStep: 'framework-selection',
      }))
    }
  }, [isTranscriptionComplete, transcriptionJob])

  // Handle framework selection
  const handleFrameworkSelect = (framework: AnalysisFramework) => {
    setState(prev => ({
      ...prev,
      selectedFramework: framework,
    }))
  }

  // Start analysis
  const handleStartAnalysis = () => {
    if (!state.transcriptionText || !state.selectedFramework) return

    setState(prev => ({
      ...prev,
      currentStep: 'analysis',
      completedSteps: [...prev.completedSteps, 'framework-selection'],
    }))

    transcriptAnalysis.analyzeTranscript(
      state.transcriptionText!,
      state.selectedFramework!.id,
      {
        source_type: 'file_upload', // or 'youtube' based on original upload
        source_id: state.jobId!,
        language: (transcriptionJob as any)?.result?.language || 'ko',
        duration: (transcriptionJob as any)?.result?.duration ? parseFloat((transcriptionJob as any).result.duration) : undefined,
      }
    )
  }

  // Handle analysis completion
  useEffect(() => {
    if (transcriptAnalysis.isSuccess && transcriptAnalysis.data) {
      setState(prev => ({
        ...prev,
        analysisId: transcriptAnalysis.data!.id,
        currentStep: 'results',
        completedSteps: [...prev.completedSteps, 'analysis'],
      }))
      
      if (onComplete) {
        onComplete(transcriptAnalysis.data.id)
      }
    }
  }, [transcriptAnalysis.isSuccess, transcriptAnalysis.data, onComplete])

  const steps = [
    { 
      key: 'upload' as const, 
      title: '파일 업로드', 
      icon: UploadIcon,
      description: '비디오/오디오 파일 또는 YouTube URL'
    },
    { 
      key: 'transcription' as const, 
      title: '전사 처리', 
      icon: FileTextIcon,
      description: '음성을 텍스트로 변환'
    },
    { 
      key: 'framework-selection' as const, 
      title: '분석 도구 선택', 
      icon: BarChart3Icon,
      description: '사용할 분석 프레임워크 선택'
    },
    { 
      key: 'analysis' as const, 
      title: '분석 실행', 
      icon: PlayIcon,
      description: '선택된 도구로 텍스트 분석'
    },
    { 
      key: 'results' as const, 
      title: '결과 확인', 
      icon: CheckCircleIcon,
      description: '분석 결과 및 시각화'
    },
  ]

  const getStepStatus = (stepKey: WorkflowStep) => {
    if (state.completedSteps.includes(stepKey)) return 'completed'
    if (state.currentStep === stepKey) return 'current'
    return 'pending'
  }

  const getOverallProgress = () => {
    const totalSteps = steps.length
    const completedCount = state.completedSteps.length
    const currentStepIndex = steps.findIndex(s => s.key === state.currentStep)
    
    // Add partial progress for current step
    let progress = completedCount
    if (state.currentStep === 'transcription' && transcriptionJob) {
      progress += 0.5 // Assume 50% progress during transcription
    } else if (state.currentStep === 'analysis' && transcriptAnalysis.isPending) {
      progress += 0.5 // Assume 50% progress during analysis
    }
    
    return Math.round((progress / totalSteps) * 100)
  }

  return (
    <div className="space-y-6">
      {/* Progress Overview */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-blue-900">분석 워크플로우</CardTitle>
            <Badge className="bg-blue-100 text-blue-800">
              {getOverallProgress()}% 완료
            </Badge>
          </div>
          <Progress value={getOverallProgress()} className="mt-2" />
        </CardHeader>
        <CardContent>
          {/* Step Timeline */}
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const status = getStepStatus(step.key)
              const Icon = step.icon
              
              return (
                <div key={step.key} className="flex items-center">
                  <div className="flex flex-col items-center">
                    {/* Step Icon */}
                    <div
                      className={cn(
                        'w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200',
                        status === 'completed' && 'bg-green-500 text-white',
                        status === 'current' && 'bg-blue-500 text-white animate-pulse',
                        status === 'pending' && 'bg-gray-200 text-gray-400'
                      )}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                    
                    {/* Step Info */}
                    <div className="mt-2 text-center">
                      <div className={cn(
                        'text-sm font-medium',
                        status === 'completed' && 'text-green-700',
                        status === 'current' && 'text-blue-700',
                        status === 'pending' && 'text-gray-500'
                      )}>
                        {step.title}
                      </div>
                      <div className="text-xs text-gray-500 mt-1 max-w-24">
                        {step.description}
                      </div>
                    </div>
                  </div>
                  
                  {/* Connector */}
                  {index < steps.length - 1 && (
                    <div className={cn(
                      'h-0.5 w-8 mx-3 transition-colors duration-300',
                      state.completedSteps.includes(steps[index + 1].key) ? 'bg-green-300' : 'bg-gray-200'
                    )} />
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Current Step Content */}
      <div className="space-y-6">
        {/* Upload Step */}
        {state.currentStep === 'upload' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <UploadIcon className="h-5 w-5 mr-2" />
                파일 업로드
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <p>파일 업로드 컴포넌트가 여기에 표시됩니다.</p>
                <p className="text-sm mt-1">업로드 완료 후 자동으로 전사가 시작됩니다.</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Transcription Step */}
        {state.currentStep === 'transcription' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileTextIcon className="h-5 w-5 mr-2" />
                전사 처리 중
              </CardTitle>
            </CardHeader>
            <CardContent>
              {transcriptionJob ? (
                <TranscriptionResult 
                  job={transcriptionJob as any}
                  showActions={false}
                />
              ) : null}
            </CardContent>
          </Card>
        )}

        {/* Framework Selection Step */}
        {state.currentStep === 'framework-selection' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3Icon className="h-5 w-5 mr-2" />
                분석 도구 선택
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Transcription Preview */}
              {state.transcriptionText && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">전사 결과 미리보기</h4>
                  <p className="text-sm text-gray-700 line-clamp-3">
                    {state.transcriptionText.substring(0, 300)}
                    {state.transcriptionText.length > 300 && '...'}
                  </p>
                  <Badge variant="secondary" className="mt-2">
                    총 {state.transcriptionText.length}자
                  </Badge>
                </div>
              )}

              {/* Framework Selector */}
              <FrameworkSelector
                selectedFramework={state.selectedFramework?.id}
                onFrameworkSelect={handleFrameworkSelect}
              />

              {/* Action Button */}
              {state.selectedFramework && (
                <div className="flex justify-center pt-4">
                  <Button
                    size="lg"
                    onClick={handleStartAnalysis}
                    className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                  >
                    <PlayIcon className="h-5 w-5 mr-2" />
                    {state.selectedFramework.name} 분석 시작
                    <ArrowRightIcon className="h-5 w-5 ml-2" />
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Analysis Step */}
        {state.currentStep === 'analysis' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <PlayIcon className="h-5 w-5 mr-2" />
                분석 실행 중
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
                  <BarChart3Icon className="h-8 w-8 text-blue-600 animate-pulse" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {state.selectedFramework?.name} 분석 중...
                </h3>
                <p className="text-gray-600">
                  텍스트를 분석하여 인사이트를 생성하고 있습니다.
                </p>
                {transcriptAnalysis.isError && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800 text-sm">
                      분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Step */}
        {state.currentStep === 'results' && state.analysisId && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CheckCircleIcon className="h-5 w-5 mr-2 text-green-600" />
                분석 완료
              </CardTitle>
            </CardHeader>
            <CardContent>
              <AnalysisResult analysisId={state.analysisId} />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}