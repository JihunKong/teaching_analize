// Framework Selector Component for choosing analysis frameworks
// Provides visual selection interface with framework descriptions

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  ComprehensiveFramework, 
  COMPREHENSIVE_FRAMEWORKS,
  comprehensiveFrameworkUtils 
} from '@/types/comprehensive-analysis'
import {
  BarChart3Icon,
  MessageCircleIcon,
  UsersIcon,
  TargetIcon,
  MessageSquareIcon,
  LayoutIcon,
  ClipboardCheckIcon,
  SettingsIcon,
  MonitorIcon,
  BrainIcon,
  GlobeIcon,
  HeartIcon,
  LinkIcon,
  ClockIcon,
  CheckIcon,
  XIcon
} from 'lucide-react'

interface FrameworkSelectorProps {
  frameworks: ComprehensiveFramework[]
  selectedFrameworks: string[]
  onFrameworkToggle: (frameworkId: string, enabled: boolean) => void
  estimatedTime: number
}

// Icon mapping for frameworks
const frameworkIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  BarChart3: BarChart3Icon,
  MessageCircleQuestion: MessageCircleIcon,
  Users: UsersIcon,
  Target: TargetIcon,
  MessageSquare: MessageSquareIcon,
  Layout: LayoutIcon,
  ClipboardCheck: ClipboardCheckIcon,
  Settings: SettingsIcon,
  Monitor: MonitorIcon,
  Brain: BrainIcon,
  Globe: GlobeIcon,
  Heart: HeartIcon,
  Link: LinkIcon,
}

export function FrameworkSelector({
  frameworks,
  selectedFrameworks,
  onFrameworkToggle,
  estimatedTime
}: FrameworkSelectorProps) {
  const handleSelectAll = () => {
    const allIds = frameworks.filter(f => f.enabled).map(f => f.id)
    allIds.forEach(id => {
      if (!selectedFrameworks.includes(id)) {
        onFrameworkToggle(id, true)
      }
    })
  }

  const handleDeselectAll = () => {
    selectedFrameworks.forEach(id => {
      onFrameworkToggle(id, false)
    })
  }

  const enabledFrameworks = frameworks.filter(f => f.enabled)
  const selectedCount = selectedFrameworks.length
  const totalCount = enabledFrameworks.length

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>분석 프레임워크 선택</CardTitle>
            <CardDescription>
              교육 효과성을 다각도로 분석할 프레임워크를 선택하세요.
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
              disabled={selectedCount === totalCount}
            >
              <CheckIcon className="h-4 w-4 mr-1" />
              전체 선택
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDeselectAll}
              disabled={selectedCount === 0}
            >
              <XIcon className="h-4 w-4 mr-1" />
              전체 해제
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Selection Summary */}
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">선택된 프레임워크:</span>
            <Badge variant="secondary">{selectedCount}/{totalCount}</Badge>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <ClockIcon className="h-4 w-4" />
            예상 시간: {Math.round(estimatedTime / 60)}분
          </div>
        </div>

        {/* Framework Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {enabledFrameworks.map((framework) => {
            const isSelected = selectedFrameworks.includes(framework.id)
            const IconComponent = frameworkIcons[framework.icon] || BrainIcon

            return (
              <div
                key={framework.id}
                className={`
                  border rounded-lg p-4 transition-all cursor-pointer
                  ${isSelected 
                    ? 'border-blue-300 bg-blue-50 shadow-sm' 
                    : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                  }
                `}
                onClick={() => onFrameworkToggle(framework.id, !isSelected)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div
                      className="p-2 rounded-lg flex-shrink-0"
                      style={{ 
                        backgroundColor: `${framework.color}15`,
                        color: framework.color
                      }}
                    >
                      <IconComponent className="h-5 w-5" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-sm">{framework.name_ko}</h4>
                        <Badge variant="outline" className="text-xs">
                          {framework.analysis_levels}단계
                        </Badge>
                      </div>
                      
                      <p className="text-xs text-gray-600 mb-2">
                        {framework.description}
                      </p>
                      
                      <div className="flex flex-wrap gap-1">
                        {framework.categories.map((category) => (
                          <Badge
                            key={category}
                            variant="secondary"
                            className="text-xs px-2 py-0.5"
                          >
                            {category}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>

                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={(e) => onFrameworkToggle(framework.id, e.target.checked)}
                    className="flex-shrink-0 mt-1"
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Framework Categories Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-sm mb-3">선택된 분석 영역</h4>
          <div className="flex flex-wrap gap-2">
            {Array.from(
              new Set(
                selectedFrameworks
                  .map(id => comprehensiveFrameworkUtils.getFramework(id))
                  .filter(Boolean)
                  .flatMap(f => f!.categories)
              )
            ).map((category) => (
              <Badge key={category} variant="outline" className="text-xs">
                {category}
              </Badge>
            ))}
          </div>
          {selectedFrameworks.length === 0 && (
            <p className="text-sm text-gray-500">프레임워크를 선택하면 분석 영역이 표시됩니다.</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}