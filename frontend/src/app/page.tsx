'use client'

import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="container">
      <div className="page-title">AIBOA</div>
      <div className="page-subtitle">AI 기반 교육 분석 플랫폼</div>
      
      <div className="grid grid-3">
        <div className="card">
          <h3>🎬 YouTube 전사</h3>
          <p>수업 영상의 YouTube URL을 입력하면 자동으로 음성을 텍스트로 변환합니다.</p>
          <div style={{ marginTop: '20px' }}>
            <Link href="/transcription" className="btn">전사 시작하기</Link>
          </div>
        </div>
        
        <div className="card">
          <h3>🧠 교육 분석</h3>
          <p>CBIL, 블룸의 택사노미 등 다양한 프레임워크로 교사의 발화를 분석합니다.</p>
          <div style={{ marginTop: '20px' }}>
            <Link href="/analysis" className="btn">분석 시작하기</Link>
          </div>
        </div>
        
        <div className="card">
          <h3>📊 보고서 생성</h3>
          <p>분석 결과를 아름다운 HTML 보고서로 생성하여 교육 개선에 활용하세요.</p>
          <div style={{ marginTop: '20px' }}>
            <Link href="/reports" className="btn">보고서 보기</Link>
          </div>
        </div>
      </div>
      
      <div className="container" style={{ marginTop: '30px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '25px', color: '#333' }}>주요 특징</h2>
        
        <div className="grid grid-2">
          <div>
            <h4>✅ 검증된 YouTube 전사 방법</h4>
            <p>youtube-transcript-api를 사용한 안정적이고 정확한 전사</p>
          </div>
          
          <div>
            <h4>🎯 다양한 분석 프레임워크</h4>
            <p>CBIL, 학생 토론, 수업 코칭 등 15개 교육 분석 도구</p>
          </div>
          
          <div>
            <h4>📈 실시간 진행 상황</h4>
            <p>전사와 분석 진행 상황을 실시간으로 모니터링</p>
          </div>
          
          <div>
            <h4>🎨 아름다운 보고서</h4>
            <p>인터랙티브 차트와 시각화가 포함된 HTML 보고서</p>
          </div>
          
          <div>
            <h4>💾 연구 데이터 축적</h4>
            <p>교사별 발화 패턴 데이터 축적 및 종단 분석</p>
          </div>
          
          <div>
            <h4>🔒 안전한 데이터 관리</h4>
            <p>사용자 인증 및 안전한 데이터 저장</p>
          </div>
        </div>
      </div>
      
      <div className="container" style={{ marginTop: '30px', textAlign: 'center' }}>
        <h2 style={{ marginBottom: '20px', color: '#333' }}>사용 방법</h2>
        <div className="grid grid-3">
          <div>
            <div style={{ fontSize: '2rem', marginBottom: '15px' }}>1️⃣</div>
            <h4>YouTube URL 입력</h4>
            <p>수업이 촬영된 YouTube 영상의 URL을 입력합니다.</p>
          </div>
          
          <div>
            <div style={{ fontSize: '2rem', marginBottom: '15px' }}>2️⃣</div>
            <h4>분석 프레임워크 선택</h4>
            <p>CBIL, 학생 토론 등 원하는 분석 방법을 선택합니다.</p>
          </div>
          
          <div>
            <div style={{ fontSize: '2rem', marginBottom: '15px' }}>3️⃣</div>
            <h4>보고서 확인</h4>
            <p>생성된 분석 보고서를 확인하고 교육에 활용합니다.</p>
          </div>
        </div>
      </div>
    </div>
  )
}