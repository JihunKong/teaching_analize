'use client'

import Link from 'next/link'
import BentoCard from '../components/BentoCard'

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <div style={{
        position: 'relative',
        overflow: 'hidden',
        padding: 'var(--space-24) 0 var(--space-16)',
        background: 'radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.1) 0%, transparent 50%)'
      }}>
        <div className="container text-center animate-fade-in">
          <div style={{
            display: 'inline-block',
            padding: 'var(--space-2) var(--space-4)',
            background: 'rgba(37, 99, 235, 0.1)',
            borderRadius: 'var(--radius-full)',
            color: 'var(--color-primary)',
            fontSize: 'var(--text-sm)',
            fontWeight: '600',
            marginBottom: 'var(--space-6)'
          }}>
            ✨ Next Generation Classroom Analysis
          </div>

          <h1 style={{
            fontSize: 'var(--text-5xl)',
            fontWeight: '800',
            letterSpacing: '-0.03em',
            marginBottom: 'var(--space-6)',
            lineHeight: '1.1'
          }}>
            Transform Your Teaching with <br />
            <span className="text-gradient">AI-Powered Insights</span>
          </h1>

          <p style={{
            fontSize: 'var(--text-xl)',
            color: 'var(--color-text-secondary)',
            maxWidth: '600px',
            margin: '0 auto var(--space-8)',
            lineHeight: '1.6'
          }}>
            From YouTube transcription to comprehensive medical-grade diagnostic reports.
            Elevate your instructional quality with data-driven feedback.
          </p>

          <div style={{ display: 'flex', gap: 'var(--space-4)', justifyContent: 'center' }}>
            <Link href="/pipeline" className="btn btn-primary btn-large">
              Start Analysis
            </Link>
            <Link href="#features" className="btn btn-secondary btn-large">
              Learn More
            </Link>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="container" style={{ padding: 'var(--space-16) var(--space-6)' }}>
        <div className="text-center mb-4">
          <h2 style={{ fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-4)' }}>
            Powerful Features
          </h2>
          <p style={{ color: 'var(--color-text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            Everything you need to analyze and improve your teaching methods.
          </p>
        </div>

        <div className="grid grid-3">
          <BentoCard
            emoji="📹"
            title="YouTube Integration"
            description="Seamlessly import and transcribe classroom videos directly from YouTube."
          />

          <BentoCard
            emoji="🧠"
            title="3D Analysis Matrix"
            description="Deep dive into teaching steps, instructional functions, and cognitive levels."
          />

          <BentoCard
            emoji="⚡️"
            title="Real-time Processing"
            description="Watch the analysis pipeline in action with real-time progress tracking."
          />

          <BentoCard
            emoji="🩺"
            title="Diagnostic Reports"
            description="Receive a medical-grade diagnosis of your teaching effectiveness."
          />

          <BentoCard
            emoji="📊"
            title="Longitudinal Data"
            description="Track your improvement over time with accumulated historical data."
          />

          <BentoCard
            emoji="🛡️"
            title="Secure & Private"
            description="Your classroom data is encrypted and stored securely."
          />
        </div>
      </div>

      {/* Usage Steps Section */}
      <div style={{ background: 'var(--color-surface-alt)', padding: 'var(--space-16) 0' }}>
        <div className="container">
          <div className="text-center mb-4">
            <h2 style={{ fontSize: 'var(--text-3xl)', marginBottom: 'var(--space-4)' }}>
              How It Works
            </h2>
          </div>

          <div className="grid grid-3">
            <div className="card text-center" style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                top: '-20px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'var(--color-primary)',
                color: 'white',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold'
              }}>1</div>
              <h3 style={{ marginTop: 'var(--space-4)' }}>Input URL</h3>
              <p style={{ color: 'var(--color-text-secondary)' }}>
                Paste the YouTube URL of your recorded class session.
              </p>
            </div>

            <div className="card text-center" style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                top: '-20px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'var(--color-primary)',
                color: 'white',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold'
              }}>2</div>
              <h3 style={{ marginTop: 'var(--space-4)' }}>AI Analysis</h3>
              <p style={{ color: 'var(--color-text-secondary)' }}>
                Our AI transcribes and analyzes the video across multiple dimensions.
              </p>
            </div>

            <div className="card text-center" style={{ position: 'relative' }}>
              <div style={{
                position: 'absolute',
                top: '-20px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'var(--color-primary)',
                color: 'white',
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold'
              }}>3</div>
              <h3 style={{ marginTop: 'var(--space-4)' }}>Get Report</h3>
              <p style={{ color: 'var(--color-text-secondary)' }}>
                Review your comprehensive diagnostic report and actionable insights.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
