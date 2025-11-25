'use client'

import React, { useState } from 'react'

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

  if (!content) {
    return <div className="text-gray-500">No analysis content available</div>
  }

  return (
    <div className="space-y-6">
      {/* Control Bar */}
      <div className="flex justify-between items-center glass-card p-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-600">
            {viewMode === 'visual' ? '🎨 시각적 보고서' : '📄 텍스트 보고서'}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode(viewMode === 'visual' ? 'text' : 'visual')}
            className="btn btn-secondary text-sm"
          >
            {viewMode === 'visual' ? '텍스트 보기' : '시각화 보기'}
          </button>
          {analysisId && (
            <>
              <button
                onClick={() => window.open(`/api/reports/html/${analysisId}`, '_blank')}
                className="btn btn-primary text-sm"
              >
                새 탭에서 열기
              </button>
              <a
                href={`/api/reports/pdf-enhanced/${analysisId}`}
                download
                className="btn btn-primary text-sm bg-purple-600 hover:bg-purple-700 border-none"
              >
                PDF 다운로드
              </a>
            </>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div className={`transition-all duration-300 ${viewMode === 'visual' ? 'visual-mode' : 'text-mode'}`}>
        {viewMode === 'visual' ? (
          <div className="glass-card overflow-hidden">
            {/* 
                Directly render HTML content. 
                Note: In a real production app, we should sanitize this content. 
                Since this is an internal tool/generated content, we assume it's safe-ish.
                We wrap it in a specific class to isolate styles if needed.
             */}
            <div
              className="report-content-wrapper p-8"
              dangerouslySetInnerHTML={{ __html: content }}
            />
          </div>
        ) : (
          <div className="glass-card p-8">
            <div className="prose max-w-none whitespace-pre-wrap text-gray-800 leading-relaxed">
              {content}
            </div>
          </div>
        )}
      </div>

      <style jsx global>{`
        /* Scoped styles for the report content to ensure it looks good within the app */
        .report-content-wrapper {
          font-family: var(--font-sans);
          color: var(--color-text-primary);
        }
        
        /* Ensure charts are responsive */
        .report-content-wrapper canvas {
          max-width: 100% !important;
          height: auto !important;
        }
      `}</style>
    </div>
  )
}
