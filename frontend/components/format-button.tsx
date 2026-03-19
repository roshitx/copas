'use client'

import { Download, ChevronRight, ImageIcon } from 'lucide-react'
import { useDownload } from '@/hooks/use-download'
import type { Format, MediaResult } from '@/types'

interface FormatButtonProps {
  format: Format
  result?: Pick<MediaResult, 'platform' | 'author'>
  disabled?: boolean
  variant?: 'desktop' | 'mobile'
}

export function FormatButton({ format, result, disabled, variant = 'desktop' }: FormatButtonProps) {
  const { downloadFormat, status } = useDownload()

  
  const isVideo = format.type.toLowerCase().includes('video') || format.type.toLowerCase().includes('mp4')
  const isImage = format.type.toLowerCase().includes('image')
  const isDownloading = status === 'loading'
  const isDisabled = disabled || isDownloading

  return (
    <button
      data-testid="format-button"
      type="button"
      disabled={isDisabled}
      onClick={() => downloadFormat(format, result)}
      className={`group w-full ${variant === 'mobile' ? 'h-12' : 'h-14'} flex items-center gap-3 px-4 rounded-xl ${variant === 'mobile' ? 'bg-zinc-900/60 hover:bg-zinc-800/80' : 'border border-zinc-800/60 bg-zinc-900/40 hover:bg-zinc-800/60 hover:border-zinc-700/80'} active:scale-[0.99] transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100`}
    >
      {isImage ? (
        <ImageIcon size={15} className="text-zinc-500 group-hover:text-amber-400 transition-colors" />
      ) : (
        <Download size={15} className="text-zinc-500 group-hover:text-amber-400 transition-colors" />
      )}
      
      <div className="flex-1 flex flex-col items-start gap-1">
        <span className="text-left text-sm font-medium text-zinc-100 leading-none line-clamp-1">
          {format.label}
        </span>
      </div>
      
      <span className="rounded-md border border-zinc-700/50 bg-zinc-800 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-zinc-400 leading-none shrink-0">
        {isImage ? 'IMAGE' : isVideo ? 'VIDEO' : 'AUDIO'}
      </span>
      
      {format.size_mb !== null && format.size_mb !== undefined && (
        <span className="text-xs text-zinc-500 shrink-0">
          {format.size_mb} MB
        </span>
      )}
      
      <ChevronRight size={14} className="text-zinc-600 group-hover:translate-x-0.5 transition-transform duration-150 shrink-0" />
    </button>
  )
}
