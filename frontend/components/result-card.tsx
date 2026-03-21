'use client'

import { useState, useCallback, useRef } from 'react'
import Image from 'next/image'
import { Film, Download } from 'lucide-react'
import { LazyMotion, m as MotionDiv, useMotionValue, useTransform, animate, useReducedMotion } from 'framer-motion'
import { useDrag } from '@use-gesture/react'
import type { MediaResult } from '@/types'
import { PlatformBadge } from '@/components/platform-badge'
import { FormatList } from '@/components/format-list'
import { FormatSheet } from '@/components/format-sheet'

const loadFramerFeatures = () => import('framer-motion').then((mod) => mod.domAnimation)


function formatDuration(seconds: number | null): string | null {
  if (!seconds) return null
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return m + ':' + s.toString().padStart(2, '0')
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
        onError={() => setFailed(true)}
      />
    )
  }
  if (count === 2) {
    return (
      <div className="absolute inset-0 flex gap-0.5">
        {thumbnails.map((src, i) => (
          <div key={'double-' + src} className="relative flex-1">
            <Image src={src} alt={title + ' ' + (i + 1)} fill className="object-cover" />
          </div>
        ))}
      </div>
    )
  }

  if (count === 3) {
    return (
      <div className="absolute inset-0 flex gap-0.5">
        <div className="relative flex-1">
          <Image src={thumbnails[0]} alt={title + ' 1'} fill className="object-cover" />
        </div>
        <div className="flex-1 flex flex-col gap-0.5">
          {thumbnails.slice(1).map((src, i) => (
            <div key={'triple-' + src} className="relative flex-1">
              <Image src={src} alt={title + ' ' + (i + 2)} fill className="object-cover" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  const show = thumbnails.slice(0, 4)
  const overflow = count - 4
  return (
    <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 gap-0.5">
      {show.map((src, i) => (
        <div key={'grid-' + src} className="relative">
          <Image src={src} alt={title + ' ' + (i + 1)} fill className="object-cover" />
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
  onFocusReturn?: () => void
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
  const thumbnails = result.thumbnails?.length ? result.thumbnails : result.thumbnail ? [result.thumbnail] : []

  const handleDismiss = useCallback(() => {
    if (isDismissing) return

    setIsDismissing(true)
    setSrAnnouncement('Hasil download ditutup')

    if (shouldReduceMotion) {
      onDismiss?.()
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
        onFocusReturn?.()
      },
    })
  }, [isDismissing, onDismiss, onFocusReturn, shouldReduceMotion, x])

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
    <LazyMotion features={loadFramerFeatures} strict>
      <div className="relative overflow-hidden">
        <div className="sr-only" aria-live="polite" aria-atomic="true">
          {srAnnouncement}
        </div>
        <div className="relative overflow-hidden">
          <MotionDiv.div
            ref={cardRef}
            data-testid="result-card"
            role="button"
            aria-label="Hasil download. Tekan Delete untuk menutup"
            tabIndex={0}
            onKeyDown={handleKeyDown}
            style={{ x, scale, opacity }}
            className="w-full rounded-2xl overflow-hidden border border-zinc-800/50 bg-zinc-950 animate-fade-up cursor-grab touch-pan-y active:cursor-grabbing outline-none focus-visible:ring-2 focus-visible:ring-amber-500/50"
          >
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
              <FormatList result={result} />
            </div>

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

          <FormatSheet result={result} open={sheetOpen} onOpenChange={setSheetOpen} />
          </MotionDiv.div>
        </div>
      </div>
    </LazyMotion>
  )
}
