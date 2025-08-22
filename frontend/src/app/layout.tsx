import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/components/providers/query-provider'
import { ToastProvider } from '@/components/providers/toast-provider'
import { ErrorBoundary } from '@/components/error-boundary'
import Navbar from '@/components/layout/navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'AIBOA - AI-Based Observation and Analysis',
    template: '%s | AIBOA',
  },
  description: 'Advanced AI-powered teaching analysis platform for educational institutions',
  keywords: ['AI', 'education', 'teaching analysis', 'CBIL', 'transcription'],
  authors: [{ name: 'AIBOA Team' }],
  viewport: 'width=device-width, initial-scale=1',
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    url: 'https://aiboa.ai',
    siteName: 'AIBOA',
    title: 'AIBOA - AI-Based Observation and Analysis',
    description: 'Advanced AI-powered teaching analysis platform',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'AIBOA Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@aiboa',
    title: 'AIBOA - Teaching Analysis Platform',
    description: 'AI-powered teaching analysis and improvement',
    images: ['/twitter-image.jpg'],
  },
  manifest: '/manifest.json',
  themeColor: '#3b82f6',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className={inter.className}>
        <ErrorBoundary>
          <QueryProvider>
            <ToastProvider>
              <div className="min-h-screen bg-gray-50">
                <ErrorBoundary>
                  <Navbar />
                </ErrorBoundary>
                <main className="flex-1">
                  <ErrorBoundary>
                    {children}
                  </ErrorBoundary>
                </main>
              </div>
            </ToastProvider>
          </QueryProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}