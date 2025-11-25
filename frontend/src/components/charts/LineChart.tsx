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
import { LINE_CHART_CONFIG } from '../../config/chartConfig'

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
  subtitle?: string
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
  subtitle,
  showLegend = true,
  responsive = true,
  maintainAspectRatio = false,
  showArea = false,
  smooth = true
}) => {
  const chartRef = useRef<ChartJS<'line'>>(null)

  const processedData = showArea ? {
    ...data,
    datasets: data.datasets.map((dataset, index) => ({
      ...dataset,
      fill: index === 0 ? 'origin' : `-${index}`,
      backgroundColor: Array.isArray(dataset.backgroundColor) 
        ? dataset.backgroundColor 
        : typeof dataset.backgroundColor === 'string'
        ? dataset.backgroundColor + '20'
        : 'rgba(75, 192, 192, 0.2)'
    }))
  } : data

  const mergedOptions: ChartOptions<'line'> = {
    ...LINE_CHART_CONFIG,
    responsive,
    maintainAspectRatio,
    ...options,
    plugins: {
      ...LINE_CHART_CONFIG.plugins,
      ...options.plugins,
      legend: {
        ...LINE_CHART_CONFIG.plugins?.legend,
        ...(options.plugins?.legend || {}),
        display: showLegend,
      },
      title: {
        display: false,
      },
    },
    elements: {
      ...LINE_CHART_CONFIG.elements,
      line: {
        ...LINE_CHART_CONFIG.elements?.line,
        tension: smooth ? 0.3 : 0,
      }
    }
  }

  useEffect(() => {
    const chart = chartRef.current
    if (chart) {
      chart.update()
    }
  }, [data])

  return (
    <div className={`chart-brutalist-container ${className}`}>
      {title && (
        <div className="chart-brutalist-title">
          {title}
        </div>
      )}
      {subtitle && (
        <div className="chart-brutalist-subtitle">
          {subtitle}
        </div>
      )}
      <div className="chart-brutalist-canvas">
        <Line
          ref={chartRef}
          data={processedData}
          options={mergedOptions}
          height={height}
          width={width}
        />
      </div>
    </div>
  )
}

export default LineChart
