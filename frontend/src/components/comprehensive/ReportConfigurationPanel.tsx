'use client'

import { useState } from 'react'

interface Framework {
  id: string
  name: string
  description: string
}

interface ReportConfiguration {
  title: string
  type: 'comparison' | 'detailed' | 'summary'
  includeRecommendations: boolean
  frameworkWeights: { [framework: string]: number }
  format: 'html' | 'pdf'
}

interface ReportConfigurationPanelProps {
  frameworks: Framework[]
  selectedFrameworks: string[]
  configuration: ReportConfiguration
  onConfigurationChange: (config: ReportConfiguration) => void
}

export default function ReportConfigurationPanel({
  frameworks,
  selectedFrameworks,
  configuration,
  onConfigurationChange
}: ReportConfigurationPanelProps) {
  const [expandedSection, setExpandedSection] = useState<'basic' | 'weights' | 'advanced' | null>('basic')

  const updateConfig = (updates: Partial<ReportConfiguration>) => {
    onConfigurationChange({ ...configuration, ...updates })
  }

  const updateFrameworkWeight = (framework: string, weight: number) => {
    updateConfig({
      frameworkWeights: {
        ...configuration.frameworkWeights,
        [framework]: weight
      }
    })
  }

  const resetWeights = () => {
    const resetWeights: { [framework: string]: number } = {}
    selectedFrameworks.forEach(framework => {
      resetWeights[framework] = 1.0
    })
    updateConfig({ frameworkWeights: resetWeights })
  }

  const getWeightDescription = (weight: number): string => {
    if (weight <= 0.5) return '매우 낮음'
    if (weight <= 0.8) return '낮음'
    if (weight <= 1.2) return '보통'
    if (weight <= 2.0) return '높음'
    return '매우 높음'
  }

  const selectedFrameworksData = frameworks.filter(fw => 
    selectedFrameworks.includes(fw.id)
  )

  const toggleSection = (section: typeof expandedSection) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="config-panel">
      <h3 style={{ marginBottom: '25px', color: '#333' }}>⚙️ 보고서 설정</h3>
      
      {/* Basic Configuration */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <div 
          style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            cursor: 'pointer',
            padding: '10px 0'
          }}
          onClick={() => toggleSection('basic')}
        >
          <h4 style={{ margin: 0 }}>📝 기본 설정</h4>
          <span style={{ fontSize: '1.2rem' }}>
            {expandedSection === 'basic' ? '▼' : '▶'}
          </span>
        </div>
        
        {expandedSection === 'basic' && (
          <div style={{ paddingTop: '15px', borderTop: '1px solid #e9ecef' }}>
            <div className="grid grid-2" style={{ marginBottom: '15px' }}>
              <div className="form-group">
                <label className="form-label">보고서 제목</label>
                <input
                  type="text"
                  className="form-input"
                  value={configuration.title}
                  onChange={(e) => updateConfig({ title: e.target.value })}
                  placeholder="보고서 제목을 입력하세요"
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">보고서 유형</label>
                <select
                  className="form-select"
                  value={configuration.type}
                  onChange={(e) => updateConfig({ type: e.target.value as any })}
                >
                  <option value="detailed">상세 분석</option>
                  <option value="comparison">비교 분석</option>
                  <option value="summary">요약 분석</option>
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <label className="form-label">
                <input
                  type="checkbox"
                  checked={configuration.includeRecommendations}
                  onChange={(e) => updateConfig({ includeRecommendations: e.target.checked })}
                  style={{ marginRight: '8px' }}
                />
                개선 권장사항 포함
              </label>
              <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                AI가 분석을 바탕으로 구체적인 개선 방안을 제안합니다.
              </small>
            </div>
          </div>
        )}
      </div>

      {/* Framework Weights */}
      {selectedFrameworksData.length > 1 && (
        <div className="card" style={{ marginBottom: '20px' }}>
          <div 
            style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              cursor: 'pointer',
              padding: '10px 0'
            }}
            onClick={() => toggleSection('weights')}
          >
            <h4 style={{ margin: 0 }}>⚖️ 프레임워크 가중치</h4>
            <span style={{ fontSize: '1.2rem' }}>
              {expandedSection === 'weights' ? '▼' : '▶'}
            </span>
          </div>
          
          {expandedSection === 'weights' && (
            <div style={{ paddingTop: '15px', borderTop: '1px solid #e9ecef' }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '15px'
              }}>
                <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>
                  각 프레임워크의 중요도를 조정하여 맞춤형 보고서를 생성하세요.
                </p>
                <button
                  className="btn btn-secondary"
                  onClick={resetWeights}
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  초기화
                </button>
              </div>
              
              <div className="grid">
                {selectedFrameworksData.map((framework) => {
                  const weight = configuration.frameworkWeights[framework.id] || 1.0
                  
                  return (
                    <div key={framework.id} className="card" style={{ padding: '15px' }}>
                      <div style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        marginBottom: '10px'
                      }}>
                        <span style={{ fontWeight: 'bold' }}>{framework.name}</span>
                        <span className="weight-display" style={{ 
                          backgroundColor: '#667eea',
                          color: 'white',
                          padding: '4px 8px',
                          borderRadius: '8px',
                          fontSize: '0.9rem'
                        }}>
                          {weight.toFixed(1)}
                        </span>
                      </div>
                      
                      <input
                        type="range"
                        min="0.1"
                        max="3.0"
                        step="0.1"
                        value={weight}
                        onChange={(e) => updateFrameworkWeight(framework.id, parseFloat(e.target.value))}
                        style={{ width: '100%', marginBottom: '8px' }}
                        aria-label={`${framework.name} 가중치`}
                      />
                      
                      <div style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between',
                        fontSize: '0.8rem',
                        color: '#666'
                      }}>
                        <span>낮음 (0.1)</span>
                        <span style={{ fontWeight: 'bold' }}>
                          {getWeightDescription(weight)}
                        </span>
                        <span>높음 (3.0)</span>
                      </div>
                      
                      <div style={{ 
                        fontSize: '0.8rem', 
                        color: '#666',
                        marginTop: '8px',
                        fontStyle: 'italic'
                      }}>
                        {framework.description}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Advanced Configuration */}
      <div className="card">
        <div 
          style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            cursor: 'pointer',
            padding: '10px 0'
          }}
          onClick={() => toggleSection('advanced')}
        >
          <h4 style={{ margin: 0 }}>🔧 고급 설정</h4>
          <span style={{ fontSize: '1.2rem' }}>
            {expandedSection === 'advanced' ? '▼' : '▶'}
          </span>
        </div>
        
        {expandedSection === 'advanced' && (
          <div style={{ paddingTop: '15px', borderTop: '1px solid #e9ecef' }}>
            <div className="form-group">
              <label className="form-label">출력 형식</label>
              <select
                className="form-select"
                value={configuration.format}
                onChange={(e) => updateConfig({ format: e.target.value as any })}
              >
                <option value="html">HTML (웹 브라우저용)</option>
                <option value="pdf">PDF (인쇄용) - 개발 중</option>
              </select>
              <small style={{ color: '#666', marginTop: '5px', display: 'block' }}>
                HTML 형식은 인터랙티브 차트와 반응형 디자인을 지원합니다.
              </small>
            </div>
          </div>
        )}
      </div>

      {/* Configuration Summary */}
      <div style={{ 
        marginTop: '20px',
        padding: '15px',
        backgroundColor: '#e8f4fd',
        border: '1px solid #b3d7ff',
        borderRadius: '8px'
      }}>
        <h5 style={{ margin: '0 0 10px 0', color: '#0c5460' }}>📊 설정 요약</h5>
        <ul style={{ margin: 0, paddingLeft: '20px', color: '#0c5460', fontSize: '0.9rem' }}>
          <li><strong>제목:</strong> {configuration.title}</li>
          <li><strong>유형:</strong> {
            configuration.type === 'detailed' ? '상세 분석' :
            configuration.type === 'comparison' ? '비교 분석' : '요약 분석'
          }</li>
          <li><strong>선택된 프레임워크:</strong> {selectedFrameworksData.length}개</li>
          <li><strong>권장사항:</strong> {configuration.includeRecommendations ? '포함' : '제외'}</li>
          <li><strong>형식:</strong> {configuration.format.toUpperCase()}</li>
        </ul>
      </div>
    </div>
  )
}