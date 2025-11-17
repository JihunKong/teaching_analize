'use client'

import Link from 'next/link'
import BentoCard from '../components/BentoCard'

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <div style={{
        textAlign: 'center',
        padding: '0 var(--space-4) var(--space-4) var(--space-4)',
        background: 'var(--color-white)',
        borderBottom: '1px solid var(--color-gray-200)'
      }}>
        <h1 style={{
          fontSize: 'var(--text-4xl)',
          fontWeight: 'var(--font-bold)',
          letterSpacing: '-0.02em',
          marginBottom: 'var(--space-2)',
          color: 'var(--color-black)',
          lineHeight: 'var(--leading-tight)'
        }}>
          TVAS
        </h1>

        <p style={{
          fontSize: 'var(--text-xl)',
          fontWeight: 'var(--font-semibold)',
          marginBottom: 'var(--space-6)',
          color: 'var(--color-gray-600)'
        }}>
          Teacher Voice Analysis System
        </p>

        <div className="card" style={{
          maxWidth: '600px',
          margin: '0 auto var(--space-6)',
          textAlign: 'left',
          padding: 'var(--space-6)'
        }}>
          <h2 style={{
            fontSize: 'var(--text-2xl)',
            fontWeight: 'var(--font-semibold)',
            marginBottom: 'var(--space-3)',
            color: 'var(--color-black)'
          }}>
            수업 분석 통합 플랫폼
          </h2>
          <p style={{
            fontSize: 'var(--text-base)',
            marginBottom: 'var(--space-4)',
            color: 'var(--color-gray-700)',
            lineHeight: 'var(--leading-relaxed)'
          }}>
            YouTube 영상 전사부터 교수 효과성 진단 보고서 생성까지 한 번에.<br />
            <strong>전사 → 분석 → 보고서</strong> 자동 분석 시스템을 제공합니다.
          </p>
          <Link href="/pipeline" className="btn btn-large">
            분석 시작하기 →
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="main">
        <h2 style={{
          fontSize: 'var(--text-3xl)',
          fontWeight: 'var(--font-semibold)',
          marginBottom: 'var(--space-6)',
          textAlign: 'center',
          color: 'var(--color-black)',
          borderBottom: '2px solid var(--color-gray-200)',
          paddingBottom: 'var(--space-3)'
        }}>
          주요 특징
        </h2>

        <div className="grid grid-3" style={{ marginBottom: 'var(--space-8)' }}>
          <BentoCard
            emoji="✅"
            title="유튜브 자막 크롤링"
            description="비용 절감을 위한 YouTube 자막 스크래핑 (향후 WhisperX 전환 예정)"
          />

          <BentoCard
            emoji="🎯"
            title="3차원 분석"
            description="수업 단계 × 교수 기능 × 인지 수준 매트릭스 분석"
          />

          <BentoCard
            emoji="📈"
            title="실시간 진행률"
            description="전사 및 분석 과정을 실시간으로 모니터링"
          />

          <BentoCard
            emoji="🏥"
            title="의료 진단 스타일 보고서"
            description="InBody 스타일의 전문적인 교수 효과성 진단 리포트"
          />

          <BentoCard
            emoji="💾"
            title="연구 데이터 축적"
            description="교사별 발화 패턴 데이터 저장 및 종단 분석 지원"
          />

          <BentoCard
            emoji="🔒"
            title="안전한 관리"
            description="사용자 인증 및 PostgreSQL 기반 안전한 데이터 저장"
          />
        </div>
      </div>

      {/* Usage Steps Section */}
      <div className="main" style={{
        borderTop: '2px solid var(--color-gray-200)',
        paddingTop: 'var(--space-8)'
      }}>
        <h2 style={{
          fontSize: 'var(--text-3xl)',
          fontWeight: 'var(--font-semibold)',
          marginBottom: 'var(--space-6)',
          textAlign: 'center',
          color: 'var(--color-black)'
        }}>
          사용 방법
        </h2>

        <div className="grid grid-3" style={{ marginBottom: 'var(--space-8)' }}>
          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: 'var(--text-4xl)',
              fontWeight: 'var(--font-bold)',
              marginBottom: 'var(--space-3)',
              color: 'var(--color-gray-900)'
            }}>01</div>
            <h3 style={{
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-semibold)',
              marginBottom: 'var(--space-2)',
              color: 'var(--color-black)'
            }}>
              YouTube URL 입력
            </h3>
            <p style={{
              color: 'var(--color-gray-600)',
              fontSize: 'var(--text-base)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              수업이 녹화된 YouTube 영상의 URL을 입력합니다
            </p>
          </div>

          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: 'var(--text-4xl)',
              fontWeight: 'var(--font-bold)',
              marginBottom: 'var(--space-3)',
              color: 'var(--color-gray-900)'
            }}>02</div>
            <h3 style={{
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-semibold)',
              marginBottom: 'var(--space-2)',
              color: 'var(--color-black)'
            }}>
              자동 분석 대기
            </h3>
            <p style={{
              color: 'var(--color-gray-600)',
              fontSize: 'var(--text-base)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              전사 및 3차원 분석이 자동으로 진행됩니다
            </p>
          </div>

          <div className="card" style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: 'var(--text-4xl)',
              fontWeight: 'var(--font-bold)',
              marginBottom: 'var(--space-3)',
              color: 'var(--color-gray-900)'
            }}>03</div>
            <h3 style={{
              fontSize: 'var(--text-xl)',
              fontWeight: 'var(--font-semibold)',
              marginBottom: 'var(--space-2)',
              color: 'var(--color-black)'
            }}>
              진단 보고서 확인
            </h3>
            <p style={{
              color: 'var(--color-gray-600)',
              fontSize: 'var(--text-base)',
              lineHeight: 'var(--leading-relaxed)'
            }}>
              생성된 진단 보고서를 확인하고 교육 개선에 활용합니다
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
