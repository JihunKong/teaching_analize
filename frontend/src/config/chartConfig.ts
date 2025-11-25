/**
 * TVAS Unified Chart Configuration
 * Monochrome Design System for Chart.js
 * 
 * Use this config for consistent chart styling across frontend and backend reports
 */

// Monochrome Color Palette (from globals.css)
export const COLORS = {
  black: '#000000',
  gray900: '#171717',
  gray800: '#262626',
  gray700: '#404040',
  gray600: '#525252',
  gray500: '#737373',
  gray400: '#A3A3A3',
  gray300: '#D4D4D4',
  gray200: '#E5E5E5',
  gray100: '#F5F5F5',
  white: '#FFFFFF',
} as const

// Chart Color Scales (grayscale gradients for data visualization)
export const CHART_COLORS = {
  // Single data series
  primary: COLORS.black,
  
  // Multiple series (5 shades)
  series: [
    COLORS.black,    // Darkest
    COLORS.gray700,
    COLORS.gray500,
    COLORS.gray400,
    COLORS.gray300,  // Lightest
  ],
  
  // Heatmap (7 shades from white to black)
  heatmap: [
    COLORS.white,
    COLORS.gray100,
    COLORS.gray200,
    COLORS.gray400,
    COLORS.gray600,
    COLORS.gray800,
    COLORS.black,
  ],
  
  // Binary (for yes/no, present/absent)
  binary: {
    active: COLORS.black,
    inactive: COLORS.gray200,
  },
  
  // Status colors (minimal differentiation)
  status: {
    success: COLORS.gray700,
    warning: COLORS.gray500,
    error: COLORS.black,
    info: COLORS.gray300,
  },
} as const

// Default Chart.js Configuration
export const DEFAULT_CHART_OPTIONS = {
  responsive: true,
  maintainAspectRatio: true,
  
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
      labels: {
        font: {
          family: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif",
          size: 12,
          weight: 700,  // Brutalist bold legend
        },
        color: COLORS.black,  // Brutalist pure black text
        padding: 16,
        usePointStyle: true,
        boxWidth: 12,  // Brutalist larger box
        boxHeight: 12,  // Brutalist larger box
      },
    },
    
    tooltip: {
      backgroundColor: COLORS.black,
      titleColor: COLORS.white,
      bodyColor: COLORS.white,
      borderColor: COLORS.black,
      borderWidth: 3,  // Brutalist thick border
      padding: 16,
      cornerRadius: 0,  // Brutalist no radius
      titleFont: {
        family: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif",
        size: 13,
        weight: 900,  // Brutalist ultra-bold
      },
      bodyFont: {
        family: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif",
        size: 12,
        weight: 500,  // Brutalist medium weight
      },
      displayColors: true,
      boxWidth: 12,
      boxHeight: 12,
      boxPadding: 8,
    },
  },
  
  scales: {
    x: {
      grid: {
        display: true,
        color: COLORS.gray300,  // Brutalist darker grid
        lineWidth: 2,  // Brutalist thicker grid
        drawTicks: true,
      },
      ticks: {
        font: {
          family: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif",
          size: 11,
          weight: 600,  // Brutalist bold ticks
        },
        color: COLORS.gray900,  // Brutalist darker text
      },
      border: {
        color: COLORS.black,  // Brutalist black border
        width: 3,  // Brutalist thick border
      },
    },
    y: {
      grid: {
        display: true,
        color: COLORS.gray300,  // Brutalist darker grid
        lineWidth: 2,  // Brutalist thicker grid
        drawTicks: true,
      },
      ticks: {
        font: {
          family: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif",
          size: 11,
          weight: 600,  // Brutalist bold ticks
        },
        color: COLORS.gray900,  // Brutalist darker text
      },
      border: {
        color: COLORS.black,  // Brutalist black border
        width: 3,  // Brutalist thick border
      },
    },
  },
} as const

// Specific Chart Type Configurations

export const BAR_CHART_CONFIG = {
  ...DEFAULT_CHART_OPTIONS,
  plugins: {
    ...DEFAULT_CHART_OPTIONS.plugins,
  },
} as const

export const LINE_CHART_CONFIG = {
  ...DEFAULT_CHART_OPTIONS,
  elements: {
    line: {
      tension: 0,  // Brutalist sharp angles (no curve)
      borderWidth: 3,  // Brutalist thick line
    },
    point: {
      radius: 5,  // Brutalist larger point
      hoverRadius: 7,  // Brutalist larger hover
      borderWidth: 3,  // Brutalist thick border
      backgroundColor: COLORS.white,
      borderColor: COLORS.black,  // Brutalist black border
    },
  },
} as const

export const RADAR_CHART_CONFIG = {
  ...DEFAULT_CHART_OPTIONS,
  scales: {
    r: {
      angleLines: {
        color: COLORS.gray400,  // Brutalist darker angle lines
        lineWidth: 2,  // Brutalist thicker lines
      },
      grid: {
        color: COLORS.gray300,  // Brutalist darker grid
        lineWidth: 2,  // Brutalist thicker grid
      },
      pointLabels: {
        font: {
          family: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif",
          size: 12,
          weight: 700,  // Brutalist bold labels
        },
        color: COLORS.black,  // Brutalist pure black
      },
      ticks: {
        font: {
          family: "'Pretendard', -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', sans-serif",
          size: 10,
          weight: 600,  // Brutalist bold ticks
        },
        color: COLORS.gray700,  // Brutalist darker ticks
        backdropColor: 'transparent',
      },
    },
  },
  elements: {
    line: {
      borderWidth: 3,  // Brutalist thick radar lines
    },
    point: {
      radius: 4,
      hoverRadius: 6,
      borderWidth: 2,
    },
  },
} as const

export const PIE_CHART_CONFIG = {
  ...DEFAULT_CHART_OPTIONS,
  plugins: {
    ...DEFAULT_CHART_OPTIONS.plugins,
    legend: {
      ...DEFAULT_CHART_OPTIONS.plugins.legend,
      position: 'right' as const,
    },
  },
  elements: {
    arc: {
      borderWidth: 3,  // Brutalist thick segment borders
      borderColor: COLORS.white,  // Brutalist white separators
    },
  },
} as const

// Helper function to create dataset with monochrome colors
export function createDataset(
  label: string,
  data: number[],
  colorIndex: number = 0,
  options: Partial<any> = {}
) {
  const backgroundColor = CHART_COLORS.series[colorIndex % CHART_COLORS.series.length]
  const borderColor = COLORS.black
  
  return {
    label,
    data,
    backgroundColor,
    borderColor,
    borderWidth: 3,  // Brutalist thick border
    ...options,
  }
}

// Helper function for heatmap data
export function getHeatmapColor(value: number, min: number, max: number): string {
  const normalized = (value - min) / (max - min)
  const index = Math.floor(normalized * (CHART_COLORS.heatmap.length - 1))
  return CHART_COLORS.heatmap[Math.max(0, Math.min(index, CHART_COLORS.heatmap.length - 1))]
}

// Export for both TypeScript and JavaScript environments
export default {
  COLORS,
  CHART_COLORS,
  DEFAULT_CHART_OPTIONS,
  BAR_CHART_CONFIG,
  LINE_CHART_CONFIG,
  RADAR_CHART_CONFIG,
  PIE_CHART_CONFIG,
  createDataset,
  getHeatmapColor,
}
