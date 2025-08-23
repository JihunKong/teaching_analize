/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    API_BASE_URL: process.env.API_BASE_URL || '',
    TRANSCRIPTION_API_URL: process.env.TRANSCRIPTION_API_URL || '/api/transcribe',
    ANALYSIS_API_URL: process.env.ANALYSIS_API_URL || '/api/analyze',
    AUTH_API_URL: process.env.AUTH_API_URL || '/api/auth',
    REPORTING_API_URL: process.env.REPORTING_API_URL || '/api/reports'
  }
}

module.exports = nextConfig