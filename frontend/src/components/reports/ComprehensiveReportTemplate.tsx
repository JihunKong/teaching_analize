'use client'

import React, { useState } from 'react'
import { ComprehensiveAnalysisResult, comprehensiveFrameworkUtils } from '../../types/comprehensive-analysis'
import { BarChart, PieChart, RadarChart, LineChart, DoughnutChart, generateChartColors } from '../charts'
import { Card } from '../ui/card'
import { PDFExportButton, PDFPreview } from '../pdf'
import { Button } from '../ui/button'
import { Eye, Download, Settings } from 'lucide-react'
import { pdfExportUtils } from '../../lib/pdf-export'

interface ComprehensiveReportTemplateProps {
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

const ComprehensiveReportTemplate: React.FC<ComprehensiveReportTemplateProps> = ({
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

  // Generate overall score chart data
  const overallScoreData = {
    labels: frameworks.map(id => {
      const fw = comprehensiveFrameworkUtils.getFramework(id)
      return fw?.name_ko.split(' ')[0] || id
    }),
    datasets: [{
      label: '프레임워크별 점수',
      data: frameworks.map(id => {
        const result = analysisResult.individual_results[id]
        // Extract score based on framework type
        if ('overall_score' in result) return (result as any).overall_score
        if ('effectiveness_score' in result) return (result as any).effectiveness_score
        if ('coherence_score' in result) return (result as any).coherence_score
        if ('cognitive_load_score' in result) return (result as any).cognitive_load_score
        return 75 // Default score
      }),
      backgroundColor: generateChartColors(frameworks.length, 'primary'),
      borderColor: generateChartColors(frameworks.length, 'primary'),
      borderWidth: 2
    }]
  }

  // Generate framework coverage pie chart
  const frameworkCoverageData = {
    labels: frameworks.map(id => {
      const fw = comprehensiveFrameworkUtils.getFramework(id)
      return fw?.name_ko || id
    }),
    datasets: [{
      data: frameworks.map(() => 100 / frameworks.length), // Equal distribution for now
      backgroundColor: generateChartColors(frameworks.length, 'gradient'),
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  // Generate insights distribution
  const insightsData = {
    labels: ['상관관계', '모순점', '강화효과', '분석공백'],
    datasets: [{
      data: [
        crossInsights.filter(i => i.insight_type === 'correlation').length,
        crossInsights.filter(i => i.insight_type === 'contradiction').length,
        crossInsights.filter(i => i.insight_type === 'reinforcement').length,
        crossInsights.filter(i => i.insight_type === 'gap').length
      ],
      backgroundColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  // Generate recommendations priority distribution
  const recommendationsPriorityData = {
    labels: ['높음', '보통', '낮음'],
    datasets: [{
      data: [
        recommendations.filter(r => r.priority === 'high').length,
        recommendations.filter(r => r.priority === 'medium').length,
        recommendations.filter(r => r.priority === 'low').length
      ],
      backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  return (
    <div className={`comprehensive-report-template ${className}`}>
      {/* Executive Summary */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-6 text-blue-600 border-b-2 border-blue-600 pb-2">
          분석 요약
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-blue-600">{summary.total_frameworks}</div>
            <div className="text-sm text-gray-600">분석 프레임워크</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-green-600">
              {Math.round(summary.analysis_coverage)}%
            </div>
            <div className="text-sm text-gray-600">분석 커버리지</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-purple-600">
              {Math.round(summary.overall_score)}
            </div>
            <div className="text-sm text-gray-600">종합 점수</div>
          </Card>
          <Card className="p-4 text-center">
            <div className="text-3xl font-bold text-orange-600">
              {summary.priority_improvements.length}
            </div>
            <div className="text-sm text-gray-600">주요 개선사항</div>
          </Card>
        </div>

        {showCharts && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <Card className="p-4">
              <BarChart
                data={overallScoreData}
                title="프레임워크별 종합 점수"
                height={300}
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
            <Card className="p-4">
              <DoughnutChart
                data={frameworkCoverageData}
                title="분석 프레임워크 구성"
                height={300}
                centerText={`${summary.total_frameworks}개`}
                centerSubtext="프레임워크"
              />
            </Card>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-3 text-green-600">주요 강점</h3>
            <ul className="space-y-2">
              {summary.key_strengths.map((strength, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </Card>
          
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-3 text-orange-600">우선 개선 영역</h3>
            <ul className="space-y-2">
              {summary.priority_improvements.map((improvement, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-orange-500 mr-2">!</span>
                  <span>{improvement}</span>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </section>

      {/* Framework Analysis Grid */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-6 text-blue-600 border-b-2 border-blue-600 pb-2">
          프레임워크별 상세 분석
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {frameworks.map(frameworkId => {
            const framework = comprehensiveFrameworkUtils.getFramework(frameworkId)
            const result = analysisResult.individual_results[frameworkId]
            
            if (!framework || !result) return null

            return (
              <Card key={frameworkId} className="p-6">
                <div className="flex items-center mb-4">
                  <div 
                    className="w-4 h-4 rounded mr-3"
                    style={{ backgroundColor: framework.color }}
                  />
                  <div>
                    <h3 className="font-semibold text-lg">{framework.name_ko}</h3>
                    <p className="text-sm text-gray-600">{framework.description}</p>
                  </div>
                </div>
                
                {/* Framework-specific content would go here */}
                <div className="mt-4">
                  <div className="text-sm text-gray-600 mb-2">주요 지표</div>
                  {/* Add framework-specific metrics */}
                  <div className="bg-gray-50 p-3 rounded">
                    <div className="text-xs text-gray-500">
                      분석 완료 • {framework.analysis_levels}단계 분석
                    </div>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>
      </section>

      {/* Cross-Framework Insights */}
      {crossInsights.length > 0 && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold mb-6 text-blue-600 border-b-2 border-blue-600 pb-2">
            교차 분석 인사이트
          </h2>
          
          {showCharts && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <Card className="p-4">
                <PieChart
                  data={insightsData}
                  title="인사이트 유형 분포"
                  height={300}
                />
              </Card>
              <Card className="p-4">
                <div className="text-center py-8">
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {crossInsights.filter(i => i.significance === 'high').length}
                  </div>
                  <div className="text-sm text-gray-600">높은 중요도 인사이트</div>
                </div>
              </Card>
            </div>
          )}
          
          <div className="space-y-4">
            {crossInsights.map((insight, index) => (
              <Card key={index} className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold">
                    {insight.insight_type === 'correlation' ? '상관관계' : 
                     insight.insight_type === 'contradiction' ? '모순점' :
                     insight.insight_type === 'reinforcement' ? '강화효과' : '분석 공백'}
                  </h3>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    insight.significance === 'high' ? 'bg-red-100 text-red-800' :
                    insight.significance === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {insight.significance === 'high' ? '높음' : 
                     insight.significance === 'medium' ? '보통' : '낮음'}
                  </span>
                </div>
                
                <p className="text-gray-700 mb-3">{insight.description}</p>
                
                <div className="mb-3">
                  <span className="text-sm font-medium text-gray-600">관련 프레임워크: </span>
                  {insight.frameworks_involved.map(fw => {
                    const framework = comprehensiveFrameworkUtils.getFramework(fw)
                    return framework?.name_ko || fw
                  }).join(', ')}
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-600">권고사항:</span>
                  <ul className="mt-2 space-y-1">
                    {insight.recommendations.map((rec, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-start">
                        <span className="text-blue-500 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold mb-6 text-blue-600 border-b-2 border-blue-600 pb-2">
            개선 권고사항
          </h2>
          
          {showCharts && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <Card className="p-4">
                <DoughnutChart
                  data={recommendationsPriorityData}
                  title="권고사항 우선순위 분포"
                  height={300}
                  centerText={`${recommendations.length}개`}
                  centerSubtext="권고사항"
                />
              </Card>
              <Card className="p-4">
                <div className="space-y-4 py-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">
                      {recommendations.filter(r => r.priority === 'high').length}
                    </div>
                    <div className="text-sm text-gray-600">높은 우선순위</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {recommendations.filter(r => r.priority === 'medium').length}
                    </div>
                    <div className="text-sm text-gray-600">보통 우선순위</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {recommendations.filter(r => r.priority === 'low').length}
                    </div>
                    <div className="text-sm text-gray-600">낮은 우선순위</div>
                  </div>
                </div>
              </Card>
            </div>
          )}
          
          <div className="space-y-4">
            {recommendations
              .sort((a, b) => {
                const priorityOrder = { high: 3, medium: 2, low: 1 }
                return priorityOrder[b.priority] - priorityOrder[a.priority]
              })
              .map((rec, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-lg">
                      {index + 1}. {rec.recommendation}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                      rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {rec.priority === 'high' ? '높음' : 
                       rec.priority === 'medium' ? '보통' : '낮음'}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div>
                      <span className="text-sm font-medium text-gray-600">관련 프레임워크:</span>
                      <div className="text-sm text-gray-700 mt-1">
                        {rec.frameworks_source.map(fw => {
                          const framework = comprehensiveFrameworkUtils.getFramework(fw)
                          return framework?.name_ko || fw
                        }).join(', ')}
                      </div>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-600">구현 난이도:</span>
                      <div className={`text-sm mt-1 font-medium ${
                        rec.implementation_difficulty === 'easy' ? 'text-green-600' :
                        rec.implementation_difficulty === 'moderate' ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {rec.implementation_difficulty === 'easy' ? '쉬움' :
                         rec.implementation_difficulty === 'moderate' ? '보통' : '어려움'}
                      </div>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-gray-600">예상 효과:</span>
                      <div className={`text-sm mt-1 font-medium ${
                        rec.expected_impact === 'high' ? 'text-green-600' :
                        rec.expected_impact === 'medium' ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        {rec.expected_impact === 'high' ? '높음' :
                         rec.expected_impact === 'medium' ? '보통' : '낮음'}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
          </div>
        </section>
      )}

      {/* Metadata */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-6 text-blue-600 border-b-2 border-blue-600 pb-2">
          분석 정보
        </h2>
        
        <Card className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {metadata.teacher && (
              <div>
                <span className="text-sm font-medium text-gray-600">교사:</span>
                <div className="text-gray-700">{metadata.teacher}</div>
              </div>
            )}
            {metadata.subject && (
              <div>
                <span className="text-sm font-medium text-gray-600">과목:</span>
                <div className="text-gray-700">{metadata.subject}</div>
              </div>
            )}
            {metadata.grade && (
              <div>
                <span className="text-sm font-medium text-gray-600">학년:</span>
                <div className="text-gray-700">{metadata.grade}</div>
              </div>
            )}
            {metadata.duration && (
              <div>
                <span className="text-sm font-medium text-gray-600">수업 시간:</span>
                <div className="text-gray-700">{metadata.duration}</div>
              </div>
            )}
            <div>
              <span className="text-sm font-medium text-gray-600">분석 소요시간:</span>
              <div className="text-gray-700">{metadata.analysisTime}</div>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-600">생성 일시:</span>
              <div className="text-gray-700">
                {new Date().toLocaleString('ko-KR')}
              </div>
            </div>
          </div>
        </Card>
      </section>

      {/* PDF Export Section */}
      {showPDFExport && (
        <section className="mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-2">PDF 내보내기</h3>
                <p className="text-gray-600 text-sm">
                  이 종합 분석 보고서를 PDF 파일로 저장하거나 미리보기할 수 있습니다.
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
                  html={document.querySelector('.comprehensive-report-template')?.outerHTML || ''}
                  filename={pdfExportUtils.generateFilename('comprehensive_report', metadata)}
                  title="종합 보고서 PDF 내보내기"
                  defaultOptions={pdfExportUtils.getReportTypeOptions('comprehensive') as any}
                  showOptionsDialog={true}
                  showProgress={true}
                  showEstimation={true}
                  variant="default"
                  className="bg-blue-600 hover:bg-blue-700 text-white"
                  onExportStart={() => console.log('PDF 내보내기 시작')}
                  onExportComplete={(success, result) => {
                    if (success) {
                      console.log('PDF 내보내기 완료:', result)
                    } else {
                      console.error('PDF 내보내기 실패:', result)
                    }
                  }}
                />
              </div>
            </div>
          </Card>
        </section>
      )}

      {/* PDF Preview Section */}
      {showPDFExport && enablePreview && showPreview && (
        <section className="mb-8">
          <PDFPreview
            html={document.querySelector('.comprehensive-report-template')?.outerHTML || ''}
            options={pdfExportUtils.getReportTypeOptions('comprehensive') as any}
            filename={pdfExportUtils.generateFilename('comprehensive_report_preview', metadata)}
            showControls={true}
            showInfo={true}
            autoGenerate={false}
            onExport={() => setShowPreview(false)}
            className="border rounded-lg"
          />
        </section>
      )}
    </div>
  )
}

export default ComprehensiveReportTemplate