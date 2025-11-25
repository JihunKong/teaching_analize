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
import { BAR_CHART_CONFIG } from '../../config/chartConfig'

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
  subtitle?: string
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
  subtitle,
  showLegend = true,
  responsive = true,
  maintainAspectRatio = false
}) => {
  const chartRef = useRef<ChartJS<'bar'>>(null)

  // Merge brutalist config with custom options
  const mergedOptions: ChartOptions<'bar'> = {
    ...BAR_CHART_CONFIG,
    responsive,
    maintainAspectRatio,
    ...options,
    plugins: {
      ...BAR_CHART_CONFIG.plugins,
      ...options.plugins,
      legend: {
        ...BAR_CHART_CONFIG.plugins?.legend,
        ...(options.plugins?.legend || {}),
        display: showLegend,
      },
      title: {
        display: false, // We handle title externally for brutalist design
      },
    },
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
        <Bar
          ref={chartRef}
          data={data}
          options={mergedOptions}
          height={height}
          width={width}
        />
      </div>
    </div>
  )
}

export default BarChart
