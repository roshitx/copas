'use client'

import { useState } from 'react'
import { Film, ImageIcon, Music, ChevronDown, Download } from 'lucide-react'
import type { MediaResult } from '@/types'
import { FormatButton } from '@/components/format-button'
import { DownloadProgress } from '@/components/download-progress'
import { useDownload } from '@/hooks/use-download'
import { groupVideoFormats, categorizeFormats } from '@/lib/format-utils'

type FilterTab = 'all' | 'video' | 'image' | 'audio'

interface FormatListProps {
  result: MediaResult
}

export function FormatList({ result }: FormatListProps) {
  const [activeTab, setActiveTab] = useState<FilterTab>('all')
  const {
    downloadAllAsZip,
    isDownloadingAll,
    downloadProgress,
    downloadStatus,
    downloadETA,
    cancelDownload,
  } = useDownload()

  const { videoFormats, imageFormats, audioFormats } = categorizeFormats(result.formats)
  const videoGroups = groupVideoFormats(videoFormats)
  const isMultiVideo = videoGroups.length > 1

  const typeCategoryCount = [videoFormats.length > 0, imageFormats.length > 0, audioFormats.length > 0].filter(Boolean).length
  const showAccordion = isMultiVideo || typeCategoryCount > 1 || imageFormats.length > 1

  const handleDownloadAll = () => downloadAllAsZip(imageFormats, result)

  const availableTabs: { key: FilterTab; label: string; count: number }[] = [
    { key: 'all', label: 'Semua', count: result.formats.length },
    ...(videoFormats.length > 0 ? [{ key: 'video' as FilterTab, label: 'Video', count: videoFormats.length }] : []),
    ...(imageFormats.length > 0 ? [{ key: 'image' as FilterTab, label: 'Foto', count: imageFormats.length }] : []),
    ...(audioFormats.length > 0 ? [{ key: 'audio' as FilterTab, label: 'Audio', count: audioFormats.length }] : []),
  ]

  const showTabs = typeCategoryCount > 1

  const filteredFormats = activeTab === 'all'
    ? result.formats
    : activeTab === 'video'
      ? videoFormats
      : activeTab === 'image'
        ? imageFormats
        : audioFormats

  return (
    <div>
      <div className="text-[11px] font-bold uppercase tracking-widest text-amber-500/80 mb-3">
        Pilih Format
      </div>

      {showTabs && (
        <div className="flex gap-1 mb-3 p-1 bg-zinc-900/60 rounded-lg">
          {availableTabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`flex-1 px-2 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeTab === tab.key
                  ? 'bg-zinc-800 text-zinc-100'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {tab.label} ({tab.count})
            </button>
          ))}
        </div>
      )}

      {activeTab !== 'all' || !showAccordion ? (
        <div data-testid="format-list" className="space-y-2">
          {activeTab === 'image' && imageFormats.length > 1 && (
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

          {activeTab === 'all' && imageFormats.length > 1 && (
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

          {filteredFormats.map((format) => (
            <FormatButton key={format.id || format.label + '-' + format.type} format={format} result={result} disabled={isDownloadingAll} />
          ))}
        </div>
      ) : (
        <div className="border border-zinc-800 rounded-xl overflow-hidden divide-y divide-zinc-800">
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
                  <div className="space-y-2">
                    {videoFormats.map((format) => (
                      <FormatButton key={format.id || format.label + '-' + format.type} format={format} result={result} disabled={isDownloadingAll} />
                    ))}
                  </div>
                )}
              </div>
            </details>
          )}

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
  )
}
