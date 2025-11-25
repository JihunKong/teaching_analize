import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'TVAS - Teacher Voice Analysis System',
  description: 'Advanced AI-powered classroom analysis platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>
        {/* Navigation */}
        <header className="header">
          <nav className="nav container">
            <div className="nav-brand">
              <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <h1>TVAS</h1>
                <span>Classroom Intelligence</span>
              </Link>
            </div>
            <div className="nav-menu">
              <Link href="/pipeline" className="nav-link">
                Analysis
              </Link>
              <Link href="/comprehensive-reports" className="nav-link">
                Reports
              </Link>
            </div>
          </nav>
        </header>

        <main>
          {children}
        </main>

        {/* Footer */}
        <footer className="footer">
          <div className="container">
            <p>&copy; 2025 TVAS. All rights reserved.</p>
            <p style={{ fontSize: 'var(--text-xs)', marginTop: 'var(--space-2)', color: 'var(--color-text-tertiary)' }}>
              Teacher Voice Analysis System
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}
