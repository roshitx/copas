'use client'

import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetFooter } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { FormatButton } from './format-button'
import { useDownload } from '@/hooks/use-download'
import type { MediaResult, Format } from '@/types'
import { Download, X, Film, Image as ImageIcon, Music } from 'lucide-react'


interface FormatSheetProps {
  result: MediaResult
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FormatSheet({ result, open, onOpenChange }: FormatSheetProps) {
  const { downloadAllAsZip, isDownloadingAll, downloadProgress, cancelDownload } = useDownload()

  const videoFormats = result.formats.filter(
    (f) => f.type.toLowerCase().includes('video') || f.type.toLowerCase().includes('mp4')
  )
  const imageFormats = result.formats.filter((f) => f.type.toLowerCase().includes('image'))
  const audioFormats = result.formats.filter((f) => f.type.toLowerCase().includes('audio'))

  // Group video formats by quality (same logic as result-card.tsx)
  const groupVideoFormats = (formats: Format[]) => {
    const groups: Record<string, Format[]> = {}
    formats.forEach((format) => {
      const qualityMatch = format.label.match(/\d+p/)
      const quality = qualityMatch ? qualityMatch[0] : 'Other'
      if (!groups[quality]) groups[quality] = []
      groups[quality].push(format)
    })
    return Object.entries(groups).sort(([a], [b]) => {
      const aNum = parseInt(a) || 0
      const bNum = parseInt(b) || 0
      return bNum - aNum
    })
  }

  const handleDownloadAll = () => {
    if (imageFormats.length > 1) {
      downloadAllAsZip(imageFormats, result)
    }
  }

  const hasMultipleVideos = videoFormats.length > 0
  const hasMultipleImages = imageFormats.length > 1
  const hasAudio = audioFormats.length > 0

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        className="h-[85vh] rounded-t-2xl border-t border-zinc-800 bg-zinc-950 px-0 text-zinc-100 [&>button]:hidden"
      >
        {/* Drag Handle */}
        <div className="mx-auto mt-3 h-1.5 w-12 rounded-full bg-zinc-700" />

        <SheetHeader className="px-4 pt-4">
          <SheetTitle className="text-left text-lg font-semibold text-zinc-100">
            Download Formats
          </SheetTitle>
          <p className="text-left text-sm text-zinc-400">
            {result.title || 'Untitled'} • {result.platform}
          </p>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto px-4 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
          {/* Video Formats */}
          {videoFormats.length > 0 && (
            <div className="mb-6">
              <div className="mb-3 flex items-center gap-2">
                <Film className="h-4 w-4 text-blue-400" />
                <span className="text-sm font-medium text-zinc-300">
                  Video {hasMultipleVideos && `(${videoFormats.length})`}
                </span>
              </div>
              <div className="space-y-2">
                {hasMultipleVideos ? (
                  groupVideoFormats(videoFormats).map(([quality, formats]) => (
                    <div key={quality}>
                      <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-zinc-500">
                        {quality}
                      </p>
                      <div className="space-y-1">
                        {formats.map((format, idx) => (
                          <FormatButton
                            key={`${format.id || idx}-${format.label}`}
                            format={format}
                            variant="mobile"
                          />
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  videoFormats.map((format, idx) => (
                    <FormatButton
                      key={`${format.id || idx}-${format.label}`}
                      format={format}
                      variant="mobile"
                    />
                  ))
                )}
              </div>
            </div>
          )}

          {/* Image Formats */}
          {imageFormats.length > 0 && (
            <div className="mb-6">
              <div className="mb-3 flex items-center gap-2">
                <ImageIcon className="h-4 w-4 text-green-400" aria-hidden="true" />
                <span className="text-sm font-medium text-zinc-300">
                  Image {hasMultipleImages && `(${imageFormats.length})`}
                </span>
              </div>
              <div className="space-y-1">
                {imageFormats.map((format, idx) => (
                  <FormatButton
                    key={`${format.id || idx}-${format.label}`}
                    format={format}
                    variant="mobile"
                  />
                ))}
              </div>
            </div>
          )}

          {/* Audio Formats */}
          {audioFormats.length > 0 && (
            <div className="mb-6">
              <div className="mb-3 flex items-center gap-2">
                <Music className="h-4 w-4 text-purple-400" />
                <span className="text-sm font-medium text-zinc-300">
                  Audio {hasAudio && `(${audioFormats.length})`}
                </span>
              </div>
              <div className="space-y-1">
                {audioFormats.map((format, idx) => (
                  <FormatButton
                    key={`${format.id || idx}-${format.label}`}
                    format={format}
                    variant="mobile"
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Download All Button - for multi-image posts */}
        {hasMultipleImages && (
          <SheetFooter className="border-t border-zinc-800 bg-zinc-950 px-4 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
            {isDownloadingAll ? (
              <div className="w-full space-y-3">
                <div className="h-2 w-full overflow-hidden rounded-full bg-zinc-800">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-300"
                    style={{ width: `${downloadProgress}%` }}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-zinc-400">
                    Downloading... {downloadProgress}%
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={cancelDownload}
                    className="h-8 gap-1 text-zinc-400 hover:text-red-400"
                  >
                    <X className="h-4 w-4" />
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <Button
                onClick={handleDownloadAll}
                className="w-full gap-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white hover:from-blue-600 hover:to-cyan-600"
              >
                <Download className="h-4 w-4" />
                Download All as ZIP
              </Button>
            )}
          </SheetFooter>
        )}
      </SheetContent>
    </Sheet>
  )
}