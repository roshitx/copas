'use client'

import { useState } from 'react'
import { Loader2, X } from 'lucide-react'
import { detectPlatform } from '@/lib/platform-detector'
import { PlatformBadge } from '@/components/platform-badge'

const PLATFORM_GLOW: Record<string, string> = {
  tiktok: 'glow-tiktok',
  instagram: 'glow-instagram',
  youtube: 'glow-youtube',
  twitter: 'glow-twitter',
  facebook: 'glow-facebook',
  threads: 'glow-threads',
}

interface UrlInputProps {
  onSubmit: (url: string) => void
  isLoading: boolean
  onReset?: () => void
}

const ZERO_WIDTH_REGEX = /[\u200B-\u200D\uFEFF]/g
const URL_IN_TEXT_REGEX = /(https?:\/\/[^\s"'<>]+)/i
const PLATFORM_URL_IN_TEXT_REGEX = /(?:(?:https?:\/\/)?(?:www\.)?(?:tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com|instagram\.com|instagr\.am|youtube\.com|youtu\.be|music\.youtube\.com|x\.com|twitter\.com|t\.co|facebook\.com|fb\.watch|fb\.me|threads\.net|threads\.com)\/[^\s"'<>]+)/i

function normalizeInput(value: string): string {
  return value.replace(ZERO_WIDTH_REGEX, '').trim()
}

function extractPastedUrl(value: string): string {
  const normalized = normalizeInput(value)
  if (!normalized) return ''

  const directMatch = normalized.match(URL_IN_TEXT_REGEX)
  if (directMatch?.[1]) return directMatch[1]

  const platformMatch = normalized.match(PLATFORM_URL_IN_TEXT_REGEX)
  if (platformMatch?.[0]) {
    const candidate = platformMatch[0]
    return candidate.startsWith('http://') || candidate.startsWith('https://')
      ? candidate
      : `https://${candidate}`
  }

  return normalized
}

export function UrlInput({ onSubmit, isLoading, onReset }: UrlInputProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)


  const normalizedUrl = normalizeInput(url)
  const platform = detectPlatform(normalizedUrl)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!normalizedUrl) return
    setError(null)
    onSubmit(normalizedUrl)
  }

  const handleClear = () => {
    setUrl('')
    setError(null)
    onReset?.()
  }

  const glowClass = platform !== 'unknown' ? PLATFORM_GLOW[platform] : ''

  return (
    <div className="relative w-full max-w-2xl">
      <div 
        className={`absolute -inset-3 rounded-3xl transition-all duration-700 ease-out pointer-events-none blur-xl ${
          platform !== 'unknown' ? 'opacity-100 ' + glowClass : 'opacity-0'
        }`} 
      />
      
      <form 
        onSubmit={handleSubmit} 
        className="relative flex items-center h-16 rounded-2xl bg-zinc-900/80 border border-zinc-800 transition-all duration-300 focus-within:border-amber-500/60 focus-within:shadow-input-focus-amber"
      >
        <input
          type="text"
          inputMode="url"
          value={url}
          onChange={(e) => {
            const raw = e.target.value
            // Extract URL from pasted text (handles share-sheet text, URLs embedded in sentences)
            setUrl(extractPastedUrl(raw))
            setError(null)
          }}

          placeholder="Tempel link video di sini..."
          className="flex-1 h-full bg-transparent px-5 text-sm sm:text-base text-zinc-100 placeholder:text-zinc-600 outline-none"
          disabled={isLoading}
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="none"
          spellCheck="false"
        />
        
        {url && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-[120px] text-zinc-500 hover:text-zinc-300"
            aria-label="Clear input"
          >
            <X size={20} />
          </button>
        )}
        
        <div className="pr-2">
          <button
            type="submit"
            disabled={isLoading || !normalizedUrl}
            className="h-11 px-6 rounded-xl bg-[#F59E0B] text-zinc-950 font-semibold text-sm hover:bg-amber-400 active:scale-95 transition-all duration-150 shadow-amber-glow disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[100px]"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Memproses...
              </>
            ) : (
              'Copas!'
            )}
          </button>
        </div>
      </form>

      {platform !== 'unknown' && !error && (
        <div className="mt-3 ml-1 animate-in fade-in duration-300">
          <PlatformBadge platform={platform} />
        </div>
      )}
      
      {error && (
        <p className="mt-2 ml-1 text-xs text-red-400">{error}</p>
      )}
    </div>
  )
}
