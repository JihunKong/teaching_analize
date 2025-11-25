'use client'

interface Analysis {
  analysis_id: string
  framework: string
  framework_name: string
  analysis: string
  character_count: number
  word_count: number
  created_at: string
  metadata?: {
    video_url?: string
    video_id?: string
    language?: string
    temperature?: number
  }
}

interface AnalysisSelectionCardProps {
  analysis: Analysis
  selected: boolean
  onToggle: (analysisId: string) => void
  frameworkColor?: string
}

export default function AnalysisSelectionCard({ 
  analysis, 
  selected, 
  onToggle,
  frameworkColor = '#667eea'
}: AnalysisSelectionCardProps) {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    onToggle(analysis.analysis_id)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onToggle(analysis.analysis_id)
    }
  }

  return (
    <div 
      className={`card analysis-card ${selected ? 'selected' : ''}`}
      style={{ 
        cursor: 'pointer',
        border: selected ? `2px solid ${frameworkColor}` : '1px solid #ddd',
        transition: 'all 0.3s ease'
      }}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-pressed={selected}
      aria-label={`${analysis.framework_name} 분석 ${selected ? '선택됨' : '선택 안됨'}`}
    >
      {/* Header with Checkbox and Framework Badge */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        marginBottom: '12px',
        gap: '12px'
      }}>
        <input
          type="checkbox"
          checked={selected}
          onChange={() => {}} // Handled by parent onClick
          style={{ 
            width: '20px', 
            height: '20px',
            accentColor: frameworkColor
          }}
          aria-hidden="true" // Hidden from screen readers as the card itself is interactive
        />
        
        <h4 style={{ margin: 0, flex: 1, color: '#333' }}>
          {analysis.framework_name}
        </h4>
        
        <span style={{ 
          backgroundColor: frameworkColor,
          color: 'white',
          padding: '4px 10px',
          borderRadius: '12px',
          fontSize: '0.8rem',
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {analysis.framework}
        </span>
      </div>
      
      {/* Analysis Statistics */}
      <div className="analysis-stats" style={{ marginBottom: '12px' }}>
        <span>
          📅 {new Date(analysis.created_at).toLocaleDateString('ko-KR')}
        </span>
        <span>
          📝 {analysis.character_count.toLocaleString()}자
        </span>
        <span>
          📊 {analysis.word_count?.toLocaleString() || 'N/A'}단어
        </span>
      </div>
      
      {/* Analysis Preview */}
      <div style={{ 
        backgroundColor: '#f8f9fa',
        border: '1px solid #e9ecef',
        borderRadius: '8px',
        padding: '12px',
        fontSize: '0.9rem',
        lineHeight: '1.5',
        maxHeight: '120px',
        overflow: 'hidden',
        position: 'relative'
      }}>
        {analysis.analysis.length > 200 
          ? `${analysis.analysis.substring(0, 200)}...` 
          : analysis.analysis
        }
        
        {analysis.analysis.length > 200 && (
          <div style={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            background: 'linear-gradient(to right, transparent, #f8f9fa 70%)',
            padding: '0 8px',
            fontSize: '0.8rem',
            color: '#666'
          }}>
            더보기
          </div>
        )}
      </div>
      
      {/* Metadata */}
      {analysis.metadata && (
        <div style={{ 
          marginTop: '10px', 
          fontSize: '0.8rem', 
          color: '#666',
          display: 'flex',
          gap: '15px',
          flexWrap: 'wrap'
        }}>
          {analysis.metadata.video_id && (
            <span>🎬 영상: {analysis.metadata.video_id}</span>
          )}
          {analysis.metadata.temperature !== undefined && (
            <span>🌡️ 온도: {analysis.metadata.temperature}</span>
          )}
          {analysis.metadata.language && (
            <span>🌐 언어: {analysis.metadata.language}</span>
          )}
        </div>
      )}
      
      {/* Selection Indicator */}
      {selected && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          backgroundColor: frameworkColor,
          color: 'white',
          borderRadius: '50%',
          width: '24px',
          height: '24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          ✓
        </div>
      )}
    </div>
  )
}