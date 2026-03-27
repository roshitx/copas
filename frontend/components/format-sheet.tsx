'use client'

import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetFooter } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { FormatButton } from './format-button'
import { useDownload } from '@/hooks/use-download'
import type { MediaResult } from '@/types'
import { Download, X, Film, Image as ImageIcon, Music } from 'lucide-react'
import { categorizeFormats, groupVideoFormats } from '@/lib/format-utils'


interface FormatSheetProps {
  result: MediaResult
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FormatSheet({ result, open, onOpenChange }: FormatSheetProps) {
  const { downloadAllAsZip, isDownloadingAll, downloadProgress, cancelDownload } = useDownload()

  const { videoFormats, imageFormats, audioFormats } = categorizeFormats(result.formats)

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
        className="h-[85vh] rounded-t-2xl border-t border-border bg-background px-0 text-foreground [&>button]:hidden"
      >
        <SheetHeader className="px-4 pt-4">
          <SheetTitle className="text-left text-lg font-semibold text-foreground">
            Download Formats
          </SheetTitle>
          <p className="text-left text-sm text-muted-foreground">
            {result.title || 'Untitled'} • {result.platform}
          </p>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto px-4 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
          {/* Video Formats */}
          {videoFormats.length > 0 && (
            <div className="mb-6">
              <div className="mb-3 flex items-center gap-2">
                <Film className="h-4 w-4 text-blue-400" />
                <span className="text-sm font-medium text-foreground/80">
                  Video {hasMultipleVideos && `(${videoFormats.length})`}
                </span>
              </div>
              <div className="space-y-2">
                {hasMultipleVideos ? (
                  groupVideoFormats(videoFormats).map((group) => (
                    <div key={group.label}>
                      <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        {group.label}
                      </p>
                      <div className="space-y-1">
                        {group.formats.map((format, idx) => (
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
                <span className="text-sm font-medium text-foreground/80">
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
                <span className="text-sm font-medium text-foreground/80">
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
          <SheetFooter className="border-t border-border bg-background px-4 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
            {isDownloadingAll ? (
              <div className="w-full space-y-3">
                <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-300"
                    style={{ width: `${downloadProgress}%` }}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    Downloading... {downloadProgress}%
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={cancelDownload}
                    className="h-8 gap-1 text-muted-foreground hover:text-red-400"
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