'use client'

import React from 'react'

export interface BrutalistInputProps {
  value: string
  onChange: (value: string) => void
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'date'
  placeholder?: string
  label?: string
  error?: string
  disabled?: boolean
  required?: boolean
  fullWidth?: boolean
  className?: string
  style?: React.CSSProperties
}

const BrutalistInput: React.FC<BrutalistInputProps> = ({
  value,
  onChange,
  type = 'text',
  placeholder,
  label,
  error,
  disabled = false,
  required = false,
  fullWidth = true,
  className = '',
  style
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value)
  }

  const widthClass = fullWidth ? 'w-full' : ''

  return (
    <div className={`form-group-brutalist ${widthClass}`} style={style}>
      {label && (
        <label className="form-brutalist-label">
          {label}
          {required && <span style={{ color: 'var(--color-gray-700)' }}> *</span>}
        </label>
      )}
      
      <input
        type={type}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={`form-brutalist-input ${className}`}
        style={{
          borderColor: error ? 'var(--color-gray-900)' : undefined,
          boxShadow: error ? '4px 4px 0 var(--color-gray-900)' : undefined
        }}
      />
      
      {error && (
        <div style={{
          marginTop: 'var(--space-2)',
          fontSize: 'var(--text-sm)',
          fontWeight: 'var(--font-bold)',
          color: 'var(--color-gray-900)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--tracking-wide)'
        }}>
          ⚠ {error}
        </div>
      )}
    </div>
  )
}

export default BrutalistInput
