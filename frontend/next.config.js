/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable static export in development to enable rewrites
  // Only use static export in production
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
  },
  // In development, proxy API requests to backend via Nginx
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost/api/:path*'
        }
      ]
    }
    return []
  }
}

module.exports = nextConfig