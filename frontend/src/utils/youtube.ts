/**
 * YouTube URL utilities
 * Extracted and adapted from existing patterns
 */

/**
 * Extract video ID from various YouTube URL formats
 * @param url - The YouTube URL to extract video ID from
 * @returns The video ID if found, null otherwise
 */
export const extractYouTubeVideoId = (url: string): string | null => {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
  const match = url.match(regex)
  return match ? match[1] : null
}

/**
 * Validate if a URL is a valid YouTube URL
 * @param url - The URL to validate
 * @returns true if valid YouTube URL, false otherwise
 */
export const isValidYouTubeUrl = (url: string): boolean => {
  return extractYouTubeVideoId(url) !== null
}

/**
 * Get YouTube video thumbnail URL
 * @param videoId - The YouTube video ID
 * @param quality - The thumbnail quality
 * @returns The thumbnail URL
 */
export const getYouTubeThumbnail = (
  videoId: string, 
  quality: 'default' | 'medium' | 'high' | 'standard' | 'maxres' = 'medium'
): string => {
  return `https://img.youtube.com/vi/${videoId}/${quality}default.jpg`
}

/**
 * Build YouTube embed URL with parameters
 * @param videoId - The YouTube video ID
 * @param options - Embed options
 * @returns The embed URL
 */
export const buildYouTubeEmbedUrl = (
  videoId: string,
  options: {
    autoplay?: boolean
    showControls?: boolean
    startTime?: number
    endTime?: number
  } = {}
): string => {
  const { autoplay = false, showControls = true, startTime, endTime } = options
  const baseUrl = `https://www.youtube.com/embed/${videoId}`
  const params = new URLSearchParams()

  if (autoplay) params.append('autoplay', '1')
  if (!showControls) params.append('controls', '0')
  if (startTime) params.append('start', startTime.toString())
  if (endTime) params.append('end', endTime.toString())
  
  params.append('rel', '0') // Don't show related videos
  params.append('modestbranding', '1') // Minimal YouTube branding
  params.append('enablejsapi', '1') // Enable JavaScript API
  
  return `${baseUrl}?${params.toString()}`
}

/**
 * Generate YouTube watch URL
 * @param videoId - The YouTube video ID
 * @param startTime - Optional start time in seconds
 * @returns The YouTube watch URL
 */
export const getYouTubeWatchUrl = (videoId: string, startTime?: number): string => {
  let url = `https://www.youtube.com/watch?v=${videoId}`
  if (startTime) {
    url += `&t=${startTime}s`
  }
  return url
}

/**
 * Format time in seconds to MM:SS format
 * @param seconds - Time in seconds
 * @returns Formatted time string
 */
export const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}