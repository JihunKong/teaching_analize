'use client'

import React, { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

export interface BarChartProps {
  data: ChartData<'bar'>
  options?: ChartOptions<'bar'>
  className?: string
  height?: number
  width?: number
  title?: string
  showLegend?: boolean
  responsive?: boolean
  maintainAspectRatio?: boolean
}

const BarChart: React.FC<BarChartProps> = ({
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
  const chartRef = useRef<ChartJS<'bar'>>(null)

  const defaultOptions: ChartOptions<'bar'> = {
    responsive,
    maintainAspectRatio,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        display: showLegend,
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
            family: 'Malgun Gothic, sans-serif'
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
            const label = context.dataset.label || ''
            const value = context.parsed.y
            return `${label}: ${typeof value === 'number' ? value.toFixed(1) : value}%`
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          font: {
            family: 'Malgun Gothic, sans-serif'
          }
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          font: {
            family: 'Malgun Gothic, sans-serif'
          },
          callback: function(value) {
            return `${value}%`
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
      // Add any additional chart initialization logic here
      chart.update()
    }
  }, [data])

  return (
    <div className={`chart-container ${className}`}>
      <Bar
        ref={chartRef}
        data={data}
        options={mergedOptions}
        height={height}
        width={width}
      />
    </div>
  )
}

export default BarChart