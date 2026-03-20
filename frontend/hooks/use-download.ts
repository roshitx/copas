'use client'

import { useCallback, useRef, useState } from 'react'
import { useDownloadStore } from '@/store/download-store'
import { useHistoryStore } from '@/store/history-store'
import {
  extractMedia,
  triggerBrowserDownload,
  toBackendUrl,
  validateDownloadToken,
  ApiClientError,
} from '@/lib/api'
import { detectPlatform, isValidUrl } from '@/lib/platform-detector'
import type { Format, MediaResult } from '@/types'

function buildFilename(
  platform: string,
  author: string | null | undefined,
  index: number,
  ext: string
): string {
  const sanitize = (s: string) => s.replace(/[^a-zA-Z0-9_-]/g, '_').toLowerCase()
  const parts = [sanitize(platform)]
  if (author) parts.push(sanitize(author))
  parts.push('copas_io')
  if (index > 0) parts.push(String(index))
  return `${parts.join('_')}.${ext}`
}

function resolveFormatUrl(format: Format): string {
  return format.download_url.startsWith('/api/')
    ? toBackendUrl(format.download_url)
    : format.download_url
}

function getTokenFromDownloadUrl(downloadUrl: string): string | null {
  const query = downloadUrl.split('?')[1]
  if (!query) return null

  const token = new URLSearchParams(query).get('token')
  return token && token.length > 0 ? token : null
}

function findMatchingFormat(formats: Format[], target: Format): Format | null {
  return (
    formats.find((candidate) => candidate.id === target.id && candidate.type === target.type) ??
    formats.find((candidate) => candidate.label === target.label && candidate.type === target.type) ??
    null
  )
}

function getExt(format: Format): string {
  if (format.type.includes('audio')) return 'mp3'
  if (format.type.includes('image')) return 'jpg'
  return 'mp4'
}

export function useDownload() {
  const store = useDownloadStore()
  const addEntry = useHistoryStore((s) => s.addEntry)
  const [isDownloadingAll, setIsDownloadingAll] = useState(false)
  const abortControllerRef = useRef<AbortController | null>(null)

  const processUrl = useCallback(async (url: string) => {
    if (!isValidUrl(url)) {
      store.setError('URL tidak valid. Pastikan URL lengkap dengan http:// atau https://')
      return
    }

    const platform = detectPlatform(url)
    store.setUrl(url)
    store.setPlatform(platform)
    store.setStatus('loading')

    try {
      const result = await extractMedia({ url })
      store.setResult(result)
      addEntry({
        url,
        platform,
        title: result.title,
        thumbnail: result.thumbnail,
      })
    } catch (err) {
      if (err instanceof ApiClientError) {
        store.setError(err.message, err.code)
      } else if (err instanceof DOMException && err.name === 'AbortError') {
        store.setError('Request timeout. Coba lagi nanti.')
      } else {
        store.setError('Gagal memproses URL. Coba lagi nanti.')
      }
    }
  }, [store])


  const downloadFormat = useCallback(async (
    format: Format,
    result?: Pick<MediaResult, 'platform' | 'author'>,
    index = 0
  ) => {
    const ext = getExt(format)
    const filename = buildFilename(
      result?.platform ?? 'copas',
      result?.author,
      index,
      ext
    )

    try {
      let selectedFormat = format

      if (format.download_url.startsWith('/api/')) {
        const token = getTokenFromDownloadUrl(format.download_url)

        if (!token) {
          throw new Error('Token download tidak ditemukan. Silakan proses ulang URL.')
        }

        try {
          await validateDownloadToken(token)
        } catch (err) {
          if (!(err instanceof ApiClientError) || err.status !== 410) {
            throw err
          }

          if (!store.url) {
            throw new Error('URL sumber tidak tersedia. Silakan tempel ulang link.')
          }

          const refreshedResult = await extractMedia({ url: store.url })
          store.setResult(refreshedResult)

          const refreshedFormat = findMatchingFormat(refreshedResult.formats, format)

          if (!refreshedFormat) {
            throw new Error('Format berubah. Pilih ulang format download.')
          }

          selectedFormat = refreshedFormat
        }
      }

      const url = resolveFormatUrl(selectedFormat)
      triggerBrowserDownload(url, filename)
      import('@/lib/confetti').then((m) => m.fireConfetti())
    } catch (err) {
      store.setDownloadStatus('error')

      if (err instanceof ApiClientError) {
        console.error('Download validation failed:', err)
        return
      }

      if (err instanceof Error) {
        console.error('Download failed:', err.message)
        return
      }

      console.error('Download failed with unknown error:', err)
    }
  }, [store])

  const cancelDownload = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    store.setDownloadStatus('idle')
    store.setDownloadProgress(0)
    store.setDownloadETA(null)
    setIsDownloadingAll(false)
  }, [store])

  const downloadAllAsZip = useCallback(async (
    formats: Format[],
    result: Pick<MediaResult, 'platform' | 'author' | 'title'>
  ) => {
    if (formats.length === 0) return

    // Reset previous download state
    abortControllerRef.current?.abort()
    abortControllerRef.current = new AbortController()
    const abortController = abortControllerRef.current

    setIsDownloadingAll(true)
    store.setDownloadStatus('downloading')
    store.setDownloadProgress(0)
    store.setDownloadETA(null)

    const startTime = Date.now()
    let completedCount = 0

    try {
      const JSZip = (await import('jszip')).default
      const zip = new JSZip()
      const folderName = buildFilename(result.platform, result.author, 0, 'zip').replace('.zip', '')
      const folder = zip.folder(folderName)!

      // Fetch files sequentially to track progress
      for (let i = 0; i < formats.length; i++) {
        // Check if cancelled
        if (abortController.signal.aborted) {
          throw new DOMException('Download cancelled', 'AbortError')
        }

        const format = formats[i]
        const url = resolveFormatUrl(format)
        const ext = getExt(format)
        const filename = buildFilename(result.platform, result.author, i + 1, ext)

        // Fetch with abort signal
        const response = await fetch(url, { signal: abortController.signal })
        if (!response.ok) throw new Error(`Failed to fetch ${filename}`)

        const blob = await response.blob()
        folder.file(filename, blob)

        // Update progress
        completedCount++
        const progress = (completedCount / formats.length) * 100
        store.setDownloadProgress(progress)

        // Calculate ETA based on average time per file
        const elapsedTime = Date.now() - startTime
        const avgTimePerFile = elapsedTime / completedCount
        const remainingFiles = formats.length - completedCount
        const remainingTimeMs = avgTimePerFile * remainingFiles

        if (remainingFiles > 0) {
          const remainingSeconds = Math.ceil(remainingTimeMs / 1000)
          if (remainingSeconds < 60) {
            store.setDownloadETA(`${remainingSeconds} detik`)
          } else {
            const minutes = Math.ceil(remainingSeconds / 60)
            store.setDownloadETA(`${minutes} menit`)
          }
        } else {
          store.setDownloadETA(null)
        }
      }

      // Check if cancelled before generating ZIP
      if (abortController.signal.aborted) {
        throw new DOMException('Download cancelled', 'AbortError')
      }

      store.setDownloadProgress(100)
      store.setDownloadStatus('complete')

      const zipBlob = await zip.generateAsync({
        type: 'blob',
        compression: 'DEFLATE',
        compressionOptions: { level: 6 },
      })

      const zipFilename = `${folderName}.zip`
      triggerBrowserDownload(URL.createObjectURL(zipBlob), zipFilename)
      import('@/lib/confetti').then((m) => m.fireConfetti())
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        // Download was cancelled - don't show error
        console.log('Download cancelled by user')
      } else {
        console.error('ZIP download failed:', err)
        store.setDownloadStatus('error')
      }
    } finally {
      abortControllerRef.current = null
      setIsDownloadingAll(false)
    }
  }, [store])

  const reset = useCallback(() => {
    cancelDownload()
    store.reset()
  }, [cancelDownload, store])

  return {
    url: store.url,
    platform: store.platform,
    status: store.status,
    result: store.result,
    error: store.error,
    errorCode: store.errorCode,
    downloadProgress: store.downloadProgress,
    downloadStatus: store.downloadStatus,
    downloadETA: store.downloadETA,
    isDownloadingAll,
    processUrl,
    downloadFormat,
    downloadAllAsZip,
    cancelDownload,
    reset,
  }
}
