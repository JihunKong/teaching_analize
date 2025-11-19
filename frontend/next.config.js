/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  env: {
    API_BASE_URL: '',
    TRANSCRIPTION_API_URL: '/api/transcribe',
    ANALYSIS_API_URL: '/api/analyze',
    AUTH_API_URL: '/api/auth',
    REPORTING_API_URL: '/api/reports'
  },
  async rewrites() {
    // Enable API proxy in both development and production
    return [
      {
        source: '/api/:path*',
        destination: 'http://gateway:8000/api/:path*'
      }
    ]
  }
}

module.exports = nextConfig
