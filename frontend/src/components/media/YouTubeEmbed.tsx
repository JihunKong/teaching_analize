'use client'

import React, { useState, useCallback } from 'react'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Play, Pause, Volume2, VolumeX, Maximize, ExternalLink } from 'lucide-react'

interface YouTubeEmbedProps {
  videoId: string
  title?: string
  className?: string
  width?: number | string
  height?: number | string
  autoplay?: boolean
  showControls?: boolean
  showTitle?: boolean
  showTimestamp?: boolean
  startTime?: number
  endTime?: number
  onPlay?: () => void
  onPause?: () => void
  onTimeUpdate?: (currentTime: number) => void
}

interface YouTubePlayerState {
  isPlaying: boolean
  isMuted: boolean
  currentTime: number
  duration: number
  volume: number
}

const YouTubeEmbed: React.FC<YouTubeEmbedProps> = ({
  videoId,
  title,
  className = '',
  width = '100%',
  height = 315,
  autoplay = false,
  showControls = true,
  showTitle = true,
  showTimestamp = false,
  startTime,
  endTime,
  onPlay,
  onPause,
  onTimeUpdate
}) => {
  const [playerState, setPlayerState] = useState<YouTubePlayerState>({
    isPlaying: false,
    isMuted: false,
    currentTime: 0,
    duration: 0,
    volume: 100
  })

  // Extract video ID from various YouTube URL formats
  const extractVideoId = useCallback((url: string): string => {
    const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
    const match = url.match(regex)
    return match ? match[1] : url
  }, [])

  const cleanVideoId = extractVideoId(videoId)

  // Build YouTube embed URL with parameters
  const buildEmbedUrl = useCallback(() => {
    const baseUrl = `https://www.youtube.com/embed/${cleanVideoId}`
    const params = new URLSearchParams()

    if (autoplay) params.append('autoplay', '1')
    if (!showControls) params.append('controls', '0')
    if (startTime) params.append('start', startTime.toString())
    if (endTime) params.append('end', endTime.toString())
    
    params.append('rel', '0') // Don't show related videos
    params.append('modestbranding', '1') // Minimal YouTube branding
    params.append('enablejsapi', '1') // Enable JavaScript API
    
    return `${baseUrl}?${params.toString()}`
  }, [cleanVideoId, autoplay, showControls, startTime, endTime])

  // Generate YouTube watch URL
  const getWatchUrl = useCallback(() => {
    let url = `https://www.youtube.com/watch?v=${cleanVideoId}`
    if (startTime) {
      url += `&t=${startTime}s`
    }
    return url
  }, [cleanVideoId, startTime])

  // Generate thumbnail URL
  const getThumbnailUrl = useCallback((quality: 'default' | 'medium' | 'high' | 'standard' | 'maxres' = 'medium') => {
    return `https://img.youtube.com/vi/${cleanVideoId}/${quality}default.jpg`
  }, [cleanVideoId])

  // Format time for display
  const formatTime = useCallback((seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }, [])

  // Handle iframe load and setup message listener for player events
  const handleIframeLoad = useCallback(() => {
    // Listen for postMessage events from YouTube iframe
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== 'https://www.youtube.com') return
      
      try {
        const data = JSON.parse(event.data)
        
        switch (data.event) {
          case 'video-progress':
            setPlayerState(prev => ({ ...prev, currentTime: data.info.currentTime }))
            onTimeUpdate?.(data.info.currentTime)
            break
          case 'onStateChange':
            const isPlaying = data.info === 1 // YT.PlayerState.PLAYING
            const isPaused = data.info === 2  // YT.PlayerState.PAUSED
            
            setPlayerState(prev => ({ ...prev, isPlaying }))
            
            if (isPlaying) onPlay?.()
            if (isPaused) onPause?.()
            break
        }
      } catch (error) {
        // Ignore parsing errors
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [onPlay, onPause, onTimeUpdate])

  return (
    <Card className={`youtube-embed-container ${className}`}>
      {showTitle && title && (
        <div className="p-4 border-b">
          <h3 className="font-semibold text-lg">{title}</h3>
          {showTimestamp && startTime && (
            <p className="text-sm text-gray-600 mt-1">
              시작 시간: {formatTime(startTime)}
              {endTime && ` - 종료 시간: ${formatTime(endTime)}`}
            </p>
          )}
        </div>
      )}
      
      <div className="relative">
        <div className="aspect-video">
          <iframe
            width={width}
            height={height}
            src={buildEmbedUrl()}
            title={title || `YouTube video ${cleanVideoId}`}
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
            onLoad={handleIframeLoad}
            className="w-full h-full rounded-lg"
          />
        </div>
        
        {/* Custom controls overlay (optional) */}
        {showControls && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-4">
            <div className="flex items-center justify-between text-white">
              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-white hover:text-gray-300"
                  onClick={() => window.open(getWatchUrl(), '_blank')}
                >
                  <ExternalLink className="w-4 h-4" />
                </Button>
              </div>
              
              {showTimestamp && (
                <div className="text-sm">
                  {formatTime(playerState.currentTime)}
                  {playerState.duration > 0 && ` / ${formatTime(playerState.duration)}`}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      
      {/* Video information */}
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              size="sm"
              variant="outline"
              onClick={() => window.open(getWatchUrl(), '_blank')}
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              YouTube에서 보기
            </Button>
          </div>
          
          <div className="text-sm text-gray-600">
            Video ID: {cleanVideoId}
          </div>
        </div>
        
        {/* Thumbnail preview (hidden by default, could be shown on hover or error) */}
        <img
          src={getThumbnailUrl('medium')}
          alt={title || 'Video thumbnail'}
          className="hidden"
          onError={(e) => {
            // Handle thumbnail load error
            console.warn('Failed to load YouTube thumbnail:', e)
          }}
        />
      </div>
    </Card>
  )
}

// Utility function to extract video ID from YouTube URLs
export const extractYouTubeVideoId = (url: string): string | null => {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
  const match = url.match(regex)
  return match ? match[1] : null
}

// Utility function to validate YouTube URL
export const isValidYouTubeUrl = (url: string): boolean => {
  return extractYouTubeVideoId(url) !== null
}

// Utility function to get video thumbnail
export const getYouTubeThumbnail = (videoId: string, quality: 'default' | 'medium' | 'high' | 'standard' | 'maxres' = 'medium'): string => {
  return `https://img.youtube.com/vi/${videoId}/${quality}default.jpg`
}

// Component for displaying video timestamp links
interface VideoTimestampProps {
  videoId: string
  timestamp: number
  label: string
  className?: string
}

export const VideoTimestamp: React.FC<VideoTimestampProps> = ({
  videoId,
  timestamp,
  label,
  className = ''
}) => {
  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.floor(seconds % 60)
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const handleClick = () => {
    const url = `https://www.youtube.com/watch?v=${videoId}&t=${timestamp}s`
    window.open(url, '_blank')
  }

  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center space-x-2 text-blue-600 hover:text-blue-800 hover:underline ${className}`}
    >
      <Play className="w-3 h-3" />
      <span>{formatTime(timestamp)}</span>
      <span>{label}</span>
    </button>
  )
}

export default YouTubeEmbed