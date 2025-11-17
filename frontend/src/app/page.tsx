'use client'

import Link from 'next/link'
import BentoCard from '../components/BentoCard'

export default function HomePage() {
  return (
    <div className="brutalist-page">
      {/* Hero Section - Ultra Brutalist */}
      <div className="brutalist-hero">
        <div className="container" style={{
          textAlign: 'center',
          padding: 'var(--space-12) var(--space-4)',
          borderBottom: '12px solid var(--color-black)',
          marginBottom: 'var(--space-8)',
          position: 'relative'
        }}>
          {/* Geometric decorations */}
          <div className="geo-square" style={{
            position: 'absolute',
            top: 'var(--space-4)',
            left: 'var(--space-4)',
            width: '80px',
            height: '80px',
            border: '8px solid var(--color-black)',
            background: 'var(--color-gray-200)'
          }} />
          
          <div className="geo-square" style={{
            position: 'absolute',
            bottom: 'var(--space-4)',
            right: 'var(--space-4)',
            width: '60px',
            height: '60px',
            border: '6px solid var(--color-black)',
            background: 'var(--color-white)'
          }} />
          
          <h1 className="brutalist-headline" style={{
            fontSize: '5rem',
            fontWeight: 'var(--font-black)',
            letterSpacing: '-0.03em',
            marginBottom: 'var(--space-2)',
            textTransform: 'uppercase',
            color: 'var(--color-black)',
            lineHeight: '1'
          }}>
            AIBOA
          </h1>
          
          <div className="brutalist-subtitle" style={{
            fontSize: 'var(--text-2xl)',
            fontWeight: 'var(--font-bold)',
            letterSpacing: 'var(--tracking-wide)',
            textTransform: 'uppercase',
            marginBottom: 'var(--space-8)',
            color: 'var(--color-gray-700)'
          }}>
            AI 기반 교육 분석 플랫폼
          </div>

          <div className="card-brutalist" style={{
            maxWidth: '600px',
            margin: '0 auto var(--space-6)',
            textAlign: 'left'
          }}>
            <h2 className="brutalist-title" style={{
              fontSize: 'var(--text-3xl)',
              fontWeight: 'var(--font-black)',
              marginBottom: 'var(--space-3)',
              textTransform: 'uppercase',
              letterSpacing: 'var(--tracking-wide)'
            }}>
              통합 분석 파이프라인
            </h2>
            <p style={{
              fontSize: 'var(--text-lg)',
              marginBottom: 'var(--space-4)',
              color: 'var(--color-gray-700)',
              lineHeight: 'var(--leading-relaxed)',
              fontWeight: 'var(--font-medium)'
            }}>
              YouTube 영상 업로드부터 보고서 생성까지 한 번에!<br />
              <strong>전사 → 분석 → 보고서</strong>를 자동으로 진행합니다.
            </p>
            <Link href="/pipeline" className="btn-brutalist btn-brutalist-primary" style={{
              display: 'inline-block',
              fontSize: 'var(--text-xl)',
              padding: 'var(--space-4) var(--space-8)'
            }}>
              지금 시작하기 →
            </Link>
          </div>
        </div>
      </div>
      
      {/* Features Section - Bento Grid */}
      <div className="container">
        <h2 className="brutalist-section-title" style={{
          fontSize: 'var(--text-4xl)',
          fontWeight: 'var(--font-black)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--tracking-wide)',
          marginBottom: 'var(--space-6)',
          textAlign: 'center',
          borderBottom: '8px solid var(--color-black)',
          paddingBottom: 'var(--space-3)'
        }}>
          주요 특징
        </h2>
        
        <div className="bento-grid" style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 'var(--space-4)',
          marginBottom: 'var(--space-8)'
        }}>
          <BentoCard
            emoji="✅"
            title="검증된 전사"
            description="Selenium 브라우저 자동화를 통한 YouTube 자막 스크래핑"
          />
          
          <BentoCard
            emoji="🎯"
            title="다양한 프레임워크"
            description="CBIL, 학생 토론, 수업 코칭 등 15개 교육 분석 도구"
          />
          
          <BentoCard
            emoji="📈"
            title="실시간 모니터링"
            description="전사와 분석 진행 상황을 실시간으로 모니터링"
          />
          
          <BentoCard
            emoji="🎨"
            title="시각화 보고서"
            description="인터랙티브 차트와 시각화가 포함된 HTML 보고서"
          />
          
          <BentoCard
            emoji="💾"
            title="연구 데이터"
            description="교사별 발화 패턴 데이터 축적 및 종단 분석"
          />
          
          <BentoCard
            emoji="🔒"
            title="안전한 관리"
            description="사용자 인증 및 안전한 데이터 저장"
          />
        </div>
      </div>
      
      {/* Usage Steps Section - Brutalist Timeline */}
      <div className="container" style={{
        borderTop: '8px solid var(--color-black)',
        paddingTop: 'var(--space-8)'
      }}>
        <h2 className="brutalist-section-title" style={{
          fontSize: 'var(--text-4xl)',
          fontWeight: 'var(--font-black)',
          textTransform: 'uppercase',
          letterSpacing: 'var(--tracking-wide)',
          marginBottom: 'var(--space-6)',
          textAlign: 'center'
        }}>
          사용 방법
        </h2>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: 'var(--space-6)',
          marginBottom: 'var(--space-8)'
        }}>
          <div className="card-brutalist-heavy" style={{ textAlign: 'center', background: 'var(--color-gray-100)' }}>
            <div style={{
              fontSize: '4rem',
              fontWeight: 'var(--font-black)',
              marginBottom: 'var(--space-3)',
              color: 'var(--color-black)'
            }}>01</div>
            <h3 style={{
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-black)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase'
            }}>
              YouTube URL 입력
            </h3>
            <p style={{
              color: 'var(--color-gray-700)',
              fontSize: 'var(--text-base)',
              fontWeight: 'var(--font-medium)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              수업이 촬영된 YouTube 영상의 URL을 입력합니다.
            </p>
          </div>
          
          <div className="card-brutalist-heavy" style={{ textAlign: 'center', background: 'var(--color-gray-100)' }}>
            <div style={{
              fontSize: '4rem',
              fontWeight: 'var(--font-black)',
              marginBottom: 'var(--space-3)',
              color: 'var(--color-black)'
            }}>02</div>
            <h3 style={{
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-black)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase'
            }}>
              프레임워크 선택
            </h3>
            <p style={{
              color: 'var(--color-gray-700)',
              fontSize: 'var(--text-base)',
              fontWeight: 'var(--font-medium)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              CBIL, 학생 토론 등 원하는 분석 방법을 선택합니다.
            </p>
          </div>
          
          <div className="card-brutalist-heavy" style={{ textAlign: 'center', background: 'var(--color-gray-100)' }}>
            <div style={{
              fontSize: '4rem',
              fontWeight: 'var(--font-black)',
              marginBottom: 'var(--space-3)',
              color: 'var(--color-black)'
            }}>03</div>
            <h3 style={{
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-black)',
              marginBottom: 'var(--space-2)',
              textTransform: 'uppercase'
            }}>
              보고서 확인
            </h3>
            <p style={{
              color: 'var(--color-gray-700)',
              fontSize: 'var(--text-base)',
              fontWeight: 'var(--font-medium)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              생성된 분석 보고서를 확인하고 교육에 활용합니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
