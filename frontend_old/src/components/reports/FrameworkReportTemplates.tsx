'use client'

import React from 'react'
import { FrameworkSpecificResult, comprehensiveFrameworkUtils } from '../../types/comprehensive-analysis'
import { BarChart, PieChart, RadarChart, DoughnutChart } from '../charts'
import { Card } from '../ui/card'
import { Badge } from '../ui/badge'

// CBIL Framework Report Template
interface CBILReportTemplateProps {
  result: any // CBILAnalysisResult
  showCharts?: boolean
  className?: string
}

export const CBILReportTemplate: React.FC<CBILReportTemplateProps> = ({
  result,
  showCharts = true,
  className = ''
}) => {
  const levels = result.cbil_levels
  
  const levelData = {
    labels: ['단순확인', '사실회상', '개념설명', '분석사고', '종합이해', '평가판단', '창의적용'],
    datasets: [{
      label: '비율 (%)',
      data: [
        levels.simple_confirmation * 100,
        levels.fact_recall * 100,
        levels.concept_explanation * 100,
        levels.analytical_thinking * 100,
        levels.comprehensive_understanding * 100,
        levels.evaluative_judgment * 100,
        levels.creative_application * 100
      ],
      backgroundColor: [
        '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', 
        '#ef4444', '#06b6d4', '#84cc16'
      ],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  const complexityData = {
    labels: ['낮은 복잡성 (1-3)', '중간 복잡성 (4-5)', '높은 복잡성 (6-7)'],
    datasets: [{
      data: [
        (levels.simple_confirmation + levels.fact_recall + levels.concept_explanation) * 100,
        (levels.analytical_thinking + levels.comprehensive_understanding) * 100,
        (levels.evaluative_judgment + levels.creative_application) * 100
      ],
      backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  return (
    <div className={`cbil-report-template ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-blue-600 mb-2">
          인지적 부담 기반 교육언어 분석 (CBIL)
        </h2>
        <p className="text-gray-600">
          교육 언어의 인지적 복잡성을 7단계로 분류하여 학습자의 인지 부하를 측정합니다.
        </p>
      </div>

      {/* Overall Score */}
      <Card className="p-6 mb-6">
        <div className="text-center">
          <div className="text-4xl font-bold text-blue-600 mb-2">
            {Math.round(result.cognitive_load_score)}
          </div>
          <div className="text-lg text-gray-600">인지 부하 점수 (0-100)</div>
          <div className="mt-4">
            <Badge variant={
              result.cognitive_load_score >= 80 ? 'destructive' :
              result.cognitive_load_score >= 60 ? 'secondary' : 'default'
            }>
              {result.cognitive_load_score >= 80 ? '높은 인지부하' :
               result.cognitive_load_score >= 60 ? '적정 인지부하' : '낮은 인지부하'}
            </Badge>
          </div>
        </div>
      </Card>

      {/* Charts */}
      {showCharts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card className="p-4">
            <BarChart
              data={levelData}
              title="인지 수준별 분포"
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
              data={complexityData}
              title="복잡성 수준 분포"
              height={300}
              centerText={`${Math.round(result.cognitive_load_score)}`}
              centerSubtext="인지부하"
            />
          </Card>
        </div>
      )}

      {/* Detailed Breakdown */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">상세 분석</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">인지 수준</th>
                <th className="text-center py-2">비율</th>
                <th className="text-left py-2">특성</th>
                <th className="text-left py-2">교육적 의미</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b">
                <td className="py-3 font-medium">1. 단순 확인</td>
                <td className="text-center">{Math.round(levels.simple_confirmation * 100)}%</td>
                <td>기본적인 이해 확인</td>
                <td>수동적 참여 유도</td>
              </tr>
              <tr className="border-b">
                <td className="py-3 font-medium">2. 사실 회상</td>
                <td className="text-center">{Math.round(levels.fact_recall * 100)}%</td>
                <td>정보 기억 및 재생</td>
                <td>기초 지식 점검</td>
              </tr>
              <tr className="border-b">
                <td className="py-3 font-medium">3. 개념 설명</td>
                <td className="text-center">{Math.round(levels.concept_explanation * 100)}%</td>
                <td>개념 이해 및 설명</td>
                <td>이해도 심화</td>
              </tr>
              <tr className="border-b">
                <td className="py-3 font-medium">4. 분석적 사고</td>
                <td className="text-center">{Math.round(levels.analytical_thinking * 100)}%</td>
                <td>논리적 분석 능력</td>
                <td>고차원적 사고 유도</td>
              </tr>
              <tr className="border-b">
                <td className="py-3 font-medium">5. 종합적 이해</td>
                <td className="text-center">{Math.round(levels.comprehensive_understanding * 100)}%</td>
                <td>통합적 사고</td>
                <td>전체적 조망 능력</td>
              </tr>
              <tr className="border-b">
                <td className="py-3 font-medium">6. 평가적 판단</td>
                <td className="text-center">{Math.round(levels.evaluative_judgment * 100)}%</td>
                <td>비판적 평가</td>
                <td>메타인지 발달</td>
              </tr>
              <tr>
                <td className="py-3 font-medium">7. 창의적 적용</td>
                <td className="text-center">{Math.round(levels.creative_application * 100)}%</td>
                <td>창의적 문제해결</td>
                <td>응용 및 전이</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      {/* Recommendations */}
      {result.recommendations && result.recommendations.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">개선 권고사항</h3>
          <ul className="space-y-3">
            {result.recommendations.map((rec: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-500 mr-2 mt-1">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  )
}

// QTA Framework Report Template
interface QTAReportTemplateProps {
  result: any // QTAAnalysisResult
  showCharts?: boolean
  className?: string
}

export const QTAReportTemplate: React.FC<QTAReportTemplateProps> = ({
  result,
  showCharts = true,
  className = ''
}) => {
  const distribution = result.question_distribution
  
  const questionTypeData = {
    labels: ['폐쇄형', '개방형', '확인형', '유도형', '탐구형', '창의형', '메타인지형'],
    datasets: [{
      data: [
        distribution.closed * 100,
        distribution.open * 100,
        distribution.checking * 100,
        distribution.leading * 100,
        distribution.inquiry * 100,
        distribution.creative * 100,
        distribution.metacognitive * 100
      ],
      backgroundColor: [
        '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', 
        '#ef4444', '#06b6d4', '#84cc16'
      ],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  const cognitiveEngagementData = {
    labels: ['인지수준', '참여도', '질문밀도'],
    datasets: [{
      label: '점수',
      data: [
        result.cognitive_level_average * 10,
        result.engagement_score,
        result.question_density * 100
      ],
      backgroundColor: 'rgba(139, 92, 246, 0.2)',
      borderColor: '#8b5cf6',
      pointBackgroundColor: '#8b5cf6',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2
    }]
  }

  return (
    <div className={`qta-report-template ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-purple-600 mb-2">
          질문 유형 분석 (QTA)
        </h2>
        <p className="text-gray-600">
          교사 질문의 유형과 패턴을 분석하여 학습자 참여도 향상 방안을 제시합니다.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round(result.question_density * 100)}
          </div>
          <div className="text-sm text-gray-600">질문 밀도</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round(result.cognitive_level_average * 10) / 10}
          </div>
          <div className="text-sm text-gray-600">평균 인지수준</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round(result.engagement_score)}
          </div>
          <div className="text-sm text-gray-600">참여도 점수</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round(result.patterns.follow_up_rate * 100)}%
          </div>
          <div className="text-sm text-gray-600">후속질문 비율</div>
        </Card>
      </div>

      {/* Charts */}
      {showCharts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card className="p-4">
            <PieChart
              data={questionTypeData}
              title="질문 유형 분포"
              height={300}
            />
          </Card>
          <Card className="p-4">
            <RadarChart
              data={cognitiveEngagementData}
              title="인지 참여 패턴"
              height={300}
              maxValue={100}
            />
          </Card>
        </div>
      )}

      {/* Question Analysis */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">질문 유형별 분석</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium mb-2">낮은 인지수준 질문</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>폐쇄형</span>
                <span>{Math.round(distribution.closed * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span>확인형</span>
                <span>{Math.round(distribution.checking * 100)}%</span>
              </div>
            </div>
          </div>
          <div>
            <h4 className="font-medium mb-2">높은 인지수준 질문</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>탐구형</span>
                <span>{Math.round(distribution.inquiry * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span>창의형</span>
                <span>{Math.round(distribution.creative * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span>메타인지형</span>
                <span>{Math.round(distribution.metacognitive * 100)}%</span>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Pattern Analysis */}
      {result.patterns && (
        <Card className="p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">질문 패턴 분석</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium">순서 분석</h4>
              <ul className="mt-2 space-y-1">
                {result.patterns.sequence_analysis.map((pattern: string, index: number) => (
                  <li key={index} className="text-sm text-gray-700">• {pattern}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="font-medium">대기 시간 지표</h4>
              <p className="text-sm text-gray-700">
                평균 대기 시간: {Math.round(result.patterns.wait_time_indicators * 10) / 10}초
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Recommendations */}
      {result.recommendations && result.recommendations.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">개선 권고사항</h3>
          <ul className="space-y-3">
            {result.recommendations.map((rec: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="text-purple-500 mr-2 mt-1">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  )
}

// SEI Framework Report Template
interface SEIReportTemplateProps {
  result: any // SEIAnalysisResult
  showCharts?: boolean
  className?: string
}

export const SEIReportTemplate: React.FC<SEIReportTemplateProps> = ({
  result,
  showCharts = true,
  className = ''
}) => {
  const levels = result.engagement_levels
  const metrics = result.interaction_metrics
  
  const engagementData = {
    labels: ['수동청취', '단순응답', '질문참여', '토론참여', '협력활동', '주도발표'],
    datasets: [{
      label: '참여도 (%)',
      data: [
        levels.passive_listening * 100,
        levels.simple_response * 100,
        levels.question_participation * 100,
        levels.discussion_participation * 100,
        levels.collaborative_activity * 100,
        levels.leading_presentation * 100
      ],
      backgroundColor: 'rgba(16, 185, 129, 0.2)',
      borderColor: '#10b981',
      pointBackgroundColor: '#10b981',
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2
    }]
  }

  const interactionData = {
    labels: ['교사 발화', '학생 응답'],
    datasets: [{
      data: [
        metrics.teacher_talk_ratio * 100,
        metrics.student_response_ratio * 100
      ],
      backgroundColor: ['#3b82f6', '#10b981'],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  }

  return (
    <div className={`sei-report-template ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-green-600 mb-2">
          학습자 참여도 지표 분석 (SEI)
        </h2>
        <p className="text-gray-600">
          학습자의 능동적 참여 정도와 참여 유형을 측정하여 수업 개선점을 도출합니다.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {Math.round(metrics.teacher_talk_ratio * 100)}%
          </div>
          <div className="text-sm text-gray-600">교사 발화 비율</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {Math.round(metrics.student_response_ratio * 100)}%
          </div>
          <div className="text-sm text-gray-600">학생 응답 비율</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {Math.round(result.participation_equity * 100)}
          </div>
          <div className="text-sm text-gray-600">참여 형평성</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {result.engagement_trend === 'increasing' ? '증가' :
             result.engagement_trend === 'stable' ? '안정' : '감소'}
          </div>
          <div className="text-sm text-gray-600">참여도 추이</div>
        </Card>
      </div>

      {/* Charts */}
      {showCharts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card className="p-4">
            <RadarChart
              data={engagementData}
              title="학습자 참여 패턴"
              height={300}
              maxValue={100}
            />
          </Card>
          <Card className="p-4">
            <DoughnutChart
              data={interactionData}
              title="발화 비율 분석"
              height={300}
              centerText="상호작용"
              centerSubtext="패턴"
            />
          </Card>
        </div>
      )}

      {/* Detailed Analysis */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">참여 수준별 분석</h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium">수동적 청취</span>
            <div className="flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                <div 
                  className="bg-red-500 h-2 rounded-full" 
                  style={{ width: `${levels.passive_listening * 100}%` }}
                />
              </div>
              <span className="text-sm">{Math.round(levels.passive_listening * 100)}%</span>
            </div>
          </div>
          
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium">단순 응답</span>
            <div className="flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                <div 
                  className="bg-orange-500 h-2 rounded-full" 
                  style={{ width: `${levels.simple_response * 100}%` }}
                />
              </div>
              <span className="text-sm">{Math.round(levels.simple_response * 100)}%</span>
            </div>
          </div>
          
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium">질문 참여</span>
            <div className="flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full" 
                  style={{ width: `${levels.question_participation * 100}%` }}
                />
              </div>
              <span className="text-sm">{Math.round(levels.question_participation * 100)}%</span>
            </div>
          </div>
          
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium">토론 참여</span>
            <div className="flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ width: `${levels.discussion_participation * 100}%` }}
                />
              </div>
              <span className="text-sm">{Math.round(levels.discussion_participation * 100)}%</span>
            </div>
          </div>
          
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium">협력 활동</span>
            <div className="flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: `${levels.collaborative_activity * 100}%` }}
                />
              </div>
              <span className="text-sm">{Math.round(levels.collaborative_activity * 100)}%</span>
            </div>
          </div>
          
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
            <span className="font-medium">주도적 발표</span>
            <div className="flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                <div 
                  className="bg-purple-500 h-2 rounded-full" 
                  style={{ width: `${levels.leading_presentation * 100}%` }}
                />
              </div>
              <span className="text-sm">{Math.round(levels.leading_presentation * 100)}%</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Recommendations */}
      {result.recommendations && result.recommendations.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">개선 권고사항</h3>
          <ul className="space-y-3">
            {result.recommendations.map((rec: string, index: number) => (
              <li key={index} className="flex items-start">
                <span className="text-green-500 mr-2 mt-1">•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  )
}

// Export all templates
export const FrameworkReportTemplates = {
  cbil: CBILReportTemplate,
  qta: QTAReportTemplate,
  sei: SEIReportTemplate
}

export default FrameworkReportTemplates