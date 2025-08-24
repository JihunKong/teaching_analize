'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useAnalysisResult, useCBILInterpretation } from '@/hooks/useAnalysis'
import { CBILAnalysisResult } from '@/types/analysis'
import { CBIL_LEVELS } from '@/types/analysis'
import { formatDateTime } from '@/lib/utils'
import { 
  BarChart3Icon, 
  TrendingUpIcon, 
  LightbulbIcon,
  DownloadIcon,
  ShareIcon,
  FileTextIcon,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

interface AnalysisResultProps {
  analysisId: string
  showActions?: boolean
  compact?: boolean
}

export function AnalysisResult({ 
  analysisId, 
  showActions = true, 
  compact = false 
}: AnalysisResultProps) {
  const { data: analysis, isLoading, error } = useAnalysisResult(analysisId)
  const interpretation = useCBILInterpretation(
    analysis?.cbil_scores
  )

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4" />
          <div className="h-32 bg-gray-200 rounded mb-4" />
          <div className="h-20 bg-gray-200 rounded" />
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-8 text-red-600">
        <p>분석 결과를 불러올 수 없습니다.</p>
        <p className="text-sm mt-1">잠시 후 다시 시도해주세요.</p>
      </div>
    )
  }

  // Display CBIL analysis results (simplified for current API)
  // TODO: Update when framework-aware API is implemented
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">분석 결과</h3>
        <Badge>
          CBIL
        </Badge>
      </div>
      <p className="text-gray-600">
        이 분석 유형에 대한 상세 표시는 개발 중입니다.
      </p>
    </div>
  )
}

// CBIL-specific analysis display component
function CBILAnalysisDisplay({ 
  result, 
  showActions, 
  compact 
}: { 
  result: CBILAnalysisResult
  showActions: boolean
  compact: boolean
}) {
  // Prepare data for charts
  const barChartData = CBIL_LEVELS.map(level => ({
    level: level.level,
    name: level.name,
    score: (result.cbil_scores[level.level.toString()] || 0) * 100,
    weight: level.weight,
  }))

  const radarChartData = barChartData

  const pieChartData = [
    { name: '기초 수준 (1-3)', value: result.level_distribution.low_level * 100, color: '#fbbf24' },
    { name: '중급 수준 (4-5)', value: result.level_distribution.mid_level * 100, color: '#60a5fa' },
    { name: '고급 수준 (6-7)', value: result.level_distribution.high_level * 100, color: '#34d399' },
  ]

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600'
    if (score >= 0.4) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (compact) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {result.overall_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-500">평균 점수</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {result.dominant_level.level}
            </div>
            <div className="text-sm text-gray-500">주요 수준</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {result.recommendations.length}
            </div>
            <div className="text-sm text-gray-500">개선사항</div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <BarChart3Icon className="h-6 w-6 mr-2" />
            CBIL 분석 결과
          </h2>
          <p className="text-gray-600 mt-1">
            분석 완료 시간: {formatDateTime(result.created_at)}
          </p>
        </div>
        {showActions && (
          <div className="flex space-x-2">
            <Button variant="outline" size="sm">
              <ShareIcon className="h-4 w-4 mr-1" />
              공유
            </Button>
            <Button variant="outline" size="sm">
              <DownloadIcon className="h-4 w-4 mr-1" />
              다운로드
            </Button>
          </div>
        )}
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="p-4 text-center">
            <TrendingUpIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-900">
              {result.overall_score.toFixed(1)}
            </div>
            <div className="text-sm text-blue-700">전체 평균 점수</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="p-4 text-center">
            <Badge className="bg-purple-100 text-purple-800 mb-2">
              Level {result.dominant_level.level}
            </Badge>
            <div className="text-lg font-bold text-purple-900">
              {result.dominant_level.name}
            </div>
            <div className="text-sm text-purple-700">주요 인지 수준</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-900">
              {(result.level_distribution.high_level * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-green-700">고차원 사고</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <CardContent className="p-4 text-center">
            <LightbulbIcon className="h-8 w-8 text-orange-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-orange-900">
              {result.recommendations.length}
            </div>
            <div className="text-sm text-orange-700">개선 제안</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>CBIL 수준별 점수</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="level" />
                <YAxis />
                <Tooltip
                  formatter={(value: any, name: any) => [`${value.toFixed(1)}%`, 'Score']}
                  labelFormatter={(level) => `Level ${level}: ${barChartData[level - 1]?.name}`}
                />
                <Bar dataKey="score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>수준별 분포</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: any) => `${value.toFixed(1)}%`} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Radar Chart */}
      <Card>
        <CardHeader>
          <CardTitle>인지적 복잡성 프로필</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarChartData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="name" tick={{ fontSize: 12 }} />
              <PolarRadiusAxis 
                angle={90} 
                domain={[0, 100]} 
                tick={{ fontSize: 10 }}
              />
              <Radar
                name="CBIL Score"
                dataKey="score"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
                strokeWidth={2}
              />
              <Tooltip formatter={(value: any) => `${value.toFixed(1)}%`} />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Detailed Level Analysis */}
      <Card>
        <CardHeader>
          <CardTitle>상세 수준 분석</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {CBIL_LEVELS.map((level) => {
              const score = result.cbil_scores[level.level.toString()] || 0
              const percentage = score * 100
              
              return (
                <div key={level.level} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <Badge variant="outline">
                        Level {level.level}
                      </Badge>
                      <h4 className="font-medium">{level.name}</h4>
                    </div>
                    <span className={`text-lg font-bold ${getScoreColor(score)}`}>
                      {percentage.toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {level.description}
                  </p>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      {result.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <LightbulbIcon className="h-5 w-5 mr-2" />
              개선 제안사항
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {result.recommendations.map((recommendation, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
                >
                  <div className="w-6 h-6 bg-yellow-500 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {index + 1}
                  </div>
                  <p className="text-gray-800">{recommendation}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Text Preview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <FileTextIcon className="h-5 w-5 mr-2" />
            분석된 텍스트 미리보기
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-800 whitespace-pre-wrap">
              {result.text_preview}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}