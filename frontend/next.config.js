/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    // Use empty string for relative API paths to work with Nginx proxy
    API_BASE_URL: '',
    TRANSCRIPTION_API_URL: '/api/transcribe',
    ANALYSIS_API_URL: '/api/analyze',
    AUTH_API_URL: '/api/auth',
    REPORTING_API_URL: '/api/reports'
  }
}

module.exports = nextConfig