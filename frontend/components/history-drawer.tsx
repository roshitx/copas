'use client'

import Image from 'next/image'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { useHistoryStore } from '@/store/history-store'
import { PlatformIcon } from '@/components/platform-icon'
import { Clock, Trash2, ExternalLink } from 'lucide-react'

function formatRelativeTime(timestamp: number): string {
  const diff = Date.now() - timestamp
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'Baru saja'
  if (minutes < 60) return minutes + ' menit lalu'
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return hours + ' jam lalu'
  const days = Math.floor(hours / 24)
  return days + ' hari lalu'
}

interface HistoryDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSelect: (url: string) => void
}

export function HistoryDrawer({ open, onOpenChange, onSelect }: HistoryDrawerProps) {
  const entries = useHistoryStore((s) => s.entries)
  const clearAll = useHistoryStore((s) => s.clearAll)

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        className="h-[70vh] rounded-t-2xl border-t border-border bg-background px-0 text-foreground [&>button]:hidden"
      >
        <SheetHeader className="px-5 pt-4">
          <div className="flex items-center justify-between">
            <SheetTitle className="flex items-center gap-2 text-left text-lg font-semibold text-foreground">
              <Clock className="h-4 w-4 text-amber-500" />
              Riwayat Download
            </SheetTitle>
            {entries.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAll}
                className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-red-400"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Hapus Semua
              </Button>
            )}
          </div>
          <SheetDescription className="text-left text-sm text-muted-foreground">
            {entries.length > 0
              ? `${entries.length} item terakhir`
              : 'Belum ada riwayat download'}
          </SheetDescription>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto px-5 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
          {entries.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Clock className="mb-3 h-10 w-10 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Belum ada riwayat</p>
              <p className="mt-1 text-xs text-muted-foreground/70">
                Download media akan muncul di sini
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {entries.map((entry) => (
                <button
                  key={entry.url}
                  type="button"
                  onClick={() => onSelect(entry.url)}
                  className="group flex w-full items-center gap-3 rounded-xl border border-border/50 bg-card/50 p-3 text-left transition-colors hover:border-border hover:bg-secondary/50"
                >
                  {entry.thumbnail ? (
                    <Image
                      src={entry.thumbnail}
                      alt=""
                      width={48}
                      height={48}
                      className="h-12 w-12 shrink-0 rounded-lg object-cover"
                      unoptimized
                    />
                  ) : (
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-secondary">
                      <PlatformIcon platform={entry.platform} size={18} className="text-muted-foreground" useColor={false} />
                    </div>
                  )}

                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-foreground">
                      {entry.title || 'Untitled'}
                    </p>
                    <div className="mt-0.5 flex items-center gap-2">
                      <PlatformIcon platform={entry.platform} size={12} className="text-muted-foreground" useColor={false} />
                      <span className="text-xs text-muted-foreground">
                        {formatRelativeTime(entry.timestamp)}
                      </span>
                    </div>
                  </div>

                  <ExternalLink className="h-4 w-4 shrink-0 text-muted-foreground/60 transition-colors group-hover:text-muted-foreground" />
                </button>
              ))}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
