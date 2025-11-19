import { Suspense } from 'react'

export default function ComprehensiveReportsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <Suspense fallback={
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        fontSize: '1.5rem',
        color: 'var(--color-gray-600)'
      }}>
        로딩 중...
      </div>
    }>
      {children}
    </Suspense>
  )
}
