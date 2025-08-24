'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function ReportsPage() {
  const [sampleAnalysis] = useState({
    analysis_id: "sample-cbil-001",
    framework: "cbil",
    framework_name: "개념기반 탐구 수업(CBIL) 분석",
    analysis: `### CBIL 7단계 분석

#### 1. Engage (흥미 유도 및 연결)
수업 초반에 교사는 학생들에게 시를 낭송하며 흥미를 유도했다. 학생들은 시를 따라 읽으며 참여했으나, 정서적·지적 호기심을 유도하는 데 있어 개념과의 명확한 연결은 부족했다. 이는 지식 중심의 정보 전달에 가까웠다. 점수: 1점

#### 2. Focus (탐구 방향 설정)
교사는 이육사의 시와 관련된 질문을 던졌으나, 질문이 주로 감상 중심이었다. 개념 중심 사고를 유도하는 본질적 질문이 부족했다. 점수: 1점

#### 3. Investigate (자료 탐색 및 개념 형성)
학생들은 시를 읽고 감상하는 활동을 했으나, 개념의 속성이나 조건을 탐색하는 활동은 부족했다. 점수: 1점

#### 4. Organize (개념 구조화)
수업에서 개념을 구조화하는 활동은 명확하지 않았다. 학생들이 정보를 단편적으로 정리하는 데 그쳤다. 점수: 1점

#### 5. Generalize (일반화 진술)
수업에서 개념을 일반화하는 활동은 명확히 드러나지 않았다. 점수: 0점

#### 6. Transfer (새로운 맥락에 적용)
수업에서 개념을 새로운 맥락에 적용하는 활동은 제한적이었다. 점수: 1점

#### 7. Reflect (사고 성찰)
학생들은 수업을 통해 자신의 사고 변화를 성찰하는 기회를 가졌으나, 구조적 성찰은 부족했다. 점수: 1점`,
    character_count: 5026,
    word_count: 1229,
    created_at: "2025-08-22T10:35:00Z",
    metadata: {
      video_url: "https://www.youtube.com/watch?v=-OLCt6WScEY",
      video_id: "-OLCt6WScEY",
      language: "ko"
    }
  })

  const generateSampleReport = async () => {
    try {
      const response = await fetch('/api/reports/generate/html', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_result: sampleAnalysis,
          template: 'comprehensive',
          title: `${sampleAnalysis.framework_name} 분석 보고서`
        }),
      })

      if (response.ok) {
        const htmlContent = await response.text()
        
        // Open HTML report in new window
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(htmlContent)
          newWindow.document.close()
        }
      } else {
        throw new Error('Report generation failed')
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('보고서 생성 중 오류가 발생했습니다. 서비스가 실행 중인지 확인해주세요.')
    }
  }

  const generateSummaryReport = async () => {
    try {
      const response = await fetch('/api/reports/generate/html', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_result: sampleAnalysis,
          template: 'summary',
          title: `${sampleAnalysis.framework_name} 요약 보고서`
        }),
      })

      if (response.ok) {
        const htmlContent = await response.text()
        
        // Open HTML report in new window
        const newWindow = window.open('', '_blank')
        if (newWindow) {
          newWindow.document.write(htmlContent)
          newWindow.document.close()
        }
      } else {
        throw new Error('Report generation failed')
      }
    } catch (error) {
      console.error('Error generating report:', error)
      alert('보고서 생성 중 오류가 발생했습니다.')
    }
  }

  const downloadJsonReport = () => {
    const jsonData = JSON.stringify(sampleAnalysis, null, 2)
    const blob = new Blob([jsonData], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = `analysis-${sampleAnalysis.analysis_id}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    
    URL.revokeObjectURL(url)
  }

  return (
    <div className="container">
      <div className="page-title">분석 보고서</div>
      <div className="page-subtitle">HTML 보고서로 분석 결과를 확인하세요</div>
      
      <div className="container">
        <h3>📊 보고서 템플릿</h3>
        <div className="grid grid-2">
          <div className="card">
            <h4>📄 종합 보고서</h4>
            <p>인터랙티브 차트와 시각화가 포함된 상세한 분석 보고서입니다.</p>
            <div style={{ marginTop: '20px' }}>
              <button
                className="btn"
                onClick={generateSampleReport}
              >
                📄 종합 보고서 보기
              </button>
            </div>
          </div>
          
          <div className="card">
            <h4>📋 요약 보고서</h4>
            <p>핵심 내용만 담은 간결한 요약 보고서입니다.</p>
            <div style={{ marginTop: '20px' }}>
              <button
                className="btn btn-secondary"
                onClick={generateSummaryReport}
              >
                📋 요약 보고서 보기
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div className="container">
        <h3>💾 데이터 내보내기</h3>
        <div className="card">
          <h4>🔄 JSON 형식</h4>
          <p>분석 결과를 JSON 형식으로 다운로드하여 다른 시스템에서 활용할 수 있습니다.</p>
          <div style={{ marginTop: '20px' }}>
            <button
              className="btn"
              onClick={downloadJsonReport}
            >
              📥 JSON 다운로드
            </button>
          </div>
        </div>
      </div>
      
      <div className="container">
        <h3>🎨 보고서 특징</h3>
        <div className="grid grid-3">
          <div className="card">
            <h4>📊 시각적 분석</h4>
            <p>차트와 그래프로 분석 결과를 직관적으로 표현합니다.</p>
            <ul style={{ marginLeft: '20px', color: '#666', fontSize: '0.9rem' }}>
              <li>반응형 디자인</li>
              <li>인터랙티브 요소</li>
              <li>인쇄 최적화</li>
            </ul>
          </div>
          
          <div className="card">
            <h4>📱 모바일 최적화</h4>
            <p>모든 기기에서 완벽하게 보이는 반응형 보고서입니다.</p>
            <ul style={{ marginLeft: '20px', color: '#666', fontSize: '0.9rem' }}>
              <li>모바일 친화적</li>
              <li>터치 인터페이스</li>
              <li>빠른 로딩</li>
            </ul>
          </div>
          
          <div className="card">
            <h4>🎨 전문적 디자인</h4>
            <p>교육 전문가를 위한 세련되고 전문적인 보고서 디자인입니다.</p>
            <ul style={{ marginLeft: '20px', color: '#666', fontSize: '0.9rem' }}>
              <li>색상 코딩</li>
              <li>타이포그래피</li>
              <li>레이아웃 최적화</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div className="container">
        <h3>📈 활용 방법</h3>
        <div className="grid grid-2">
          <div>
            <h4>🎯 개인 활용</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li>자신의 수업 개선점 파악</li>
              <li>교수법 변화 추적</li>
              <li>학습자 중심 수업 설계</li>
              <li>동료 교사와 경험 공유</li>
            </ul>
          </div>
          
          <div>
            <h4>🏫 기관 활용</h4>
            <ul style={{ marginLeft: '20px', color: '#666' }}>
              <li>교사 연수 자료로 활용</li>
              <li>수업 컨설팅 도구</li>
              <li>교육과정 개선 근거</li>
              <li>수업 품질 관리</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div className="status status-info" style={{ marginTop: '30px' }}>
        <strong>💡 안내:</strong> 위의 샘플 보고서는 실제 수업 분석 결과를 기반으로 한 예시입니다. 
        실제 분석을 진행하려면 <Link href="/transcription" style={{ color: '#0c5460', fontWeight: 'bold' }}>전사 페이지</Link>에서 
        YouTube URL을 입력하거나 <Link href="/analysis" style={{ color: '#0c5460', fontWeight: 'bold' }}>분석 페이지</Link>에서 
        텍스트를 직접 입력하세요.
      </div>
    </div>
  )
}