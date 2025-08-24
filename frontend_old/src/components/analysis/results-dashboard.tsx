// Results Dashboard Component for displaying comprehensive analysis results
// Provides tabbed interface for individual framework results, comparisons, and insights

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { 
  ComprehensiveAnalysisResult,
  FrameworkSpecificResult,
  comprehensiveFrameworkUtils,
  CBILAnalysisResult,
  QTAAnalysisResult,
  SEIAnalysisResult
} from '@/types/comprehensive-analysis'
import {
  BarChartIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  AlertCircleIcon,
  CheckCircleIcon,
  InfoIcon,
  DownloadIcon,
  ShareIcon,
  FilterIcon,
  EyeIcon
} from 'lucide-react'

interface ResultsDashboardProps {
  results: ComprehensiveAnalysisResult
  selectedFrameworks: string[]
}

interface FrameworkResultCardProps {
  frameworkId: string
  result: FrameworkSpecificResult
  isExpanded?: boolean
  onToggleExpanded?: () => void
}

// Individual framework result card component
function FrameworkResultCard({ 
  frameworkId, 
  result, 
  isExpanded = false, 
  onToggleExpanded 
}: FrameworkResultCardProps) {
  const framework = comprehensiveFrameworkUtils.getFramework(frameworkId)
  
  if (!framework) return null

  // Extract score based on framework type
  const getScore = (result: FrameworkSpecificResult): number => {
    if ('cognitive_load_score' in result) return result.cognitive_load_score
    if ('engagement_score' in result) return result.engagement_score
    if ('coherence_score' in result) return result.coherence_score
    if ('effectiveness_score' in result) return result.effectiveness_score
    if ('overall_score' in result) return (result as any).overall_score
    return 0
  }

  const score = getScore(result)
  const scoreColor = score >= 80 ? 'text-green-600' : score >= 60 ? 'text-yellow-600' : 'text-red-600'

  return (
    <Card className="h-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="p-2 rounded-lg"
              style={{ backgroundColor: `${framework.color}15` }}
            >
              <BarChartIcon 
                className="h-5 w-5"
                style={{ color: framework.color }}
              />
            </div>
            <div>
              <CardTitle className="text-lg">{framework.name_ko}</CardTitle>
              <CardDescription className="text-sm">{framework.description}</CardDescription>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-2xl font-bold ${scoreColor}`}>
              {score.toFixed(1)}
            </div>
            <div className="text-xs text-gray-500">/ 100</div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Score Progress Bar */}
        <div className="mb-4">
          <Progress value={score} className="h-2" />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>낮음</span>
            <span>보통</span>
            <span>높음</span>
          </div>
        </div>

        {/* Framework-specific content */}
        <div className="space-y-3">
          {renderFrameworkSpecificContent(frameworkId, result)}
        </div>

        {/* Recommendations Preview */}
        {result && 'recommendations' in result && result.recommendations && (
          <div className="mt-4">
            <h4 className="font-medium text-sm mb-2">주요 권장사항</h4>
            <div className="space-y-1">
              {result.recommendations.slice(0, isExpanded ? result.recommendations.length : 2).map((rec, index) => (
                <div key={index} className="text-xs text-gray-600 flex items-start gap-2">
                  <div className="w-1 h-1 bg-gray-400 rounded-full mt-2 flex-shrink-0" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
            {result.recommendations.length > 2 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleExpanded}
                className="mt-2 p-0 h-auto text-xs"
              >
                {isExpanded ? '간략히 보기' : `${result.recommendations.length - 2}개 더 보기`}
                <EyeIcon className="h-3 w-3 ml-1" />
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Render framework-specific visualizations and metrics
function renderFrameworkSpecificContent(frameworkId: string, result: FrameworkSpecificResult) {
  switch (frameworkId) {
    case 'cbil':
      const cibilResult = result as CBILAnalysisResult
      return (
        <div className="space-y-2">
          <h4 className="font-medium text-sm">인지 수준 분포</h4>
          <div className="space-y-1">
            {Object.entries(cibilResult.cbil_levels || {}).map(([level, score]) => (
              <div key={level} className="flex justify-between items-center text-xs">
                <span className="capitalize">{level.replace('_', ' ')}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-1">
                    <div 
                      className="bg-blue-500 h-1 rounded-full"
                      style={{ width: `${score}%` }}
                    />
                  </div>
                  <span className="w-8 text-right">{score}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )

    case 'qta':
      const qtaResult = result as QTAAnalysisResult
      return (
        <div className="space-y-2">
          <h4 className="font-medium text-sm">질문 유형 분포</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.entries(qtaResult.question_distribution || {}).map(([type, count]) => (
              <div key={type} className="flex justify-between">
                <span>{type}</span>
                <Badge variant="outline" className="text-xs">{count}</Badge>
              </div>
            ))}
          </div>
        </div>
      )

    case 'sei':
      const seiResult = result as SEIAnalysisResult
      return (
        <div className="space-y-2">
          <h4 className="font-medium text-sm">참여 수준</h4>
          <div className="space-y-1">
            {Object.entries(seiResult.engagement_levels || {}).map(([level, percentage]) => (
              <div key={level} className="flex justify-between items-center text-xs">
                <span>{level.replace('_', ' ')}</span>
                <span>{percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      )

    default:
      return (
        <div className="text-xs text-gray-500 text-center py-4">
          상세 분석 결과가 준비 중입니다.
        </div>
      )
  }
}

export function ResultsDashboard({ results, selectedFrameworks }: ResultsDashboardProps) {
  const [expandedFrameworks, setExpandedFrameworks] = useState<Set<string>>(new Set())
  const [activeTab, setActiveTab] = useState('individual')

  const toggleExpanded = (frameworkId: string) => {
    setExpandedFrameworks(prev => {
      const newSet = new Set(prev)
      if (newSet.has(frameworkId)) {
        newSet.delete(frameworkId)
      } else {
        newSet.add(frameworkId)
      }
      return newSet
    })
  }

  const getOverallTrend = () => {
    const score = results.overall_summary.overall_score
    if (score >= 80) return { icon: TrendingUpIcon, color: 'text-green-600', label: '우수' }
    if (score >= 60) return { icon: InfoIcon, color: 'text-yellow-600', label: '보통' }
    return { icon: TrendingDownIcon, color: 'text-red-600', label: '개선 필요' }
  }

  const trend = getOverallTrend()
  const TrendIcon = trend.icon

  return (
    <div className="space-y-6">
      {/* Overall Summary Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">분석 결과 종합</CardTitle>
              <CardDescription>
                {results.frameworks_analyzed.length}개 프레임워크 분석 완료 • 
                {new Date(results.analysis_metadata.created_at).toLocaleDateString('ko-KR')}
              </CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className={`text-3xl font-bold ${trend.color}`}>
                  {results.overall_summary.overall_score.toFixed(1)}
                </div>
                <div className="flex items-center gap-1">
                  <TrendIcon className={`h-4 w-4 ${trend.color}`} />
                  <span className={`text-sm font-medium ${trend.color}`}>
                    {trend.label}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <DownloadIcon className="h-4 w-4 mr-2" />
                  PDF 다운로드
                </Button>
                <Button variant="outline" size="sm">
                  <ShareIcon className="h-4 w-4 mr-2" />
                  공유
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Main Results Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="individual">개별 프레임워크</TabsTrigger>
          <TabsTrigger value="comparison">비교 분석</TabsTrigger>
          <TabsTrigger value="insights">통합 인사이트</TabsTrigger>
          <TabsTrigger value="recommendations">종합 권장사항</TabsTrigger>
        </TabsList>

        {/* Individual Framework Results */}
        <TabsContent value="individual" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(results.individual_results).map(([frameworkId, result]) => (
              <FrameworkResultCard
                key={frameworkId}
                frameworkId={frameworkId}
                result={result}
                isExpanded={expandedFrameworks.has(frameworkId)}
                onToggleExpanded={() => toggleExpanded(frameworkId)}
              />
            ))}
          </div>
        </TabsContent>

        {/* Comparison Analysis */}
        <TabsContent value="comparison" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>프레임워크 간 비교</CardTitle>
              <CardDescription>
                각 프레임워크의 점수와 특성을 비교합니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(results.individual_results).map(([frameworkId, result]) => {
                  const framework = comprehensiveFrameworkUtils.getFramework(frameworkId)
                  const score = 'cognitive_load_score' in result ? result.cognitive_load_score :
                               'engagement_score' in result ? result.engagement_score :
                               'coherence_score' in result ? result.coherence_score :
                               'effectiveness_score' in result ? result.effectiveness_score : 0

                  return (
                    <div key={frameworkId} className="flex items-center gap-4">
                      <div className="w-32 text-sm font-medium truncate">
                        {framework?.name_ko}
                      </div>
                      <div className="flex-1">
                        <Progress value={score} className="h-2" />
                      </div>
                      <div className="w-16 text-right text-sm font-medium">
                        {score.toFixed(1)}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cross-Framework Insights */}
        <TabsContent value="insights" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Strengths */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                  주요 강점
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {results.overall_summary.key_strengths.map((strength, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-sm">{strength}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Areas for Improvement */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertCircleIcon className="h-5 w-5 text-orange-600" />
                  개선 영역
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {results.overall_summary.priority_improvements.map((improvement, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0" />
                      <span className="text-sm">{improvement}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Cross-Framework Insights */}
          {results.cross_framework_insights.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>프레임워크 간 연관성 분석</CardTitle>
                <CardDescription>
                  여러 프레임워크에서 발견된 패턴과 상관관계입니다.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.cross_framework_insights.map((insight, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">
                          {insight.frameworks_involved.join(' + ')} 연관성
                        </h4>
                        <Badge 
                          variant={insight.significance === 'high' ? 'default' : 'secondary'}
                        >
                          {insight.significance === 'high' ? '높음' : 
                           insight.significance === 'medium' ? '보통' : '낮음'}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">
                        {insight.description}
                      </p>
                      <div className="space-y-1">
                        {insight.recommendations.map((rec, recIndex) => (
                          <div key={recIndex} className="flex items-start gap-2 text-xs">
                            <div className="w-1 h-1 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                            <span>{rec}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Comprehensive Recommendations */}
        <TabsContent value="recommendations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>종합 권장사항</CardTitle>
              <CardDescription>
                우선순위에 따라 정리된 실행 가능한 개선 방안입니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.recommendations.map((rec, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge 
                          variant={rec.priority === 'high' ? 'destructive' : 
                                   rec.priority === 'medium' ? 'default' : 'secondary'}
                        >
                          {rec.priority === 'high' ? '높은 우선순위' :
                           rec.priority === 'medium' ? '보통 우선순위' : '낮은 우선순위'}
                        </Badge>
                        <Badge variant="outline">
                          {rec.implementation_difficulty === 'easy' ? '쉬움' :
                           rec.implementation_difficulty === 'moderate' ? '보통' : '어려움'}
                        </Badge>
                      </div>
                      <Badge variant="secondary">
                        {rec.expected_impact === 'high' ? '높은 효과' :
                         rec.expected_impact === 'medium' ? '보통 효과' : '낮은 효과'}
                      </Badge>
                    </div>
                    
                    <p className="text-sm mb-2">{rec.recommendation}</p>
                    
                    <div className="text-xs text-gray-500">
                      관련 프레임워크: {rec.frameworks_source.map(id => 
                        comprehensiveFrameworkUtils.getFramework(id)?.name_ko
                      ).join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}