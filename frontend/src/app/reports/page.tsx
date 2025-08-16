'use client'

import React, { useState, useMemo } from 'react'
import { Card } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Badge } from '../../components/ui/badge'
import { Input } from '../../components/ui/input'
import { Select } from '../../components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { Progress } from '../../components/ui/progress'
import useReportGeneration from '../../hooks/useReportGeneration'
import { useAnalysisHistory } from '../../hooks/useAnalysis'
import ComprehensiveReportTemplate from '../../components/reports/ComprehensiveReportTemplate'
import { FrameworkReportTemplates } from '../../components/reports/FrameworkReportTemplates'
import YouTubeEmbed, { extractYouTubeVideoId, isValidYouTubeUrl } from '../../components/media/YouTubeEmbed'
import { comprehensiveFrameworkUtils } from '../../types/comprehensive-analysis'
import {
  FileText,
  Download,
  Eye,
  Trash2,
  Share2,
  Printer,
  Plus,
  Search,
  Filter,
  Calendar,
  Clock,
  BarChart3,
  PieChart,
  TrendingUp,
  Users,
  PlayCircle,
  ExternalLink
} from 'lucide-react'

const ReportsPage: React.FC = () => {
  const {
    generatedReports,
    isLoading,
    error,
    generationState,
    generateComprehensiveReport,
    generateFrameworkReport,
    deleteReport,
    downloadReport,
    previewReport,
    printReport,
    shareReport
  } = useReportGeneration()

  const { data: analysisResults = [] } = useAnalysisHistory()

  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'comprehensive' | 'summary' | 'individual'>('all')
  const [sortBy, setSortBy] = useState<'date' | 'title' | 'type'>('date')
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [youtubeUrl, setYoutubeUrl] = useState('')

  // Filter and sort reports
  const filteredReports = useMemo(() => {
    let filtered = generatedReports

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(report =>
        report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.metadata.teacher?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.metadata.subject?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by type
    if (filterType !== 'all') {
      filtered = filtered.filter(report => report.type === filterType)
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        case 'title':
          return a.title.localeCompare(b.title)
        case 'type':
          return a.type.localeCompare(b.type)
        default:
          return 0
      }
    })

    return filtered
  }, [generatedReports, searchTerm, filterType, sortBy])

  // Handle report generation from existing analysis
  const handleGenerateFromAnalysis = async (analysisId: string, type: 'comprehensive' | 'individual') => {
    const analysis = analysisResults.find(result => result.id === analysisId)
    if (!analysis) return

    const metadata = {
      teacher: analysis.metadata?.teacher || '',
      subject: analysis.metadata?.subject || '',
      grade: analysis.metadata?.grade_level || '',
      duration: analysis.metadata?.duration?.toString() || '',
      analysisTime: '완료'
    }

    try {
      if (type === 'comprehensive' && 'frameworks_analyzed' in analysis) {
        await generateComprehensiveReport(analysis as any, metadata)
      } else if (type === 'individual') {
        // Generate individual reports for each framework
        if ('frameworks_analyzed' in analysis) {
          const comprehensiveAnalysis = analysis as any
          for (const frameworkId of comprehensiveAnalysis.frameworks_analyzed) {
            const result = comprehensiveAnalysis.individual_results[frameworkId]
            if (result) {
              await generateFrameworkReport(frameworkId, result, metadata)
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to generate report:', error)
    }
  }

  // Handle YouTube URL processing
  const handleYouTubeProcess = () => {
    if (!isValidYouTubeUrl(youtubeUrl)) {
      alert('올바른 YouTube URL을 입력해주세요.')
      return
    }

    const videoId = extractYouTubeVideoId(youtubeUrl)
    if (videoId) {
      // This would typically trigger transcription and analysis
      console.log('Processing YouTube video:', videoId)
      // You would integrate this with your transcription service
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getReportTypeIcon = (type: string) => {
    switch (type) {
      case 'comprehensive':
        return <BarChart3 className="w-4 h-4" />
      case 'summary':
        return <PieChart className="w-4 h-4" />
      case 'individual':
        return <TrendingUp className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const getReportTypeName = (type: string) => {
    switch (type) {
      case 'comprehensive':
        return '종합 보고서'
      case 'summary':
        return '요약 보고서'
      case 'individual':
        return '개별 프레임워크'
      default:
        return '보고서'
    }
  }

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">분석 보고서</h1>
          <p className="text-gray-600 mt-2">
            생성된 보고서를 관리하고 새로운 보고서를 생성할 수 있습니다.
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)} className="flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          새 보고서 생성
        </Button>
      </div>

      {/* Generation Status */}
      {generationState.isGenerating && (
        <Card className="p-6 mb-6 bg-blue-50 border-blue-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-blue-900">보고서 생성 중...</h3>
            <span className="text-sm text-blue-700">{Math.round(generationState.progress)}%</span>
          </div>
          <Progress value={generationState.progress} className="mb-2" />
          <p className="text-sm text-blue-700">{generationState.currentStep}</p>
        </Card>
      )}

      {/* YouTube Video Processing */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <PlayCircle className="w-5 h-5 mr-2 text-red-600" />
          YouTube 영상 분석
        </h3>
        <div className="flex gap-4">
          <Input
            placeholder="YouTube URL을 입력하세요 (예: https://www.youtube.com/watch?v=...)"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            className="flex-1"
          />
          <Button 
            onClick={handleYouTubeProcess}
            disabled={!isValidYouTubeUrl(youtubeUrl)}
          >
            분석 시작
          </Button>
        </div>
        
        {/* YouTube Preview */}
        {isValidYouTubeUrl(youtubeUrl) && (
          <div className="mt-6">
            <YouTubeEmbed
              videoId={extractYouTubeVideoId(youtubeUrl) || ''}
              title="분석 대상 영상"
              height={300}
              showControls={true}
              showTitle={true}
              showTimestamp={true}
            />
          </div>
        )}
      </Card>

      <Tabs defaultValue="reports" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="reports">생성된 보고서</TabsTrigger>
          <TabsTrigger value="templates">보고서 템플릿</TabsTrigger>
          <TabsTrigger value="analytics">보고서 분석</TabsTrigger>
        </TabsList>

        {/* Generated Reports Tab */}
        <TabsContent value="reports" className="space-y-6">
          {/* Filters and Search */}
          <Card className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="보고서 제목, 교사명, 과목으로 검색..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <div className="flex gap-2">
                <Select
                  value={filterType}
                  onValueChange={(value: any) => setFilterType(value)}
                >
                  <option value="all">모든 유형</option>
                  <option value="comprehensive">종합 보고서</option>
                  <option value="summary">요약 보고서</option>
                  <option value="individual">개별 프레임워크</option>
                </Select>
                
                <Select
                  value={sortBy}
                  onValueChange={(value: any) => setSortBy(value)}
                >
                  <option value="date">생성 날짜순</option>
                  <option value="title">제목순</option>
                  <option value="type">유형순</option>
                </Select>
              </div>
            </div>
          </Card>

          {/* Reports List */}
          {isLoading ? (
            <Card className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">보고서를 불러오는 중...</p>
            </Card>
          ) : filteredReports.length === 0 ? (
            <Card className="p-8 text-center">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm ? '검색 결과가 없습니다' : '생성된 보고서가 없습니다'}
              </h3>
              <p className="text-gray-600 mb-4">
                {searchTerm ? '다른 검색어를 시도해보세요.' : '새로운 보고서를 생성해보세요.'}
              </p>
              {!searchTerm && (
                <Button onClick={() => setShowCreateDialog(true)}>
                  첫 번째 보고서 생성하기
                </Button>
              )}
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredReports.map((report) => (
                <Card key={report.id} className="p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center">
                      {getReportTypeIcon(report.type)}
                      <span className="ml-2 font-medium">{report.title}</span>
                    </div>
                    <Badge variant="outline">
                      {getReportTypeName(report.type)}
                    </Badge>
                  </div>

                  <div className="space-y-2 mb-4 text-sm text-gray-600">
                    {report.metadata.teacher && (
                      <div className="flex items-center">
                        <Users className="w-4 h-4 mr-2" />
                        {report.metadata.teacher}
                      </div>
                    )}
                    {report.metadata.subject && (
                      <div className="flex items-center">
                        <BarChart3 className="w-4 h-4 mr-2" />
                        {report.metadata.subject}
                      </div>
                    )}
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      {formatDate(report.createdAt)}
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      분석 프레임워크: {report.frameworkIds.length}개
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => previewReport(report.id)}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      미리보기
                    </Button>
                    
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadReport(report.id, 'html')}
                    >
                      <Download className="w-4 h-4 mr-1" />
                      다운로드
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => printReport(report.id)}
                    >
                      <Printer className="w-4 h-4" />
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => shareReport(report.id)}
                    >
                      <Share2 className="w-4 h-4" />
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteReport(report.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">사용 가능한 보고서 템플릿</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(FrameworkReportTemplates).map(([frameworkId, TemplateComponent]) => {
                const framework = comprehensiveFrameworkUtils.getFramework(frameworkId)
                if (!framework) return null

                return (
                  <Card key={frameworkId} className="p-4">
                    <div className="flex items-center mb-3">
                      <div 
                        className="w-4 h-4 rounded mr-3"
                        style={{ backgroundColor: framework.color }}
                      />
                      <h4 className="font-medium">{framework.name_ko}</h4>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">{framework.description}</p>
                    <Button size="sm" variant="outline" className="w-full">
                      템플릿 미리보기
                    </Button>
                  </Card>
                )
              })}
            </div>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="p-6 text-center">
              <div className="text-3xl font-bold text-blue-600">{generatedReports.length}</div>
              <div className="text-sm text-gray-600">총 생성된 보고서</div>
            </Card>
            
            <Card className="p-6 text-center">
              <div className="text-3xl font-bold text-green-600">
                {generatedReports.filter(r => r.type === 'comprehensive').length}
              </div>
              <div className="text-sm text-gray-600">종합 보고서</div>
            </Card>
            
            <Card className="p-6 text-center">
              <div className="text-3xl font-bold text-purple-600">
                {generatedReports.filter(r => r.type === 'individual').length}
              </div>
              <div className="text-sm text-gray-600">개별 프레임워크</div>
            </Card>
            
            <Card className="p-6 text-center">
              <div className="text-3xl font-bold text-orange-600">
                {new Set(generatedReports.flatMap(r => r.frameworkIds)).size}
              </div>
              <div className="text-sm text-gray-600">분석된 프레임워크</div>
            </Card>
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">최근 활동</h3>
            <div className="space-y-3">
              {generatedReports.slice(0, 5).map((report) => (
                <div key={report.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                  <div className="flex items-center">
                    {getReportTypeIcon(report.type)}
                    <span className="ml-3 font-medium">{report.title}</span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {formatDate(report.createdAt)}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Report Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">새 보고서 생성</h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">기존 분석 결과로부터 생성</h4>
                <div className="space-y-2">
                  {analysisResults.slice(0, 5).map((analysis) => (
                    <div key={analysis.id} className="flex items-center justify-between p-3 border rounded">
                      <div>
                        <div className="font-medium">{analysis.text_preview.slice(0, 50)}...</div>
                        <div className="text-sm text-gray-600">
                          {new Date(analysis.created_at).toLocaleDateString('ko-KR')}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={() => handleGenerateFromAnalysis(analysis.id, 'comprehensive')}
                        >
                          종합 보고서
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleGenerateFromAnalysis(analysis.id, 'individual')}
                        >
                          개별 보고서
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                취소
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}

export default ReportsPage