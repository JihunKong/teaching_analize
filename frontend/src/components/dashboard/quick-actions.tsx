'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { UploadIcon, LinkIcon, BarChart3Icon } from 'lucide-react'

export function QuickActions() {
  return (
    <div className="space-y-3">
      <Link href="/transcription">
        <Button className="w-full justify-start" variant="outline">
          <UploadIcon className="h-4 w-4 mr-2" />
          파일 전사
        </Button>
      </Link>
      
      <Link href="/transcription">
        <Button className="w-full justify-start" variant="outline">
          <LinkIcon className="h-4 w-4 mr-2" />
          YouTube 전사
        </Button>
      </Link>
      
      <Link href="/analysis">
        <Button className="w-full justify-start" variant="outline">
          <BarChart3Icon className="h-4 w-4 mr-2" />
          텍스트 분석
        </Button>
      </Link>
    </div>
  )
}