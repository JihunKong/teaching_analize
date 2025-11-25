'use client'

import Link from 'next/link'
import { useState } from 'react'

interface NavLinkProps {
  href: string
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
}

const NavLink: React.FC<NavLinkProps> = ({ href, children, variant = 'secondary' }) => {
  const [isHovered, setIsHovered] = useState(false)

  const primaryStyle = {
    display: 'inline-block',
    padding: 'var(--space-2) var(--space-4)',
    background: 'var(--color-white)',
    color: 'var(--color-black)',
    border: '3px solid var(--color-white)',
    fontWeight: 'var(--font-black)' as const,
    fontSize: 'var(--text-sm)',
    textTransform: 'uppercase' as const,
    letterSpacing: 'var(--tracking-wide)',
    textDecoration: 'none',
    transition: 'all 0.15s ease',
    boxShadow: isHovered ? '2px 2px 0 var(--color-white)' : '4px 4px 0 var(--color-white)',
    transform: isHovered ? 'translate(2px, 2px)' : 'translate(0, 0)'
  }

  const secondaryStyle = {
    display: 'inline-block',
    padding: 'var(--space-2) var(--space-4)',
    background: isHovered ? 'var(--color-gray-900)' : 'var(--color-black)',
    color: 'var(--color-white)',
    border: '3px solid var(--color-white)',
    fontWeight: 'var(--font-black)' as const,
    fontSize: 'var(--text-sm)',
    textTransform: 'uppercase' as const,
    letterSpacing: 'var(--tracking-wide)',
    textDecoration: 'none',
    transition: 'all 0.15s ease',
    boxShadow: isHovered ? '2px 2px 0 var(--color-white)' : '4px 4px 0 var(--color-white)',
    transform: isHovered ? 'translate(2px, 2px)' : 'translate(0, 0)'
  }

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ display: 'inline-block' }}
    >
      <Link
        href={href}
        style={variant === 'primary' ? primaryStyle : secondaryStyle}
      >
        {children}
      </Link>
    </div>
  )
}

export default function BrutalistNav() {
  return (
    <header style={{
      background: 'var(--color-black)',
      borderBottom: '12px solid var(--color-white)',
      boxShadow: '0 8px 0 var(--color-black)',
      position: 'sticky',
      top: '0',
      zIndex: '1000'
    }}>
      <nav style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 'var(--space-4) var(--space-6)',
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {/* Brand */}
        <div style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: 'var(--space-3)'
        }}>
          <h1 style={{
            fontSize: 'var(--text-3xl)',
            fontWeight: 'var(--font-black)',
            color: 'var(--color-white)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--tracking-wider)',
            margin: '0',
            lineHeight: '1'
          }}>
            AIBOA
          </h1>
          <span style={{
            fontSize: 'var(--text-sm)',
            fontWeight: 'var(--font-bold)',
            color: 'var(--color-gray-300)',
            textTransform: 'uppercase',
            letterSpacing: 'var(--tracking-wide)',
            paddingLeft: 'var(--space-3)',
            borderLeft: '3px solid var(--color-white)'
          }}>
            AI 교육 분석
          </span>
        </div>
        
        {/* Navigation */}
        <div style={{
          display: 'flex',
          gap: 'var(--space-2)'
        }}>
          <NavLink href="/" variant="primary">홈</NavLink>
          <NavLink href="/pipeline">파이프라인</NavLink>
          <NavLink href="/comprehensive-reports">종합보고서</NavLink>
        </div>
      </nav>
    </header>
  )
}
