// Base API response structure
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
  status: number
}

// Pagination structure
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Common status types
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type ServiceHealth = 'healthy' | 'unhealthy' | 'degraded'

// File upload types
export interface FileUpload {
  file: File
  language?: string
  format?: string
}

// Job progress information
export interface JobProgress {
  current: number
  total: number
  percentage: number
  stage: string
  eta?: number // estimated time remaining in seconds
}