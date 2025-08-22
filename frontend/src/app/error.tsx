'use client'

import { useEffect } from 'react'
import { AlertTriangleIcon, RefreshCwIcon, HomeIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <AlertTriangleIcon className="h-6 w-6 text-red-500" />
            <CardTitle className="text-red-700">애플리케이션 오류</CardTitle>
          </div>
          <CardDescription>
            예상치 못한 오류가 발생했습니다. 아래 버튼을 사용하여 문제를 해결해보세요.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {process.env.NODE_ENV === 'development' && (
            <div className="p-3 bg-gray-100 rounded text-sm font-mono text-gray-700 overflow-auto max-h-32">
              <div className="font-bold text-red-600 mb-1">Error:</div>
              <div>{error.message}</div>
              {error.digest && (
                <>
                  <div className="font-bold text-red-600 mt-2 mb-1">Error ID:</div>
                  <div>{error.digest}</div>
                </>
              )}
              {error.stack && (
                <>
                  <div className="font-bold text-red-600 mt-2 mb-1">Stack:</div>
                  <div className="whitespace-pre-wrap text-xs">
                    {error.stack}
                  </div>
                </>
              )}
            </div>
          )}
          
          <div className="grid grid-cols-1 gap-2">
            <Button onClick={reset} variant="default" className="w-full">
              <RefreshCwIcon className="h-4 w-4 mr-2" />
              다시 시도
            </Button>
            <Button 
              onClick={() => window.location.href = '/'} 
              variant="outline" 
              className="w-full"
            >
              <HomeIcon className="h-4 w-4 mr-2" />
              홈으로 이동
            </Button>
            <Button 
              onClick={() => window.location.reload()} 
              variant="ghost" 
              className="w-full"
            >
              페이지 새로고침
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}