'use client'

import { Skeleton } from '@/components/ui/skeleton'

export function SkeletonResult() {
  return (
    <div
      className="w-full rounded-2xl overflow-hidden border border-zinc-800/50 bg-zinc-950"
      aria-busy="true"
      aria-label="Loading content"
      role="status"
    >
      {/* Thumbnail placeholder - matches aspect-video bg-zinc-900 */}
      <div className="relative aspect-video bg-zinc-900">
        <Skeleton shimmer className="absolute inset-0 rounded-none bg-zinc-800/50" />

        {/* Platform badge placeholder - bottom-left */}
        <div className="absolute bottom-3 left-3">
          <Skeleton shimmer className="h-6 w-20 rounded-full bg-zinc-800/70" />
        </div>

        {/* Duration placeholder - bottom-right */}
        <div className="absolute bottom-3 right-3">
          <Skeleton shimmer className="h-5 w-12 rounded-md bg-zinc-800/70" />
        </div>

        {/* Media count badge placeholder - top-right */}
        <div className="absolute top-3 right-3">
          <Skeleton shimmer className="h-5 w-16 rounded-md bg-zinc-800/70" />
        </div>
      </div>

      <div className="p-5 space-y-4">
        {/* Title placeholder - matches line-clamp-2 leading-snug */}
        <div className="space-y-2">
          <Skeleton shimmer className="h-5 w-full rounded-lg bg-zinc-800/50" />
          <Skeleton shimmer className="h-5 w-3/4 rounded-lg bg-zinc-800/50" />
        </div>

        {/* Divider - matches border-t border-zinc-800/60 */}
        <div className="border-t border-zinc-800/60" />

        {/* Format section */}
        <div>
          {/* "Pilih Format" header placeholder */}
          <Skeleton shimmer className="h-3 w-24 rounded-md bg-zinc-800/50 mb-3" />

          {/* Format buttons placeholder - matches FormatButton layout */}
          <div className="space-y-2">
            <Skeleton
              shimmer
              className="h-14 w-full rounded-xl bg-zinc-800/50"
            />
            <Skeleton
              shimmer
              className="h-14 w-full rounded-xl bg-zinc-800/50"
            />
            <Skeleton
              shimmer
              className="h-14 w-full rounded-xl bg-zinc-800/50"
            />
          </div>
        </div>
      </div>

      {/* Visually hidden text for screen readers */}
      <span className="sr-only">Loading media information...</span>
    </div>
  )
}
