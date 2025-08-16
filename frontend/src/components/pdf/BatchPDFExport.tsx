/**
 * Batch PDF Export Component
 * 
 * Handles batch PDF generation for multiple reports with:
 * - Queue management
 * - Progress tracking per item
 * - Error handling and retry logic
 * - Combined PDF option
 * - Export history
 */

import React, { useState, useCallback, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { Checkbox } from '../ui/checkbox'
import { Alert, AlertDescription } from '../ui/alert'
import {
  Download,
  FileText,
  Loader2,
  CheckCircle2,
  XCircle,
  RotateCw,
  Trash2,
  Plus,
  Settings,
  Clock,
  Package
} from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog'
import usePDFExport from '../../hooks/usePDFExport'

interface PDFExportOptions {
  format: 'A4' | 'A3' | 'Letter' | 'Legal'
  quality: 'low' | 'medium' | 'high' | 'ultra'
  dpi: number
  includeCharts: boolean
  includeMetadata: boolean
  watermark?: {
    text: string
    opacity: number
  }
}

interface BatchPDFExportItem {
  id: string
  title: string
  html: string
  filename?: string
}
import PDFOptions from './PDFOptions'

export interface BatchPDFExportProps {
  items: BatchPDFExportItem[]
  onItemsChange?: (items: BatchPDFExportItem[]) => void
  onExportComplete?: (results: any) => void
  defaultOptions?: Partial<PDFExportOptions>
  showCombinedOption?: boolean
  className?: string
}

interface BatchQueueItem extends BatchPDFExportItem {
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress?: number
  error?: string
  result?: any
  selected: boolean
}

const BatchPDFExport: React.FC<BatchPDFExportProps> = ({
  items,
  onItemsChange,
  onExportComplete,
  defaultOptions = {},
  showCombinedOption = true,
  className = ''
}) => {
  const {
    batchExportToPDF,
    addToQueue,
    processQueue,
    queueCount,
    isExporting,
    currentProgress,
    estimateGenerationTime,
    estimateFileSize
  } = usePDFExport()

  const [queueItems, setQueueItems] = useState<BatchQueueItem[]>([])
  const [showOptions, setShowOptions] = useState(false)
  const [batchOptions, setBatchOptions] = useState<Partial<PDFExportOptions>>(defaultOptions)
  const [createCombinedPDF, setCreateCombinedPDF] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [overallProgress, setOverallProgress] = useState(0)
  const [results, setResults] = useState<any>(null)

  // Initialize queue items
  useEffect(() => {
    const newQueueItems: BatchQueueItem[] = items.map((item, index) => ({
      ...item,
      status: 'pending',
      selected: true
    }))
    setQueueItems(newQueueItems)
  }, [items])

  const selectedItems = queueItems.filter(item => item.selected)
  const completedItems = queueItems.filter(item => item.status === 'completed')
  const failedItems = queueItems.filter(item => item.status === 'failed')

  const totalEstimatedTime = selectedItems.reduce((total, item) => {
    return total + estimateGenerationTime(item.html, batchOptions as any)
  }, 0)

  const totalEstimatedSize = selectedItems.reduce((total, item) => {
    return total + estimateFileSize(item.html, batchOptions as any)
  }, 0)

  const handleItemToggle = useCallback((id: string, selected: boolean) => {
    setQueueItems(prev => prev.map(item =>
      item.id === id ? { ...item, selected } : item
    ))
  }, [])

  const handleSelectAll = useCallback((selected: boolean) => {
    setQueueItems(prev => prev.map(item => ({ ...item, selected })))
  }, [])

  const handleRemoveItem = useCallback((id: string) => {
    const updatedItems = queueItems.filter(item => item.id !== id)
    setQueueItems(updatedItems)
    
    if (onItemsChange) {
      onItemsChange(updatedItems.map(({ status, progress, error, result, selected, ...item }) => item))
    }
  }, [queueItems, onItemsChange])

  const handleRetryItem = useCallback((id: string) => {
    setQueueItems(prev => prev.map(item =>
      item.id === id ? { ...item, status: 'pending', error: undefined } : item
    ))
  }, [])

  const handleStartBatchExport = useCallback(async () => {
    if (selectedItems.length === 0) return

    setIsProcessing(true)
    setOverallProgress(0)
    setResults(null)

    try {
      // Update all selected items to processing
      setQueueItems(prev => prev.map(item =>
        item.selected ? { ...item, status: 'processing', progress: 0 } : item
      ))

      const batchItems: BatchPDFExportItem[] = selectedItems.map(item => ({
        id: item.id,
        title: item.title,
        html: item.html,
        options: batchOptions
      }))

      const result = await batchExportToPDF(batchItems, batchOptions as any)

      // Update items with results
      setQueueItems(prev => prev.map(item => {
        if (!item.selected) return item

        const itemResult = result.results.find(r => r.filename.includes(item.title))
        return {
          ...item,
          status: itemResult?.success ? 'completed' : 'failed',
          progress: 100,
          error: itemResult?.error,
          result: itemResult
        }
      }))

      setResults(result)
      setOverallProgress(100)
      onExportComplete?.(result)

    } catch (error) {
      console.error('Batch export failed:', error)
      setQueueItems(prev => prev.map(item =>
        item.selected ? { ...item, status: 'failed', error: 'Batch export failed' } : item
      ))
    } finally {
      setIsProcessing(false)
    }
  }, [selectedItems, batchOptions, batchExportToPDF, onExportComplete])

  const handleOptionsConfirm = useCallback((options: Partial<PDFExportOptions>) => {
    setBatchOptions(options)
    setShowOptions(false)
  }, [])

  const formatFileSize = (kb: number): string => {
    if (kb < 1024) return `${kb} KB`
    return `${(kb / 1024).toFixed(1)} MB`
  }

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}초`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}분 ${remainingSeconds}초`
  }

  const getStatusIcon = (status: BatchQueueItem['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-gray-500" />
      case 'processing':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return null
    }
  }

  const getStatusBadge = (status: BatchQueueItem['status']) => {
    switch (status) {
      case 'pending':
        return <Badge variant="secondary">대기 중</Badge>
      case 'processing':
        return <Badge variant="default">처리 중</Badge>
      case 'completed':
        return <Badge variant="secondary">완료</Badge>
      case 'failed':
        return <Badge variant="destructive">실패</Badge>
      default:
        return null
    }
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">일괄 PDF 내보내기</h3>
          <p className="text-sm text-gray-600">
            여러 보고서를 한 번에 PDF로 내보냅니다.
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={() => setShowOptions(true)}
            disabled={isProcessing}
          >
            <Settings className="w-4 h-4 mr-2" />
            옵션 설정
          </Button>
          
          <Button
            onClick={handleStartBatchExport}
            disabled={selectedItems.length === 0 || isProcessing}
          >
            <Download className="w-4 h-4 mr-2" />
            {isProcessing ? '내보내는 중...' : `내보내기 (${selectedItems.length}개)`}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{queueItems.length}</div>
              <div className="text-sm text-gray-600">총 항목</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{selectedItems.length}</div>
              <div className="text-sm text-gray-600">선택된 항목</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {formatTime(totalEstimatedTime)}
              </div>
              <div className="text-sm text-gray-600">예상 시간</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {formatFileSize(totalEstimatedSize)}
              </div>
              <div className="text-sm text-gray-600">예상 크기</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Batch Options */}
      {showCombinedOption && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">추가 옵션</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="createCombinedPDF"
                checked={createCombinedPDF}
                onCheckedChange={(checked) => setCreateCombinedPDF(checked as boolean)}
              />
              <label htmlFor="createCombinedPDF" className="text-sm">
                모든 보고서를 하나의 PDF로 결합
              </label>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overall Progress */}
      {isProcessing && (
        <Card>
          <CardContent className="pt-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>전체 진행률</span>
                <span>{overallProgress}%</span>
              </div>
              <Progress value={overallProgress} className="w-full" />
              {currentProgress && (
                <div className="text-xs text-gray-500">{currentProgress.message}</div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Summary */}
      {results && (
        <Alert>
          <Package className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              <div>✅ 성공: {completedItems.length}개</div>
              {failedItems.length > 0 && <div>❌ 실패: {failedItems.length}개</div>}
              <div>📁 총 크기: {formatFileSize(results.totalSize / 1024)}</div>
              <div>⏱️ 총 시간: {formatTime(results.totalTime)}</div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Queue Items */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">내보낼 항목</CardTitle>
            <div className="flex items-center space-x-2">
              <Checkbox
                checked={selectedItems.length === queueItems.length && queueItems.length > 0}
                onCheckedChange={handleSelectAll}
              />
              <span className="text-sm">전체 선택</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {queueItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              내보낼 항목이 없습니다.
            </div>
          ) : (
            <div className="space-y-2">
              {queueItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50"
                >
                  <Checkbox
                    checked={item.selected}
                    onCheckedChange={(checked) => handleItemToggle(item.id, checked as boolean)}
                    disabled={isProcessing}
                  />

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <FileText className="w-4 h-4 flex-shrink-0" />
                      <span className="font-medium truncate">{item.title}</span>
                      {getStatusIcon(item.status)}
                      {getStatusBadge(item.status)}
                    </div>
                    
                    {item.status === 'processing' && item.progress !== undefined && (
                      <div className="mt-2">
                        <Progress value={item.progress} className="w-full h-2" />
                      </div>
                    )}
                    
                    {item.error && (
                      <div className="mt-1 text-xs text-red-600">{item.error}</div>
                    )}
                  </div>

                  <div className="flex items-center space-x-1">
                    {item.status === 'failed' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRetryItem(item.id)}
                        disabled={isProcessing}
                      >
                        <RotateCw className="w-4 h-4" />
                      </Button>
                    )}
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveItem(item.id)}
                      disabled={isProcessing}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Options Dialog */}
      <Dialog open={showOptions} onOpenChange={setShowOptions}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>일괄 내보내기 옵션</DialogTitle>
            <DialogDescription>
              모든 선택된 항목에 적용될 기본 PDF 옵션을 설정하세요.
              개별 항목의 옵션이 있는 경우 해당 옵션이 우선 적용됩니다.
            </DialogDescription>
          </DialogHeader>

          <PDFOptions
            initialOptions={batchOptions}
            onConfirm={handleOptionsConfirm}
            onCancel={() => setShowOptions(false)}
            showPreview={false}
            showEstimation={false}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default BatchPDFExport