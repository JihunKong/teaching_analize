/**
 * PDF Export Button Component
 * 
 * Main button component for triggering PDF exports with loading states,
 * progress indication, and error handling.
 */

import React, { useState, useCallback } from 'react'
import { Button } from '../ui/button'
import { Progress } from '../ui/progress'
import { AlertCircle, Download, Loader2, FileText, Settings } from 'lucide-react'
import { Alert, AlertDescription } from '../ui/alert'
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
import PDFOptions from './PDFOptions'

export interface PDFExportButtonProps {
  // Content to export
  html: string
  filename: string
  title?: string
  
  // Button appearance
  variant?: 'default' | 'outline' | 'secondary' | 'ghost'
  size?: 'sm' | 'lg'
  className?: string
  
  // Export options
  defaultOptions?: Partial<PDFExportOptions>
  showOptionsDialog?: boolean
  
  // Callbacks
  onExportStart?: () => void
  onExportComplete?: (success: boolean, result?: any) => void
  onExportError?: (error: string) => void
  
  // UI customization
  showProgress?: boolean
  showEstimation?: boolean
  icon?: React.ReactNode
  children?: React.ReactNode
}

const PDFExportButton: React.FC<PDFExportButtonProps> = ({
  html,
  filename,
  title = 'PDF 내보내기',
  variant = 'default',
  size = 'md',
  className = '',
  defaultOptions = {},
  showOptionsDialog = false,
  onExportStart,
  onExportComplete,
  onExportError,
  showProgress = true,
  showEstimation = false,
  icon,
  children
}) => {
  const {
    exportToPDF,
    isExporting,
    currentProgress,
    estimateGenerationTime,
    estimateFileSize,
    validateOptions
  } = usePDFExport()

  const [showOptions, setShowOptions] = useState(false)
  const [exportOptions, setExportOptions] = useState<Partial<PDFExportOptions>>(defaultOptions)
  const [error, setError] = useState<string | null>(null)
  const [estimatedTime, setEstimatedTime] = useState<number>(0)
  const [estimatedSize, setEstimatedSize] = useState<number>(0)

  // Calculate estimates when options change
  React.useEffect(() => {
    if (showEstimation) {
      setEstimatedTime(estimateGenerationTime(html, exportOptions as any))
      setEstimatedSize(estimateFileSize(html, exportOptions as any))
    }
  }, [html, exportOptions, showEstimation, estimateGenerationTime, estimateFileSize])

  const handleExport = useCallback(async () => {
    setError(null)
    
    // Validate options
    const validationErrors = validateOptions(exportOptions as any)
    if (validationErrors.length > 0) {
      setError(validationErrors.join(', '))
      return
    }

    try {
      onExportStart?.()
      
      const result = await exportToPDF(html, filename, exportOptions as any)
      
      if (result.success) {
        onExportComplete?.(true, result)
      } else {
        const errorMsg = result.error || 'PDF 생성에 실패했습니다'
        setError(errorMsg)
        onExportError?.(errorMsg)
        onExportComplete?.(false, result)
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : '예상치 못한 오류가 발생했습니다'
      setError(errorMsg)
      onExportError?.(errorMsg)
      onExportComplete?.(false)
    }
  }, [
    html,
    filename,
    exportOptions,
    exportToPDF,
    validateOptions,
    onExportStart,
    onExportComplete,
    onExportError
  ])

  const handleOptionsClick = useCallback(() => {
    if (showOptionsDialog) {
      setShowOptions(true)
    } else {
      handleExport()
    }
  }, [showOptionsDialog, handleExport])

  const handleOptionsConfirm = useCallback((options: Partial<PDFExportOptions>) => {
    setExportOptions(options)
    setShowOptions(false)
    handleExport()
  }, [handleExport])

  const formatFileSize = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${seconds}초`
    }
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}분 ${remainingSeconds}초`
  }

  const getButtonContent = () => {
    if (isExporting) {
      return (
        <>
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          내보내는 중...
        </>
      )
    }

    if (children) {
      return children
    }

    return (
      <>
        {icon || <Download className="w-4 h-4 mr-2" />}
        {title}
      </>
    )
  }

  return (
    <>
      <div className="space-y-4">
        {/* Main Export Button */}
        <div className="flex items-center space-x-2">
          <Button
            variant={variant}
            size={size as any}
            className={className}
            onClick={handleOptionsClick}
            disabled={isExporting}
          >
            {getButtonContent()}
          </Button>

          {showOptionsDialog && !isExporting && (
            <Button
              variant="outline"
              size={size as any}
              onClick={() => setShowOptions(true)}
              title="PDF 옵션 설정"
            >
              <Settings className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Estimation Display */}
        {showEstimation && !isExporting && (
          <div className="text-sm text-gray-600 space-y-1">
            <div className="flex items-center space-x-4">
              <span>예상 생성 시간: {formatTime(estimatedTime)}</span>
              <span>예상 파일 크기: {formatFileSize(estimatedSize * 1024)}</span>
            </div>
          </div>
        )}

        {/* Progress Indicator */}
        {showProgress && isExporting && currentProgress && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>{currentProgress.message}</span>
              <span>{currentProgress.progress}%</span>
            </div>
            <Progress value={currentProgress.progress} className="w-full" />
            {currentProgress.estimatedTimeRemaining && (
              <div className="text-xs text-gray-500">
                남은 시간: {formatTime(currentProgress.estimatedTimeRemaining)}
              </div>
            )}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>

      {/* Options Dialog */}
      <Dialog open={showOptions} onOpenChange={setShowOptions}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <FileText className="w-5 h-5" />
              <span>PDF 내보내기 옵션</span>
            </DialogTitle>
            <DialogDescription>
              PDF 생성 옵션을 설정하세요. 설정한 옵션은 이번 내보내기에만 적용됩니다.
            </DialogDescription>
          </DialogHeader>

          <PDFOptions
            initialOptions={exportOptions}
            onConfirm={handleOptionsConfirm}
            onCancel={() => setShowOptions(false)}
            showPreview={true}
            showEstimation={true}
            htmlContent={html}
          />
        </DialogContent>
      </Dialog>
    </>
  )
}

export default PDFExportButton