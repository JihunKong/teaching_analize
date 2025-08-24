'use client'

import React, { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions,
  ChartData
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export interface LineChartProps {
  data: ChartData<'line'>
  options?: ChartOptions<'line'>
  className?: string
  height?: number
  width?: number
  title?: string
  showLegend?: boolean
  responsive?: boolean
  maintainAspectRatio?: boolean
  showArea?: boolean
  smooth?: boolean
}

const LineChart: React.FC<LineChartProps> = ({
  data,
  options = {},
  className = '',
  height = 300,
  width,
  title,
  showLegend = true,
  responsive = true,
  maintainAspectRatio = false,
  showArea = false,
  smooth = true
}) => {
  const chartRef = useRef<ChartJS<'line'>>(null)

  const defaultOptions: ChartOptions<'line'> = {
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
      },
      filler: {
        propagate: false
      }
    },
    scales: {
      x: {
        grid: {
          display: true,
          color: 'rgba(0, 0, 0, 0.05)'
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
    },
    elements: {
      point: {
        radius: 4,
        hoverRadius: 6,
        borderWidth: 2,
        hoverBorderWidth: 3
      },
      line: {
        borderWidth: 3,
        tension: smooth ? 0.3 : 0,
        fill: showArea
      }
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart'
    },
    hover: {
      // animationDuration: 300 // Chart.js v4 property difference
    }
  }

  // Process data to add area fill if requested
  const processedData = showArea ? {
    ...data,
    datasets: data.datasets.map((dataset, index) => ({
      ...dataset,
      fill: index === 0 ? 'origin' : `-${index}`,
      backgroundColor: Array.isArray(dataset.backgroundColor) 
        ? dataset.backgroundColor 
        : typeof dataset.backgroundColor === 'string'
        ? dataset.backgroundColor + '20' // Add transparency
        : 'rgba(75, 192, 192, 0.2)'
    }))
  } : data

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
      <Line
        ref={chartRef}
        data={processedData}
        options={mergedOptions}
        height={height}
        width={width}
      />
    </div>
  )
}

export default LineChart