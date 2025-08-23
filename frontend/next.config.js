/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // API configuration for backend integration
  async rewrites() {
    // Use Docker service names for internal communication, fallback to new server IP
    const transcriptionUrl = process.env.TRANSCRIPTION_API_URL || 'http://43.203.128.246:8000';
    const analysisUrl = process.env.ANALYSIS_API_URL || 'http://43.203.128.246:8001';
    const authUrl = process.env.AUTH_API_URL || 'http://43.203.128.246:8002';
    const workflowUrl = process.env.WORKFLOW_API_URL || 'http://43.203.128.246:8003';
    
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
      {
        source: '/api/auth/:path*',
        destination: `${authUrl}/api/auth/:path*`,
      },
      {
        source: '/api/workflow/:path*',
        destination: `${workflowUrl}/api/workflow/:path*`,
      },
    ];
  },

  // Environment variables for client-side
  env: {
    TRANSCRIPTION_API_URL: process.env.TRANSCRIPTION_API_URL || 'http://43.203.128.246:8000',
    ANALYSIS_API_URL: process.env.ANALYSIS_API_URL || 'http://43.203.128.246:8001',
    AUTH_API_URL: process.env.AUTH_API_URL || 'http://43.203.128.246:8002',
    WORKFLOW_API_URL: process.env.WORKFLOW_API_URL || 'http://43.203.128.246:8003',
  },

  // Image optimization
  images: {
    domains: ['localhost', '3.38.107.23', '43.203.128.246', 'youtube.com', 'img.youtube.com'],
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