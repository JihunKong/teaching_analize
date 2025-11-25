'use client'

import { useState } from 'react'

interface BentoCardProps {
  title: string
  description: string
  emoji: string
}

export default function BentoCard({ title, description, emoji }: BentoCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div
      className="bento-card"
      style={{
        border: '4px solid var(--color-black)',
        padding: 'var(--space-4)',
        background: 'var(--color-white)',
        boxShadow: isHovered ? '4px 4px 0 var(--color-black)' : '8px 8px 0 var(--color-black)',
        transform: isHovered ? 'translate(4px, 4px)' : 'translate(0, 0)',
        transition: 'transform 0.15s ease, box-shadow 0.15s ease'
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <h3 style={{
        fontSize: 'var(--text-xl)',
        fontWeight: 'var(--font-black)',
        marginBottom: 'var(--space-2)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--tracking-normal)'
      }}>
        {emoji} {title}
      </h3>
      <p style={{
        color: 'var(--color-gray-700)',
        fontSize: 'var(--text-base)',
        fontWeight: 'var(--font-medium)',
        lineHeight: 'var(--leading-relaxed)'
      }}>
        {description}
      </p>
    </div>
  )
}
