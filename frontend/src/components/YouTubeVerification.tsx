'use client'

import React, { useState, useCallback, useEffect } from 'react'
import {
  extractYouTubeVideoId,
  isValidYouTubeUrl,
  buildYouTubeEmbedUrl,
  getYouTubeThumbnail,
  getYouTubeWatchUrl
} from '../utils/youtube'

interface YouTubeVerificationProps {
  onConfirm: (videoId: string, url: string) => void
  className?: string
}

interface VideoInfo {
  videoId: string
  originalUrl: string
  embedUrl: string
  thumbnailUrl: string
  watchUrl: string
}

const YouTubeVerification: React.FC<YouTubeVerificationProps> = ({
  onConfirm,
  className = ''
}) => {
  const [inputUrl, setInputUrl] = useState('')
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null)
  const [validationError, setValidationError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Reset video info when input changes
  useEffect(() => {
    if (inputUrl.trim() === '') {
      setVideoInfo(null)
      setValidationError('')
    }
  }, [inputUrl])

  // Validate and process YouTube URL
  const validateUrl = useCallback((url: string): VideoInfo | null => {
    if (!url.trim()) {
      setValidationError('YouTube URL을 입력해주세요.')
      return null
    }

    if (!isValidYouTubeUrl(url.trim())) {
      setValidationError('올바른 YouTube URL을 입력해주세요.')
      return null
    }

    const videoId = extractYouTubeVideoId(url.trim())
    if (!videoId) {
      setValidationError('비디오 ID를 추출할 수 없습니다.')
      return null
    }

    setValidationError('')
    return {
      videoId,
      originalUrl: url.trim(),
      embedUrl: buildYouTubeEmbedUrl(videoId),
      thumbnailUrl: getYouTubeThumbnail(videoId, 'medium'),
      watchUrl: getYouTubeWatchUrl(videoId)
    }
  }, [])

  // Handle URL input submission (Enter key or button click)
  const handleUrlSubmit = useCallback(() => {
    setIsLoading(true)
    
    const info = validateUrl(inputUrl)
    if (info) {
      setVideoInfo(info)
    }
    
    setIsLoading(false)
  }, [inputUrl, validateUrl])

  // Handle Enter key press
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleUrlSubmit()
    }
  }, [handleUrlSubmit])

  // Handle confirmation
  const handleConfirmVideo = useCallback(() => {
    if (videoInfo) {
      onConfirm(videoInfo.videoId, videoInfo.originalUrl)
    }
  }, [videoInfo, onConfirm])

  // Handle thumbnail load error
  const handleThumbnailError = useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
    console.warn('Failed to load YouTube thumbnail, using fallback')
    // Use a placeholder SVG data URI instead of hiding
    e.currentTarget.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="80" height="60" viewBox="0 0 80 60"%3E%3Crect width="80" height="60" fill="%23e0e0e0"/%3E%3Ctext x="50%25" y="50%25" font-family="Arial" font-size="12" fill="%23666" text-anchor="middle" dominant-baseline="middle"%3EVideo%3C/text%3E%3C/svg%3E'
  }, [])

  return (
    <div className={`youtube-verification ${className}`}>
      {/* Step 1: URL Input */}
      <div className="form-group">
        <label className="form-label" htmlFor="youtube-url-verify">
          YouTube URL 입력
        </label>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            id="youtube-url-verify"
            type="url"
            className="form-input"
            placeholder="https://www.youtube.com/watch?v=..."
            value={inputUrl}
            onChange={(e) => setInputUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            aria-describedby="url-verify-help"
            style={{ flex: 1 }}
          />
          <button
            className="btn"
            onClick={handleUrlSubmit}
            disabled={isLoading || !inputUrl.trim()}
            style={{ minWidth: '100px' }}
          >
            {isLoading ? '확인 중...' : '미리보기'}
          </button>
        </div>
        <small id="url-verify-help" style={{ color: '#666', marginTop: '5px', display: 'block' }}>
          YouTube URL을 입력하고 Enter를 누르거나 미리보기 버튼을 클릭하세요.
        </small>
        
        {/* Validation Error */}
        {validationError && (
          <div 
            className="status status-error" 
            style={{ marginTop: '10px', padding: '10px', fontSize: '0.9rem' }}
            role="alert"
          >
            {validationError}
          </div>
        )}
      </div>

      {/* Step 2: Video Preview/Embed */}
      {videoInfo && (
        <div className="video-verification-section" style={{ marginTop: '30px' }}>
          <h4 style={{ marginBottom: '20px', color: '#333' }}>
            📺 영상 확인
          </h4>
          
          <div className="video-preview-container">
            {/* Video Embed */}
            <div 
              className="video-embed" 
              style={{ 
                position: 'relative',
                paddingBottom: '56.25%', // 16:9 aspect ratio
                height: 0,
                overflow: 'hidden',
                borderRadius: '10px',
                marginBottom: '20px'
              }}
            >
              <iframe
                src={videoInfo.embedUrl}
                title="YouTube video preview"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  borderRadius: '10px'
                }}
              />
            </div>

            {/* Video Info */}
            <div 
              className="video-info" 
              style={{ 
                background: '#f8f9fa', 
                padding: '15px', 
                borderRadius: '8px',
                marginBottom: '20px'
              }}
            >
              <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '10px', alignItems: 'center' }}>
                <img
                  src={videoInfo.thumbnailUrl}
                  alt="Video thumbnail"
                  onError={handleThumbnailError}
                  style={{
                    width: '80px',
                    height: '60px',
                    objectFit: 'cover',
                    borderRadius: '5px'
                  }}
                />
                <div>
                  <p><strong>Video ID:</strong> {videoInfo.videoId}</p>
                  <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '5px' }}>
                    <a 
                      href={videoInfo.watchUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: '#667eea', textDecoration: 'underline' }}
                    >
                      YouTube에서 원본 영상 보기
                    </a>
                  </p>
                </div>
              </div>
            </div>

            {/* Step 3: Confirmation */}
            <div className="verification-actions" style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: '15px' }}>
                <p style={{ color: '#666', fontSize: '0.95rem' }}>
                  위 영상이 전사하려는 영상이 맞나요?
                </p>
              </div>
              
              <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
                <button
                  className="btn btn-large"
                  onClick={handleConfirmVideo}
                  style={{ minWidth: '150px' }}
                >
                  ✅ 확인 완료
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setVideoInfo(null)
                    setInputUrl('')
                    setValidationError('')
                  }}
                  style={{ minWidth: '100px' }}
                >
                  다시 입력
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default YouTubeVerification