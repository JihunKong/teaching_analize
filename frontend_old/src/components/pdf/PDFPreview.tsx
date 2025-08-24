/**
 * PDF Preview Component
 * 
 * Provides PDF preview functionality before export with:
 * - Live preview of PDF rendering
 * - Zoom controls
 * - Page navigation
 * - Options comparison
 * - Quality assessment
 */

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { Alert, AlertDescription } from '../ui/alert'
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  Download,
  Loader2,
  AlertCircle,
  Eye,
  RefreshCw,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  FileText
} from 'lucide-react'
import usePDFExport from '../../hooks/usePDFExport'

interface PDFExportOptions {
  format: 'A4' | 'A3' | 'Letter' | 'Legal'
  quality: 'low' | 'medium' | 'high' | 'ultra'
  dpi: number
  includeCharts: boolean
  includeMetadata: boolean
  watermark?: { text: string; opacity: number }
}

export interface PDFPreviewProps {
  html: string
  options: Partial<PDFExportOptions>
  filename: string
  onExport?: () => void
  onOptionsChange?: () => void
  className?: string
  showControls?: boolean
  showInfo?: boolean
  autoGenerate?: boolean
}

const PDFPreview: React.FC<PDFPreviewProps> = ({
  html,
  options,
  filename,
  onExport,
  onOptionsChange,
  className = '',
  showControls = true,
  showInfo = true,
  autoGenerate = true
}) => {
  const {
    createPreview,
    estimateGenerationTime,
    estimateFileSize,
    exportToPDF
  } = usePDFExport()

  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [zoom, setZoom] = useState(100)
  const [rotation, setRotation] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [isExporting, setIsExporting] = useState(false)

  const previewRef = useRef<HTMLIFrameElement>(null)
  const regenerateTimeoutRef = useRef<NodeJS.Timeout>()

  // Auto-generate preview when options change
  useEffect(() => {
    if (autoGenerate && html) {
      // Debounce regeneration
      if (regenerateTimeoutRef.current) {
        clearTimeout(regenerateTimeoutRef.current)
      }
      
      regenerateTimeoutRef.current = setTimeout(() => {
        generatePreview()
      }, 1000)
    }

    return () => {
      if (regenerateTimeoutRef.current) {
        clearTimeout(regenerateTimeoutRef.current)
      }
    }
  }, [html, options, autoGenerate])

  const generatePreview = useCallback(async () => {
    if (!html) {
      setError('미리보기할 내용이 없습니다.')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const url = await createPreview(html, options as any)
      setPreviewUrl(url)
      setCurrentPage(1)
      
      // Estimate page count (simplified)
      const estimatedSize = estimateFileSize(html, options as any)
      const estimatedPages = Math.max(1, Math.ceil(estimatedSize / 50))
      setTotalPages(estimatedPages)
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '미리보기 생성에 실패했습니다.'
      setError(errorMessage)
      console.error('PDF 미리보기 오류:', err)
    } finally {
      setIsGenerating(false)
    }
  }, [html, options, createPreview, estimateFileSize])

  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(200, prev + 25))
  }, [])

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(50, prev - 25))
  }, [])

  const handleRotate = useCallback(() => {
    setRotation(prev => (prev + 90) % 360)
  }, [])

  const handleExport = useCallback(async () => {
    if (!html) return

    setIsExporting(true)
    try {
      await exportToPDF(html, filename, options as any)
      onExport?.()
    } catch (err) {
      console.error('PDF 내보내기 오류:', err)
    } finally {
      setIsExporting(false)
    }
  }, [html, filename, options, exportToPDF, onExport])

  const handleFullscreen = useCallback(() => {
    if (previewUrl) {
      window.open(previewUrl, '_blank', 'width=1200,height=800,scrollbars=yes')
    }
  }, [previewUrl])

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

  const getPreviewStyle = (): React.CSSProperties => ({
    transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
    transformOrigin: 'center center',
    transition: 'transform 0.3s ease'
  })

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Eye className="w-5 h-5" />
          <h3 className="text-lg font-medium">PDF 미리보기</h3>
          {isGenerating && (
            <Badge variant="secondary" className="ml-2">
              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
              생성 중
            </Badge>
          )}
        </div>

        {showControls && (
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={generatePreview}
              disabled={isGenerating || !html}
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              새로고침
            </Button>
            
            {onOptionsChange && (
              <Button
                variant="outline"
                size="sm"
                onClick={onOptionsChange}
              >
                옵션 변경
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Preview Info */}
      {showInfo && html && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {formatTime(estimateGenerationTime(html, options as any))}
                </div>
                <div className="text-sm text-gray-600">예상 생성시간</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {formatFileSize(estimateFileSize(html, options as any))}
                </div>
                <div className="text-sm text-gray-600">예상 파일크기</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {totalPages}
                </div>
                <div className="text-sm text-gray-600">예상 페이지</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {options.quality || 'medium'}
                </div>
                <div className="text-sm text-gray-600">품질 설정</div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Preview Container */}
      <Card className="overflow-hidden">
        {showControls && (
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleZoomOut}
                  disabled={zoom <= 50}
                >
                  <ZoomOut className="w-4 h-4" />
                </Button>
                
                <span className="text-sm min-w-[60px] text-center">
                  {zoom}%
                </span>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleZoomIn}
                  disabled={zoom >= 200}
                >
                  <ZoomIn className="w-4 h-4" />
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRotate}
                >
                  <RotateCw className="w-4 h-4" />
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleFullscreen}
                  disabled={!previewUrl}
                >
                  <Maximize2 className="w-4 h-4" />
                </Button>
              </div>

              <div className="flex items-center space-x-2">
                {totalPages > 1 && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                      disabled={currentPage <= 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    
                    <span className="text-sm">
                      {currentPage} / {totalPages}
                    </span>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                      disabled={currentPage >= totalPages}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </>
                )}

                <Button
                  onClick={handleExport}
                  disabled={isExporting || !previewUrl}
                  size="sm"
                >
                  {isExporting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                      내보내는 중...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-1" />
                      PDF 내보내기
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardHeader>
        )}

        <CardContent className="p-0">
          <div className="relative bg-gray-100 min-h-[400px] flex items-center justify-center overflow-hidden">
            {isGenerating ? (
              <div className="text-center space-y-4">
                <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
                <div className="text-sm text-gray-600">PDF 미리보기 생성 중...</div>
                <Progress value={50} className="w-48" />
              </div>
            ) : previewUrl ? (
              <div className="w-full h-full flex items-center justify-center">
                <iframe
                  ref={previewRef}
                  src={previewUrl}
                  className="border-0 bg-white shadow-lg"
                  style={{
                    width: '210mm',
                    height: '297mm',
                    maxWidth: '100%',
                    maxHeight: '80vh',
                    ...getPreviewStyle()
                  }}
                  title="PDF Preview"
                />
              </div>
            ) : (
              <div className="text-center space-y-4">
                <FileText className="w-12 h-12 mx-auto text-gray-400" />
                <div className="text-gray-600">
                  {html ? '새로고침 버튼을 클릭하여 미리보기를 생성하세요.' : '미리보기할 내용을 선택하세요.'}
                </div>
                {html && (
                  <Button onClick={generatePreview} disabled={isGenerating}>
                    <Eye className="w-4 h-4 mr-2" />
                    미리보기 생성
                  </Button>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      {previewUrl && showControls && (
        <div className="flex justify-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => window.open(previewUrl, '_blank')}
          >
            새 창에서 보기
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              const link = document.createElement('a')
              link.href = previewUrl
              link.download = filename.replace('.pdf', '_preview.pdf')
              link.click()
            }}
          >
            미리보기 다운로드
          </Button>
        </div>
      )}
    </div>
  )
}

export default PDFPreview