import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

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
              <Link href="/" className="nav-link">홈</Link>
              <Link href="/transcription" className="nav-link">전사</Link>
              <Link href="/analysis" className="nav-link">분석</Link>
              <Link href="/reports" className="nav-link">보고서</Link>
              <Link href="/comprehensive-reports" className="nav-link">종합보고서</Link>
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