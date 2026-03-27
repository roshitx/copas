'use client'

import { X, Download, Clock } from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'

interface DownloadProgressProps {
  progress: number
  status: 'idle' | 'downloading' | 'complete' | 'error'
  eta: string | null
  fileCount: number
  onCancel: () => void
  className?: string
}

export function DownloadProgress({
  progress,
  status,
  eta,
  fileCount,
  onCancel,
  className,
}: DownloadProgressProps) {
  const isDownloading = status === 'downloading'
  const isComplete = status === 'complete'
  const isError = status === 'error'

  const progressText = isComplete
    ? 'Selesai!'
    : isError
      ? 'Gagal'
      : `${Math.round(progress)}%`

  return (
    <div
      className={cn(
        'w-full rounded-xl border border-border/60 bg-background/80 p-4 backdrop-blur-sm',
        className
      )}
      role="region"
      aria-label="Download progress"
      aria-live="polite"
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <div
            className={cn(
              'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
              isComplete
                ? 'bg-green-500/20 text-green-400'
                : isError
                  ? 'bg-red-500/20 text-red-400'
                  : 'bg-amber-500/20 text-amber-400'
            )}
          >
            <Download className="h-4 w-4" aria-hidden="true" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">
              {isComplete
                ? 'Download selesai'
                : isError
                  ? 'Download gagal'
                  : `Mengunduh ${fileCount} file`}
            </p>
            <p className="text-xs text-muted-foreground">
              {isDownloading && eta && (
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" aria-hidden="true" />
                  Estimasi: {eta}
                </span>
              )}
              {isDownloading && !eta && 'Memproses...'}
              {isComplete && 'File siap diunduh'}
              {isError && 'Terjadi kesalahan'}
            </p>
          </div>
        </div>

        {/* Cancel button */}
        {isDownloading && (
          <button
            onClick={onCancel}
            className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground/80 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
            aria-label="Cancel download"
            type="button"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        )}
      </div>

      {/* Progress bar container */}
      <div className="relative">
        <Progress
          value={progress}
          className={cn(
            'h-2 w-full',
            isComplete && '[&>div]:bg-green-500',
            isError && '[&>div]:bg-red-500'
          )}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(progress)}
          aria-label="Download progress percentage"
        />

        {/* Shimmer effect overlay */}
        {isDownloading && (
          <div
            className="pointer-events-none absolute inset-0 overflow-hidden rounded-full"
            aria-hidden="true"
          >
            <div
              className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-white/20 to-transparent"
              style={{
                transform: 'translateX(-100%)',
              }}
            />
          </div>
        )}
      </div>

      {/* Progress percentage */}
      <div className="mt-2 flex items-center justify-between">
        <span
          className={cn(
            'text-xs font-medium tabular-nums',
            isComplete && 'text-green-400',
            isError && 'text-red-400',
            isDownloading && 'text-amber-400'
          )}
        >
          {progressText}
        </span>
        <span className="text-xs text-muted-foreground">
          {Math.round((progress / 100) * fileCount)} / {fileCount}
        </span>
      </div>
    </div>
  )
}
