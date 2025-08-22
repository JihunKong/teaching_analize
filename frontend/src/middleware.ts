import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Routes that require authentication
const protectedRoutes = [
  '/admin',
  '/dashboard',
  '/profile'
]

// Routes that should redirect authenticated users away
const authRoutes = [
  '/login'
]

// Public routes that don't require authentication
const publicRoutes = [
  '/',
  '/transcription',
  '/analysis',
  '/health'
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get('aiboa_access_token')?.value || 
                request.headers.get('authorization')?.replace('Bearer ', '')

  // Check if user is authenticated
  const isAuthenticated = !!token && !isTokenExpired(token)

  // Handle protected routes
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }

    // Check admin routes
    if (pathname.startsWith('/admin')) {
      try {
        const userRole = getUserRoleFromToken(token)
        if (userRole !== 'admin') {
          // Redirect non-admin users to home
          return NextResponse.redirect(new URL('/', request.url))
        }
      } catch (error) {
        // Invalid token, redirect to login
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set('redirect', pathname)
        return NextResponse.redirect(loginUrl)
      }
    }
  }

  // Handle auth routes (redirect authenticated users)
  if (authRoutes.some(route => pathname.startsWith(route))) {
    if (isAuthenticated) {
      const redirectUrl = request.nextUrl.searchParams.get('redirect')
      return NextResponse.redirect(new URL(redirectUrl || '/', request.url))
    }
  }

  // Add auth headers to API requests
  if (pathname.startsWith('/api/')) {
    const response = NextResponse.next()
    
    if (isAuthenticated) {
      response.headers.set('authorization', `Bearer ${token}`)
    }
    
    return response
  }

  return NextResponse.next()
}

/**
 * Check if JWT token is expired
 */
function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Date.now() / 1000
    return payload.exp < currentTime
  } catch (error) {
    return true
  }
}

/**
 * Get user role from JWT token
 */
function getUserRoleFromToken(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.role || payload.user_role || null
  } catch (error) {
    return null
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public directory)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}