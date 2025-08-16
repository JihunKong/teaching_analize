/**
 * PDF Export Demo Page
 * 
 * Comprehensive demonstration of all PDF export features including:
 * - Individual report exports
 * - Batch export functionality
 * - PDF preview
 * - Settings management
 * - Different export formats
 */

'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Button } from '../../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { Badge } from '../../components/ui/badge'
import { Alert, AlertDescription } from '../../components/ui/alert'
import {
  FileText,
  Download,
  Settings,
  Eye,
  Package,
  Zap,
  BarChart3,
  ClipboardList,
  BookOpen,
  Info
} from 'lucide-react'

// PDF Components
import {
  PDFExportButton,
  PDFPreview,
  BatchPDFExport
} from '../../components/pdf'
import PDFSettings from '../../components/settings/PDFSettings'

// Report Templates
import { 
  ComprehensiveReportTemplate,
  SummaryReportTemplate,
  ActionPlanTemplate
} from '../../components/reports'

// Mock data for demonstration
const mockAnalysisResult = {
  id: 'demo_analysis_1',
  request_id: 'demo_request_1',
  frameworks_analyzed: ['cbil', 'qta', 'sei'],
  overall_summary: {
    total_segments: 45,
    average_score: 78,
    strengths: ['명확한 설명', '적절한 피드백'],
    areas_for_improvement: ['질문 다양성', '학습자 참여도']
  },
  recommendations: [
    {
      recommendation: '다양한 질문 유형을 활용하여 학습자의 사고력을 증진시키세요',
      priority: 'high' as const,
      frameworks_source: ['qta'],
      specific_actions: ['개방형 질문 증가', '토론 시간 확대'],
      expected_impact: 'high' as const
    },
    {
      recommendation: '학습자의 능동적 참여를 유도하는 활동을 늘려보세요',
      priority: 'medium' as const,
      frameworks_source: ['sei'],
      specific_actions: ['그룹 활동 도입', '발표 기회 확대'],
      expected_impact: 'medium' as const
    }
  ],
  cross_framework_insights: [
    {
      insight: '질문 기법과 학습자 참여도는 밀접한 상관관계를 보입니다',
      related_frameworks: ['qta', 'sei'],
      confidence: 0.85
    }
  ],
  individual_results: {
    cbil: {
      overall_score: 75,
      level_distribution: { low_level: 30, mid_level: 50, high_level: 20 },
      dominant_level: { level: 3, name: '개념 설명', percentage: 35 }
    },
    qta: {
      effectiveness_score: 82,
      question_types: { factual: 40, analytical: 35, creative: 25 },
      patterns: ['주로 사실 확인 질문 사용']
    },
    sei: {
      engagement_score: 70,
      participation_metrics: { active: 60, passive: 40 },
      trends: ['중간 수준의 참여도 유지']
    }
  },
  analysis_metadata: {
    total_analysis_time: 23,
    processed_segments: 45,
    confidence_score: 0.87
  }
}

const mockMetadata = {
  teacher: '김선생님',
  subject: '과학',
  grade: '중학교 2학년',
  duration: '45분',
  analysisTime: '23초'
}

const PDFDemoPage: React.FC = () => {
  const [activeDemo, setActiveDemo] = useState<string>('individual')
  const [showSettings, setShowSettings] = useState(false)

  // Sample HTML content for demonstrations
  const sampleHTML = `
    <div style="padding: 20px; font-family: Arial, sans-serif;">
      <h1 style="color: #2563eb;">AIBOA 분석 보고서</h1>
      <p>이것은 PDF 내보내기 데모를 위한 샘플 HTML 콘텐츠입니다.</p>
      <div style="background: #f3f4f6; padding: 15px; margin: 10px 0; border-radius: 8px;">
        <h3>주요 분석 결과</h3>
        <ul>
          <li>전체 점수: 78점</li>
          <li>강점: 명확한 설명, 적절한 피드백</li>
          <li>개선 영역: 질문 다양성, 학습자 참여도</li>
        </ul>
      </div>
    </div>
  `

  // Batch export items for demonstration
  const batchItems = [
    {
      id: 'comprehensive_1',
      title: '종합 분석 보고서',
      html: sampleHTML
    },
    {
      id: 'summary_1',
      title: '요약 보고서',
      html: sampleHTML.replace('종합 분석', '요약')
    },
    {
      id: 'action_plan_1',
      title: '실행 계획서',
      html: sampleHTML.replace('분석 보고서', '실행 계획서')
    }
  ]

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">PDF 내보내기 시스템 데모</h1>
        <p className="text-gray-600 mb-6">
          AIBOA 플랫폼의 포괄적인 PDF 내보내기 기능을 체험해보세요.
        </p>
        
        <div className="flex items-center space-x-4">
          <Badge variant="outline" className="flex items-center space-x-1">
            <FileText className="w-3 h-3" />
            <span>다중 형식 지원</span>
          </Badge>
          <Badge variant="outline" className="flex items-center space-x-1">
            <Eye className="w-3 h-3" />
            <span>실시간 미리보기</span>
          </Badge>
          <Badge variant="outline" className="flex items-center space-x-1">
            <Package className="w-3 h-3" />
            <span>일괄 내보내기</span>
          </Badge>
          <Badge variant="outline" className="flex items-center space-x-1">
            <Settings className="w-3 h-3" />
            <span>세부 설정</span>
          </Badge>
        </div>
      </div>

      <Tabs value={activeDemo} onValueChange={setActiveDemo} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="individual" className="flex items-center space-x-2">
            <FileText className="w-4 h-4" />
            <span>개별 내보내기</span>
          </TabsTrigger>
          <TabsTrigger value="batch" className="flex items-center space-x-2">
            <Package className="w-4 h-4" />
            <span>일괄 내보내기</span>
          </TabsTrigger>
          <TabsTrigger value="preview" className="flex items-center space-x-2">
            <Eye className="w-4 h-4" />
            <span>미리보기</span>
          </TabsTrigger>
          <TabsTrigger value="templates" className="flex items-center space-x-2">
            <BookOpen className="w-4 h-4" />
            <span>보고서 템플릿</span>
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>설정</span>
          </TabsTrigger>
        </TabsList>

        {/* Individual Export Demo */}
        <TabsContent value="individual" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>개별 PDF 내보내기</span>
              </CardTitle>
              <CardDescription>
                단일 보고서를 PDF로 내보내는 기본 기능을 테스트해보세요.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="p-4">
                  <h4 className="font-medium mb-2 flex items-center space-x-2">
                    <BarChart3 className="w-4 h-4 text-blue-600" />
                    <span>종합 보고서</span>
                  </h4>
                  <p className="text-sm text-gray-600 mb-4">
                    모든 분석 프레임워크를 포함한 상세 보고서
                  </p>
                  <PDFExportButton
                    html={sampleHTML}
                    filename="comprehensive_report_demo.pdf"
                    title="PDF 내보내기"
                    showOptionsDialog={true}
                    showProgress={true}
                    showEstimation={true}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  />
                </Card>

                <Card className="p-4">
                  <h4 className="font-medium mb-2 flex items-center space-x-2">
                    <Zap className="w-4 h-4 text-green-600" />
                    <span>요약 보고서</span>
                  </h4>
                  <p className="text-sm text-gray-600 mb-4">
                    핵심 내용만 간추린 간결한 보고서
                  </p>
                  <PDFExportButton
                    html={sampleHTML.replace('종합 분석', '요약')}
                    filename="summary_report_demo.pdf"
                    title="PDF 내보내기"
                    showOptionsDialog={true}
                    showProgress={true}
                    showEstimation={true}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  />
                </Card>

                <Card className="p-4">
                  <h4 className="font-medium mb-2 flex items-center space-x-2">
                    <ClipboardList className="w-4 h-4 text-purple-600" />
                    <span>실행 계획서</span>
                  </h4>
                  <p className="text-sm text-gray-600 mb-4">
                    구체적인 개선 방안과 실행 계획
                  </p>
                  <PDFExportButton
                    html={sampleHTML.replace('분석 보고서', '실행 계획서')}
                    filename="action_plan_demo.pdf"
                    title="PDF 내보내기"
                    showOptionsDialog={true}
                    showProgress={true}
                    showEstimation={true}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  />
                </Card>
              </div>

              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  각 버튼을 클릭하면 PDF 옵션 설정 대화상자가 열립니다. 
                  원하는 설정을 선택한 후 PDF를 생성할 수 있습니다.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Batch Export Demo */}
        <TabsContent value="batch" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Package className="w-5 h-5" />
                <span>일괄 PDF 내보내기</span>
              </CardTitle>
              <CardDescription>
                여러 보고서를 한 번에 PDF로 내보내는 기능을 테스트해보세요.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <BatchPDFExport
                items={batchItems}
                showCombinedOption={true}
                onExportComplete={(results) => {
                  console.log('일괄 내보내기 완료:', results)
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preview Demo */}
        <TabsContent value="preview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Eye className="w-5 h-5" />
                <span>PDF 미리보기</span>
              </CardTitle>
              <CardDescription>
                PDF를 생성하기 전에 미리보기로 확인할 수 있습니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PDFPreview
                html={sampleHTML}
                options={{
                  format: 'A4',
                  quality: 'high',
                  includeCharts: true,
                  includeMetadata: true,
                  dpi: 150
                }}
                filename="preview_demo.pdf"
                showControls={true}
                showInfo={true}
                autoGenerate={true}
                className="border rounded-lg"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Report Templates Demo */}
        <TabsContent value="templates" className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            {/* Comprehensive Report Template */}
            <Card>
              <CardHeader>
                <CardTitle>종합 분석 보고서 템플릿</CardTitle>
                <CardDescription>
                  모든 분석 프레임워크 결과를 포함한 완전한 보고서 템플릿
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ComprehensiveReportTemplate
                  analysisResult={mockAnalysisResult as any}
                  metadata={mockMetadata}
                  showCharts={true}
                  showPDFExport={true}
                  enablePreview={true}
                  className="scale-75 origin-top-left"
                />
              </CardContent>
            </Card>

            {/* Summary Report Template */}
            <Card>
              <CardHeader>
                <CardTitle>요약 보고서 템플릿</CardTitle>
                <CardDescription>
                  핵심 내용만 간추린 간결한 보고서 템플릿
                </CardDescription>
              </CardHeader>
              <CardContent>
                <SummaryReportTemplate
                  analysisResult={mockAnalysisResult as any}
                  metadata={mockMetadata}
                  showCharts={true}
                  showPDFExport={true}
                  enablePreview={true}
                  className="scale-75 origin-top-left"
                />
              </CardContent>
            </Card>

            {/* Action Plan Template */}
            <Card>
              <CardHeader>
                <CardTitle>실행 계획서 템플릿</CardTitle>
                <CardDescription>
                  구체적인 개선 방안과 실행 계획이 포함된 템플릿
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ActionPlanTemplate
                  analysisResult={mockAnalysisResult as any}
                  metadata={mockMetadata}
                  timeframe="1month"
                  showPDFExport={true}
                  enablePreview={true}
                  className="scale-75 origin-top-left"
                />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Demo */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="w-5 h-5" />
                <span>PDF 내보내기 설정</span>
              </CardTitle>
              <CardDescription>
                PDF 내보내기의 기본 설정을 관리하고 사용자 정의할 수 있습니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PDFSettings
                onSettingsChange={(settings) => {
                  console.log('설정 변경:', settings)
                }}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <div className="mt-12 pt-8 border-t">
        <div className="text-center text-gray-600">
          <p className="mb-2">
            AIBOA PDF 내보내기 시스템은 다양한 형식과 옵션을 지원하여
            사용자의 요구에 맞는 고품질 PDF를 생성합니다.
          </p>
          <div className="flex justify-center space-x-4 text-sm">
            <span>• A4, Letter, A3 형식 지원</span>
            <span>• 한글 폰트 최적화</span>
            <span>• 차트 및 이미지 포함</span>
            <span>• 일괄 처리 지원</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PDFDemoPage