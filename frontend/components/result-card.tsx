'use client'

import { useState, useCallback, useRef } from 'react'
import Image from 'next/image'
import { Film, ImageIcon, Music, ChevronDown, Download } from 'lucide-react'
import { motion, useMotionValue, useTransform, animate, useReducedMotion } from 'framer-motion'
import { useDrag } from '@use-gesture/react'
import type { MediaResult } from '@/types'
import { PlatformBadge } from '@/components/platform-badge'
import { FormatButton } from '@/components/format-button'
import { FormatSheet } from '@/components/format-sheet'
import { DownloadProgress } from '@/components/download-progress'
import { useDownload } from '@/hooks/use-download'


function formatDuration(seconds: number | null): string | null {
  if (!seconds) return null
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return m + ':' + s.toString().padStart(2, '0')
}

// Group video formats by their video index ("Video 1 · 640p" → group 1)
function groupVideoFormats(videoFormats: MediaResult['formats']) {
  const groups = new Map<string, { label: string; formats: typeof videoFormats }>()
  for (const fmt of videoFormats) {
    const match = fmt.label.match(/^Video (\d+) ·/)
    if (match) {
      const key = match[1]
      if (!groups.has(key)) {
        groups.set(key, { label: 'Video ' + key, formats: [] })
      }
      groups.get(key)!.formats.push(fmt)
    } else {
      // Non-indexed video (single-video post) — put in "default" group
      if (!groups.has('default')) {
        groups.set('default', { label: 'Video', formats: [] })
      }
      groups.get('default')!.formats.push(fmt)
    }
  }
  return Array.from(groups.values())
}

interface ThumbnailGridProps {
  thumbnails: string[]
  title: string
}

function ThumbnailGrid({ thumbnails, title }: ThumbnailGridProps) {
  const [failed, setFailed] = useState(false)
  const count = thumbnails.length

  const placeholder = (
    <div className="absolute inset-0 flex items-center justify-center bg-zinc-900">
      <Film className="w-10 h-10 text-zinc-700" />
    </div>
  )

  if (count === 0 || failed) return placeholder

  if (count === 1) {
    return (
      <Image
        src={thumbnails[0]}
        alt={title || 'Thumbnail'}
        fill
        className="object-cover"
        unoptimized
        onError={() => setFailed(true)}
      />
    )
  }
  if (count === 2) {
    return (
      <div className="absolute inset-0 flex gap-0.5">
        {thumbnails.map((src, i) => (
          <div key={'double-' + src} className="relative flex-1">
            <Image src={src} alt={title + ' ' + (i + 1)} fill className="object-cover" unoptimized />
          </div>
        ))}
      </div>
    )
  }

  if (count === 3) {
    return (
      <div className="absolute inset-0 flex gap-0.5">
        <div className="relative flex-1">
          <Image src={thumbnails[0]} alt={title + ' 1'} fill className="object-cover" unoptimized />
        </div>
        <div className="flex-1 flex flex-col gap-0.5">
          {thumbnails.slice(1).map((src, i) => (
            <div key={'triple-' + src} className="relative flex-1">
              <Image src={src} alt={title + ' ' + (i + 2)} fill className="object-cover" unoptimized />
            </div>
          ))}
        </div>
      </div>
    )
  }

  // 4+ thumbnails: 2x2 grid with overflow badge
  const show = thumbnails.slice(0, 4)
  const overflow = count - 4
  return (
    <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 gap-0.5">
      {show.map((src, i) => (
        <div key={'grid-' + src} className="relative">
          <Image src={src} alt={title + ' ' + (i + 1)} fill className="object-cover" unoptimized />
          {i === 3 && overflow > 0 && (
            <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
              <span className="text-white font-black text-xl">+{overflow}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

interface ResultCardProps {
  result: MediaResult
  onDismiss?: () => void
  onFocusReturn?: () => void  // Callback to return focus to URL input
}

export function ResultCard({ result, onDismiss, onFocusReturn }: ResultCardProps) {
  const [sheetOpen, setSheetOpen] = useState(false)
  const [isDismissing, setIsDismissing] = useState(false)
  const [srAnnouncement, setSrAnnouncement] = useState('')
  const cardRef = useRef<HTMLDivElement | null>(null)
  const x = useMotionValue(0)
  const scale = useTransform(x, [-200, 0, 200], [0.9, 1, 0.9])
  const opacity = useTransform(x, [-200, 0, 200], [0.6, 1, 0.6])
  const shouldReduceMotion = useReducedMotion()

  const durationStr = formatDuration(result.duration)
  const {
    downloadAllAsZip,
    isDownloadingAll,
    downloadProgress,
    downloadStatus,
    downloadETA,
    cancelDownload,
  } = useDownload()


  const videoFormats = result.formats.filter(
    (f) => f.type.toLowerCase().includes('video') || f.type.toLowerCase().includes('mp4')
  )
  const imageFormats = result.formats.filter((f) => f.type.toLowerCase().includes('image'))
  const audioFormats = result.formats.filter((f) => f.type.toLowerCase().includes('audio'))

  const videoGroups = groupVideoFormats(videoFormats)
  const isMultiVideo = videoGroups.length > 1

  // Show accordion if: multiple video groups, or multiple media type categories
  const typeCategoryCount = [videoFormats.length > 0, imageFormats.length > 0, audioFormats.length > 0].filter(Boolean).length
  const showAccordion = isMultiVideo || typeCategoryCount > 1 || imageFormats.length > 1

  const thumbnails = result.thumbnails?.length ? result.thumbnails : result.thumbnail ? [result.thumbnail] : []

  const handleDownloadAll = () => downloadAllAsZip(imageFormats, result)

  const handleDismiss = useCallback(() => {
    if (isDismissing) return
    
    setIsDismissing(true)
    
    // Announce dismiss action to screen readers
    setSrAnnouncement('Hasil download ditutup')
    
    if (shouldReduceMotion) {
      // Skip animation for reduced motion
      onDismiss?.()
      // Return focus after dismiss
      setTimeout(() => onFocusReturn?.(), 0)
      return
    }
    
    const direction = x.get() > 0 ? 1 : -1
    animate(x, direction * 500, {
      type: 'spring',
      stiffness: 500,
      damping: 30,
      onComplete: () => {
        onDismiss?.()
        // Return focus after dismiss
        onFocusReturn?.()
      },
    })
  }, [isDismissing, onDismiss, onFocusReturn, shouldReduceMotion, x])
  
  // Keyboard handler for dismiss (Delete/Escape keys)
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Delete' || e.key === 'Backspace' || e.key === 'Escape') {
      e.preventDefault()
      handleDismiss()
    }
  }, [handleDismiss])

  useDrag(
    ({ movement: [mx], velocity: [vx], last, memo }) => {
      if (isDismissing) return

      if (last) {
        const threshold = 100
        const velocityThreshold = 0.5
        const shouldDismiss =
          Math.abs(mx) > threshold || Math.abs(vx) > velocityThreshold

        if (shouldDismiss) {
          handleDismiss()
        } else {
          animate(x, 0, { type: 'spring', stiffness: 500, damping: 30 })
        }
      } else {
        x.set(mx)
      }

      return memo
    },
    {
      target: cardRef,
      axis: 'x',
      filterTaps: true,
      from: () => [x.get(), 0],
    }
  )

  return (
    <div className="relative overflow-hidden">
      {/* Screen reader announcement area */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {srAnnouncement}
      </div>
      <div className="relative overflow-hidden">
        <motion.div
          ref={cardRef}
          data-testid="result-card"
          role="button"
          aria-label="Hasil download. Tekan Delete untuk menutup"
          tabIndex={0}
          onKeyDown={handleKeyDown}
          style={{ x, scale, opacity }}
          className="w-full rounded-2xl overflow-hidden border border-zinc-800/50 bg-zinc-950 animate-fade-up cursor-grab touch-pan-y active:cursor-grabbing outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50"
        >
          {/* Thumbnail — bento grid or single */}
          <div className="relative aspect-video bg-zinc-900">
            <ThumbnailGrid thumbnails={thumbnails} title={result.title} />

            <div className="absolute inset-0 vignette pointer-events-none" />

            <div className="absolute bottom-3 left-3">
              <PlatformBadge platform={result.platform} />
            </div>

            {durationStr && (
              <div className="absolute bottom-3 right-3 rounded-md bg-black/70 backdrop-blur-sm px-2 py-0.5 text-xs font-medium text-zinc-300 tabular-nums">
                {durationStr}
              </div>
            )}

            {thumbnails.length > 1 && (
              <div className="absolute top-3 right-3 rounded-md bg-black/70 backdrop-blur-sm px-2 py-0.5 text-xs font-bold text-zinc-200 tabular-nums">
                {thumbnails.length} media
              </div>
            )}
          </div>

          <div className="p-5 space-y-4">
            <h2 className="text-base font-semibold text-zinc-100 line-clamp-2 leading-snug">
              {result.title || 'Untitled'}
            </h2>

            <div className="border-t border-zinc-800/60" />

            <div className="hidden md:block">
              <div className="text-[11px] font-bold uppercase tracking-widest text-amber-500/80 mb-3">
                Pilih Format
              </div>

              {!showAccordion ? (
                <div data-testid="format-list" className="space-y-2">
                  {/* Show Download All for multi-image flat list */}
                  {imageFormats.length > 1 && (
                    <>
                      {isDownloadingAll ? (
                        <DownloadProgress
                          progress={downloadProgress}
                          status={downloadStatus}
                          eta={downloadETA}
                          fileCount={imageFormats.length}
                          onCancel={cancelDownload}
                        />
                      ) : (
                        <button
                          type="button"
                          data-testid="download-all-button"
                          onClick={handleDownloadAll}
                          disabled={isDownloadingAll}
                          className="w-full flex items-center justify-between gap-3 rounded-xl border border-amber-500/30 bg-amber-500/5 px-4 py-3 text-sm font-semibold text-amber-400 transition-colors hover:bg-amber-500/10 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <div className="flex items-center gap-2">
                            <Download className="w-4 h-4" />
                            <span>Download Semua Foto</span>
                          </div>
                          <span className="text-xs font-normal text-amber-400/70">{imageFormats.length} foto</span>
                        </button>
                      )}
                    </>
                  )}
                  {result.formats.map((format) => (
                    <FormatButton key={format.id || format.label + '-' + format.type} format={format} result={result} disabled={isDownloadingAll} />
                  ))}
                </div>
              ) : (
                <div className="border border-zinc-800 rounded-xl overflow-hidden divide-y divide-zinc-800">
                  {/* Videos section */}
                  {videoFormats.length > 0 && (
                    <details data-testid="video-section" open className="group">
                      <summary className="flex items-center gap-2 px-4 py-3 cursor-pointer list-none [&::-webkit-details-marker]:hidden h-11 bg-zinc-900/40 hover:bg-zinc-800/60 transition-colors">
                        <Film className="w-4 h-4 text-zinc-400 shrink-0" />
                        <span className="text-sm font-black tracking-tighter text-zinc-100 uppercase flex-1 truncate">
                          Videos
                        </span>
                        <span className="text-xs text-zinc-500 font-medium shrink-0">
                          {isMultiVideo ? videoGroups.length + ' video' : videoFormats.length}
                        </span>
                        <ChevronDown className="w-4 h-4 text-zinc-500 transition-transform duration-200 group-open:rotate-180 shrink-0" />
                      </summary>

                      <div className="p-3 space-y-3 bg-zinc-950/50">
                        {isMultiVideo ? (
                          /* Nested per-video accordions */
                          videoGroups.map((group) => (
                            <details key={group.label} data-testid="video-group" open className="group/inner border border-zinc-800/70 rounded-lg overflow-hidden">
                              <summary className="flex items-center gap-2 px-3 py-2.5 cursor-pointer list-none [&::-webkit-details-marker]:hidden bg-zinc-900/60 hover:bg-zinc-800/50 transition-colors">
                                <Film className="w-3.5 h-3.5 text-amber-500/70 shrink-0" />
                                <span className="text-xs font-black tracking-tight text-zinc-200 uppercase flex-1 truncate">
                                  {group.label}
                                </span>
                                <span className="text-[10px] text-zinc-500 font-medium shrink-0">
                                  {group.formats.length} kualitas
                                </span>
                                <ChevronDown className="w-3.5 h-3.5 text-zinc-600 transition-transform duration-200 group-open/inner:rotate-180 shrink-0" />
                              </summary>
                              <div className="p-2 space-y-1.5 bg-zinc-950/70">
                                {group.formats.map((format) => (
                                  <FormatButton key={format.id || group.label + '-' + format.label + '-' + format.type} format={format} result={result} disabled={isDownloadingAll} />
                                ))}
                              </div>
                            </details>
                          ))
                        ) : (
                          /* Single-source video — flat list of qualities */
                          <div className="space-y-2">
                            {videoFormats.map((format) => (
                              <FormatButton key={format.id || format.label + '-' + format.type} format={format} result={result} disabled={isDownloadingAll} />
                            ))}
                          </div>
                        )}
                      </div>
                    </details>
                  )}

                  {/* Images section */}
                  {imageFormats.length > 0 && (
                    <details data-testid="image-section" className="group">
                      <summary className="flex items-center gap-2 px-4 py-3 cursor-pointer list-none [&::-webkit-details-marker]:hidden h-11 bg-zinc-900/40 hover:bg-zinc-800/60 transition-colors">
                        <ImageIcon className="w-4 h-4 text-zinc-400 shrink-0" />
                        <span className="text-sm font-black tracking-tighter text-zinc-100 uppercase flex-1 truncate">
                          Images
                        </span>
                        <span className="text-xs text-zinc-500 font-medium shrink-0">{imageFormats.length}</span>
                        <ChevronDown className="w-4 h-4 text-zinc-500 transition-transform duration-200 group-open:rotate-180 shrink-0" />
                      </summary>
                      <div className="p-3 space-y-2 bg-zinc-950/50">
                        {imageFormats.length > 1 && (
                          <button
                            type="button"
                            data-testid="download-all-button"
                            onClick={handleDownloadAll}
                            disabled={isDownloadingAll}
                            className="w-full h-12 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-black text-sm tracking-widest uppercase rounded-lg transition-colors flex items-center justify-center gap-2 mb-2 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            <Download className="w-4 h-4 shrink-0" />
                            <span className="truncate">
                              {isDownloadingAll ? 'DOWNLOADING...' : 'DOWNLOAD SEMUA (' + imageFormats.length + ') FOTO'}
                            </span>
                          </button>
                        )}
                        {imageFormats.map((format) => (
                          <FormatButton key={format.id || format.label + '-' + format.type} format={format} result={result} disabled={isDownloadingAll} />
                        ))}
                      </div>
                    </details>
                  )}

                  {/* Audio section */}
                  {audioFormats.length > 0 && (
                    <details data-testid="audio-section" className="group">
                      <summary className="flex items-center gap-2 px-4 py-3 cursor-pointer list-none [&::-webkit-details-marker]:hidden h-11 bg-zinc-900/40 hover:bg-zinc-800/60 transition-colors">
                        <Music className="w-4 h-4 text-zinc-400 shrink-0" />
                        <span className="text-sm font-black tracking-tighter text-zinc-100 uppercase flex-1 truncate">
                          Audio
                        </span>
                        <span className="text-xs text-zinc-500 font-medium shrink-0">{audioFormats.length}</span>
                        <ChevronDown className="w-4 h-4 text-zinc-500 transition-transform duration-200 group-open:rotate-180 shrink-0" />
                      </summary>
                      <div className="p-3 space-y-2 bg-zinc-950/50">
                        {audioFormats.map((format) => (
                          <FormatButton key={format.id || format.label + '-' + format.type} format={format} result={result} disabled={isDownloadingAll} />
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              )}
            </div>

            {/* Mobile download button */}
            <button
              type="button"
              data-testid="mobile-download-button"
              onClick={() => setSheetOpen(true)}
              className="md:hidden w-full h-12 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-black text-sm tracking-widest uppercase rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4 shrink-0" />
              <span>Download</span>
            </button>
          </div>

          {/* Mobile bottom sheet */}
          <FormatSheet result={result} open={sheetOpen} onOpenChange={setSheetOpen} />
        </motion.div>
      </div>
    </div>
  )
}
