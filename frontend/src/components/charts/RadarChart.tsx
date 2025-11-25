'use client'

import React, { useEffect, useRef } from 'react'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  ChartOptions,
  ChartData
} from 'chart.js'
import { Radar } from 'react-chartjs-2'
import { RADAR_CHART_CONFIG } from '../../config/chartConfig'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
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
  subtitle?: string
  showLegend?: boolean
  responsive?: boolean
  maintainAspectRatio?: boolean
}

const RadarChart: React.FC<RadarChartProps> = ({
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
  const chartRef = useRef<ChartJS<'radar'>>(null)

  const mergedOptions: ChartOptions<'radar'> = {
    ...RADAR_CHART_CONFIG,
    responsive,
    maintainAspectRatio,
    ...options,
    plugins: {
      ...RADAR_CHART_CONFIG.plugins,
      ...options.plugins,
      legend: {
        ...RADAR_CHART_CONFIG.plugins?.legend,
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
        <Radar
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

export default RadarChart
