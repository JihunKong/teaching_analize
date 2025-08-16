'use client'

import React, { useState } from 'react'
import { ComprehensiveAnalysisResult, comprehensiveFrameworkUtils } from '../../types/comprehensive-analysis'
import { BarChart, DoughnutChart, generateChartColors } from '../charts'
import { Card } from '../ui/card'
import { Badge } from '../ui/badge'
import { Progress } from '../ui/progress'
import { TrendingUp, TrendingDown, Minus, AlertTriangle, CheckCircle, Clock, Eye, Download } from 'lucide-react'
import { PDFExportButton, PDFPreview } from '../pdf'
import { Button } from '../ui/button'
import { pdfExportUtils } from '../../lib/pdf-export'

interface SummaryReportTemplateProps {
  analysisResult: ComprehensiveAnalysisResult
  metadata: {
    teacher?: string
    subject?: string
    grade?: string
    duration?: string
    analysisTime: string
  }
  showCharts?: boolean
  className?: string
  showPDFExport?: boolean
  enablePreview?: boolean
}

const SummaryReportTemplate: React.FC<SummaryReportTemplateProps> = ({
  analysisResult,
  metadata,
  showCharts = true,
  className = '',
  showPDFExport = true,
  enablePreview = false
}) => {
  const [showPreview, setShowPreview] = useState(false)
  const frameworks = analysisResult.frameworks_analyzed
  const summary = analysisResult.overall_summary
  const recommendations = analysisResult.recommendations
  const crossInsights = analysisResult.cross_framework_insights

  // Calculate framework scores for quick overview
  const frameworkScores = frameworks.map(id => {
    const result = analysisResult.individual_results[id]
    let score = 75 // Default score
    
    if ('overall_score' in result) score = (result as any).overall_score
    else if ('effectiveness_score' in result) score = (result as any).effectiveness_score
    else if ('coherence_score' in result) score = (result as any).coherence_score
    else if ('cognitive_load_score' in result) score = (result as any).cognitive_load_score
    
    return {
      frameworkId: id,
      framework: comprehensiveFrameworkUtils.getFramework(id),
      score: Math.round(score)
    }
  })

  // Categorize scores
  const highPerformance = frameworkScores.filter(f => f.score >= 80)
  const mediumPerformance = frameworkScores.filter(f => f.score >= 60 && f.score < 80)
  const lowPerformance = frameworkScores.filter(f => f.score < 60)

  // Priority recommendations
  const highPriorityRecs = recommendations.filter(r => r.priority === 'high')
  const criticalInsights = crossInsights.filter(i => i.significance === 'high')

  // Overall performance data for chart
  const performanceData = {
    labels: ['우수', '보통', '개선필요'],
    datasets: [{
      data: [highPerformance.length, mediumPerformance.length, lowPerformance.length],
      backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  // Top framework scores
  const topFrameworksData = {
    labels: frameworkScores
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
      .map(f => f.framework?.name_ko.split(' ')[0] || f.frameworkId),
    datasets: [{
      label: '점수',
      data: frameworkScores
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)
        .map(f => f.score),
      backgroundColor: generateChartColors(5, 'primary'),
      borderColor: generateChartColors(5, 'primary'),
      borderWidth: 2
    }]
  }

  const getTrendIcon = (score: number) => {
    if (score >= 80) return <TrendingUp className="w-4 h-4 text-green-600" />
    if (score >= 60) return <Minus className="w-4 h-4 text-yellow-600" />
    return <TrendingDown className="w-4 h-4 text-red-600" />
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPerformanceLevel = (score: number) => {
    if (score >= 80) return '우수'
    if (score >= 60) return '보통'
    return '개선필요'
  }

  return (
    <div className={`summary-report-template ${className}`}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-blue-600 mb-2">교육 분석 요약 보고서</h1>
        <p className="text-gray-600">
          {frameworks.length}개 프레임워크를 통한 종합적 교육 품질 분석 결과입니다.
        </p>
      </div>

      {/* Key Metrics Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card className="p-6 text-center">
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {Math.round(summary.overall_score)}
          </div>
          <div className="text-sm text-gray-600">종합 점수</div>
          <div className="mt-2">
            {getTrendIcon(summary.overall_score)}
          </div>
        </Card>

        <Card className="p-6 text-center">
          <div className="text-3xl font-bold text-green-600 mb-2">
            {Math.round(summary.analysis_coverage)}%
          </div>
          <div className="text-sm text-gray-600">분석 커버리지</div>
          <Progress value={summary.analysis_coverage} className="mt-2" />
        </Card>

        <Card className="p-6 text-center">
          <div className="text-3xl font-bold text-orange-600 mb-2">
            {highPriorityRecs.length}
          </div>
          <div className="text-sm text-gray-600">긴급 개선사항</div>
          <div className="mt-2">
            {highPriorityRecs.length > 0 ? (
              <AlertTriangle className="w-4 h-4 text-orange-600 mx-auto" />
            ) : (
              <CheckCircle className="w-4 h-4 text-green-600 mx-auto" />
            )}
          </div>
        </Card>

        <Card className="p-6 text-center">
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {criticalInsights.length}
          </div>
          <div className="text-sm text-gray-600">중요 인사이트</div>
          <div className="mt-2">
            <Clock className="w-4 h-4 text-purple-600 mx-auto" />
          </div>
        </Card>
      </div>

      {/* Performance Overview Charts */}
      {showCharts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">성과 분포</h3>
            <DoughnutChart
              data={performanceData}
              height={250}
              centerText={`${frameworks.length}개`}
              centerSubtext="프레임워크"
            />
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">상위 프레임워크 성과</h3>
            <BarChart
              data={topFrameworksData}
              height={250}
              options={{
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 100
                  }
                }
              }}
            />
          </Card>
        </div>
      )}

      {/* Framework Performance Grid */}
      <Card className="p-6 mb-8">
        <h3 className="text-lg font-semibold mb-6">프레임워크별 성과 요약</h3>
        
        <div className="space-y-4">
          {/* High Performance */}
          {highPerformance.length > 0 && (
            <div>
              <h4 className="font-medium text-green-600 mb-3 flex items-center">
                <CheckCircle className="w-4 h-4 mr-2" />
                우수 성과 ({highPerformance.length}개)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {highPerformance.map(({ frameworkId, framework, score }) => (
                  <div key={frameworkId} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded mr-2"
                        style={{ backgroundColor: framework?.color || '#10b981' }}
                      />
                      <span className="text-sm font-medium">{framework?.name_ko || frameworkId}</span>
                    </div>
                    <Badge variant="default" className="bg-green-100 text-green-800">
                      {score}점
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Medium Performance */}
          {mediumPerformance.length > 0 && (
            <div>
              <h4 className="font-medium text-yellow-600 mb-3 flex items-center">
                <Minus className="w-4 h-4 mr-2" />
                보통 성과 ({mediumPerformance.length}개)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {mediumPerformance.map(({ frameworkId, framework, score }) => (
                  <div key={frameworkId} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded mr-2"
                        style={{ backgroundColor: framework?.color || '#f59e0b' }}
                      />
                      <span className="text-sm font-medium">{framework?.name_ko || frameworkId}</span>
                    </div>
                    <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                      {score}점
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Low Performance */}
          {lowPerformance.length > 0 && (
            <div>
              <h4 className="font-medium text-red-600 mb-3 flex items-center">
                <AlertTriangle className="w-4 h-4 mr-2" />
                개선 필요 ({lowPerformance.length}개)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {lowPerformance.map(({ frameworkId, framework, score }) => (
                  <div key={frameworkId} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex items-center">
                      <div 
                        className="w-3 h-3 rounded mr-2"
                        style={{ backgroundColor: framework?.color || '#ef4444' }}
                      />
                      <span className="text-sm font-medium">{framework?.name_ko || frameworkId}</span>
                    </div>
                    <Badge variant="destructive" className="bg-red-100 text-red-800">
                      {score}점
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Key Strengths and Areas for Improvement */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-green-600 flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            주요 강점
          </h3>
          <ul className="space-y-3">
            {summary.key_strengths.map((strength, index) => (
              <li key={index} className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-gray-700">{strength}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 text-orange-600 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            개선 영역
          </h3>
          <ul className="space-y-3">
            {summary.priority_improvements.map((improvement, index) => (
              <li key={index} className="flex items-start">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                <span className="text-gray-700">{improvement}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      {/* Critical Insights */}
      {criticalInsights.length > 0 && (
        <Card className="p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4 text-purple-600">중요 발견사항</h3>
          <div className="space-y-4">
            {criticalInsights.map((insight, index) => (
              <div key={index} className="p-4 bg-purple-50 rounded-lg border-l-4 border-purple-500">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-purple-900">
                    {insight.insight_type === 'correlation' ? '상관관계 발견' : 
                     insight.insight_type === 'contradiction' ? '모순점 발견' :
                     insight.insight_type === 'reinforcement' ? '강화효과 확인' : '분석 공백 식별'}
                  </h4>
                  <Badge variant="outline" className="border-purple-500 text-purple-700">
                    높은 중요도
                  </Badge>
                </div>
                <p className="text-purple-800 mb-3">{insight.description}</p>
                <div className="text-sm text-purple-700">
                  <strong>관련 영역:</strong> {insight.frameworks_involved.map(fw => {
                    const framework = comprehensiveFrameworkUtils.getFramework(fw)
                    return framework?.name_ko || fw
                  }).join(', ')}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Immediate Action Items */}
      {highPriorityRecs.length > 0 && (
        <Card className="p-6 mb-8">
          <h3 className="text-lg font-semibold mb-4 text-red-600 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            즉시 조치 필요사항
          </h3>
          <div className="space-y-4">
            {highPriorityRecs.slice(0, 3).map((rec, index) => (
              <div key={index} className="p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
                <h4 className="font-medium text-red-900 mb-2">{rec.recommendation}</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                  <div>
                    <span className="text-red-700 font-medium">관련 영역:</span>
                    <div className="text-red-600">
                      {rec.frameworks_source.map(fw => {
                        const framework = comprehensiveFrameworkUtils.getFramework(fw)
                        return framework?.name_ko || fw
                      }).join(', ')}
                    </div>
                  </div>
                  <div>
                    <span className="text-red-700 font-medium">구현 난이도:</span>
                    <div className="text-red-600">
                      {rec.implementation_difficulty === 'easy' ? '쉬움' :
                       rec.implementation_difficulty === 'moderate' ? '보통' : '어려움'}
                    </div>
                  </div>
                  <div>
                    <span className="text-red-700 font-medium">예상 효과:</span>
                    <div className="text-red-600">
                      {rec.expected_impact === 'high' ? '높음' :
                       rec.expected_impact === 'medium' ? '보통' : '낮음'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Summary Statistics */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">분석 통계</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{frameworks.length}</div>
            <div className="text-sm text-gray-600">분석 프레임워크</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{recommendations.length}</div>
            <div className="text-sm text-gray-600">총 권고사항</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{crossInsights.length}</div>
            <div className="text-sm text-gray-600">교차 인사이트</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {metadata.analysisTime}
            </div>
            <div className="text-sm text-gray-600">분석 소요시간</div>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            {metadata.teacher && (
              <div>
                <span className="font-medium text-gray-600">교사:</span>
                <div className="text-gray-900">{metadata.teacher}</div>
              </div>
            )}
            {metadata.subject && (
              <div>
                <span className="font-medium text-gray-600">과목:</span>
                <div className="text-gray-900">{metadata.subject}</div>
              </div>
            )}
            {metadata.grade && (
              <div>
                <span className="font-medium text-gray-600">학년:</span>
                <div className="text-gray-900">{metadata.grade}</div>
              </div>
            )}
            {metadata.duration && (
              <div>
                <span className="font-medium text-gray-600">수업 시간:</span>
                <div className="text-gray-900">{metadata.duration}</div>
              </div>
            )}
            <div>
              <span className="font-medium text-gray-600">분석 일시:</span>
              <div className="text-gray-900">{new Date().toLocaleString('ko-KR')}</div>
            </div>
            <div>
              <span className="font-medium text-gray-600">보고서 유형:</span>
              <div className="text-gray-900">요약 보고서</div>
            </div>
          </div>
        </div>
      </Card>

      {/* PDF Export Section */}
      {showPDFExport && (
        <Card className="p-6 mt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">PDF 내보내기</h3>
              <p className="text-gray-600 text-sm">
                이 요약 보고서를 PDF 파일로 저장하거나 미리보기할 수 있습니다.
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              {enablePreview && (
                <Button
                  variant="outline"
                  onClick={() => setShowPreview(!showPreview)}
                  className="flex items-center space-x-2"
                >
                  <Eye className="w-4 h-4" />
                  <span>{showPreview ? '미리보기 닫기' : 'PDF 미리보기'}</span>
                </Button>
              )}
              
              <PDFExportButton
                html={document.querySelector('.summary-report-template')?.outerHTML || ''}
                filename={pdfExportUtils.generateFilename('summary_report', metadata)}
                title="요약 보고서 PDF 내보내기"
                defaultOptions={pdfExportUtils.getReportTypeOptions('summary') as any}
                showOptionsDialog={true}
                showProgress={true}
                showEstimation={true}
                variant="default"
                className="bg-green-600 hover:bg-green-700 text-white"
                onExportComplete={(success, result) => {
                  if (success) {
                    console.log('요약 보고서 PDF 내보내기 완료:', result)
                  }
                }}
              />
            </div>
          </div>
        </Card>
      )}

      {/* PDF Preview Section */}
      {showPDFExport && enablePreview && showPreview && (
        <div className="mt-6">
          <PDFPreview
            html={document.querySelector('.summary-report-template')?.outerHTML || ''}
            options={pdfExportUtils.getReportTypeOptions('summary') as any}
            filename={pdfExportUtils.generateFilename('summary_report_preview', metadata)}
            showControls={true}
            showInfo={true}
            autoGenerate={false}
            onExport={() => setShowPreview(false)}
            className="border rounded-lg"
          />
        </div>
      )}
    </div>
  )
}

export default SummaryReportTemplate