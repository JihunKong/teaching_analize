'use client'

import React from 'react'

export interface BrutalistCardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'heavy' | 'hover'
  title?: string
  subtitle?: string
  onClick?: () => void
  style?: React.CSSProperties
}

const BrutalistCard: React.FC<BrutalistCardProps> = ({
  children,
  className = '',
  variant = 'default',
  title,
  subtitle,
  onClick,
  style
}) => {
  const baseClass = variant === 'heavy' 
    ? 'card-brutalist-heavy' 
    : variant === 'hover'
    ? 'card-brutalist-hover'
    : 'card-brutalist'

  const isClickable = !!onClick

  return (
    <div 
      className={`${baseClass} ${className}`}
      onClick={onClick}
      style={{
        cursor: isClickable ? 'pointer' : 'default',
        ...style
      }}
    >
      {title && (
        <div className="brutalist-card-title" style={{
          fontSize: 'var(--text-xl)',
          fontWeight: 'var(--font-black)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--tracking-wide)',
          marginBottom: subtitle ? 'var(--space-2)' : 'var(--space-3)',
          borderBottom: '3px solid var(--color-black)',
          paddingBottom: 'var(--space-2)'
        }}>
          {title}
        </div>
      )}
      
      {subtitle && (
        <div className="brutalist-card-subtitle" style={{
          fontSize: 'var(--text-sm)',
          fontWeight: 'var(--font-semibold)',
          color: 'var(--color-gray-600)',
          marginBottom: 'var(--space-3)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--tracking-normal)'
        }}>
          {subtitle}
        </div>
      )}
      
      <div className="brutalist-card-content">
        {children}
      </div>
    </div>
  )
}

export default BrutalistCard
