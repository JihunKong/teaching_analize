'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  UserIcon, 
  LogOutIcon, 
  SettingsIcon,
  ShieldIcon,
  MenuIcon
} from 'lucide-react'
import { getStoredUser, isAuthenticated, logout, User } from '@/lib/auth'

export default function Navbar() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isAuth, setIsAuth] = useState(false)

  useEffect(() => {
    const checkAuth = () => {
      const authenticated = isAuthenticated()
      const userData = getStoredUser()
      setIsAuth(authenticated)
      setUser(userData)
    }

    // Check on mount
    checkAuth()

    // Listen for auth changes
    const handleStorageChange = () => checkAuth()
    window.addEventListener('storage', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [])

  const handleLogout = async () => {
    try {
      await logout()
      setIsAuth(false)
      setUser(null)
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const handleLogin = () => {
    router.push('/login')
  }

  return (
    <nav className="bg-white shadow-sm border-b sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <div 
              className="h-10 w-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center cursor-pointer"
              onClick={() => router.push('/')}
            >
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <div>
              <h1 
                className="text-xl font-bold text-gray-900 cursor-pointer"
                onClick={() => router.push('/')}
              >
                AIBOA
              </h1>
              <p className="text-xs text-gray-500">AI 교육 분석 플랫폼</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            <Button 
              variant="ghost" 
              onClick={() => router.push('/transcription')}
              className="text-gray-600 hover:text-gray-900"
            >
              전사하기
            </Button>
            <Button 
              variant="ghost" 
              onClick={() => router.push('/analysis')}
              className="text-gray-600 hover:text-gray-900"
            >
              분석하기
            </Button>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {isAuth && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                    <Avatar className="h-10 w-10">
                      <AvatarImage 
                        src={user.profile?.avatar_url} 
                        alt={user.username}
                      />
                      <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                        {user.username.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end">
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium">{user.profile?.full_name || user.username}</p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                    {user.role && (
                      <p className="text-xs text-blue-600 font-medium capitalize mt-1">
                        {user.role}
                      </p>
                    )}
                  </div>
                  <DropdownMenuSeparator />
                  
                  <DropdownMenuItem onClick={() => router.push('/profile')}>
                    <UserIcon className="mr-2 h-4 w-4" />
                    내 프로필
                  </DropdownMenuItem>
                  
                  {user.role === 'admin' && (
                    <DropdownMenuItem onClick={() => router.push('/admin')}>
                      <ShieldIcon className="mr-2 h-4 w-4" />
                      관리자 패널
                    </DropdownMenuItem>
                  )}
                  
                  <DropdownMenuItem onClick={() => router.push('/settings')}>
                    <SettingsIcon className="mr-2 h-4 w-4" />
                    설정
                  </DropdownMenuItem>
                  
                  <DropdownMenuSeparator />
                  
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOutIcon className="mr-2 h-4 w-4" />
                    로그아웃
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center space-x-3">
                <Button variant="outline" onClick={handleLogin}>
                  로그인
                </Button>
                <Button onClick={() => router.push('/register')} className="bg-gradient-to-r from-blue-600 to-purple-600">
                  시작하기
                </Button>
              </div>
            )}

            {/* Mobile menu button */}
            <div className="md:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MenuIcon className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => router.push('/transcription')}>
                    전사하기
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => router.push('/analysis')}>
                    분석하기
                  </DropdownMenuItem>
                  {!isAuth && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem onClick={handleLogin}>
                        로그인
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => router.push('/register')}>
                        시작하기
                      </DropdownMenuItem>
                    </>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}