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
      className={`group w-full ${variant === 'mobile' ? 'h-12' : 'h-14'} flex items-center gap-3 px-4 rounded-xl ${variant === 'mobile' ? 'bg-card/60 hover:bg-secondary/80' : 'border border-border/60 bg-card/40 hover:bg-secondary/60 hover:border-border/80'} active:scale-[0.99] transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100`}
    >
      {isImage ? (
        <ImageIcon size={15} className="text-muted-foreground group-hover:text-amber-400 transition-colors" />
      ) : (
        <Download size={15} className="text-muted-foreground group-hover:text-amber-400 transition-colors" />
      )}
      
      <div className="flex-1 flex flex-col items-start gap-1">
        <span className="text-left text-sm font-medium text-foreground leading-none line-clamp-1">
          {format.label}
        </span>
      </div>
      
      <span className="rounded-md border border-border/50 bg-secondary px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground leading-none shrink-0">
        {isImage ? 'IMAGE' : isVideo ? 'VIDEO' : 'AUDIO'}
      </span>
      
      {format.size_mb !== null && format.size_mb !== undefined && (
        <span className="text-xs text-muted-foreground shrink-0">
          {format.size_mb} MB
        </span>
      )}
      
      <ChevronRight size={14} className="text-muted-foreground/60 group-hover:translate-x-0.5 transition-transform duration-150 shrink-0" />
    </button>
  )
}
