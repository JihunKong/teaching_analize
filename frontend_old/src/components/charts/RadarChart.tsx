'use client'

import React, { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData
} from 'chart.js'
import { Radar } from 'react-chartjs-2'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Title,
  Tooltip,
  Legend
)

export interface RadarChartProps {
  data: ChartData<'radar'>
  options?: ChartOptions<'radar'>
  className?: string
  height?: number
  width?: number
  title?: string
  showLegend?: boolean
  responsive?: boolean
  maintainAspectRatio?: boolean
  maxValue?: number
}

const RadarChart: React.FC<RadarChartProps> = ({
  data,
  options = {},
  className = '',
  height = 400,
  width,
  title,
  showLegend = true,
  responsive = true,
  maintainAspectRatio = false,
  maxValue = 100
}) => {
  const chartRef = useRef<ChartJS<'radar'>>(null)

  const defaultOptions: ChartOptions<'radar'> = {
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
            const value = context.parsed.r
            return `${label}: ${typeof value === 'number' ? value.toFixed(1) : value}%`
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        max: maxValue,
        min: 0,
        pointLabels: {
          font: {
            size: 11,
            family: 'Malgun Gothic, sans-serif'
          },
          color: '#374151'
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
          lineWidth: 1
        },
        angleLines: {
          color: 'rgba(0, 0, 0, 0.1)',
          lineWidth: 1
        },
        ticks: {
          display: true,
          stepSize: maxValue / 5,
          font: {
            size: 10,
            family: 'Malgun Gothic, sans-serif'
          },
          callback: function(value) {
            return `${value}%`
          },
          backdropColor: 'transparent'
        }
      }
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6,
        borderWidth: 2
      },
      line: {
        borderWidth: 2,
        tension: 0.1
      }
    }
  }

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    plugins: {
      ...defaultOptions.plugins,
      ...options.plugins
    },
    scales: {
      ...defaultOptions.scales,
      ...options.scales
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
      <Radar
        ref={chartRef}
        data={data}
        options={mergedOptions}
        height={height}
        width={width}
      />
    </div>
  )
}

export default RadarChart