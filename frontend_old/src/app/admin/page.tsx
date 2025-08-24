'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  UsersIcon, 
  ActivityIcon, 
  BarChart3Icon,
  FileTextIcon,
  RefreshCwIcon,
  LogOutIcon,
  AlertCircleIcon,
  TrendingUpIcon,
  EyeIcon,
  DownloadIcon
} from 'lucide-react'
import { getStoredUser, logout, getCurrentUser, isAuthenticated } from '@/lib/auth'

interface AdminStats {
  total_users: number
  active_users_today: number
  total_transcriptions: number
  total_analyses: number
  transcriptions_today: number
  analyses_today: number
  popular_frameworks: Array<{
    framework_id: string
    name: string
    usage_count: number
  }>
}

interface UserData {
  id: string
  email: string
  username: string
  role: string
  created_at: string
  last_login: string
  is_active: boolean
  transcription_count: number
  analysis_count: number
}

interface LogEntry {
  id: string
  timestamp: string
  level: string
  service: string
  message: string
  user_id?: string
  request_id?: string
  details?: any
}

export default function AdminDashboard() {
  const router = useRouter()
  const [user, setUser] = useState(getStoredUser())
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [users, setUsers] = useState<UserData[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [selectedTab, setSelectedTab] = useState('overview')

  // Check authentication and admin role
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login?redirect=/admin')
      return
    }

    const currentUser = getStoredUser()
    if (!currentUser || currentUser.role !== 'admin') {
      router.push('/')
      return
    }

    setUser(currentUser)
    loadAdminData()
  }, [router])

  const loadAdminData = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Load statistics
      await Promise.all([
        loadStatistics(),
        loadUsers(),
        loadLogs()
      ])
    } catch (error) {
      console.error('Failed to load admin data:', error)
      setError('관리자 데이터를 불러오는데 실패했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  const loadStatistics = async () => {
    try {
      const response = await fetch('/api/admin/statistics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('aiboa_access_token')}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to load statistics:', error)
    }
  }

  const loadUsers = async () => {
    try {
      const response = await fetch('/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('aiboa_access_token')}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data.users || [])
      }
    } catch (error) {
      console.error('Failed to load users:', error)
    }
  }

  const loadLogs = async () => {
    try {
      const response = await fetch('/api/admin/logs?limit=50', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('aiboa_access_token')}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setLogs(data.logs || [])
      }
    } catch (error) {
      console.error('Failed to load logs:', error)
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR')
  }

  const getLevelBadgeColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return 'destructive'
      case 'warn':
        return 'secondary'
      case 'info':
        return 'default'
      default:
        return 'outline'
    }
  }

  if (!user) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded flex items-center justify-center">
                <span className="text-white font-bold text-sm">AI</span>
              </div>
              <h1 className="text-xl font-semibold text-gray-900">AIBOA 관리자</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                {user.profile?.full_name || user.username}님 환영합니다
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push('/')}
              >
                메인으로
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
              >
                <LogOutIcon className="h-4 w-4 mr-2" />
                로그아웃
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircleIcon className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">관리자 대시보드</h2>
            <p className="text-gray-600">시스템 현황 및 사용자 관리</p>
          </div>
          <Button onClick={loadAdminData} disabled={isLoading}>
            <RefreshCwIcon className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList className="mb-6">
            <TabsTrigger value="overview">개요</TabsTrigger>
            <TabsTrigger value="users">사용자 관리</TabsTrigger>
            <TabsTrigger value="logs">시스템 로그</TabsTrigger>
            <TabsTrigger value="analytics">분석 통계</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">전체 사용자</CardTitle>
                  <UsersIcon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    오늘 활성: {stats?.active_users_today || 0}명
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">전체 전사</CardTitle>
                  <FileTextIcon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_transcriptions || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    오늘: {stats?.transcriptions_today || 0}건
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">전체 분석</CardTitle>
                  <BarChart3Icon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats?.total_analyses || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    오늘: {stats?.analyses_today || 0}건
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">시스템 상태</CardTitle>
                  <ActivityIcon className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">정상</div>
                  <p className="text-xs text-muted-foreground">
                    모든 서비스 운영 중
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Popular Frameworks */}
            <Card>
              <CardHeader>
                <CardTitle>인기 분석 프레임워크</CardTitle>
                <CardDescription>가장 많이 사용되는 분석 도구</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {stats?.popular_frameworks?.slice(0, 5).map((framework, index) => (
                    <div key={framework.framework_id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-blue-600">{index + 1}</span>
                        </div>
                        <span className="font-medium">{framework.name}</span>
                      </div>
                      <Badge variant="secondary">{framework.usage_count}회</Badge>
                    </div>
                  )) || (
                    <p className="text-gray-500 text-center py-4">데이터를 불러오는 중...</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>사용자 목록</CardTitle>
                <CardDescription>등록된 모든 사용자를 관리합니다.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {users.length > 0 ? users.map((userData) => (
                    <div key={userData.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4">
                          <div>
                            <h3 className="font-medium">{userData.username}</h3>
                            <p className="text-sm text-gray-600">{userData.email}</p>
                          </div>
                          <Badge 
                            variant={userData.role === 'admin' ? 'default' : 'secondary'}
                          >
                            {userData.role}
                          </Badge>
                          <Badge 
                            variant={userData.is_active ? 'default' : 'destructive'}
                          >
                            {userData.is_active ? '활성' : '비활성'}
                          </Badge>
                        </div>
                        <div className="mt-2 text-xs text-gray-500">
                          가입: {formatDate(userData.created_at)} | 
                          마지막 로그인: {userData.last_login ? formatDate(userData.last_login) : '없음'} |
                          전사: {userData.transcription_count}건 | 분석: {userData.analysis_count}건
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button size="sm" variant="outline">
                          <EyeIcon className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  )) : (
                    <p className="text-gray-500 text-center py-8">사용자 데이터를 불러오는 중...</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Logs Tab */}
          <TabsContent value="logs">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>시스템 로그</CardTitle>
                    <CardDescription>최근 시스템 활동 및 오류 로그</CardDescription>
                  </div>
                  <Button size="sm" variant="outline">
                    <DownloadIcon className="h-4 w-4 mr-2" />
                    로그 다운로드
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {logs.length > 0 ? logs.map((log) => (
                    <div key={log.id} className="text-sm border-l-4 border-gray-200 pl-4 py-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Badge variant={getLevelBadgeColor(log.level) as any}>
                            {log.level.toUpperCase()}
                          </Badge>
                          <span className="font-medium">{log.service}</span>
                          <span className="text-gray-500">
                            {formatDate(log.timestamp)}
                          </span>
                        </div>
                      </div>
                      <p className="mt-1 text-gray-700">{log.message}</p>
                      {log.details && (
                        <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
                          <pre>{JSON.stringify(log.details, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  )) : (
                    <p className="text-gray-500 text-center py-8">로그 데이터를 불러오는 중...</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>사용량 추이</CardTitle>
                  <CardDescription>일별 서비스 사용량 통계</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    차트 구현 예정
                    <TrendingUpIcon className="h-8 w-8 ml-2" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>프레임워크 사용 분포</CardTitle>
                  <CardDescription>분석 프레임워크별 사용 비율</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    차트 구현 예정
                    <BarChart3Icon className="h-8 w-8 ml-2" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}