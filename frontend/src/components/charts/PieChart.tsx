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
import { Pie } from 'react-chartjs-2'

ChartJS.register(
  ArcElement,
  Title,
  Tooltip,
  Legend
)

export interface PieChartProps {
  data: ChartData<'pie'>
  options?: ChartOptions<'pie'>
  className?: string
  height?: number
  width?: number
  title?: string
  showLegend?: boolean
  responsive?: boolean
  maintainAspectRatio?: boolean
}

const PieChart: React.FC<PieChartProps> = ({
  data,
  options = {},
  className = '',
  height = 300,
  width,
  title,
  showLegend = true,
  responsive = true,
  maintainAspectRatio = false
}) => {
  const chartRef = useRef<ChartJS<'pie'>>(null)

  const defaultOptions: ChartOptions<'pie'> = {
    responsive,
    maintainAspectRatio,
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

  return (
    <div className={`chart-container ${className}`}>
      <Pie
        ref={chartRef}
        data={data}
        options={mergedOptions}
        height={height}
        width={width}
      />
    </div>
  )
}

export default PieChart