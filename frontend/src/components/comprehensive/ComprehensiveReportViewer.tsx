'use client'

import { useState } from 'react'

interface ComprehensiveReportViewerProps {
  reportHtml: string
  title: string
  onClose?: () => void
  onDownload?: () => void
}

export default function ComprehensiveReportViewer({ 
  reportHtml, 
  title, 
  onClose, 
  onDownload 
}: ComprehensiveReportViewerProps) {
  const [viewMode, setViewMode] = useState<'embedded' | 'fullscreen'>('embedded')

  const openInNewTab = () => {
    const newWindow = window.open('', '_blank')
    if (newWindow) {
      newWindow.document.write(reportHtml)
      newWindow.document.close()
    }
  }

  const downloadReport = () => {
    const blob = new Blob([reportHtml], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = `${title.replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().toISOString().split('T')[0]}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    
    URL.revokeObjectURL(url)
    
    if (onDownload) onDownload()
  }

  return (
    <div className="comprehensive-report-viewer">
      {/* Report Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '15px 20px',
        background: '#f8f9fa',
        borderBottom: '1px solid #dee2e6',
        borderRadius: '10px 10px 0 0'
      }}>
        <div>
          <h3 style={{ margin: 0, color: '#333' }}>{title}</h3>
          <small style={{ color: '#666' }}>
            생성일: {new Date().toLocaleDateString('ko-KR')}
          </small>
        </div>
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className="btn btn-secondary"
            onClick={() => setViewMode(viewMode === 'embedded' ? 'fullscreen' : 'embedded')}
            style={{ padding: '8px 15px', fontSize: '0.9rem' }}
          >
            {viewMode === 'embedded' ? '전체화면' : '임베디드'}
          </button>
          
          <button
            className="btn"
            onClick={openInNewTab}
            style={{ padding: '8px 15px', fontSize: '0.9rem' }}
          >
            새 탭에서 열기
          </button>
          
          <button
            className="btn"
            onClick={downloadReport}
            style={{ padding: '8px 15px', fontSize: '0.9rem' }}
          >
            다운로드
          </button>
          
          {onClose && (
            <button
              className="btn btn-secondary"
              onClick={onClose}
              style={{ padding: '8px 15px', fontSize: '0.9rem' }}
            >
              닫기
            </button>
          )}
        </div>
      </div>

      {/* Report Content */}
      <div style={{
        height: viewMode === 'fullscreen' ? '80vh' : '600px',
        border: '1px solid #dee2e6',
        borderTop: 'none',
        borderRadius: '0 0 10px 10px',
        overflow: 'hidden'
      }}>
        <iframe
          srcDoc={reportHtml}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            background: 'white'
          }}
          title={title}
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
      
      {/* Report Controls */}
      <div style={{
        padding: '15px 20px',
        background: '#f8f9fa',
        borderTop: '1px solid #dee2e6',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '0.9rem',
        color: '#666'
      }}>
        <div>
          보고서 크기: {(new Blob([reportHtml]).size / 1024).toFixed(1)} KB
        </div>
        
        <div style={{ display: 'flex', gap: '15px' }}>
          <button
            className="btn btn-secondary"
            onClick={() => window.print()}
            style={{ padding: '6px 12px', fontSize: '0.8rem' }}
          >
            인쇄
          </button>
          
          <button
            className="btn btn-secondary"
            onClick={() => {
              navigator.clipboard.writeText(window.location.href)
                .then(() => alert('링크가 클립보드에 복사되었습니다.'))
                .catch(() => alert('링크 복사에 실패했습니다.'))
            }}
            style={{ padding: '6px 12px', fontSize: '0.8rem' }}
          >
            링크 복사
          </button>
        </div>
      </div>
    </div>
  )
}