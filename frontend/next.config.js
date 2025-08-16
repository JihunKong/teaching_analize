/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // API configuration for backend integration
  async rewrites() {
    const transcriptionUrl = process.env.TRANSCRIPTION_API_URL || 'http://transcription:8000';
    const analysisUrl = process.env.ANALYSIS_API_URL || 'http://analysis:8001';
    
    return [
      {
        source: '/api/transcribe/:path*',
        destination: `${transcriptionUrl}/api/transcribe/:path*`,
      },
      {
        source: '/api/analyze/:path*', 
        destination: `${analysisUrl}/api/analyze/:path*`,
      },
      {
        source: '/api/analysis/:path*',
        destination: `${analysisUrl}/api/analysis/:path*`,
      },
      {
        source: '/api/statistics/:path*',
        destination: `${analysisUrl}/api/statistics/:path*`,
      },
    ];
  },

  // Environment variables for client-side
  env: {
    TRANSCRIPTION_API_URL: process.env.TRANSCRIPTION_API_URL || 'http://localhost:8000',
    ANALYSIS_API_URL: process.env.ANALYSIS_API_URL || 'http://localhost:8001',
  },

  // Image optimization
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
  },

  // Compression
  compress: true,

  // Security headers
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },

  // Experimental features
  experimental: {
    serverComponentsExternalPackages: ['@radix-ui'],
  },
};

module.exports = nextConfig;