import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useDownload } from '@/hooks/use-download'
import { useDownloadStore } from '@/store/download-store'
import { ApiClientError } from '@/lib/api'

vi.mock('jszip', () => ({
  default: class MockJSZip {
    folder() { return { file: vi.fn() } }
    async generateAsync() { return new Blob(['zip'], { type: 'application/zip' }) }
  },
}))

vi.mock('@/lib/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/api')>()
  return {
    ...actual,
    extractMedia: vi.fn(),
    triggerBrowserDownload: vi.fn(),
    validateDownloadToken: vi.fn(),
  }
})

vi.mock('@/lib/confetti', () => ({ fireConfetti: vi.fn() }))

vi.mock('@/store/history-store', () => ({
  useHistoryStore: vi.fn((selector: (s: { addEntry: ReturnType<typeof vi.fn> }) => unknown) =>
    selector({ addEntry: vi.fn() })
  ),
}))

const getApi = async () => {
  const mod = await import('@/lib/api')
  return {
    extractMedia: vi.mocked(mod.extractMedia),
    triggerBrowserDownload: vi.mocked(mod.triggerBrowserDownload),
    validateDownloadToken: vi.mocked(mod.validateDownloadToken),
  }
}

const mockMediaResult = {
  platform: 'tiktok' as const,
  title: 'Test Video',
  thumbnail: null,
  thumbnails: [],
  author: 'creator',
  duration: 30,
  formats: [
    {
      id: '720p',
      label: 'Video 720p',
      type: 'video/mp4',
      size_mb: 5.0,
      download_url: '/api/download?token=test-token-abc',
    },
  ],
}

const mockFormat = mockMediaResult.formats[0]

beforeEach(() => {
  useDownloadStore.getState().reset()
  vi.clearAllMocks()
})

describe('useDownload — processUrl', () => {
  it('sets error for invalid URL', async () => {
    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.processUrl('not-a-url')
    })

    expect(result.current.error).toContain('URL tidak valid')
    expect(result.current.status).toBe('error')
  })

  it('sets result on successful extraction', async () => {
    const api = await getApi()
    api.extractMedia.mockResolvedValueOnce(mockMediaResult)

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.processUrl('https://www.tiktok.com/@user/video/1234567890')
    })

    expect(result.current.status).toBe('success')
    expect(result.current.result?.title).toBe('Test Video')
    expect(result.current.platform).toBe('tiktok')
  })

  it('sets error with code on ApiClientError', async () => {
    const api = await getApi()
    api.extractMedia.mockRejectedValueOnce(
      new ApiClientError('EXTRACTION_FAILED', 'Gagal mengekstrak', 422)
    )

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.processUrl('https://www.tiktok.com/@user/video/1234567890')
    })

    expect(result.current.error).toBe('Gagal mengekstrak')
    expect(result.current.errorCode).toBe('EXTRACTION_FAILED')
    expect(result.current.status).toBe('error')
  })

  it('sets timeout message on AbortError', async () => {
    const api = await getApi()
    const abortError = new DOMException('The operation was aborted', 'AbortError')
    api.extractMedia.mockRejectedValueOnce(abortError)

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.processUrl('https://www.tiktok.com/@user/video/1234567890')
    })

    expect(result.current.error).toContain('timeout')
    expect(result.current.status).toBe('error')
  })

  it('sets generic error on unknown exception', async () => {
    const api = await getApi()
    api.extractMedia.mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.processUrl('https://www.tiktok.com/@user/video/1234567890')
    })

    expect(result.current.error).toContain('Gagal memproses')
    expect(result.current.status).toBe('error')
  })

  it('detects platform from URL before fetching', async () => {
    const api = await getApi()
    api.extractMedia.mockResolvedValueOnce(mockMediaResult)

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.processUrl('https://x.com/user/status/9876543210')
    })

    expect(result.current.platform).toBe('twitter')
  })
})

describe('useDownload — downloadFormat', () => {
  it('triggers download for non-api URL directly', async () => {
    const api = await getApi()

    const { result } = renderHook(() => useDownload())
    const directFormat = { ...mockFormat, download_url: 'https://cdn.example.com/file.mp4' }

    await act(async () => {
      await result.current.downloadFormat(directFormat, { platform: 'youtube', author: 'creator' })
    })

    expect(api.validateDownloadToken).not.toHaveBeenCalled()
    expect(api.triggerBrowserDownload).toHaveBeenCalledWith(
      'https://cdn.example.com/file.mp4',
      expect.stringContaining('youtube')
    )
  })

  it('validates token then downloads for /api/ URL', async () => {
    const api = await getApi()
    api.validateDownloadToken.mockResolvedValueOnce(undefined)

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.downloadFormat(mockFormat, { platform: 'tiktok', author: 'creator' })
    })

    expect(api.validateDownloadToken).toHaveBeenCalledWith('test-token-abc')
    expect(api.triggerBrowserDownload).toHaveBeenCalled()
  })

  it('refreshes extraction on expired token (410) then downloads', async () => {
    const api = await getApi()

    api.validateDownloadToken.mockRejectedValueOnce(
      new ApiClientError('TOKEN_EXPIRED', 'Token expired', 410)
    )
    const refreshedResult = {
      ...mockMediaResult,
      formats: [{ ...mockFormat, download_url: '/api/download?token=new-token-xyz' }],
    }
    api.extractMedia.mockResolvedValueOnce(refreshedResult)

    // Seed store url so refresh knows what to re-extract
    useDownloadStore.getState().setUrl('https://www.tiktok.com/@user/video/1234567890')

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.downloadFormat(mockFormat, { platform: 'tiktok', author: 'creator' })
    })

    expect(api.extractMedia).toHaveBeenCalledWith({
      url: 'https://www.tiktok.com/@user/video/1234567890',
    })
    expect(api.triggerBrowserDownload).toHaveBeenCalled()
  })

  it('sets error when token is missing from /api/ URL', async () => {
    const { result } = renderHook(() => useDownload())
    const noTokenFormat = { ...mockFormat, download_url: '/api/download?notoken=here' }

    await act(async () => {
      await result.current.downloadFormat(noTokenFormat, { platform: 'tiktok', author: null })
    })

    expect(result.current.error).toContain('Token download tidak ditemukan')
  })

  it('builds filename with platform and author', async () => {
    const api = await getApi()
    api.validateDownloadToken.mockResolvedValueOnce(undefined)

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.downloadFormat(mockFormat, { platform: 'instagram', author: 'my user' })
    })

    const [[, filename]] = vi.mocked(api.triggerBrowserDownload).mock.calls
    expect(filename).toMatch(/instagram/)
    expect(filename).toMatch(/my_user/)
    expect(filename).toMatch(/copas_io/)
    expect(filename).toMatch(/\.mp4$/)
  })

  it('uses mp3 extension for audio formats', async () => {
    const api = await getApi()
    api.validateDownloadToken.mockResolvedValueOnce(undefined)

    const audioFormat = { ...mockFormat, type: 'audio/mp4', download_url: '/api/download?token=audio-tok' }
    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.downloadFormat(audioFormat, { platform: 'youtube', author: null })
    })

    const [[, filename]] = vi.mocked(api.triggerBrowserDownload).mock.calls
    expect(filename).toMatch(/\.mp3$/)
  })
})

describe('useDownload — cancelDownload', () => {
  it('resets download status to idle', () => {
    const { result } = renderHook(() => useDownload())

    act(() => {
      useDownloadStore.getState().setDownloadStatus('downloading')
      result.current.cancelDownload()
    })

    expect(result.current.downloadStatus).toBe('idle')
    expect(result.current.downloadProgress).toBe(0)
    expect(result.current.isDownloadingAll).toBe(false)
  })
})

describe('useDownload — downloadAllAsZip', () => {
  const mockBlob = new Blob(['video'], { type: 'video/mp4' })

  beforeEach(() => {
    global.URL.createObjectURL = vi.fn().mockReturnValue('blob:mock')
  })

  it('does nothing when formats list is empty', async () => {
    const api = await getApi()
    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.downloadAllAsZip([], { platform: 'tiktok', author: null, title: 'Test' })
    })

    expect(api.triggerBrowserDownload).not.toHaveBeenCalled()
  })

  it('fetches each format, generates zip and triggers download', async () => {
    const api = await getApi()
    global.fetch = vi.fn()
      .mockResolvedValueOnce({ ok: true, blob: async () => mockBlob } as Response)
      .mockResolvedValueOnce({ ok: true, blob: async () => mockBlob } as Response)

    const twoFormats = [
      { ...mockFormat, id: '720p', download_url: 'https://cdn.example.com/1.mp4' },
      { ...mockFormat, id: '480p', download_url: 'https://cdn.example.com/2.mp4' },
    ]

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.downloadAllAsZip(twoFormats, { platform: 'instagram', author: 'user', title: 'Album' })
    })

    expect(global.fetch).toHaveBeenCalledTimes(2)
    expect(result.current.isDownloadingAll).toBe(false)
    expect(result.current.downloadStatus).toBe('complete')
    expect(api.triggerBrowserDownload).toHaveBeenCalledWith('blob:mock', expect.stringMatching(/\.zip$/))
  })

  it('sets downloadStatus to error when fetch fails', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({ ok: false } as Response)

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.downloadAllAsZip(
        [{ ...mockFormat, download_url: 'https://cdn.example.com/1.mp4' }],
        { platform: 'tiktok', author: null, title: 'Test' }
      )
    })

    expect(result.current.downloadStatus).toBe('error')
    expect(result.current.isDownloadingAll).toBe(false)
  })

  it('cancelDownload resets state during or after zip download', async () => {
    const { result } = renderHook(() => useDownload())

    // Simulate an in-progress download state
    act(() => {
      useDownloadStore.getState().setDownloadStatus('downloading')
      useDownloadStore.getState().setDownloadProgress(50)
    })

    act(() => { result.current.cancelDownload() })

    expect(result.current.downloadStatus).toBe('idle')
    expect(result.current.downloadProgress).toBe(0)
    expect(result.current.isDownloadingAll).toBe(false)
  })
})

describe('useDownload — reset', () => {
  it('resets all state', async () => {
    const api = await getApi()
    api.extractMedia.mockResolvedValueOnce(mockMediaResult)

    const { result } = renderHook(() => useDownload())

    await act(async () => {
      await result.current.processUrl('https://www.tiktok.com/@user/video/1234567890')
    })
    expect(result.current.result).not.toBeNull()

    act(() => { result.current.reset() })

    expect(result.current.result).toBeNull()
    expect(result.current.status).toBe('idle')
    expect(result.current.error).toBeNull()
  })
})
