/**
 * PDF Export Hook for AIBOA Platform
 * 
 * Handles PDF generation process with:
 * - Progress tracking
 * - Error handling and retry logic
 * - Download management
 * - Export queue for batch operations
 * - Settings management
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import PDFExportService, {
  PDFExportOptions,
  PDFExportProgress,
  PDFExportResult,
  BatchPDFExportItem,
  BatchPDFExportResult,
  pdfExportUtils,
  DEFAULT_PDF_OPTIONS
} from '../lib/pdf-export'

export interface PDFExportState {
  isExporting: boolean
  progress: PDFExportProgress | null
  queue: PDFExportQueueItem[]
  history: PDFExportHistoryItem[]
  settings: PDFExportSettings
}

export interface PDFExportQueueItem {
  id: string
  title: string
  html: string
  filename: string
  options: PDFExportOptions
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  createdAt: string
  startedAt?: string
  completedAt?: string
  result?: PDFExportResult
  error?: string
  retryCount: number
}

export interface PDFExportHistoryItem {
  id: string
  title: string
  filename: string
  fileSize: number
  pages: number
  generationTime: number
  exportedAt: string
  options: PDFExportOptions
  downloadUrl?: string
}

export interface PDFExportSettings {
  defaultOptions: PDFExportOptions
  autoDownload: boolean
  keepHistory: boolean
  maxHistoryItems: number
  maxRetries: number
  retryDelay: number // seconds
  enablePreview: boolean
  showProgressDialog: boolean
}

export interface UsePDFExportReturn {
  // State
  exportState: PDFExportState
  isExporting: boolean
  currentProgress: PDFExportProgress | null
  queueCount: number
  historyCount: number

  // Single export
  exportToPDF: (
    html: string,
    filename: string,
    options?: Partial<PDFExportOptions>
  ) => Promise<PDFExportResult>

  // Batch export
  batchExportToPDF: (
    items: BatchPDFExportItem[],
    options?: Partial<PDFExportOptions>
  ) => Promise<BatchPDFExportResult>

  // Preview
  createPreview: (
    html: string,
    options?: Partial<PDFExportOptions>
  ) => Promise<string>

  // Queue management
  addToQueue: (
    html: string,
    title: string,
    filename: string,
    options?: Partial<PDFExportOptions>
  ) => string
  removeFromQueue: (id: string) => void
  processQueue: () => Promise<void>
  clearQueue: () => void
  retryQueueItem: (id: string) => Promise<void>

  // History management
  getHistory: () => PDFExportHistoryItem[]
  clearHistory: () => void
  deleteHistoryItem: (id: string) => void
  downloadFromHistory: (id: string) => void

  // Settings
  updateSettings: (settings: Partial<PDFExportSettings>) => void
  resetSettings: () => void

  // Utilities
  estimateGenerationTime: (html: string, options?: Partial<PDFExportOptions>) => number
  estimateFileSize: (html: string, options?: Partial<PDFExportOptions>) => number
  validateOptions: (options: Partial<PDFExportOptions>) => string[]
  cancelExport: () => void
}

const STORAGE_KEYS = {
  HISTORY: 'aiboa_pdf_export_history',
  SETTINGS: 'aiboa_pdf_export_settings',
  QUEUE: 'aiboa_pdf_export_queue'
}

const DEFAULT_SETTINGS: PDFExportSettings = {
  defaultOptions: DEFAULT_PDF_OPTIONS,
  autoDownload: true,
  keepHistory: true,
  maxHistoryItems: 100,
  maxRetries: 3,
  retryDelay: 5,
  enablePreview: true,
  showProgressDialog: true
}

export const usePDFExport = (): UsePDFExportReturn => {
  const queryClient = useQueryClient()
  const serviceRef = useRef<PDFExportService | null>(null)
  
  const [exportState, setExportState] = useState<PDFExportState>({
    isExporting: false,
    progress: null,
    queue: [],
    history: [],
    settings: DEFAULT_SETTINGS
  })

  // Load settings and history on mount
  const { data: settings } = useQuery({
    queryKey: ['pdf-export-settings'],
    queryFn: () => {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.SETTINGS)
        return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS
      } catch {
        return DEFAULT_SETTINGS
      }
    },
    staleTime: Infinity
  })

  const { data: history = [] } = useQuery({
    queryKey: ['pdf-export-history'],
    queryFn: () => {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.HISTORY)
        return saved ? JSON.parse(saved) : []
      } catch {
        return []
      }
    },
    staleTime: 60 * 1000 // 1 minute
  })

  const { data: queue = [] } = useQuery({
    queryKey: ['pdf-export-queue'],
    queryFn: () => {
      try {
        const saved = localStorage.getItem(STORAGE_KEYS.QUEUE)
        return saved ? JSON.parse(saved) : []
      } catch {
        return []
      }
    },
    staleTime: 0
  })

  // Update state when data changes
  useEffect(() => {
    setExportState(prev => ({
      ...prev,
      settings: settings || DEFAULT_SETTINGS,
      history: history || [],
      queue: queue || []
    }))
  }, [settings, history, queue])

  // Progress callback for PDF service
  const handleProgress = useCallback((progress: PDFExportProgress) => {
    setExportState(prev => ({
      ...prev,
      progress,
      isExporting: progress.stage !== 'complete' && progress.stage !== 'error'
    }))
  }, [])

  // Get or create PDF service
  const getPDFService = useCallback(() => {
    if (!serviceRef.current) {
      serviceRef.current = new PDFExportService(handleProgress)
    }
    return serviceRef.current
  }, [handleProgress])

  // Save data to storage
  const saveToStorage = useCallback((key: keyof typeof STORAGE_KEYS, data: any) => {
    try {
      localStorage.setItem(STORAGE_KEYS[key], JSON.stringify(data))
      queryClient.setQueryData([`pdf-export-${key.toLowerCase()}`], data)
    } catch (error) {
      console.error(`Failed to save ${key}:`, error)
    }
  }, [queryClient])

  // Add to history
  const addToHistory = useCallback((
    result: PDFExportResult,
    title: string,
    options: PDFExportOptions
  ) => {
    if (!exportState.settings.keepHistory) return

    const historyItem: PDFExportHistoryItem = {
      id: `history_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title,
      filename: result.filename,
      fileSize: result.size,
      pages: result.pages,
      generationTime: result.generationTime,
      exportedAt: new Date().toISOString(),
      options,
      downloadUrl: result.url
    }

    const updatedHistory = [historyItem, ...exportState.history]
      .slice(0, exportState.settings.maxHistoryItems)

    saveToStorage('HISTORY', updatedHistory)
  }, [exportState.history, exportState.settings, saveToStorage])

  // Single PDF export
  const exportToPDF = useCallback(async (
    html: string,
    filename: string,
    options: Partial<PDFExportOptions> = {}
  ): Promise<PDFExportResult> => {
    const mergedOptions = { ...exportState.settings.defaultOptions, ...options }
    const service = getPDFService()

    setExportState(prev => ({ ...prev, isExporting: true }))

    try {
      const result = await service.exportToPDF(html, filename, mergedOptions)
      
      if (result.success) {
        addToHistory(result, filename.replace('.pdf', ''), mergedOptions)
      }

      return result
    } finally {
      setExportState(prev => ({ ...prev, isExporting: false, progress: null }))
    }
  }, [exportState.settings.defaultOptions, getPDFService, addToHistory])

  // Batch PDF export
  const batchExportToPDF = useCallback(async (
    items: BatchPDFExportItem[],
    options: Partial<PDFExportOptions> = {}
  ): Promise<BatchPDFExportResult> => {
    const mergedOptions = { ...exportState.settings.defaultOptions, ...options }
    const service = getPDFService()

    setExportState(prev => ({ ...prev, isExporting: true }))

    try {
      const result = await service.batchExportToPDF(items, mergedOptions)
      
      // Add successful exports to history
      result.results.forEach((exportResult, index) => {
        if (exportResult.success) {
          addToHistory(exportResult, items[index].title, mergedOptions)
        }
      })

      return result
    } finally {
      setExportState(prev => ({ ...prev, isExporting: false, progress: null }))
    }
  }, [exportState.settings.defaultOptions, getPDFService, addToHistory])

  // Create preview
  const createPreview = useCallback(async (
    html: string,
    options: Partial<PDFExportOptions> = {}
  ): Promise<string> => {
    if (!exportState.settings.enablePreview) {
      throw new Error('미리보기가 비활성화되어 있습니다')
    }

    const mergedOptions = { ...exportState.settings.defaultOptions, ...options }
    const service = getPDFService()

    return await service.createPDFPreview(html, mergedOptions)
  }, [exportState.settings, getPDFService])

  // Queue management
  const addToQueue = useCallback((
    html: string,
    title: string,
    filename: string,
    options: Partial<PDFExportOptions> = {}
  ): string => {
    const queueItem: PDFExportQueueItem = {
      id: `queue_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      title,
      html,
      filename,
      options: { ...exportState.settings.defaultOptions, ...options },
      status: 'pending',
      createdAt: new Date().toISOString(),
      retryCount: 0
    }

    const updatedQueue = [...exportState.queue, queueItem]
    saveToStorage('QUEUE', updatedQueue)

    return queueItem.id
  }, [exportState.queue, exportState.settings.defaultOptions, saveToStorage])

  const removeFromQueue = useCallback((id: string) => {
    const updatedQueue = exportState.queue.filter(item => item.id !== id)
    saveToStorage('QUEUE', updatedQueue)
  }, [exportState.queue, saveToStorage])

  const processQueue = useCallback(async () => {
    const pendingItems = exportState.queue.filter(item => item.status === 'pending')
    if (pendingItems.length === 0) return

    for (const item of pendingItems) {
      try {
        // Update status to processing
        const updatedQueue = exportState.queue.map(qItem =>
          qItem.id === item.id
            ? { ...qItem, status: 'processing' as const, startedAt: new Date().toISOString() }
            : qItem
        )
        saveToStorage('QUEUE', updatedQueue)

        // Export PDF
        const result = await exportToPDF(item.html, item.filename, item.options)

        // Update with result
        const finalQueue = exportState.queue.map(qItem =>
          qItem.id === item.id
            ? {
                ...qItem,
                status: result.success ? 'completed' as const : 'failed' as const,
                completedAt: new Date().toISOString(),
                result,
                error: result.error
              }
            : qItem
        )
        saveToStorage('QUEUE', finalQueue)

      } catch (error) {
        // Handle error
        const errorQueue = exportState.queue.map(qItem =>
          qItem.id === item.id
            ? {
                ...qItem,
                status: 'failed' as const,
                completedAt: new Date().toISOString(),
                error: error instanceof Error ? error.message : '알 수 없는 오류'
              }
            : qItem
        )
        saveToStorage('QUEUE', errorQueue)
      }
    }
  }, [exportState.queue, exportToPDF, saveToStorage])

  const clearQueue = useCallback(() => {
    saveToStorage('QUEUE', [])
  }, [saveToStorage])

  const retryQueueItem = useCallback(async (id: string) => {
    const item = exportState.queue.find(qItem => qItem.id === id)
    if (!item || item.retryCount >= exportState.settings.maxRetries) {
      return
    }

    // Reset item status
    const updatedQueue = exportState.queue.map(qItem =>
      qItem.id === id
        ? {
            ...qItem,
            status: 'pending' as const,
            retryCount: qItem.retryCount + 1,
            error: undefined
          }
        : qItem
    )
    saveToStorage('QUEUE', updatedQueue)

    // Wait before retry
    setTimeout(() => {
      processQueue()
    }, exportState.settings.retryDelay * 1000)
  }, [exportState.queue, exportState.settings, saveToStorage, processQueue])

  // History management
  const getHistory = useCallback(() => {
    return exportState.history
  }, [exportState.history])

  const clearHistory = useCallback(() => {
    saveToStorage('HISTORY', [])
  }, [saveToStorage])

  const deleteHistoryItem = useCallback((id: string) => {
    const updatedHistory = exportState.history.filter(item => item.id !== id)
    saveToStorage('HISTORY', updatedHistory)
  }, [exportState.history, saveToStorage])

  const downloadFromHistory = useCallback((id: string) => {
    const item = exportState.history.find(historyItem => historyItem.id === id)
    if (item && item.downloadUrl) {
      const a = document.createElement('a')
      a.href = item.downloadUrl
      a.download = item.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }, [exportState.history])

  // Settings management
  const updateSettings = useCallback((newSettings: Partial<PDFExportSettings>) => {
    const updatedSettings = { ...exportState.settings, ...newSettings }
    saveToStorage('SETTINGS', updatedSettings)
  }, [exportState.settings, saveToStorage])

  const resetSettings = useCallback(() => {
    saveToStorage('SETTINGS', DEFAULT_SETTINGS)
  }, [saveToStorage])

  // Utilities
  const estimateGenerationTime = useCallback((
    html: string,
    options: Partial<PDFExportOptions> = {}
  ): number => {
    const service = getPDFService()
    return service.estimateGenerationTime(html, options)
  }, [getPDFService])

  const estimateFileSize = useCallback((
    html: string,
    options: Partial<PDFExportOptions> = {}
  ): number => {
    return pdfExportUtils.estimateFileSize(html, options)
  }, [])

  const validateOptions = useCallback((options: Partial<PDFExportOptions>): string[] => {
    return pdfExportUtils.validateOptions(options)
  }, [])

  const cancelExport = useCallback(() => {
    const service = getPDFService()
    service.cancelExport()
    setExportState(prev => ({ ...prev, isExporting: false, progress: null }))
  }, [getPDFService])

  return {
    // State
    exportState,
    isExporting: exportState.isExporting,
    currentProgress: exportState.progress,
    queueCount: exportState.queue.length,
    historyCount: exportState.history.length,

    // Single export
    exportToPDF,

    // Batch export
    batchExportToPDF,

    // Preview
    createPreview,

    // Queue management
    addToQueue,
    removeFromQueue,
    processQueue,
    clearQueue,
    retryQueueItem,

    // History management
    getHistory,
    clearHistory,
    deleteHistoryItem,
    downloadFromHistory,

    // Settings
    updateSettings,
    resetSettings,

    // Utilities
    estimateGenerationTime,
    estimateFileSize,
    validateOptions,
    cancelExport
  }
}

export default usePDFExport