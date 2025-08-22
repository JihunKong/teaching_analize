'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { EyeIcon, EyeOffIcon, AlertCircleIcon, LoaderIcon, CheckCircleIcon } from 'lucide-react'
import { isAuthenticated } from '@/lib/auth'

interface RegisterData {
  username: string
  email: string
  password: string
  confirmPassword: string
  fullName?: string
}

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState<RegisterData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/')
    }
  }, [router])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (error) setError(null)
  }

  const validateForm = (): string | null => {
    if (!formData.username.trim()) {
      return '사용자명을 입력해주세요.'
    }
    if (!formData.email.trim()) {
      return '이메일을 입력해주세요.'
    }
    if (!formData.email.includes('@')) {
      return '올바른 이메일 형식을 입력해주세요.'
    }
    if (!formData.password.trim()) {
      return '비밀번호를 입력해주세요.'
    }
    if (formData.password.length < 6) {
      return '비밀번호는 6자 이상이어야 합니다.'
    }
    if (formData.password !== formData.confirmPassword) {
      return '비밀번호가 일치하지 않습니다.'
    }
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      // Validate form
      const validationError = validateForm()
      if (validationError) {
        throw new Error(validationError)
      }

      // For now, simulate registration
      // In a real app, you would call your registration API here
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setSuccess(true)
      
      // Show success message and redirect to login after delay
      setTimeout(() => {
        router.push('/login?message=registration_success')
      }, 2000)

    } catch (error) {
      console.error('Registration error:', error)
      setError(error instanceof Error ? error.message : '회원가입 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <CheckCircleIcon className="mx-auto h-12 w-12 text-green-500 mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-2">회원가입 완료!</h1>
              <p className="text-gray-600 mb-4">
                계정이 성공적으로 생성되었습니다. 잠시 후 로그인 페이지로 이동합니다.
              </p>
              <div className="animate-pulse">
                <LoaderIcon className="mx-auto h-6 w-6 animate-spin text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo and Title */}
        <div className="text-center">
          <div className="mx-auto h-12 w-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mb-4">
            <span className="text-white font-bold text-xl">AI</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">AIBOA</h1>
          <p className="text-gray-600 mt-2">AI 기반 교육 분석 플랫폼</p>
        </div>

        {/* Registration Form */}
        <Card>
          <CardHeader>
            <CardTitle>회원가입</CardTitle>
            <CardDescription>
              새 계정을 만들어 교육 분석 서비스를 시작하세요.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Full Name Field */}
              <div className="space-y-2">
                <Label htmlFor="fullName">이름 (선택사항)</Label>
                <Input
                  id="fullName"
                  name="fullName"
                  type="text"
                  placeholder="홍길동"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  disabled={isLoading}
                  className="w-full"
                />
              </div>

              {/* Username Field */}
              <div className="space-y-2">
                <Label htmlFor="username">사용자명</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                  disabled={isLoading}
                  className="w-full"
                />
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email">이메일</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="your.email@example.com"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  disabled={isLoading}
                  className="w-full"
                />
              </div>

              {/* Password Field */}
              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="6자 이상의 비밀번호"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    disabled={isLoading}
                    className="w-full pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOffIcon className="h-4 w-4" />
                    ) : (
                      <EyeIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm Password Field */}
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">비밀번호 확인</Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    placeholder="비밀번호를 다시 입력하세요"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    required
                    disabled={isLoading}
                    className="w-full pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    disabled={isLoading}
                  >
                    {showConfirmPassword ? (
                      <EyeOffIcon className="h-4 w-4" />
                    ) : (
                      <EyeIcon className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <Alert variant="destructive">
                  <AlertCircleIcon className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Submit Button */}
              <Button 
                type="submit" 
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <LoaderIcon className="h-4 w-4 mr-2 animate-spin" />
                    회원가입 중...
                  </>
                ) : (
                  '회원가입'
                )}
              </Button>

              {/* Login Link */}
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  이미 계정이 있으신가요?{' '}
                  <button
                    type="button"
                    onClick={() => router.push('/login')}
                    className="text-blue-600 hover:underline font-medium"
                    disabled={isLoading}
                  >
                    로그인하기
                  </button>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500">
          <p>© 2024 AIBOA. All rights reserved.</p>
          <p className="mt-1">
            문의: <a href="mailto:admin@aiboa.com" className="text-blue-600 hover:underline">admin@aiboa.com</a>
          </p>
        </div>
      </div>
    </div>
  )
}