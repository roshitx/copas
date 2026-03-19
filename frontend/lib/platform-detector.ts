import type { Platform } from '@/types'

const PLATFORM_PATTERNS: Record<Platform, RegExp[]> = {
  tiktok: [
    /tiktok\.com\/@[\w.]+\/video\/\d+/i,
    /vm\.tiktok\.com\/[\w]+/i,
    /vt\.tiktok\.com\/[\w]+/i,
    /tiktok\.com\/t\/[\w]+/i,
  ],
  instagram: [
    /instagram\.com\/(?:p|reel|tv)\/[\w-]+/i,
    /instagram\.com\/stories\/[\w.]+\/\d+/i,
    /instagr\.am\/p\/[\w-]+/i,
  ],
  youtube: [
    /youtube\.com\/watch\?v=[\w-]+/i,
    /youtu\.be\/[\w-]+/i,
    /youtube\.com\/shorts\/[\w-]+/i,
    /music\.youtube\.com\/watch\?v=[\w-]+/i,
    /youtube\.com\/live\/[\w-]+/i,
  ],
  twitter: [
    /(?:twitter|x)\.com\/[\w]+\/status\/\d+/i,
    /t\.co\/[\w]+/i,
  ],
  facebook: [
    /facebook\.com\/(?:watch\/?\?v=|[\w.]+\/videos\/|reel\/)\d+/i,
    /fb\.watch\/[\w]+/i,
    /fb\.me\/[\w]+/i,
    /facebook\.com\/share\/v\/[\w]+/i,
  ],
  threads: [
    /threads\.net\/@[\w.]+\/post\/[\w-]+/i,
    /threads\.net\/t\/[\w-]+/i,
    /threads\.com\/@[\w.]+\/post\/[\w-]+/i,
    /threads\.com\/t\/[\w-]+/i,
  ],
  unknown: [],
}

export function detectPlatform(url: string): Platform {
  try {
    const normalizedUrl = url.trim().toLowerCase()

    for (const [platform, patterns] of Object.entries(PLATFORM_PATTERNS) as [Platform, RegExp[]][]) {
      if (platform === 'unknown') continue
      for (const pattern of patterns) {
        if (pattern.test(normalizedUrl)) {
          return platform
        }
      }
    }

    // Fallback: hostname-based detection for bare domain URLs
    const hostname = new URL(url.trim()).hostname.replace('www.', '')
    if (hostname.includes('tiktok.com')) return 'tiktok'
    if (hostname.includes('instagram.com')) return 'instagram'
    if (hostname.includes('youtube.com') || hostname === 'youtu.be') return 'youtube'
    if (hostname.includes('twitter.com') || hostname === 'x.com') return 'twitter'
    if (hostname.includes('facebook.com') || hostname === 'fb.watch') return 'facebook'
    if (hostname.includes('threads.net') || hostname.includes('threads.com')) return 'threads'
  } catch {
    // Invalid URL — return unknown
  }

  return 'unknown'
}

export function isValidUrl(url: string): boolean {
  try {
    const parsed = new URL(url.trim())
    return ['http:', 'https:'].includes(parsed.protocol)
  } catch {
    return false
  }
}

export const PLATFORM_LABELS: Record<Platform, string> = {
  tiktok: 'TikTok',
  instagram: 'Instagram',
  youtube: 'YouTube',
  twitter: 'X / Twitter',
  facebook: 'Facebook',
  threads: 'Threads',
  unknown: 'Unknown',
}

export const PLATFORM_COLORS: Record<Platform, string> = {
  tiktok: 'bg-black border-white/20 text-white',
  instagram: 'bg-gradient-to-r from-purple-600 to-pink-500 text-white border-transparent',
  youtube: 'bg-red-600 text-white border-transparent',
  twitter: 'bg-sky-500 text-white border-transparent',
  facebook: 'bg-blue-600 text-white border-transparent',
  threads: 'bg-zinc-800 text-white border-white/10',
  unknown: 'bg-muted text-muted-foreground border-border',
}
