'use client'

import React, { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData
} from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import { PIE_CHART_CONFIG } from '../../config/chartConfig'

ChartJS.register(
  ArcElement,
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
  subtitle?: string
  showLegend?: boolean
  responsive?: boolean
  maintainAspectRatio?: boolean
}

const DoughnutChart: React.FC<DoughnutChartProps> = ({
  data,
  options = {},
  className = '',
  height = 300,
  width,
  title,
  subtitle,
  showLegend = true,
  responsive = true,
  maintainAspectRatio = true
}) => {
  const chartRef = useRef<ChartJS<'doughnut'>>(null)

  const mergedOptions: ChartOptions<'doughnut'> = {
    ...PIE_CHART_CONFIG,
    responsive,
    maintainAspectRatio,
    ...options,
    plugins: {
      ...PIE_CHART_CONFIG.plugins,
      ...options.plugins,
      legend: {
        ...PIE_CHART_CONFIG.plugins?.legend,
        ...(options.plugins?.legend || {}),
        display: showLegend,
      },
      title: {
        display: false,
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
        <Doughnut
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

export default DoughnutChart
