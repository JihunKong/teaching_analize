'use client'

import React from 'react'
import { BarChart, DoughnutChart } from '../charts'
import { ChartData } from 'chart.js'

interface LanguageMetricsProps {
  transcript: string
  characterCount: number
  wordCount: number
  videoDuration?: number // in seconds
}

const LanguageMetrics: React.FC<LanguageMetricsProps> = ({
  transcript,
  characterCount,
  wordCount,
  videoDuration
}) => {
  // Calculate language metrics
  const sentences = transcript.split(/[.!?]+/).filter(s => s.trim().length > 0)
  const sentenceCount = sentences.length
  const avgWordsPerSentence = sentenceCount > 0 ? (wordCount / sentenceCount).toFixed(1) : '0'
  const avgCharsPerWord = wordCount > 0 ? (characterCount / wordCount).toFixed(1) : '0'
  
  // Calculate words per minute if duration is available
  const wordsPerMinute = videoDuration ? ((wordCount / videoDuration) * 60).toFixed(0) : null
  
  // Count questions vs statements
  const questionSentences = transcript.split(/\?+/).length - 1
  const statementSentences = sentenceCount - questionSentences
  
  // Count Korean vs English characters (rough estimation)
  const koreanChars = (transcript.match(/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/g) || []).length
  const englishChars = (transcript.match(/[a-zA-Z]/g) || []).length
  const otherChars = characterCount - koreanChars - englishChars
  
  // Create chart data for complexity metrics
  const complexityData: ChartData<'bar'> = {
    labels: ['평균 문장 길이', '평균 단어 길이', '문장 수', '질문 비율(%)'],
    datasets: [{
      label: '언어 복잡도',
      data: [
        parseFloat(avgWordsPerSentence),
        parseFloat(avgCharsPerWord),
        sentenceCount,
        sentenceCount > 0 ? parseFloat(((questionSentences / sentenceCount) * 100).toFixed(1)) : 0
      ],
      backgroundColor: [
        '#3b82f6',
        '#10b981', 
        '#f59e0b',
        '#ef4444'
      ],
      borderColor: [
        '#1d4ed8',
        '#047857',
        '#d97706', 
        '#dc2626'
      ],
      borderWidth: 1
    }]
  }

  // Create chart data for language composition
  const languageCompositionData: ChartData<'doughnut'> = {
    labels: ['한국어', '영어', '기타'],
    datasets: [{
      data: [koreanChars, englishChars, otherChars],
      backgroundColor: [
        '#3b82f6',
        '#10b981',
        '#f59e0b'
      ],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  }

  const metricsStats = [
    { label: '총 단어 수', value: wordCount.toLocaleString(), icon: '📝' },
    { label: '총 문자 수', value: characterCount.toLocaleString(), icon: '🔤' },
    { label: '문장 수', value: sentenceCount.toLocaleString(), icon: '📄' },
    { label: '질문 수', value: questionSentences.toLocaleString(), icon: '❓' },
    ...(wordsPerMinute ? [{ label: '분당 단어 수', value: wordsPerMinute, icon: '⏱️' }] : [])
  ]

  return (
    <div className="language-metrics">
      <h3 style={{ marginBottom: '25px', color: '#2C3E50', fontSize: '20px' }}>
        📊 언어 분석 지표
      </h3>
      
      {/* Metrics Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '15px', 
        marginBottom: '30px' 
      }}>
        {metricsStats.map((stat, index) => (
          <div key={index} style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '20px',
            borderRadius: '12px',
            textAlign: 'center',
            boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)'
          }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>{stat.icon}</div>
            <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '5px' }}>
              {stat.value}
            </div>
            <div style={{ fontSize: '14px', opacity: 0.9 }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
        gap: '30px' 
      }}>
        <div style={{ 
          background: 'white', 
          padding: '25px', 
          borderRadius: '15px', 
          boxShadow: '0 5px 15px rgba(0,0,0,0.08)' 
        }}>
          <BarChart
            data={complexityData}
            title="언어 복잡도 분석"
            height={300}
            options={{
              plugins: {
                legend: { display: false }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    callback: function(value) {
                      return value // Remove % for complexity metrics
                    }
                  }
                }
              }
            }}
          />
        </div>

        <div style={{ 
          background: 'white', 
          padding: '25px', 
          borderRadius: '15px', 
          boxShadow: '0 5px 15px rgba(0,0,0,0.08)' 
        }}>
          <DoughnutChart
            data={languageCompositionData}
            title="언어 구성 비율"
            height={300}
            options={{
              plugins: {
                legend: {
                  position: 'bottom' as const
                },
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      const label = context.label || ''
                      const value = context.parsed
                      const total = context.dataset.data.reduce((a: any, b: any) => a + b, 0)
                      const percentage = ((value / total) * 100).toFixed(1)
                      return `${label}: ${value.toLocaleString()}자 (${percentage}%)`
                    }
                  }
                }
              }
            }}
          />
        </div>
      </div>

      {/* Detailed Analysis */}
      <div style={{ 
        marginTop: '30px', 
        background: '#f8f9fa', 
        padding: '20px', 
        borderRadius: '12px',
        border: '1px solid #e9ecef'
      }}>
        <h4 style={{ marginBottom: '15px', color: '#2C3E50' }}>📋 상세 분석</h4>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '15px',
          fontSize: '14px',
          lineHeight: '1.6'
        }}>
          <div>
            <strong>문장 구조:</strong><br/>
            • 평균 문장당 단어 수: {avgWordsPerSentence}개<br/>
            • 평균 단어당 문자 수: {avgCharsPerWord}자<br/>
            • 질문 비율: {sentenceCount > 0 ? ((questionSentences / sentenceCount) * 100).toFixed(1) : '0'}%
          </div>
          <div>
            <strong>언어 특성:</strong><br/>
            • 한국어 문자: {koreanChars.toLocaleString()}자 ({characterCount > 0 ? ((koreanChars / characterCount) * 100).toFixed(1) : '0'}%)<br/>
            • 영어 문자: {englishChars.toLocaleString()}자 ({characterCount > 0 ? ((englishChars / characterCount) * 100).toFixed(1) : '0'}%)<br/>
            {wordsPerMinute && <span>• 발화 속도: {wordsPerMinute} 단어/분</span>}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LanguageMetrics