'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { TranscriptionResult } from '@/components/transcription/transcription-result'
import { Layout } from '@/components/layout/layout'
import { 
  useUploadFile, 
  useTranscribeYouTube, 
  useJobStatusPolling, 
  useTranscriptionHealth 
} from '@/hooks/useTranscription'
import { TranscriptionJob } from '@/lib/api'
import { 
  UploadIcon, 
  YoutubeIcon, 
  FileAudioIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  ExternalLinkIcon
} from 'lucide-react'

export default function TranscriptionPage() {
  // States for different transcription methods
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [language, setLanguage] = useState('ko')
  const [currentJob, setCurrentJob] = useState<TranscriptionJob | null>(null)
  const [activeTab, setActiveTab] = useState('youtube')

  // API hooks
  const uploadFileMutation = useUploadFile()
  const transcribeYouTubeMutation = useTranscribeYouTube()
  const { data: health } = useTranscriptionHealth()
  
  // Poll job status if we have a current job
  const { job, isCompleted, isFailed, isProcessing } = useJobStatusPolling(
    currentJob?.job_id
  )

  // Update current job when polling returns new data
  const effectiveJob = (job || currentJob) as TranscriptionJob | null

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'video/mp4', 'video/mpeg']
      if (!allowedTypes.includes(file.type)) {
        alert('지원되지 않는 파일 형식입니다. MP3, WAV, MP4 파일만 업로드할 수 있습니다.')
        return
      }
      
      // Validate file size (max 100MB)
      if (file.size > 100 * 1024 * 1024) {
        alert('파일 크기가 너무 큽니다. 100MB 이하의 파일만 업로드할 수 있습니다.')
        return
      }
      
      setSelectedFile(file)
    }
  }

  const handleFileUpload = async () => {
    if (!selectedFile) return
    
    try {
      const result = await uploadFileMutation.mutateAsync({
        file: selectedFile,
        language
      })
      setCurrentJob(result)
    } catch (error) {
      console.error('File upload failed:', error)
    }
  }

  const handleYouTubeTranscribe = async () => {
    if (!youtubeUrl.trim()) return
    
    try {
      const result = await transcribeYouTubeMutation.mutateAsync({
        youtube_url: youtubeUrl.trim(),
        language
      })
      setCurrentJob(result)
    } catch (error) {
      console.error('YouTube transcription failed:', error)
    }
  }

  const isYouTubeUrl = (url: string) => {
    return url.includes('youtube.com') || url.includes('youtu.be')
  }

  const getYouTubeEmbedUrl = (url: string) => {
    if (!url) return null
    
    let videoId = ''
    if (url.includes('youtube.com/watch?v=')) {
      videoId = url.split('v=')[1]?.split('&')[0]
    } else if (url.includes('youtu.be/')) {
      videoId = url.split('youtu.be/')[1]?.split('?')[0]
    }
    
    return videoId ? `https://www.youtube.com/embed/${videoId}` : null
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Page Header */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900">음성 전사</h1>
          <p className="text-gray-600">
            음성 파일이나 YouTube 동영상을 텍스트로 변환합니다.
          </p>
        </div>

        {/* Service Health Check */}
        {health && (
          <Alert>
            <CheckCircleIcon className="h-4 w-4" />
            <AlertDescription>
              전사 서비스가 정상적으로 작동 중입니다.
            </AlertDescription>
          </Alert>
        )}

        {!health && (
          <Alert variant="destructive">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              전사 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.
            </AlertDescription>
          </Alert>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle>전사 요청</CardTitle>
              <CardDescription>
                파일 업로드 또는 YouTube URL을 입력하여 전사를 시작하세요.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="youtube">
                    <YoutubeIcon className="h-4 w-4 mr-2" />
                    YouTube
                  </TabsTrigger>
                  <TabsTrigger value="file">
                    <FileAudioIcon className="h-4 w-4 mr-2" />
                    파일 업로드
                  </TabsTrigger>
                </TabsList>

                {/* YouTube Tab */}
                <TabsContent value="youtube" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="youtube-url">YouTube URL</Label>
                    <Input
                      id="youtube-url"
                      placeholder="https://www.youtube.com/watch?v=..."
                      value={youtubeUrl}
                      onChange={(e) => setYoutubeUrl(e.target.value)}
                    />
                  </div>

                  {/* YouTube Preview */}
                  {youtubeUrl && isYouTubeUrl(youtubeUrl) && getYouTubeEmbedUrl(youtubeUrl) && (
                    <div className="space-y-2">
                      <Label>동영상 미리보기</Label>
                      <div className="aspect-video">
                        <iframe
                          src={getYouTubeEmbedUrl(youtubeUrl)!}
                          className="w-full h-full rounded-lg"
                          allowFullScreen
                        />
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="language-youtube">언어</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ko">한국어</SelectItem>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="ja">日本語</SelectItem>
                        <SelectItem value="zh">中文</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button
                    onClick={handleYouTubeTranscribe}
                    disabled={!youtubeUrl.trim() || transcribeYouTubeMutation.isPending}
                    className="w-full"
                  >
                    {transcribeYouTubeMutation.isPending ? (
                      '전사 요청 중...'
                    ) : (
                      <>
                        <YoutubeIcon className="h-4 w-4 mr-2" />
                        YouTube 전사 시작
                      </>
                    )}
                  </Button>
                </TabsContent>

                {/* File Upload Tab */}
                <TabsContent value="file" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="file-upload">음성/비디오 파일</Label>
                    <Input
                      id="file-upload"
                      type="file"
                      accept="audio/*,video/*"
                      onChange={handleFileSelect}
                    />
                    {selectedFile && (
                      <p className="text-sm text-gray-600">
                        선택된 파일: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="language-file">언어</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ko">한국어</SelectItem>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="ja">日本語</SelectItem>
                        <SelectItem value="zh">中文</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button
                    onClick={handleFileUpload}
                    disabled={!selectedFile || uploadFileMutation.isPending}
                    className="w-full"
                  >
                    {uploadFileMutation.isPending ? (
                      '업로드 중...'
                    ) : (
                      <>
                        <UploadIcon className="h-4 w-4 mr-2" />
                        파일 업로드 및 전사 시작
                      </>
                    )}
                  </Button>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Result Section */}
          <Card>
            <CardHeader>
              <CardTitle>전사 결과</CardTitle>
              <CardDescription>
                전사 작업의 진행 상황과 결과를 확인하세요.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {effectiveJob ? (
                <TranscriptionResult 
                  job={effectiveJob} 
                  autoNavigateToAnalysis={true}
                  showActions={true}
                />
              ) : (
                <div className="text-center py-8 text-gray-500">
                  전사 작업이 시작되면 여기에 결과가 표시됩니다.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Error Handling */}
        {(uploadFileMutation.error || transcribeYouTubeMutation.error) && (
          <Alert variant="destructive">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              전사 작업 중 오류가 발생했습니다: {
                uploadFileMutation.error?.message || 
                transcribeYouTubeMutation.error?.message
              }
            </AlertDescription>
          </Alert>
        )}
      </div>
    </Layout>
  )
}