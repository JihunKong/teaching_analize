'use client'

import React, { useMemo } from 'react'
import { BarChart, DoughnutChart } from '../charts'
import { ChartData } from 'chart.js'

interface WordFrequencyProps {
  transcript: string
  maxWords?: number
}

const WordFrequency: React.FC<WordFrequencyProps> = ({
  transcript,
  maxWords = 20
}) => {
  const wordAnalysis = useMemo(() => {
    if (!transcript || transcript.trim().length === 0) {
      return {
        topWords: [],
        educationalWords: [],
        questionWords: []
      }
    }

    // Clean and tokenize text
    const cleanText = transcript
      .toLowerCase()
      .replace(/[^\w\s가-힣]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
    
    const words = cleanText.split(' ').filter(word => word.length > 1)
    
    // Korean stop words (common words to filter out)
    const stopWords = new Set([
      '그', '이', '저', '것', '수', '때', '할', '하', '는', '다', '에', '의', '가', '을', '를', '이', '그리고', 
      '하지만', '그런데', '그래서', '또', '그냥', '좀', '잠깐', '음', '어', '아', '네', '예', '그렇게',
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'
    ])
    
    // Count word frequencies
    const wordCount = new Map<string, number>()
    words.forEach(word => {
      if (!stopWords.has(word) && word.length > 1) {
        wordCount.set(word, (wordCount.get(word) || 0) + 1)
      }
    })
    
    // Sort by frequency
    const sortedWords = Array.from(wordCount.entries())
      .sort(([,a], [,b]) => b - a)
      .slice(0, maxWords)
    
    // Categorize educational words
    const educationalKeywords = new Set([
      '학습', '교육', '수업', '학생', '선생님', '교사', '공부', '연구', '분석', '이해', '설명', '질문', '답변',
      '개념', '이론', '실습', '과제', '평가', '토론', '발표', '참여', '활동', '경험', '지식', '정보',
      'learning', 'education', 'student', 'teacher', 'study', 'research', 'analysis', 'concept', 'theory'
    ])
    
    const questionKeywords = new Set([
      '무엇', '어떻게', '왜', '언제', '어디서', '누구', '어떤', '몇', '얼마나',
      'what', 'how', 'why', 'when', 'where', 'who', 'which', 'how many', 'how much'
    ])
    
    const educationalWords = sortedWords.filter(([word]) => 
      educationalKeywords.has(word) || Array.from(educationalKeywords).some(keyword => word.includes(keyword))
    )
    
    const questionWords = sortedWords.filter(([word]) => 
      questionKeywords.has(word) || Array.from(questionKeywords).some(keyword => word.includes(keyword))
    )
    
    return {
      topWords: sortedWords,
      educationalWords: educationalWords.slice(0, 10),
      questionWords: questionWords.slice(0, 10)
    }
  }, [transcript, maxWords])

  // Create chart data for top words
  const topWordsData: ChartData<'bar'> = {
    labels: wordAnalysis.topWords.slice(0, 15).map(([word]) => word),
    datasets: [{
      label: '출현 빈도',
      data: wordAnalysis.topWords.slice(0, 15).map(([, count]) => count),
      backgroundColor: '#3b82f6',
      borderColor: '#1d4ed8',
      borderWidth: 1
    }]
  }

  // Create chart data for word categories
  const totalWords = wordAnalysis.topWords.reduce((sum, [, count]) => sum + count, 0)
  const educationalCount = wordAnalysis.educationalWords.reduce((sum, [, count]) => sum + count, 0)
  const questionCount = wordAnalysis.questionWords.reduce((sum, [, count]) => sum + count, 0)
  const otherCount = totalWords - educationalCount - questionCount

  const categoriesData: ChartData<'doughnut'> = {
    labels: ['교육 관련', '질문 관련', '기타 단어'],
    datasets: [{
      data: [educationalCount, questionCount, otherCount],
      backgroundColor: ['#10b981', '#f59e0b', '#6b7280'],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  }

  if (!transcript || transcript.trim().length === 0) {
    return (
      <div className="word-frequency">
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>📝</div>
          <p>전사된 텍스트가 없습니다.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="word-frequency">
      <h3 style={{ marginBottom: '25px', color: '#2C3E50', fontSize: '20px' }}>
        🔤 단어 빈도 분석
      </h3>

      {/* Summary Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '15px', 
        marginBottom: '30px' 
      }}>
        <div style={{
          background: 'linear-gradient(135deg, #10b981 0%, #047857 100%)',
          color: 'white',
          padding: '20px',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>📚</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '5px' }}>
            {educationalCount}
          </div>
          <div style={{ fontSize: '14px', opacity: 0.9 }}>교육 관련 단어</div>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
          color: 'white',
          padding: '20px',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>❓</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '5px' }}>
            {questionCount}
          </div>
          <div style={{ fontSize: '14px', opacity: 0.9 }}>질문 관련 단어</div>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
          color: 'white',
          padding: '20px',
          borderRadius: '12px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>📈</div>
          <div style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '5px' }}>
            {wordAnalysis.topWords.length}
          </div>
          <div style={{ fontSize: '14px', opacity: 0.9 }}>고유 단어 수</div>
        </div>
      </div>

      {/* Charts */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
        gap: '30px',
        marginBottom: '30px'
      }}>
        <div style={{ 
          background: 'white', 
          padding: '25px', 
          borderRadius: '15px', 
          boxShadow: '0 5px 15px rgba(0,0,0,0.08)' 
        }}>
          <BarChart
            data={topWordsData}
            title="빈도별 상위 단어 (15개)"
            height={350}
            options={{
              indexAxis: 'y' as const,
              plugins: {
                legend: { display: false },
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return `출현 횟수: ${context.parsed.x}회`
                    }
                  }
                }
              },
              scales: {
                x: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1
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
            data={categoriesData}
            title="단어 카테고리 분포"
            height={350}
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
                      const percentage = ((value / totalWords) * 100).toFixed(1)
                      return `${label}: ${value}개 (${percentage}%)`
                    }
                  }
                }
              }
            }}
          />
        </div>
      </div>

      {/* Word Lists */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '20px' 
      }}>
        {wordAnalysis.educationalWords.length > 0 && (
          <div style={{ 
            background: '#f0fdf4', 
            padding: '20px', 
            borderRadius: '12px',
            border: '1px solid #bbf7d0'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#065f46' }}>📚 교육 관련 핵심 단어</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {wordAnalysis.educationalWords.slice(0, 8).map(([word, count], index) => (
                <span key={index} style={{
                  background: '#10b981',
                  color: 'white',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}>
                  {word} ({count})
                </span>
              ))}
            </div>
          </div>
        )}

        {wordAnalysis.questionWords.length > 0 && (
          <div style={{ 
            background: '#fffbeb', 
            padding: '20px', 
            borderRadius: '12px',
            border: '1px solid #fed7aa'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#92400e' }}>❓ 질문 관련 단어</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {wordAnalysis.questionWords.slice(0, 8).map(([word, count], index) => (
                <span key={index} style={{
                  background: '#f59e0b',
                  color: 'white',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}>
                  {word} ({count})
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default WordFrequency