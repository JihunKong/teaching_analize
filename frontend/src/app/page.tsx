'use client'

import { Suspense } from 'react'
import { Layout } from '@/components/layout/layout'
import { DashboardOverview } from '@/components/dashboard/dashboard-overview'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { QuickActions } from '@/components/dashboard/quick-actions'
import { SystemStatus } from '@/components/dashboard/system-status'
import { PageHeader } from '@/components/ui/page-header'
import { Card } from '@/components/ui/card'

export default function HomePage() {
  return (
    <Layout>
      <div className="space-y-8">
        <PageHeader
          title="대시보드"
          description="AIBOA 플랫폼 개요 및 최근 활동"
        />

        <div className="grid gap-6">
          {/* Overview Cards */}
          <Suspense fallback={<div className="animate-pulse">Loading overview...</div>}>
            <DashboardOverview />
          </Suspense>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Quick Actions */}
            <div className="lg:col-span-1">
              <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">빠른 작업</h2>
                <QuickActions />
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="lg:col-span-2">
              <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">최근 활동</h2>
                <Suspense fallback={<div className="animate-pulse">Loading activity...</div>}>
                  <RecentActivity />
                </Suspense>
              </Card>
            </div>
          </div>

          {/* System Status */}
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">시스템 상태</h2>
            <Suspense fallback={<div className="animate-pulse">Loading status...</div>}>
              <SystemStatus />
            </Suspense>
          </Card>
        </div>
      </div>
    </Layout>
  )
}