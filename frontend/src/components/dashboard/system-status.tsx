'use client'

import { Badge } from '@/components/ui/badge'
import { CheckCircleIcon, XCircleIcon, AlertCircleIcon } from 'lucide-react'

interface ServiceStatus {
  name: string
  status: 'healthy' | 'unhealthy' | 'degraded'
  latency?: string
  uptime?: string
}

export function SystemStatus() {
  // Mock data - would come from health check APIs
  const services: ServiceStatus[] = [
    {
      name: '전사 서비스',
      status: 'healthy',
      latency: '142ms',
      uptime: '99.9%',
    },
    {
      name: '분석 서비스',
      status: 'healthy', 
      latency: '89ms',
      uptime: '99.8%',
    },
    {
      name: 'OpenAI API',
      status: 'healthy',
      latency: '234ms',
      uptime: '99.5%',
    },
    {
      name: 'YouTube API',
      status: 'degraded',
      latency: '1.2s',
      uptime: '85.2%',
    },
  ]

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />
      case 'unhealthy':
        return <XCircleIcon className="h-4 w-4 text-red-500" />
      case 'degraded':
        return <AlertCircleIcon className="h-4 w-4 text-yellow-500" />
    }
  }

  const getStatusBadge = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return <Badge className="bg-green-100 text-green-800">정상</Badge>
      case 'unhealthy':
        return <Badge className="bg-red-100 text-red-800">오류</Badge>
      case 'degraded':
        return <Badge className="bg-yellow-100 text-yellow-800">지연</Badge>
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {services.map((service) => (
        <div
          key={service.name}
          className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              {getStatusIcon(service.status)}
              <h3 className="font-medium text-gray-900">{service.name}</h3>
            </div>
            {getStatusBadge(service.status)}
          </div>
          
          <div className="space-y-2 text-sm text-gray-600">
            {service.latency && (
              <div className="flex justify-between">
                <span>응답 시간:</span>
                <span className="font-mono">{service.latency}</span>
              </div>
            )}
            {service.uptime && (
              <div className="flex justify-between">
                <span>가동률:</span>
                <span className="font-mono">{service.uptime}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}