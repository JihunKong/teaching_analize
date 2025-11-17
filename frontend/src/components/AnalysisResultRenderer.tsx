'use client'

import React, { useState, useEffect, useRef } from 'react'

interface AnalysisResultRendererProps {
  content: string
  analysisId?: string
  framework?: string
}

export default function AnalysisResultRenderer({
  content,
  analysisId,
  framework
}: AnalysisResultRendererProps) {
  const [viewMode, setViewMode] = useState<'visual' | 'text'>('visual')
  const [iframeError, setIframeError] = useState(false)
  const [contentHeight, setContentHeight] = useState<number>(600) // 기본 높이 600px
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // Debug logging
  console.log('AnalysisResultRenderer:', { analysisId, viewMode, hasContent: !!content })

  // postMessage 리스너 - iframe 내부에서 높이 정보 수신
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // 보안: origin 체크 (같은 도메인에서만 허용)
      if (event.origin !== window.location.origin) {
        return
      }

      // iframe에서 전송한 높이 정보 처리
      if (event.data && event.data.type === 'iframe-height') {
        const newHeight = event.data.height
        console.log('Received iframe height:', newHeight)

        // 최소 400px, 최대 2000px로 제한
        const boundedHeight = Math.max(400, Math.min(newHeight, 2000))
        setContentHeight(boundedHeight)
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [])

  if (!content) {
    return <div className="text-gray-500">No analysis content available</div>
  }

  // Show visual report if analysisId is available
  if (analysisId && viewMode === 'visual' && !iframeError) {
    return (
      <div className="space-y-4">
        {/* Control buttons */}
        <div className="flex justify-end gap-2">
          <button
            onClick={() => setViewMode('text')}
            className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition"
          >
            텍스트 보기
          </button>
          <button
            onClick={() => window.open(`/api/reports/html/${analysisId}`, '_blank')}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            새 탭에서 열기
          </button>
          <a
            href={`/api/reports/pdf-enhanced/${analysisId}`}
            download
            className="px-4 py-2 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 transition inline-block"
          >
            PDF 다운로드
          </a>
        </div>

        {/* Visual Report in iframe */}
        <div className="border border-gray-300 rounded-lg overflow-hidden shadow-lg bg-white">
          <iframe
            ref={iframeRef}
            src={`/api/reports/html/${analysisId}`}
            className="w-full transition-all duration-300"
            style={{
              height: `${contentHeight}px`,
              minHeight: '400px',
              maxHeight: '2000px',
              border: 'none'
            }}
            title="Analysis Report"
            onLoad={() => {
              console.log('iframe loaded successfully')
            }}
            onError={() => {
              console.error('iframe failed to load visual report')
              setIframeError(true)
            }}
          />
        </div>

        {/* Info message */}
        <div className="text-sm text-gray-600 mt-2 p-3 bg-blue-50 rounded">
          💡 시각적 보고서가 표시됩니다. Chart.js 차트와 그라데이션 디자인이 포함되어 있습니다.
          {iframeError && (
            <div className="text-red-600 mt-2">
              ⚠️ 시각적 보고서 로딩에 실패했습니다. 텍스트 모드로 전환합니다.
            </div>
          )}
        </div>
      </div>
    )
  }

  // Fallback to text view
  return (
    <div className="space-y-4">
      {analysisId && (
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-gray-600">
            {!iframeError ? (
              <span>📄 텍스트 모드로 보고 있습니다</span>
            ) : (
              <span className="text-red-600">⚠️ 시각적 보고서 로딩 실패 - 텍스트로 표시</span>
            )}
          </div>
          <button
            onClick={() => {
              setIframeError(false)
              setViewMode('visual')
            }}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            🎨 시각화 보기
          </button>
        </div>
      )}
      {!analysisId && (
        <div className="text-sm text-amber-600 p-3 bg-amber-50 rounded mb-4">
          ⚠️ 시각적 보고서를 사용할 수 없습니다 (analysis_id 누락). 텍스트로 표시합니다.
        </div>
      )}
      <div className="analysis-result prose max-w-none bg-white p-6 rounded-lg shadow">
        <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
          {content}
        </div>
      </div>
    </div>
  )
}
