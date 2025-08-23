/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://43.203.128.246',
    TRANSCRIPTION_API_URL: process.env.TRANSCRIPTION_API_URL || 'http://43.203.128.246/api/transcribe',
    ANALYSIS_API_URL: process.env.ANALYSIS_API_URL || 'http://43.203.128.246/api/analyze',
    AUTH_API_URL: process.env.AUTH_API_URL || 'http://43.203.128.246/api/auth',
    REPORTING_API_URL: process.env.REPORTING_API_URL || 'http://43.203.128.246/api/reports'
  }
}

module.exports = nextConfig