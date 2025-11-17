'use client'

import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface AnalysisResultRendererProps {
  content: string
  className?: string
}

const AnalysisResultRenderer: React.FC<AnalysisResultRendererProps> = ({ content, className = '' }) => {
  return (
    <div className={`analysis-result-content ${className}`} style={{
      lineHeight: '1.8',
      fontFamily: 'Georgia, "Malgun Gothic", "맑은 고딕", serif'
    }}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // 제목 스타일링 - #### 1. Engage 형식
          h4: ({ children }) => (
            <div style={{
              fontSize: '1.1rem',
              fontWeight: 'bold',
              color: '#2980b9',
              margin: '15px 0 10px 0',
              padding: '8px 15px',
              background: 'linear-gradient(135deg, #ebf8ff 0%, #f0f8ff 100%)',
              borderLeft: '4px solid #3498db',
              borderRadius: '0 8px 8px 0',
              boxShadow: '0 2px 4px rgba(52, 152, 219, 0.1)'
            }}>
              {children}
            </div>
          ),
          h3: ({ children }) => (
            <div style={{
              fontSize: '1.2rem',
              fontWeight: 'bold',
              color: '#34495e',
              margin: '18px 0 12px 0',
              padding: '8px 0',
              borderBottom: '1px solid #bdc3c7'
            }}>
              {children}
            </div>
          ),
          h2: ({ children }) => (
            <div style={{
              fontSize: '1.4rem',
              fontWeight: 'bold',
              color: '#2c3e50',
              margin: '20px 0 15px 0',
              padding: '10px 0',
              borderBottom: '2px solid #3498db'
            }}>
              {children}
            </div>
          ),
          // 강조 텍스트 - **점수: X점** 형식
          strong: ({ children }) => {
            const text = children?.toString() || ''
            if (text.includes('점수:')) {
              return (
                <span style={{
                  display: 'inline-block',
                  background: 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)',
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '0.9rem',
                  fontWeight: 'bold',
                  margin: '5px 0',
                  boxShadow: '0 2px 6px rgba(46, 204, 113, 0.3)',
                  textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                }}>
                  {children}
                </span>
              )
            }
            return (
              <strong style={{
                color: '#e74c3c',
                fontWeight: '600'
              }}>
                {children}
              </strong>
            )
          },
          // 리스트 스타일링
          ul: ({ children }) => (
            <ul style={{
              margin: '12px 0',
              paddingLeft: '0',
              listStyle: 'none'
            }}>
              {children}
            </ul>
          ),
          li: ({ children }) => (
            <li style={{
              position: 'relative',
              margin: '8px 0',
              paddingLeft: '25px',
              color: '#2c3e50'
            }}>
              <span style={{
                position: 'absolute',
                left: '0',
                top: '0',
                color: '#27ae60',
                fontWeight: 'bold',
                fontSize: '1.1rem'
              }}>✓</span>
              {children}
            </li>
          ),
          // 일반 텍스트 단락
          p: ({ children }) => (
            <p style={{
              margin: '12px 0',
              color: '#2c3e50',
              textAlign: 'justify'
            }}>
              {children}
            </p>
          ),
          // 블록 인용
          blockquote: ({ children }) => (
            <div style={{
              margin: '15px 0',
              padding: '15px 20px',
              background: '#f8f9fa',
              borderLeft: '5px solid #6c757d',
              borderRadius: '0 8px 8px 0',
              fontStyle: 'italic',
              color: '#495057',
              boxShadow: '0 2px 4px rgba(108, 117, 125, 0.1)'
            }}>
              {children}
            </div>
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default AnalysisResultRenderer