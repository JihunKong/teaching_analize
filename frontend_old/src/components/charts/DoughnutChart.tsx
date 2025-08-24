'use client'

import React, { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData
} from 'chart.js'
import { Doughnut } from 'react-chartjs-2'

ChartJS.register(
  ArcElement,
  Title,
  Tooltip,
  Legend
)

export interface DoughnutChartProps {
  data: ChartData<'doughnut'>
  options?: ChartOptions<'doughnut'>
  className?: string
  height?: number
  width?: number
  title?: string
  showLegend?: boolean
  responsive?: boolean
  maintainAspectRatio?: boolean
  centerText?: string
  centerSubtext?: string
}

const DoughnutChart: React.FC<DoughnutChartProps> = ({
  data,
  options = {},
  className = '',
  height = 300,
  width,
  title,
  showLegend = true,
  responsive = true,
  maintainAspectRatio = false,
  centerText,
  centerSubtext
}) => {
  const chartRef = useRef<ChartJS<'doughnut'>>(null)

  const defaultOptions: ChartOptions<'doughnut'> = {
    responsive,
    maintainAspectRatio,
    cutout: '60%', // Creates the doughnut hole
    plugins: {
      legend: {
        display: showLegend,
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
            family: 'Malgun Gothic, sans-serif'
          },
          generateLabels: function(chart) {
            const data = chart.data
            if (data.labels && data.datasets.length) {
              return data.labels.map((label, i) => {
                const meta = chart.getDatasetMeta(0)
                const dataset = data.datasets[0]
                const value = dataset.data[i] as number
                const total = (dataset.data as number[]).reduce((acc, val) => acc + val, 0)
                const percentage = ((value / total) * 100).toFixed(1)
                
                return {
                  text: `${label}: ${percentage}%`,
                  fillStyle: Array.isArray(dataset.backgroundColor) 
                    ? dataset.backgroundColor[i] 
                    : dataset.backgroundColor,
                  hidden: isNaN(value) || (meta.data[i] as any)?.hidden,
                  index: i,
                  pointStyle: 'circle'
                }
              })
            }
            return []
          }
        }
      },
      title: {
        display: !!title,
        text: title,
        font: {
          size: 16,
          weight: 'bold',
          family: 'Malgun Gothic, sans-serif'
        },
        padding: {
          top: 10,
          bottom: 30
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 6,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const label = context.label || ''
            const value = context.parsed as number
            const total = (context.dataset.data as number[]).reduce((acc, val) => acc + val, 0)
            const percentage = ((value / total) * 100).toFixed(1)
            return `${label}: ${percentage}% (${value.toFixed(1)})`
          }
        }
      }
    },
    elements: {
      arc: {
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverBorderWidth: 3
      }
    },
    animation: {
      animateRotate: true,
      animateScale: false,
      duration: 1000
    }
  }

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    plugins: {
      ...defaultOptions.plugins,
      ...options.plugins
    }
  }

  useEffect(() => {
    const chart = chartRef.current
    if (chart) {
      chart.update()
    }
  }, [data])

  // Custom center text plugin
  useEffect(() => {
    if (centerText && chartRef.current) {
      const chart = chartRef.current
      const ctx = chart.ctx
      
      // Register custom plugin for center text
      const centerTextPlugin = {
        id: 'centerText',
        beforeDraw: (chart: any) => {
          const width = chart.width
          const height = chart.height
          const ctx = chart.ctx
          
          ctx.restore()
          const fontSize = (height / 114).toFixed(2)
          ctx.font = `bold ${fontSize}em Malgun Gothic, sans-serif`
          ctx.textBaseline = 'middle'
          ctx.fillStyle = '#374151'
          
          const textX = Math.round((width - ctx.measureText(centerText).width) / 2)
          const textY = height / 2 - (centerSubtext ? 10 : 0)
          
          ctx.fillText(centerText, textX, textY)
          
          if (centerSubtext) {
            ctx.font = `${(Number(fontSize) * 0.6)}em Malgun Gothic, sans-serif`
            ctx.fillStyle = '#6B7280'
            const subtextX = Math.round((width - ctx.measureText(centerSubtext).width) / 2)
            const subtextY = height / 2 + 15
            ctx.fillText(centerSubtext, subtextX, subtextY)
          }
          
          ctx.save()
        }
      }
      
      // This would need to be registered properly with Chart.js
      // For now, we'll use the onLoad callback
    }
  }, [centerText, centerSubtext])

  return (
    <div className={`chart-container relative ${className}`}>
      <Doughnut
        ref={chartRef}
        data={data}
        options={mergedOptions}
        height={height}
        width={width}
      />
      {centerText && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <div className="text-lg font-bold text-gray-700">{centerText}</div>
          {centerSubtext && (
            <div className="text-sm text-gray-500">{centerSubtext}</div>
          )}
        </div>
      )}
    </div>
  )
}

export default DoughnutChart