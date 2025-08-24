import Link from 'next/link'
import { FileQuestionIcon, HomeIcon, ArrowLeftIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-lg text-center">
        <CardHeader>
          <div className="mx-auto mb-4">
            <FileQuestionIcon className="h-16 w-16 text-gray-400" />
          </div>
          <CardTitle className="text-2xl text-gray-900">페이지를 찾을 수 없습니다</CardTitle>
          <CardDescription>
            요청하신 페이지가 존재하지 않거나 이동되었습니다.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-2">
            <Button asChild variant="default" className="w-full">
              <Link href="/">
                <HomeIcon className="h-4 w-4 mr-2" />
                홈으로 이동
              </Link>
            </Button>
            <Button asChild variant="outline" className="w-full">
              <Link href="/transcription">
                전사 서비스 이용하기
              </Link>
            </Button>
            <Button 
              onClick={() => window.history.back()} 
              variant="ghost" 
              className="w-full"
            >
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              이전 페이지로
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}