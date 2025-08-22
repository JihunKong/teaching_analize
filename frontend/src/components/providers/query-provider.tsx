'use client'

import { QueryClient, QueryClientProvider, QueryErrorResetBoundary } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'
import { QueryErrorBoundary, QueryErrorFallback } from '@/components/error-boundary'

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes
        retry: (failureCount, error: any) => {
          // Don't retry on 401, 403, or 404
          if (error?.response?.status === 401 || 
              error?.response?.status === 403 || 
              error?.response?.status === 404) {
            return false
          }
          return failureCount < 3
        },
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        refetchOnWindowFocus: false, // Disable auto-refetch on window focus
        refetchOnReconnect: 'always', // Refetch when connection is restored
      },
      mutations: {
        retry: (failureCount, error: any) => {
          // Don't retry on client errors (4xx)
          if (error?.response?.status >= 400 && error?.response?.status < 500) {
            return false
          }
          return failureCount < 1
        },
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      <QueryErrorResetBoundary>
        {({ reset }) => (
          <QueryErrorBoundary fallback={QueryErrorFallback}>
            {children}
          </QueryErrorBoundary>
        )}
      </QueryErrorResetBoundary>
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  )
}