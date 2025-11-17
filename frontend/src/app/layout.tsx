import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'TVAS - Teacher Voice Analysis System',
  description: '교사 발화 분석을 통한 수업 진단 시스템',
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
        {/* Navigation */}
        <header className="header">
          <nav className="nav">
            <div className="nav-brand">
              <Link href="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                <h1>TVAS</h1>
                <span>수업 분석 시스템</span>
              </Link>
            </div>
            <div className="nav-menu">
              <Link href="/pipeline" className="nav-link">
                분석 시스템
              </Link>
              <Link href="/comprehensive-reports" className="nav-link">
                보고서
              </Link>
            </div>
          </nav>
        </header>

        <main>
          {children}
        </main>

        {/* Footer */}
        <footer className="footer">
          <p>&copy; 2025 TVAS - Teacher Voice Analysis System</p>
        </footer>
      </body>
    </html>
  )
}
