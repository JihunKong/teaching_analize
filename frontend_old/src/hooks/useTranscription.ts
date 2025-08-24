'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { transcriptionService, TranscriptionJob, TranscriptionRequest } from '@/lib/api'

// Query keys
export const transcriptionKeys = {
  all: ['transcription'] as const,
  job: (id: string) => [...transcriptionKeys.all, 'job', id] as const,
  health: () => [...transcriptionKeys.all, 'health'] as const,
}

// Hook for uploading files
export function useUploadFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ file, language }: { file: File; language?: string }) =>
      transcriptionService.uploadFile(file, language),
    onSuccess: (data) => {
      // Add the new job to the cache
      queryClient.setQueryData(transcriptionKeys.job(data.job_id), data)
      // Invalidate the all transcriptions query if it exists
      queryClient.invalidateQueries({ queryKey: transcriptionKeys.all })
    },
    onError: (error) => {
      console.error('File upload failed:', error)
    },
  })
}

// Hook for YouTube transcription
export function useTranscribeYouTube() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (request: TranscriptionRequest) =>
      transcriptionService.transcribeYouTube(request),
    onSuccess: (data) => {
      // Add the new job to the cache
      queryClient.setQueryData(transcriptionKeys.job(data.job_id), data)
      // Invalidate the all transcriptions query if it exists
      queryClient.invalidateQueries({ queryKey: transcriptionKeys.all })
    },
    onError: (error) => {
      console.error('YouTube transcription failed:', error)
    },
  })
}

// Hook for getting job status
export function useJobStatus(jobId: string | undefined, options?: {
  enabled?: boolean
  refetchInterval?: number
}) {
  return useQuery({
    queryKey: transcriptionKeys.job(jobId || ''),
    queryFn: () => transcriptionService.getJobStatus(jobId!),
    enabled: !!jobId && options?.enabled !== false,
    refetchInterval: (query) => {
      // Auto-refresh if job is still processing
      const data = query?.state?.data as any
      if (data?.status === 'processing' || data?.status === 'pending') {
        return options?.refetchInterval || 2000 // 2 seconds
      }
      return false
    },
    retry: (failureCount, error: any) => {
      // Don't retry if job not found
      if (error?.response?.status === 404) {
        return false
      }
      return failureCount < 3
    },
  })
}

// Hook for transcription service health
export function useTranscriptionHealth() {
  return useQuery({
    queryKey: transcriptionKeys.health(),
    queryFn: transcriptionService.healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
    retry: 1,
  })
}

// Custom hook for polling job status until completion
export function useJobStatusPolling(jobId: string | undefined) {
  const { data, isLoading, error } = useJobStatus(jobId, {
    enabled: !!jobId,
    refetchInterval: 2000,
  })

  const isCompleted = data?.status === 'completed'
  const isFailed = data?.status === 'failed'
  const isProcessing = data?.status === 'processing' || data?.status === 'pending'

  return {
    job: data,
    isLoading,
    error,
    isCompleted,
    isFailed,
    isProcessing,
  }
}

// Hook for managing multiple transcription jobs
export function useTranscriptionJobs() {
  const queryClient = useQueryClient()

  const getJob = (jobId: string) => {
    return queryClient.getQueryData<TranscriptionJob>(transcriptionKeys.job(jobId))
  }

  const getAllJobs = (): TranscriptionJob[] => {
    const queryCache = queryClient.getQueryCache()
    const jobs: TranscriptionJob[] = []

    queryCache
      .findAll({ queryKey: transcriptionKeys.all })
      .forEach((query) => {
        if (query.queryKey.includes('job') && query.state.data) {
          jobs.push(query.state.data as TranscriptionJob)
        }
      })

    return jobs.sort((a, b) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  }

  const clearCompletedJobs = () => {
    const jobs = getAllJobs()
    jobs.forEach((job) => {
      if (job.status === 'completed' || job.status === 'failed') {
        queryClient.removeQueries({ queryKey: transcriptionKeys.job(job.job_id) })
      }
    })
  }

  return {
    getJob,
    getAllJobs,
    clearCompletedJobs,
  }
}