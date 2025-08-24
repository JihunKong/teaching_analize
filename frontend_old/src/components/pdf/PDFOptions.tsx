/**
 * PDF Options Component
 * 
 * Comprehensive options panel for PDF export configuration including:
 * - Format and quality settings
 * - Layout and margin configuration
 * - Content options (headers, footers, watermarks)
 * - Korean font support
 * - Preview and estimation
 */

import React, { useState, useEffect, useCallback } from 'react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Checkbox } from '../ui/checkbox'
import { Slider } from '../ui/slider'
import { Badge } from '../ui/badge'
import { 
  FileText, 
  Layout, 
  Palette, 
  Settings, 
  Eye, 
  Save,
  RotateCcw,
  Download,
  Info,
  Zap
} from 'lucide-react'
import { Alert, AlertDescription } from '../ui/alert'
import usePDFExport from '../../hooks/usePDFExport'

interface PDFExportOptions {
  format: 'A4' | 'A3' | 'Letter' | 'Legal'
  quality: 'low' | 'medium' | 'high' | 'ultra'
  dpi: number
  includeCharts: boolean
  includeMetadata: boolean
  watermark?: { text: string; opacity: number }
}
import { DEFAULT_PDF_OPTIONS, pdfExportUtils } from '../../lib/pdf-export'

export interface PDFOptionsProps {
  initialOptions?: Partial<PDFExportOptions>
  onConfirm: (options: Partial<PDFExportOptions>) => void
  onCancel: () => void
  showPreview?: boolean
  showEstimation?: boolean
  htmlContent?: string
  className?: string
}

const PDFOptions: React.FC<PDFOptionsProps> = ({
  initialOptions = {},
  onConfirm,
  onCancel,
  showPreview = false,
  showEstimation = false,
  htmlContent = '',
  className = ''
}) => {
  const {
    createPreview,
    estimateGenerationTime,
    estimateFileSize,
    validateOptions
  } = usePDFExport()

  const [options, setOptions] = useState<any>({
    ...DEFAULT_PDF_OPTIONS,
    ...initialOptions
  })

  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false)
  const [estimatedTime, setEstimatedTime] = useState(0)
  const [estimatedSize, setEstimatedSize] = useState(0)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  // Validate options and update estimates
  useEffect(() => {
    const errors = validateOptions(options)
    setValidationErrors(errors)

    if (htmlContent && showEstimation) {
      setEstimatedTime(estimateGenerationTime(htmlContent, options))
      setEstimatedSize(estimateFileSize(htmlContent, options))
    }
  }, [options, htmlContent, showEstimation, validateOptions, estimateGenerationTime, estimateFileSize])

  const updateOption = useCallback(<K extends keyof PDFExportOptions>(
    key: K,
    value: PDFExportOptions[K]
  ) => {
    setOptions((prev: any) => ({ ...prev, [key]: value }))
  }, [])

  const updateMargin = useCallback((side: string, value: number) => {
    setOptions((prev: any) => ({
      ...prev,
      margin: { ...prev.margin, [side]: value }
    }))
  }, [])

  const handleGeneratePreview = useCallback(async () => {
    if (!htmlContent || !showPreview) return

    setIsGeneratingPreview(true)
    try {
      const url = await createPreview(htmlContent, options)
      setPreviewUrl(url)
    } catch (error) {
      console.error('미리보기 생성 실패:', error)
    } finally {
      setIsGeneratingPreview(false)
    }
  }, [htmlContent, options, showPreview, createPreview])

  const handleReset = useCallback(() => {
    setOptions({ ...DEFAULT_PDF_OPTIONS, ...initialOptions })
    setPreviewUrl(null)
  }, [initialOptions])

  const handleConfirm = useCallback(() => {
    if (validationErrors.length === 0) {
      onConfirm(options)
    }
  }, [options, validationErrors, onConfirm])

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

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Quick Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">빠른 설정</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
              onClick={() => setOptions({ ...DEFAULT_PDF_OPTIONS, ...pdfExportUtils.getReportTypeOptions('comprehensive') })}
            >
              <FileText className="w-4 h-4 mr-2" />
              종합 보고서
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
              onClick={() => setOptions({ ...DEFAULT_PDF_OPTIONS, ...pdfExportUtils.getReportTypeOptions('summary') })}
            >
              <Zap className="w-4 h-4 mr-2" />
              요약 보고서
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
              onClick={() => setOptions({ ...DEFAULT_PDF_OPTIONS, ...pdfExportUtils.getReportTypeOptions('actionPlan') })}
            >
              <Settings className="w-4 h-4 mr-2" />
              실행 계획서
            </Button>
          </CardContent>
        </Card>

        {showEstimation && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">예상 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>생성 시간:</span>
                <Badge variant="secondary">{formatTime(estimatedTime)}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>파일 크기:</span>
                <Badge variant="secondary">{formatFileSize(estimatedSize)}</Badge>
              </div>
              <div className="flex justify-between text-sm">
                <span>품질:</span>
                <Badge variant="outline">{options.quality}</Badge>
              </div>
            </CardContent>
          </Card>
        )}

        {showPreview && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">미리보기</CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={handleGeneratePreview}
                disabled={isGeneratingPreview || !htmlContent}
              >
                <Eye className="w-4 h-4 mr-2" />
                {isGeneratingPreview ? '생성 중...' : '미리보기'}
              </Button>
              {previewUrl && (
                <div className="mt-2">
                  <a
                    href={previewUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    새 창에서 보기
                  </a>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <Alert variant="destructive">
          <Info className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-1">
              {validationErrors.map((error, index) => (
                <div key={index}>• {error}</div>
              ))}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Detailed Options */}
      <Tabs defaultValue="format" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="format" className="flex items-center space-x-1">
            <Layout className="w-4 h-4" />
            <span>형식</span>
          </TabsTrigger>
          <TabsTrigger value="content" className="flex items-center space-x-1">
            <FileText className="w-4 h-4" />
            <span>내용</span>
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center space-x-1">
            <Palette className="w-4 h-4" />
            <span>외관</span>
          </TabsTrigger>
          <TabsTrigger value="advanced" className="flex items-center space-x-1">
            <Settings className="w-4 h-4" />
            <span>고급</span>
          </TabsTrigger>
        </TabsList>

        {/* Format Tab */}
        <TabsContent value="format" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="format">페이지 형식</Label>
              <Select
                value={options.format}
                onValueChange={(value) => updateOption('format', value as PDFExportOptions['format'])}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="A4">A4 (210×297mm)</SelectItem>
                  <SelectItem value="Letter">Letter (216×279mm)</SelectItem>
                  <SelectItem value="A3">A3 (297×420mm)</SelectItem>
                  <SelectItem value="Legal">Legal (216×356mm)</SelectItem>
                  <SelectItem value="Custom">사용자 정의</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="orientation">방향</Label>
              <Select
                value={options.orientation || 'portrait'}
                onValueChange={(value) => setOptions((prev: any) => ({ ...prev, orientation: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="portrait">세로</SelectItem>
                  <SelectItem value="landscape">가로</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="quality">품질</Label>
              <Select
                value={options.quality}
                onValueChange={(value) => updateOption('quality', value as PDFExportOptions['quality'])}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">낮음 (빠름)</SelectItem>
                  <SelectItem value="medium">보통</SelectItem>
                  <SelectItem value="high">높음</SelectItem>
                  <SelectItem value="ultra">최고 (느림)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="dpi">DPI</Label>
              <Select
                value={options.dpi.toString()}
                onValueChange={(value) => updateOption('dpi', parseInt(value) as PDFExportOptions['dpi'])}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="72">72 DPI (웹용)</SelectItem>
                  <SelectItem value="96">96 DPI (표준)</SelectItem>
                  <SelectItem value="150">150 DPI (고품질)</SelectItem>
                  <SelectItem value="300">300 DPI (인쇄용)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Custom Size */}
          {options.format === 'Custom' && (
            <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg">
              <div className="space-y-2">
                <Label htmlFor="customWidth">너비 (mm)</Label>
                <Input
                  id="customWidth"
                  type="number"
                  value={options.customSize?.width || 210}
                  onChange={(e) => setOptions((prev: any) => ({
                    ...prev,
                    customSize: {
                      ...prev.customSize,
                      width: parseInt(e.target.value) || 210
                    }
                  }))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="customHeight">높이 (mm)</Label>
                <Input
                  id="customHeight"
                  type="number"
                  value={options.customSize?.height || 297}
                  onChange={(e) => setOptions((prev: any) => ({
                    ...prev,
                    customSize: {
                      ...prev.customSize,
                      height: parseInt(e.target.value) || 297
                    }
                  }))}
                />
              </div>
            </div>
          )}

          {/* Margins */}
          <div className="space-y-4">
            <Label>여백 (mm)</Label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="marginTop" className="text-sm">상단</Label>
                <Input
                  id="marginTop"
                  type="number"
                  value={options.margin.top}
                  onChange={(e) => updateMargin('top', parseInt(e.target.value) || 0)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marginBottom" className="text-sm">하단</Label>
                <Input
                  id="marginBottom"
                  type="number"
                  value={options.margin.bottom}
                  onChange={(e) => updateMargin('bottom', parseInt(e.target.value) || 0)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marginLeft" className="text-sm">좌측</Label>
                <Input
                  id="marginLeft"
                  type="number"
                  value={options.margin.left}
                  onChange={(e) => updateMargin('left', parseInt(e.target.value) || 0)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marginRight" className="text-sm">우측</Label>
                <Input
                  id="marginRight"
                  type="number"
                  value={options.margin.right}
                  onChange={(e) => updateMargin('right', parseInt(e.target.value) || 0)}
                />
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Content Tab */}
        <TabsContent value="content" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium">페이지 요소</h4>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="includePageNumbers"
                    checked={options.includePageNumbers}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, includePageNumbers: checked as boolean }))}
                  />
                  <Label htmlFor="includePageNumbers">페이지 번호</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="includeHeader"
                    checked={options.includeHeader}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, includeHeader: checked as boolean }))}
                  />
                  <Label htmlFor="includeHeader">머리글</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="includeFooter"
                    checked={options.includeFooter}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, includeFooter: checked as boolean }))}
                  />
                  <Label htmlFor="includeFooter">바닥글</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="tableOfContents"
                    checked={options.tableOfContents}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, tableOfContents: checked as boolean }))}
                  />
                  <Label htmlFor="tableOfContents">목차</Label>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">콘텐츠</h4>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="includeCharts"
                    checked={options.includeCharts}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, includeCharts: checked as boolean }))}
                  />
                  <Label htmlFor="includeCharts">차트 및 그래프</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="breakPages"
                    checked={options.breakPages}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, breakPages: checked as boolean }))}
                  />
                  <Label htmlFor="breakPages">자동 페이지 나누기</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="koreanFont"
                    checked={options.koreanFont}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, koreanFont: checked as boolean }))}
                  />
                  <Label htmlFor="koreanFont">한글 폰트 지원</Label>
                </div>
              </div>
            </div>
          </div>

          {/* Font Family */}
          {options.koreanFont && (
            <div className="space-y-2">
              <Label htmlFor="fontFamily">폰트</Label>
              <Input
                id="fontFamily"
                value={options.fontFamily || ''}
                onChange={(e) => setOptions((prev: any) => ({ ...prev, fontFamily: e.target.value }))}
                placeholder="예: NanumGothic, Arial, sans-serif"
              />
            </div>
          )}
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance" className="space-y-4">
          <div className="space-y-6">
            {/* Watermark */}
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="includeWatermark"
                  checked={options.includeWatermark}
                  onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, includeWatermark: checked as boolean }))}
                />
                <Label htmlFor="includeWatermark">워터마크</Label>
              </div>

              {options.includeWatermark && (
                <div className="space-y-4 pl-6 border-l-2 border-gray-200">
                  <div className="space-y-2">
                    <Label htmlFor="watermarkText">워터마크 텍스트</Label>
                    <Input
                      id="watermarkText"
                      value={options.watermarkText || ''}
                      onChange={(e) => setOptions((prev: any) => ({ ...prev, watermarkText: e.target.value }))}
                      placeholder="예: AIBOA Report"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="watermarkOpacity">투명도: {Math.round((options.watermarkOpacity || 0.1) * 100)}%</Label>
                    <Slider
                      id="watermarkOpacity"
                      value={[(options.watermarkOpacity || 0.1) * 100]}
                      onValueChange={(value) => setOptions((prev: any) => ({ ...prev, watermarkOpacity: value[0] / 100 }))}
                      max={50}
                      min={5}
                      step={5}
                      className="w-full"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Metadata */}
            <div className="space-y-4">
              <h4 className="font-medium">문서 정보</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">제목</Label>
                  <Input
                    id="title"
                    value={options.title || ''}
                    onChange={(e) => setOptions((prev: any) => ({ ...prev, title: e.target.value }))}
                    placeholder="문서 제목"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="author">작성자</Label>
                  <Input
                    id="author"
                    value={options.author || ''}
                    onChange={(e) => setOptions((prev: any) => ({ ...prev, author: e.target.value }))}
                    placeholder="작성자 이름"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="subject">주제</Label>
                  <Input
                    id="subject"
                    value={options.subject || ''}
                    onChange={(e) => setOptions((prev: any) => ({ ...prev, subject: e.target.value }))}
                    placeholder="문서 주제"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="keywords">키워드</Label>
                  <Input
                    id="keywords"
                    value={options.keywords?.join(', ') || ''}
                    onChange={(e) => setOptions((prev: any) => ({ ...prev, keywords: e.target.value.split(',').map(k => k.trim()).filter(Boolean) }))}
                    placeholder="키워드 (쉼표로 구분)"
                  />
                </div>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Advanced Tab */}
        <TabsContent value="advanced" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium">최적화</h4>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="enableOptimization"
                    checked={options.enableOptimization}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, enableOptimization: checked as boolean }))}
                  />
                  <Label htmlFor="enableOptimization">PDF 최적화</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="compressImages"
                    checked={options.compressImages}
                    onCheckedChange={(checked) => setOptions((prev: any) => ({ ...prev, compressImages: checked as boolean }))}
                  />
                  <Label htmlFor="compressImages">이미지 압축</Label>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h4 className="font-medium">기타</h4>
              <div className="space-y-2">
                <Label htmlFor="creator">생성 프로그램</Label>
                <Input
                  id="creator"
                  value={options.creator || ''}
                  onChange={(e) => setOptions((prev: any) => ({ ...prev, creator: e.target.value }))}
                  placeholder="예: AIBOA Platform"
                />
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex justify-between pt-6 border-t">
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-2" />
            초기화
          </Button>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={onCancel}>
            취소
          </Button>
          <Button 
            onClick={handleConfirm}
            disabled={validationErrors.length > 0}
          >
            <Download className="w-4 h-4 mr-2" />
            PDF 생성
          </Button>
        </div>
      </div>
    </div>
  )
}

export default PDFOptions