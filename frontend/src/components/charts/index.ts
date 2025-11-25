// Chart Components Export
export { default as BarChart } from './BarChart'
export { default as PieChart } from './PieChart'
export { default as RadarChart } from './RadarChart'
export { default as LineChart } from './LineChart'
export { default as DoughnutChart } from './DoughnutChart'

// Chart configuration helpers
export * from './BarChart'
export * from './PieChart'
export * from './RadarChart'
export * from './LineChart'
export * from './DoughnutChart'

// Framework-specific chart utilities
export const chartColors = {
  cbil: '#3b82f6',
  qta: '#8b5cf6',
  sei: '#10b981',
  loa: '#f59e0b',
  cea: '#ef4444',
  cma: '#06b6d4',
  asa: '#84cc16',
  dia: '#ec4899',
  tia: '#6366f1',
  cta: '#7c3aed',
  cra: '#059669',
  ita: '#dc2626',
  rwc: '#0891b2'
}

export const chartColorPalettes = {
  primary: [
    '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', 
    '#ef4444', '#06b6d4', '#84cc16', '#ec4899',
    '#6366f1', '#7c3aed', '#059669', '#dc2626', '#0891b2'
  ],
  pastel: [
    '#93c5fd', '#c4b5fd', '#6ee7b7', '#fcd34d',
    '#fca5a5', '#67e8f9', '#bef264', '#f9a8d4',
    '#a5b4fc', '#c4b5fd', '#6ee7b7', '#fca5a5', '#67e8f9'
  ],
  gradient: [
    'rgba(59, 130, 246, 0.8)', 'rgba(139, 92, 246, 0.8)', 'rgba(16, 185, 129, 0.8)',
    'rgba(245, 158, 11, 0.8)', 'rgba(239, 68, 68, 0.8)', 'rgba(6, 182, 212, 0.8)',
    'rgba(132, 204, 22, 0.8)', 'rgba(236, 72, 153, 0.8)', 'rgba(99, 102, 241, 0.8)',
    'rgba(124, 58, 237, 0.8)', 'rgba(5, 150, 105, 0.8)', 'rgba(220, 38, 38, 0.8)',
    'rgba(8, 145, 178, 0.8)'
  ]
}

export const getFrameworkColor = (frameworkId: string): string => {
  return chartColors[frameworkId as keyof typeof chartColors] || '#6b7280'
}

export const generateChartColors = (count: number, palette: 'primary' | 'pastel' | 'gradient' = 'primary'): string[] => {
  const colors = chartColorPalettes[palette]
  const result: string[] = []
  
  for (let i = 0; i < count; i++) {
    result.push(colors[i % colors.length])
  }
  
  return result
}