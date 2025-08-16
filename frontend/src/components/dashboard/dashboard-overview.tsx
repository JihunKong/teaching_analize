'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileTextIcon, MicIcon, BarChart3Icon, TrendingUpIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string
  change: string
  trend: 'up' | 'down' | 'neutral'
  icon: React.ComponentType<{ className?: string }>
}

function StatCard({ title, value, change, trend, icon: Icon }: StatCardProps) {
  return (
    <Card className="transition-all hover:shadow-md">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-gray-400" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-900">{value}</div>
        <div className={`text-xs flex items-center mt-1 ${
          trend === 'up' ? 'text-green-600' : 
          trend === 'down' ? 'text-red-600' : 
          'text-gray-500'
        }`}>
          <TrendingUpIcon className={`h-3 w-3 mr-1 ${
            trend === 'down' ? 'rotate-180' : ''
          }`} />
          {change}
        </div>
      </CardContent>
    </Card>
  )
}

export function DashboardOverview() {
  // This would normally come from API calls
  const stats = [
    {
      title: '총 전사 작업',
      value: '1,234',
      change: '+12% from last month',
      trend: 'up' as const,
      icon: MicIcon,
    },
    {
      title: '분석 완료',
      value: '987',
      change: '+8% from last month',
      trend: 'up' as const,
      icon: BarChart3Icon,
    },
    {
      title: '생성된 보고서',
      value: '456',
      change: '+15% from last month',
      trend: 'up' as const,
      icon: FileTextIcon,
    },
    {
      title: '평균 CBIL 점수',
      value: '4.2',
      change: '+0.3 from last month',
      trend: 'up' as const,
      icon: TrendingUpIcon,
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  )
}