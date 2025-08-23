import './globals.css'
import type { Metadata } from 'next'

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
      <body>
        <header className="header">
          <nav className="nav">
            <div className="nav-brand">
              <h1>AIBOA</h1>
              <span>AI 교육 분석</span>
            </div>
            <div className="nav-menu">
              <a href="/" className="nav-link">홈</a>
              <a href="/transcription" className="nav-link">전사</a>
              <a href="/analysis" className="nav-link">분석</a>
              <a href="/reports" className="nav-link">보고서</a>
            </div>
          </nav>
        </header>
        
        <main className="main">
          {children}
        </main>
        
        <footer className="footer">
          <p>&copy; 2025 AIBOA - AI 기반 교육 분석 플랫폼</p>
        </footer>
      </body>
    </html>
  )
}