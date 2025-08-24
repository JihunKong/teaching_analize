'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useAnalysisFrameworks } from '@/hooks/useAnalysis'
import { AnalysisFramework } from '@/types/analysis'
import { CheckCircleIcon, ArrowRightIcon, InfoIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface OldFrameworkSelectorProps {
  selectedFramework?: string
  onFrameworkSelect: (framework: AnalysisFramework) => void
  disabled?: boolean
  className?: string
}

export function OldFrameworkSelector({
  selectedFramework,
  onFrameworkSelect,
  disabled = false,
  className,
}: OldFrameworkSelectorProps) {
  const { data: frameworks, isLoading } = useAnalysisFrameworks()
  const [hoveredFramework, setHoveredFramework] = useState<string | null>(null)

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">분석 도구 선택</h3>
        <div className="grid gap-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-200 animate-pulse rounded-lg" />
          ))}
        </div>
      </div>
    )
  }

  const enabledFrameworks = frameworks?.filter(f => f.enabled) || []

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">분석 도구 선택</h3>
        {selectedFramework && (
          <Badge className="bg-green-100 text-green-800">
            선택됨
          </Badge>
        )}
      </div>

      <div className="grid gap-3">
        {enabledFrameworks.map((framework) => {
          const isSelected = selectedFramework === framework.id
          const isHovered = hoveredFramework === framework.id

          return (
            <Card
              key={framework.id}
              className={cn(
                'cursor-pointer transition-all duration-200 hover:shadow-md',
                isSelected && 'ring-2 ring-primary-500 bg-primary-50',
                isHovered && !isSelected && 'shadow-md scale-105',
                disabled && 'cursor-not-allowed opacity-50'
              )}
              onMouseEnter={() => !disabled && setHoveredFramework(framework.id)}
              onMouseLeave={() => setHoveredFramework(null)}
              onClick={() => !disabled && onFrameworkSelect(framework)}
            >
              <CardContent className="p-4">
                <div className="flex items-start space-x-3">
                  {/* Framework Icon */}
                  <div 
                    className={cn(
                      'w-12 h-12 rounded-lg flex items-center justify-center text-white text-lg font-bold',
                      'transition-transform duration-200',
                      isHovered && 'scale-110'
                    )}
                    style={{ backgroundColor: framework.color || '#3b82f6' }}
                  >
                    {framework.name.charAt(0)}
                  </div>

                  {/* Framework Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-gray-900 truncate">
                        {framework.name}
                      </h4>
                      {isSelected && (
                        <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                      {framework.description}
                    </p>

                    {/* Categories */}
                    {framework.categories && framework.categories.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {framework.categories.slice(0, 3).map((category) => (
                          <Badge
                            key={category}
                            variant="secondary"
                            className="text-xs bg-gray-100 text-gray-700"
                          >
                            {category}
                          </Badge>
                        ))}
                        {framework.categories.length > 3 && (
                          <Badge variant="secondary" className="text-xs bg-gray-100 text-gray-700">
                            +{framework.categories.length - 3}
                          </Badge>
                        )}
                      </div>
                    )}

                    {/* Version */}
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-gray-500">
                        v{framework.version}
                      </span>
                      
                      {(isHovered || isSelected) && (
                        <Button
                          size="sm"
                          variant={isSelected ? "default" : "outline"}
                          className={cn(
                            'transition-opacity duration-200',
                            isSelected ? 'opacity-100' : 'opacity-75 hover:opacity-100'
                          )}
                          onClick={(e) => {
                            e.stopPropagation()
                            if (!disabled) onFrameworkSelect(framework)
                          }}
                        >
                          {isSelected ? '선택됨' : '선택하기'}
                          <ArrowRightIcon className="h-4 w-4 ml-1" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Expanded Info on Hover */}
                {isHovered && !disabled && (
                  <div className="mt-3 pt-3 border-t border-gray-200 animate-fade-in">
                    <div className="flex items-start space-x-2">
                      <InfoIcon className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      <div className="text-xs text-gray-600">
                        <p>이 분석 도구는 교사의 발화를 체계적으로 분석하여 인지적 수준을 측정합니다.</p>
                        <p className="mt-1 font-medium">
                          예상 분석 시간: 2-5초 • 정확도: 95%+
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {enabledFrameworks.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <InfoIcon className="h-12 w-12 mx-auto mb-3 opacity-50" />
          <p>사용 가능한 분석 도구가 없습니다.</p>
          <p className="text-sm mt-1">잠시 후 다시 시도해주세요.</p>
        </div>
      )}
    </div>
  )
}