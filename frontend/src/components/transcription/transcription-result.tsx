'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { TranscriptionJob } from '@/lib/api'
import { formatDateTime, formatDuration } from '@/lib/utils'
import { 
  CheckCircleIcon, 
  AlertCircleIcon, 
  ClockIcon,
  DownloadIcon,
  PlayIcon,
  CopyIcon,
  ChevronUpIcon,
  ChevronDownIcon
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

interface TranscriptionResultProps {
  job: TranscriptionJob
  showActions?: boolean
  compact?: boolean
  className?: string
  autoNavigateToAnalysis?: boolean
  onAnalysisNavigate?: () => void
}

export function TranscriptionResult({ 
  job, 
  showActions = true, 
  compact = false,
  className,
  autoNavigateToAnalysis = false,
  onAnalysisNavigate
}: TranscriptionResultProps) {
  const router = useRouter()
  const [hasAutoNavigated, setHasAutoNavigated] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)

  // Auto-navigation logic when transcription completes
  useEffect(() => {
    if (
      autoNavigateToAnalysis && 
      job.status === 'completed' && 
      job.result?.text && 
      !hasAutoNavigated
    ) {
      // Wait a brief moment to show completion, then navigate
      const timer = setTimeout(() => {
        setHasAutoNavigated(true)
        if (onAnalysisNavigate) {
          onAnalysisNavigate()
        } else {
          // Store transcription data for analysis page in the expected format
          const transcriptionData = {
            job_id: job.job_id,
            transcript: job.result?.text || '',
            language: job.result?.language || 'ko',
            source_type: job.source_type || 'file',
            source_info: {
              title: job.source_url ? 'YouTube 동영상' : '업로드 파일',
              duration: job.result?.duration,
              url: job.source_url
            }
          }
          sessionStorage.setItem('transcriptionData', JSON.stringify(transcriptionData))
          router.push('/analysis')
        }
      }, 2000) // 2 second delay to show completion message

      return () => clearTimeout(timer)
    }
  }, [job.status, job.result?.text, autoNavigateToAnalysis, hasAutoNavigated, onAnalysisNavigate, router, job])

  const handleNavigateToAnalysis = () => {
    // Store transcription data for analysis page in the expected format
    const transcriptionData = {
      job_id: job.job_id,
      transcript: job.result?.text || '',
      language: job.result?.language || 'ko',
      source_type: job.source_type || 'file',
      source_info: {
        title: job.source_url ? 'YouTube 동영상' : '업로드 파일',
        duration: job.result?.duration,
        url: job.source_url
      }
    }
    
    sessionStorage.setItem('transcriptionData', JSON.stringify(transcriptionData))
    
    if (onAnalysisNavigate) {
      onAnalysisNavigate()
    } else {
      router.push('/analysis')
    }
  }

  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'failed':
        return <AlertCircleIcon className="h-5 w-5 text-red-500" />
      case 'processing':
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-spin" />
    }
  }

  const getStatusText = () => {
    switch (job.status) {
      case 'completed':
        return '완료'
      case 'failed':
        return '실패'
      case 'processing':
        return '처리중'
      case 'pending':
        return '대기중'
    }
  }

  const getStatusColor = () => {
    switch (job.status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'processing':
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
    }
  }

  const getProgress = () => {
    switch (job.status) {
      case 'completed':
        return 100
      case 'failed':
        return 0
      case 'processing':
        return 60 // Estimate
      case 'pending':
        return 20
      default:
        return 0
    }
  }

  const handleCopyText = () => {
    if (job.result?.text) {
      navigator.clipboard.writeText(job.result.text)
      // TODO: Add toast notification
    }
  }

  const handleDownload = () => {
    if (job.result?.text) {
      const blob = new Blob([job.result.text], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `transcription-${job.job_id}.txt`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  if (compact) {
    return (
      <div className={cn('flex items-center space-x-3 p-3 border rounded-lg', className)}>
        {getStatusIcon()}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-900 truncate">
              작업 ID: {job.job_id.substring(0, 8)}
            </span>
            <Badge className={getStatusColor()}>
              {getStatusText()}
            </Badge>
          </div>
          {(job.status === 'processing' || job.status === 'pending') && (
            <Progress value={getProgress()} className="mt-2 h-1" />
          )}
        </div>
      </div>
    )
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {getStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              전사 결과
            </h3>
            <p className="text-sm text-gray-500">
              작업 ID: {job.job_id}
            </p>
          </div>
        </div>
        <Badge className={getStatusColor()}>
          {getStatusText()}
        </Badge>
      </div>

      {/* Progress */}
      {(job.status === 'processing' || job.status === 'pending') && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">진행률</span>
            <span className="font-medium">{getProgress()}%</span>
          </div>
          <Progress value={getProgress()} />
        </div>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">생성 시간:</span>
          <p className="font-medium">{formatDateTime(job.created_at)}</p>
        </div>
        {job.completed_at && (
          <div>
            <span className="text-gray-500">완료 시간:</span>
            <p className="font-medium">{formatDateTime(job.completed_at)}</p>
          </div>
        )}
        {job.result?.language && (
          <div>
            <span className="text-gray-500">언어:</span>
            <p className="font-medium">{job.result.language === 'ko' ? '한국어' : job.result.language}</p>
          </div>
        )}
        {job.result?.duration && (
          <div>
            <span className="text-gray-500">재생 시간:</span>
            <p className="font-medium">{job.result.duration}</p>
          </div>
        )}
      </div>

      {/* Error */}
      {job.status === 'failed' && job.error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">{job.error}</p>
        </div>
      )}

      {/* Result Text */}
      {job.result?.text && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900">전사 텍스트</h4>
            {showActions && (
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleCopyText}
                >
                  <CopyIcon className="h-4 w-4 mr-1" />
                  복사
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleDownload}
                >
                  <DownloadIcon className="h-4 w-4 mr-1" />
                  다운로드
                </Button>
              </div>
            )}
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-gray-500">
                {job.result.text.length.toLocaleString()}자 • 약 {Math.ceil(job.result.text.length / 500)}분 읽기
              </span>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsExpanded(!isExpanded)}
                className="h-6 px-2 text-xs"
              >
                {isExpanded ? (
                  <>
                    <ChevronUpIcon className="h-3 w-3 mr-1" />
                    접기
                  </>
                ) : (
                  <>
                    <ChevronDownIcon className="h-3 w-3 mr-1" />
                    전체보기
                  </>
                )}
              </Button>
            </div>
            <div className={cn(
              "overflow-y-auto transition-all duration-300",
              isExpanded ? "max-h-none" : "max-h-60"
            )}>
              <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                {job.result.text}
              </p>
            </div>
          </div>

          {/* Segments */}
          {job.result.segments && job.result.segments.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium text-gray-900">시간별 구간</h4>
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {job.result.segments.map((segment, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-2 bg-white border rounded text-sm"
                  >
                    <div className="flex-shrink-0 w-20 text-gray-500 font-mono">
                      {formatDuration(segment.start)} - {formatDuration(segment.end)}
                    </div>
                    <p className="flex-1 text-gray-800">{segment.text}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      {showActions && job.status === 'completed' && job.result?.text && (
        <div className="flex justify-center pt-4">
          {autoNavigateToAnalysis && !hasAutoNavigated ? (
            <div className="text-center space-y-2">
              <div className="text-sm text-blue-600 font-medium">
                🎉 전사 완료! 곧 분석 페이지로 이동합니다...
              </div>
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-blue-500 to-purple-600"
                onClick={handleNavigateToAnalysis}
              >
                <PlayIcon className="h-5 w-5 mr-2" />
                지금 분석하러 가기
              </Button>
            </div>
          ) : (
            <Button 
              size="lg" 
              className="bg-gradient-to-r from-blue-500 to-purple-600"
              onClick={handleNavigateToAnalysis}
            >
              <PlayIcon className="h-5 w-5 mr-2" />
              분석하러 가기
            </Button>
          )}
        </div>
      )}
    </div>
  )
}