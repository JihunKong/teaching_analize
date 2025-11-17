import './globals.css'
import type { Metadata } from 'next'
import BrutalistNav from '../components/BrutalistNav'

export const metadata: Metadata = {
  title: 'AIBOA - AI 교육 분석 플랫폼',
  description: 'YouTube 영상을 통한 교사 발화 분석 시스템',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          as="style"
          crossOrigin="anonymous"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css"
        />
      </head>
      <body>
        <BrutalistNav />
        
        <main style={{
          minHeight: 'calc(100vh - 300px)',
          paddingBottom: 'var(--space-8)'
        }}>
          {children}
        </main>
        
        {/* Brutalist Footer */}
        <footer style={{
          background: 'var(--color-black)',
          borderTop: '8px solid var(--color-white)',
          padding: 'var(--space-6)',
          marginTop: 'var(--space-8)'
        }}>
          <div style={{
            maxWidth: '1400px',
            margin: '0 auto',
            textAlign: 'center'
          }}>
            <p style={{
              color: 'var(--color-white)',
              fontSize: 'var(--text-sm)',
              fontWeight: 'var(--font-bold)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--tracking-wide)',
              margin: '0'
            }}>
              &copy; 2025 AIBOA - AI 기반 교육 분석 플랫폼
            </p>
            <div style={{
              marginTop: 'var(--space-3)',
              display: 'flex',
              justifyContent: 'center',
              gap: 'var(--space-2)'
            }}>
              <div style={{
                width: '40px',
                height: '4px',
                background: 'var(--color-white)'
              }} />
              <div style={{
                width: '20px',
                height: '4px',
                background: 'var(--color-gray-400)'
              }} />
              <div style={{
                width: '30px',
                height: '4px',
                background: 'var(--color-white)'
              }} />
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
