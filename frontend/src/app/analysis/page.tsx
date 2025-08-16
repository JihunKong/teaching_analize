'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Layout } from '@/components/layout/layout'
import { FrameworkSelector } from '@/components/analysis/framework-selector'
import { ResultsDashboard } from '@/components/analysis/results-dashboard'
import { useParallelAnalysis } from '@/hooks/useParallelAnalysis'
import { 
  COMPREHENSIVE_FRAMEWORKS, 
  ComprehensiveAnalysisResult,
  comprehensiveFrameworkUtils 
} from '@/types/comprehensive-analysis'
import { 
  PlayIcon, 
  PauseIcon, 
  RefreshCwIcon,
  CheckCircleIcon,
  AlertTriangleIcon,
  TimerIcon,
  BrainIcon
} from 'lucide-react'

interface TranscriptionData {
  job_id: string
  transcript: string
  language: string
  source_type: 'file' | 'youtube'
  source_info?: {
    title?: string
    duration?: number
    url?: string
  }
}

export default function AnalysisPage() {
  const router = useRouter()
  const [transcriptionData, setTranscriptionData] = useState<TranscriptionData | null>(null)
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>(
    COMPREHENSIVE_FRAMEWORKS.filter(f => f.enabled).slice(0, 5).map(f => f.id)
  )
  const [activeTab, setActiveTab] = useState('setup')
  
  // Parallel analysis hook
  const {
    startAnalysis,
    pauseAnalysis,
    resumeAnalysis,
    resetAnalysis,
    progress,
    results,
    isRunning,
    isPaused,
    error,
    estimatedTimeRemaining,
    completedFrameworks,
    currentFramework
  } = useParallelAnalysis()

  // Load transcription data from sessionStorage on mount
  useEffect(() => {
    const storedData = sessionStorage.getItem('transcriptionData')
    if (storedData) {
      try {
        const data = JSON.parse(storedData)
        setTranscriptionData(data)
      } catch (error) {
        console.error('Failed to parse transcription data:', error)
        // Redirect back to transcription if invalid data
        router.push('/transcription')
      }
    } else {
      // No transcription data, redirect to transcription page
      router.push('/transcription')
    }
  }, [router])

  // Auto-switch to results tab when analysis completes
  useEffect(() => {
    if (progress === 100 && results) {
      setActiveTab('results')
    }
  }, [progress, results])

  const handleStartAnalysis = async () => {
    if (!transcriptionData || selectedFrameworks.length === 0) {
      return
    }

    try {
      await startAnalysis({
        frameworks: selectedFrameworks,
        text: transcriptionData.transcript,
        parallel_execution: true,
        temperature: 0.3,
        include_cross_analysis: true,
        metadata: {
          source_type: transcriptionData.source_type === 'file' ? 'file_upload' : transcriptionData.source_type,
          source_id: transcriptionData.job_id,
          language: transcriptionData.language
        }
      })
      setActiveTab('progress')
    } catch (error) {
      console.error('Failed to start analysis:', error)
    }
  }

  const handleFrameworkToggle = (frameworkId: string, enabled: boolean) => {
    setSelectedFrameworks(prev => 
      enabled 
        ? [...prev, frameworkId]
        : prev.filter(id => id !== frameworkId)
    )
  }

  const handleResetAnalysis = () => {
    resetAnalysis()
    setActiveTab('setup')
  }

  const getEstimatedTime = () => {
    const baseTimePerFramework = 30 // seconds
    return selectedFrameworks.length * baseTimePerFramework
  }

  const getAnalysisStatusColor = () => {
    if (error) return 'text-red-600'
    if (progress === 100) return 'text-green-600'
    if (isRunning) return 'text-blue-600'
    if (isPaused) return 'text-yellow-600'
    return 'text-gray-600'
  }

  if (!transcriptionData) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto space-y-6">
          <Alert variant="destructive">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              전사 데이터를 불러올 수 없습니다. 전사 페이지로 이동합니다.
            </AlertDescription>
          </Alert>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Page Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <BrainIcon className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">종합 교육 분석</h1>
            {transcriptionData.source_info?.title && (
              <Badge variant="outline" className="ml-auto">
                {transcriptionData.source_info.title}
              </Badge>
            )}
          </div>
          <p className="text-gray-600">
            13개 교육학 프레임워크를 통한 다각도 수업 분석
          </p>
        </div>

        {/* Transcription Info Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">분석 대상 정보</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium">소스 유형:</span>{' '}
                <Badge variant={transcriptionData.source_type === 'youtube' ? 'secondary' : 'outline'}>
                  {transcriptionData.source_type === 'youtube' ? 'YouTube' : '파일'}
                </Badge>
              </div>
              <div>
                <span className="font-medium">언어:</span> {transcriptionData.language.toUpperCase()}
              </div>
              <div>
                <span className="font-medium">텍스트 길이:</span> {transcriptionData.transcript.length.toLocaleString()}자
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Analysis Interface */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="setup" disabled={isRunning && !isPaused}>
              1. 프레임워크 선택
            </TabsTrigger>
            <TabsTrigger value="progress" disabled={!isRunning && progress === 0}>
              2. 분석 진행
            </TabsTrigger>
            <TabsTrigger value="results" disabled={!results}>
              3. 결과 확인
            </TabsTrigger>
            <TabsTrigger value="comparison" disabled={!results}>
              4. 종합 비교
            </TabsTrigger>
          </TabsList>

          {/* Setup Tab */}
          <TabsContent value="setup" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Framework Selection */}
              <div className="lg:col-span-2">
                <FrameworkSelector
                  frameworks={COMPREHENSIVE_FRAMEWORKS}
                  selectedFrameworks={selectedFrameworks}
                  onFrameworkToggle={handleFrameworkToggle}
                  estimatedTime={getEstimatedTime()}
                />
              </div>

              {/* Analysis Settings */}
              <Card>
                <CardHeader>
                  <CardTitle>분석 설정</CardTitle>
                  <CardDescription>
                    선택된 프레임워크로 분석을 시작합니다.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>선택된 프레임워크:</span>
                      <Badge>{selectedFrameworks.length}개</Badge>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>예상 소요 시간:</span>
                      <span className="flex items-center gap-1">
                        <TimerIcon className="h-3 w-3" />
                        {Math.round(getEstimatedTime() / 60)}분
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>병렬 실행:</span>
                      <Badge variant="secondary">활성화</Badge>
                    </div>
                  </div>

                  <Button
                    onClick={handleStartAnalysis}
                    disabled={selectedFrameworks.length === 0 || isRunning}
                    className="w-full"
                  >
                    <PlayIcon className="h-4 w-4 mr-2" />
                    분석 시작
                  </Button>

                  {selectedFrameworks.length === 0 && (
                    <Alert>
                      <AlertTriangleIcon className="h-4 w-4" />
                      <AlertDescription>
                        최소 1개 이상의 프레임워크를 선택해주세요.
                      </AlertDescription>
                    </Alert>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Progress Tab */}
          <TabsContent value="progress" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle className="text-lg">분석 진행 상황</CardTitle>
                  <div className="flex gap-2">
                    {isRunning && !isPaused && (
                      <Button variant="outline" size="sm" onClick={pauseAnalysis}>
                        <PauseIcon className="h-4 w-4 mr-2" />
                        일시정지
                      </Button>
                    )}
                    {isPaused && (
                      <Button variant="outline" size="sm" onClick={resumeAnalysis}>
                        <PlayIcon className="h-4 w-4 mr-2" />
                        재개
                      </Button>
                    )}
                    <Button variant="outline" size="sm" onClick={handleResetAnalysis}>
                      <RefreshCwIcon className="h-4 w-4 mr-2" />
                      초기화
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Overall Progress */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">전체 진행률</span>
                    <span className={`text-sm font-medium ${getAnalysisStatusColor()}`}>
                      {progress.toFixed(1)}%
                    </span>
                  </div>
                  <Progress value={progress} className="h-2" />
                  {estimatedTimeRemaining > 0 && (
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>완료: {completedFrameworks.length}/{selectedFrameworks.length}</span>
                      <span>남은 시간: 약 {Math.round(estimatedTimeRemaining / 60)}분</span>
                    </div>
                  )}
                </div>

                {/* Current Framework */}
                {currentFramework && (
                  <div className="border rounded-lg p-4 bg-blue-50">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
                      <span className="font-medium">
                        현재 분석 중: {comprehensiveFrameworkUtils.getFramework(currentFramework)?.name_ko}
                      </span>
                    </div>
                  </div>
                )}

                {/* Framework Progress Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {selectedFrameworks.map(frameworkId => {
                    const framework = comprehensiveFrameworkUtils.getFramework(frameworkId)
                    const isCompleted = completedFrameworks.includes(frameworkId)
                    const isCurrent = currentFramework === frameworkId
                    
                    return (
                      <div
                        key={frameworkId}
                        className={`border rounded-lg p-3 ${
                          isCompleted ? 'bg-green-50 border-green-200' :
                          isCurrent ? 'bg-blue-50 border-blue-200' :
                          'bg-gray-50 border-gray-200'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium truncate">
                            {framework?.name_ko}
                          </span>
                          {isCompleted && (
                            <CheckCircleIcon className="h-4 w-4 text-green-600" />
                          )}
                          {isCurrent && (
                            <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse" />
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>

                {/* Error Display */}
                {error && (
                  <Alert variant="destructive">
                    <AlertTriangleIcon className="h-4 w-4" />
                    <AlertDescription>
                      분석 중 오류가 발생했습니다: {error.message}
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Results Tab */}
          <TabsContent value="results" className="space-y-6">
            {results && (
              <ResultsDashboard 
                results={results}
                selectedFrameworks={selectedFrameworks}
              />
            )}
          </TabsContent>

          {/* Comparison Tab */}
          <TabsContent value="comparison" className="space-y-6">
            {results && (
              <Card>
                <CardHeader>
                  <CardTitle>종합 비교 분석</CardTitle>
                  <CardDescription>
                    모든 프레임워크 결과를 종합하여 교육적 통찰을 제공합니다.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Cross-framework insights and overall summary will be displayed here */}
                  <div className="text-center py-8 text-gray-500">
                    종합 비교 분석 결과가 여기에 표시됩니다.
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  )
}