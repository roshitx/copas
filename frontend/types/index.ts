export type Platform =
  | 'tiktok'
  | 'instagram'
  | 'youtube'
  | 'twitter'
  | 'facebook'
  | 'threads'
  | 'unknown'

export type DownloadStatus = 'idle' | 'loading' | 'success' | 'error'

export interface Format {
  id: string
  label: string
  type: string // "video/mp4" | "audio/mp3"
  size_mb: number | null
  download_url: string
}

export interface MediaResult {
  platform: Platform
  title: string
  thumbnail: string | null
  thumbnails: string[]  // For bento grid
  author: string | null
  duration: number | null // seconds
  formats: Format[]
}

export interface ExtractRequest {
  url: string
}

export interface ApiError {
  error: string
  message: string
}


export type ErrorCode =
  | 'UNSUPPORTED_PLATFORM'
  | 'ACCESS_DENIED'
  | 'EXTRACTION_FAILED'
  | 'RATE_LIMITED'
  | 'NETWORK_ERROR'
  | 'TIMEOUT'
  | 'UNKNOWN_ERROR'

export interface PlatformErrorConfig {
  platform: Platform
  displayName: string
  messages: Record<ErrorCode, string>
  genericMessage: string
  suggestedActions: string[]
}