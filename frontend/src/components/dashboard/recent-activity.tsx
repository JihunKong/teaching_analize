'use client'

import { Badge } from '@/components/ui/badge'
import { formatDateTime } from '@/lib/utils'

interface Activity {
  id: string
  type: 'transcription' | 'analysis' | 'report'
  title: string
  status: 'completed' | 'processing' | 'failed'
  timestamp: string
}

export function RecentActivity() {
  // Mock data - would come from API
  const activities: Activity[] = [
    {
      id: '1',
      type: 'transcription',
      title: '수학 수업 - 2차 함수',
      status: 'completed',
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
    },
    {
      id: '2', 
      type: 'analysis',
      title: '영어 수업 CBIL 분석',
      status: 'processing',
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 minutes ago
    },
    {
      id: '3',
      type: 'report',
      title: '주간 교육 분석 보고서',
      status: 'completed',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
    },
    {
      id: '4',
      type: 'transcription',
      title: 'YouTube: 온라인 수업 사례',
      status: 'failed',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(), // 3 hours ago
    },
  ]

  const getStatusColor = (status: Activity['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'processing':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: Activity['status']) => {
    switch (status) {
      case 'completed':
        return '완료'
      case 'processing':
        return '처리중'
      case 'failed':
        return '실패'
      default:
        return '알 수 없음'
    }
  }

  if (activities.length === 0) {
    return (
      <div className="text-center text-gray-500 py-8">
        아직 활동이 없습니다.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div
          key={activity.id}
          className="flex items-center justify-between p-4 rounded-lg border hover:bg-gray-50 transition-colors"
        >
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <h4 className="font-medium text-gray-900">{activity.title}</h4>
              <Badge
                variant="secondary"
                className={getStatusColor(activity.status)}
              >
                {getStatusText(activity.status)}
              </Badge>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {formatDateTime(activity.timestamp)}
            </p>
          </div>
          
          <div className="text-sm text-gray-400 capitalize">
            {activity.type === 'transcription' && '전사'}
            {activity.type === 'analysis' && '분석'}  
            {activity.type === 'report' && '보고서'}
          </div>
        </div>
      ))}
    </div>
  )
}