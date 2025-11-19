'use client'

interface BentoCardProps {
  title: string
  description: string
  emoji: string
}

export default function BentoCard({ title, description, emoji }: BentoCardProps) {
  return (
    <div className="card">
      <h3 style={{
        fontSize: 'var(--text-lg)',
        fontWeight: 'var(--font-semibold)',
        marginBottom: 'var(--space-2)',
        color: 'var(--color-black)'
      }}>
        {emoji} {title}
      </h3>
      <p style={{
        color: 'var(--color-gray-600)',
        fontSize: 'var(--text-base)',
        lineHeight: 'var(--leading-relaxed)'
      }}>
        {description}
      </p>
    </div>
  )
}
