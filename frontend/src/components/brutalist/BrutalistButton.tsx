'use client'

import React from 'react'

export interface BrutalistButtonProps {
  children: React.ReactNode
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  fullWidth?: boolean
  className?: string
  style?: React.CSSProperties
}

const BrutalistButton: React.FC<BrutalistButtonProps> = ({
  children,
  onClick,
  type = 'button',
  variant = 'primary',
  size = 'medium',
  disabled = false,
  fullWidth = false,
  className = '',
  style
}) => {
  const getVariantClass = () => {
    switch (variant) {
      case 'primary':
        return 'btn-brutalist btn-brutalist-primary'
      case 'secondary':
        return 'btn-brutalist btn-brutalist-secondary'
      case 'outline':
        return 'btn-brutalist btn-brutalist-outline'
      case 'ghost':
        return 'btn-brutalist btn-brutalist-ghost'
      default:
        return 'btn-brutalist'
    }
  }

  const getSizeClass = () => {
    switch (size) {
      case 'small':
        return 'btn-brutalist-sm'
      case 'large':
        return 'btn-brutalist-large'
      default:
        return ''
    }
  }

  const widthClass = fullWidth ? 'w-full' : ''

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${getVariantClass()} ${getSizeClass()} ${widthClass} ${className}`}
      style={{
        opacity: disabled ? 0.5 : 1,
        cursor: disabled ? 'not-allowed' : 'pointer',
        ...style
      }}
    >
      {children}
    </button>
  )
}

export default BrutalistButton
