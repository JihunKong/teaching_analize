'use client'

import React, { useState } from 'react'
import { ComprehensiveAnalysisResult, PrioritizedRecommendation, comprehensiveFrameworkUtils } from '../../types/comprehensive-analysis'
import { Card } from '../ui/card'
import { Badge } from '../ui/badge'
import { Progress } from '../ui/progress'
import { Button } from '../ui/button'
import { PDFExportButton, PDFPreview } from '../pdf'
import { pdfExportUtils } from '../../lib/pdf-export'
import { 
  Calendar, 
  CheckCircle, 
  Clock, 
  Target, 
  TrendingUp, 
  Users, 
  BookOpen, 
  Lightbulb,
  AlertTriangle,
  Star,
  ArrowRight,
  Plus,
  Eye,
  Download
} from 'lucide-react'

interface ActionPlanTemplateProps {
  analysisResult: ComprehensiveAnalysisResult
  metadata: {
    teacher?: string
    subject?: string
    grade?: string
    duration?: string
    analysisTime: string
  }
  timeframe?: '1week' | '1month' | '1semester' | 'custom'
  className?: string
  showPDFExport?: boolean
  enablePreview?: boolean
}

interface ActionItem {
  id: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  timeline: 'immediate' | 'short' | 'medium' | 'long'
  difficulty: 'easy' | 'moderate' | 'challenging'
  impact: 'high' | 'medium' | 'low'
  frameworks: string[]
  steps: string[]
  resources: string[]
  successMetrics: string[]
  estimatedHours: number
}

const ActionPlanTemplate: React.FC<ActionPlanTemplateProps> = ({
  analysisResult,
  metadata,
  timeframe = '1month',
  className = '',
  showPDFExport = true,
  enablePreview = false
}) => {
  const [showPreview, setShowPreview] = useState(false)
  const recommendations = analysisResult.recommendations
  const summary = analysisResult.overall_summary

  // Transform recommendations into structured action items
  const actionItems: ActionItem[] = recommendations.map((rec, index) => ({
    id: `action_${index + 1}`,
    title: rec.recommendation,
    description: `${rec.frameworks_source.map(fw => {
      const framework = comprehensiveFrameworkUtils.getFramework(fw)
      return framework?.name_ko || fw
    }).join(', ')} 영역 개선을 위한 실행 계획`,
    priority: rec.priority,
    timeline: rec.priority === 'high' ? 'immediate' : 
              rec.priority === 'medium' ? 'short' : 'medium',
    difficulty: rec.implementation_difficulty,
    impact: rec.expected_impact,
    frameworks: rec.frameworks_source,
    steps: generateActionSteps(rec),
    resources: generateResources(rec),
    successMetrics: generateSuccessMetrics(rec),
    estimatedHours: estimateHours(rec)
  }))

  // Generate action steps based on recommendation
  function generateActionSteps(rec: PrioritizedRecommendation): string[] {
    const baseSteps = [
      '현재 상태 평가 및 기준선 설정',
      '구체적인 실행 계획 수립',
      '필요한 자료 및 도구 준비',
      '실행 및 모니터링',
      '결과 평가 및 피드백 반영'
    ]
    
    // Add framework-specific steps
    const frameworkSteps: string[] = []
    rec.frameworks_source.forEach(fw => {
      switch (fw) {
        case 'cbil':
          frameworkSteps.push('학습자 인지 부하 수준 모니터링')
          frameworkSteps.push('질문 복잡도 단계적 조정')
          break
        case 'qta':
          frameworkSteps.push('질문 유형 분석 및 다양화')
          frameworkSteps.push('대기 시간 확보 및 후속 질문 연습')
          break
        case 'sei':
          frameworkSteps.push('학습자 참여 기회 확대')
          frameworkSteps.push('상호작용 패턴 개선')
          break
        // Add more framework-specific steps
      }
    })
    
    return [...baseSteps, ...frameworkSteps]
  }

  // Generate resources based on recommendation
  function generateResources(rec: PrioritizedRecommendation): string[] {
    const resources = [
      '교육 전문서적 및 연구자료',
      '온라인 교육 플랫폼 및 도구',
      '동료 교사와의 협력 네트워크'
    ]
    
    // Add framework-specific resources
    rec.frameworks_source.forEach(fw => {
      const framework = comprehensiveFrameworkUtils.getFramework(fw)
      if (framework) {
        resources.push(`${framework.name_ko} 관련 전문 자료`)
      }
    })
    
    if ((rec as any).difficulty === 'challenging') {
      resources.push('전문가 컨설팅 및 멘토링')
      resources.push('교사 연수 프로그램 참여')
    }
    
    return resources
  }

  // Generate success metrics
  function generateSuccessMetrics(rec: PrioritizedRecommendation): string[] {
    const metrics = [
      '학습자 참여도 증가',
      '교육 목표 달성도 향상',
      '교실 분위기 개선'
    ]
    
    // Add framework-specific metrics
    rec.frameworks_source.forEach(fw => {
      switch (fw) {
        case 'cbil':
          metrics.push('고차원적 사고 질문 비율 증가')
          break
        case 'qta':
          metrics.push('다양한 질문 유형 사용률 향상')
          break
        case 'sei':
          metrics.push('학습자 능동적 참여 시간 증가')
          break
        // Add more metrics
      }
    })
    
    return metrics
  }

  // Estimate hours needed
  function estimateHours(rec: PrioritizedRecommendation): number {
    let hours = 5 // Base hours
    
    if ((rec as any).difficulty === 'challenging') hours += 10
    else if ((rec as any).difficulty === 'moderate') hours += 5
    
    if (rec.expected_impact === 'high') hours += 5
    
    hours += rec.frameworks_source.length * 2 // Additional hours per framework
    
    return hours
  }

  // Group actions by timeline
  const immediateActions = actionItems.filter(item => item.timeline === 'immediate')
  const shortTermActions = actionItems.filter(item => item.timeline === 'short')
  const mediumTermActions = actionItems.filter(item => item.timeline === 'medium')
  const longTermActions = actionItems.filter(item => item.timeline === 'long')

  const getTimelineIcon = (timeline: string) => {
    switch (timeline) {
      case 'immediate': return <AlertTriangle className="w-4 h-4" />
      case 'short': return <Clock className="w-4 h-4" />
      case 'medium': return <Calendar className="w-4 h-4" />
      case 'long': return <Target className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const getTimelineName = (timeline: string) => {
    switch (timeline) {
      case 'immediate': return '즉시 실행 (1-2일)'
      case 'short': return '단기 목표 (1-2주)'
      case 'medium': return '중기 목표 (1-2개월)'
      case 'long': return '장기 목표 (3개월+)'
      default: return '미정'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '⭐'
      case 'moderate': return '⭐⭐'
      case 'challenging': return '⭐⭐⭐'
      default: return '⭐'
    }
  }

  const totalEstimatedHours = actionItems.reduce((sum, item) => sum + item.estimatedHours, 0)

  return (
    <div className={`action-plan-template ${className}`}>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-blue-600 mb-2">교사 전문성 향상 실행 계획</h1>
        <p className="text-gray-600">
          분석 결과를 바탕으로 한 구체적이고 실행 가능한 개선 방안을 제시합니다.
        </p>
      </div>

      {/* Plan Overview */}
      <Card className="p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2 text-blue-600" />
          실행 계획 개요
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{actionItems.length}</div>
            <div className="text-sm text-gray-600">총 실행 항목</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{immediateActions.length}</div>
            <div className="text-sm text-gray-600">즉시 실행</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{totalEstimatedHours}</div>
            <div className="text-sm text-gray-600">예상 소요시간</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {Math.round(summary.overall_score)}
            </div>
            <div className="text-sm text-gray-600">현재 점수</div>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">목표 설정</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium text-blue-800">단기 목표:</span>
              <div className="text-blue-700">긴급 개선사항 해결</div>
            </div>
            <div>
              <span className="font-medium text-blue-800">중기 목표:</span>
              <div className="text-blue-700">교육 품질 10% 향상</div>
            </div>
            <div>
              <span className="font-medium text-blue-800">장기 목표:</span>
              <div className="text-blue-700">지속적 전문성 개발</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Immediate Actions */}
      {immediateActions.length > 0 && (
        <Card className="p-6 mb-8 border-red-200">
          <h2 className="text-xl font-semibold mb-4 text-red-600 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            즉시 실행 항목 ({immediateActions.length}개)
          </h2>
          <div className="space-y-4">
            {immediateActions.map((item, index) => (
              <div key={item.id} className="p-4 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-red-900">{index + 1}. {item.title}</h3>
                    <p className="text-red-700 text-sm mt-1">{item.description}</p>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <Badge className="bg-red-100 text-red-800">긴급</Badge>
                    <span className="text-xs">{getDifficultyIcon(item.difficulty)}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-red-800 mb-2">주요 실행 단계:</h4>
                    <ul className="space-y-1">
                      {item.steps.slice(0, 3).map((step, stepIndex) => (
                        <li key={stepIndex} className="flex items-start text-red-700">
                          <ArrowRight className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-red-800 mb-2">성공 지표:</h4>
                    <ul className="space-y-1">
                      {item.successMetrics.slice(0, 2).map((metric, metricIndex) => (
                        <li key={metricIndex} className="flex items-start text-red-700">
                          <CheckCircle className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                          {metric}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="mt-3 pt-3 border-t border-red-200">
                  <div className="flex items-center justify-between text-xs text-red-600">
                    <span>예상 소요시간: {item.estimatedHours}시간</span>
                    <span>관련 영역: {item.frameworks.length}개</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Short-term Actions */}
      {shortTermActions.length > 0 && (
        <Card className="p-6 mb-8 border-orange-200">
          <h2 className="text-xl font-semibold mb-4 text-orange-600 flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            단기 실행 항목 ({shortTermActions.length}개) - 1-2주
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {shortTermActions.map((item, index) => (
              <div key={item.id} className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-orange-900">{index + 1}. {item.title}</h3>
                  <span className="text-xs">{getDifficultyIcon(item.difficulty)}</span>
                </div>
                
                <div className="space-y-3 text-sm">
                  <div>
                    <h4 className="font-medium text-orange-800">핵심 단계:</h4>
                    <div className="mt-1 space-y-1">
                      {item.steps.slice(0, 2).map((step, stepIndex) => (
                        <div key={stepIndex} className="flex items-start text-orange-700">
                          <span className="w-4 h-4 bg-orange-200 rounded-full text-xs flex items-center justify-center mr-2 mt-0.5 flex-shrink-0">
                            {stepIndex + 1}
                          </span>
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-orange-800">필요 자원:</h4>
                    <div className="mt-1 text-orange-700">
                      {item.resources.slice(0, 2).join(', ')}
                    </div>
                  </div>
                </div>
                
                <div className="mt-3 pt-3 border-t border-orange-200 text-xs text-orange-600">
                  <div className="flex justify-between">
                    <span>소요시간: {item.estimatedHours}시간</span>
                    <span>예상효과: {item.impact === 'high' ? '높음' : item.impact === 'medium' ? '보통' : '낮음'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Medium-term Actions */}
      {mediumTermActions.length > 0 && (
        <Card className="p-6 mb-8 border-blue-200">
          <h2 className="text-xl font-semibold mb-4 text-blue-600 flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            중기 실행 항목 ({mediumTermActions.length}개) - 1-2개월
          </h2>
          <div className="space-y-6">
            {mediumTermActions.map((item, index) => (
              <div key={item.id} className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-blue-900">{index + 1}. {item.title}</h3>
                    <p className="text-blue-700 text-sm mt-1">{item.description}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className="border-blue-300 text-blue-700">
                      {item.priority === 'high' ? '높음' : item.priority === 'medium' ? '보통' : '낮음'}
                    </Badge>
                    <span className="text-xs">{getDifficultyIcon(item.difficulty)}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-blue-800 mb-2">실행 단계:</h4>
                    <ul className="space-y-1">
                      {item.steps.map((step, stepIndex) => (
                        <li key={stepIndex} className="flex items-start text-blue-700">
                          <span className="w-5 h-5 bg-blue-200 rounded text-xs flex items-center justify-center mr-2 mt-0.5 flex-shrink-0">
                            {stepIndex + 1}
                          </span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-blue-800 mb-2">필요 자원:</h4>
                    <ul className="space-y-1">
                      {item.resources.map((resource, resourceIndex) => (
                        <li key={resourceIndex} className="flex items-start text-blue-700">
                          <BookOpen className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                          {resource}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-medium text-blue-800 mb-2">성공 지표:</h4>
                    <ul className="space-y-1">
                      {item.successMetrics.map((metric, metricIndex) => (
                        <li key={metricIndex} className="flex items-start text-blue-700">
                          <TrendingUp className="w-3 h-3 mr-2 mt-0.5 flex-shrink-0" />
                          {metric}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-blue-200">
                  <div className="flex items-center justify-between text-xs text-blue-600">
                    <span>예상 소요시간: {item.estimatedHours}시간</span>
                    <span>관련 프레임워크: {item.frameworks.map(fw => {
                      const framework = comprehensiveFrameworkUtils.getFramework(fw)
                      return framework?.name_ko.split(' ')[0] || fw
                    }).join(', ')}</span>
                    <span>구현 난이도: {item.difficulty === 'easy' ? '쉬움' : item.difficulty === 'moderate' ? '보통' : '어려움'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Progress Tracking */}
      <Card className="p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
          진행 상황 추적
        </h2>
        
        <div className="space-y-4">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">전체 진행률</span>
              <span className="text-sm text-gray-600">0% 완료</span>
            </div>
            <Progress value={0} className="h-2" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-3 bg-red-50 rounded border border-red-200">
              <div className="text-sm font-medium text-red-800">즉시 실행</div>
              <div className="text-lg font-bold text-red-600">0/{immediateActions.length}</div>
              <Progress value={0} className="h-1 mt-1" />
            </div>
            
            <div className="p-3 bg-orange-50 rounded border border-orange-200">
              <div className="text-sm font-medium text-orange-800">단기 목표</div>
              <div className="text-lg font-bold text-orange-600">0/{shortTermActions.length}</div>
              <Progress value={0} className="h-1 mt-1" />
            </div>
            
            <div className="p-3 bg-blue-50 rounded border border-blue-200">
              <div className="text-sm font-medium text-blue-800">중기 목표</div>
              <div className="text-lg font-bold text-blue-600">0/{mediumTermActions.length}</div>
              <Progress value={0} className="h-1 mt-1" />
            </div>
            
            <div className="p-3 bg-green-50 rounded border border-green-200">
              <div className="text-sm font-medium text-green-800">장기 목표</div>
              <div className="text-lg font-bold text-green-600">0/{longTermActions.length}</div>
              <Progress value={0} className="h-1 mt-1" />
            </div>
          </div>
        </div>
      </Card>

      {/* Success Tips */}
      <Card className="p-6 mb-8 bg-green-50 border-green-200">
        <h2 className="text-xl font-semibold mb-4 text-green-600 flex items-center">
          <Lightbulb className="w-5 h-5 mr-2" />
          성공을 위한 조언
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-green-800 mb-3">실행 원칙</h3>
            <ul className="space-y-2 text-green-700">
              <li className="flex items-start">
                <Star className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                작은 변화부터 시작하여 점진적으로 확대
              </li>
              <li className="flex items-start">
                <Star className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                정기적인 자기 평가와 피드백 수집
              </li>
              <li className="flex items-start">
                <Star className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                동료 교사와의 경험 공유 및 협력
              </li>
              <li className="flex items-start">
                <Star className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                학습자 반응과 참여도 지속적 관찰
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-green-800 mb-3">지원 자원</h3>
            <ul className="space-y-2 text-green-700">
              <li className="flex items-start">
                <Plus className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                교육청 제공 교사 연수 프로그램
              </li>
              <li className="flex items-start">
                <Plus className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                온라인 교육 플랫폼 및 자료
              </li>
              <li className="flex items-start">
                <Plus className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                교사 학습공동체 참여
              </li>
              <li className="flex items-start">
                <Plus className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                교육 전문서적 및 연구논문
              </li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Contact and Support */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <Users className="w-5 h-5 mr-2 text-blue-600" />
          지원 및 문의
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold mb-3">이 실행 계획에 대해</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div>
                <span className="font-medium">생성 일시:</span> {new Date().toLocaleString('ko-KR')}
              </div>
              <div>
                <span className="font-medium">분석 기준:</span> {analysisResult.frameworks_analyzed.length}개 프레임워크
              </div>
              <div>
                <span className="font-medium">대상 교사:</span> {metadata.teacher || '미지정'}
              </div>
              <div>
                <span className="font-medium">과목:</span> {metadata.subject || '미지정'}
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="font-semibold mb-3">추가 지원</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div>개인별 맞춤 컨설팅이 필요한 경우 전문가와 상담 가능</div>
              <div>실행 과정에서의 어려움이나 질문사항은 언제든 문의</div>
              <div>정기적인 진행상황 점검 및 계획 수정 지원</div>
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
                이 실행 계획서를 PDF 파일로 저장하여 인쇄하거나 공유할 수 있습니다.
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
                html={document.querySelector('.action-plan-template')?.outerHTML || ''}
                filename={pdfExportUtils.generateFilename('action_plan', metadata)}
                title="실행 계획서 PDF 내보내기"
                defaultOptions={pdfExportUtils.getReportTypeOptions('actionPlan') as any}
                showOptionsDialog={true}
                showProgress={true}
                showEstimation={true}
                variant="default"
                className="bg-purple-600 hover:bg-purple-700 text-white"
                onExportComplete={(success, result) => {
                  if (success) {
                    console.log('실행 계획서 PDF 내보내기 완료:', result)
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
            html={document.querySelector('.action-plan-template')?.outerHTML || ''}
            options={pdfExportUtils.getReportTypeOptions('actionPlan') as any}
            filename={pdfExportUtils.generateFilename('action_plan_preview', metadata)}
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

export default ActionPlanTemplate