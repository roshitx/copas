import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ApiClientError, toBackendUrl, getDownloadUrl, triggerBrowserDownload } from '@/lib/api'

// handleResponse is not exported, so we test it via extractMedia with mocked fetch
const BACKEND_URL = 'http://localhost:8000'

describe('ApiClientError', () => {
  it('has correct name, code, message, status', () => {
    const err = new ApiClientError('EXTRACTION_FAILED', 'Extraction error', 422)
    expect(err.name).toBe('ApiClientError')
    expect(err.code).toBe('EXTRACTION_FAILED')
    expect(err.message).toBe('Extraction error')
    expect(err.status).toBe(422)
  })

  it('is instance of Error', () => {
    expect(new ApiClientError('CODE', 'msg')).toBeInstanceOf(Error)
  })

  it('status is optional', () => {
    const err = new ApiClientError('CODE', 'msg')
    expect(err.status).toBeUndefined()
  })
})

describe('toBackendUrl', () => {
  it('prepends backend URL for relative paths', () => {
    expect(toBackendUrl('/api/extract')).toBe(`${BACKEND_URL}/api/extract`)
  })

  it('returns absolute http URL unchanged', () => {
    expect(toBackendUrl('http://other.com/path')).toBe('http://other.com/path')
  })

  it('returns absolute https URL unchanged', () => {
    expect(toBackendUrl('https://cdn.example.com/file.mp4')).toBe('https://cdn.example.com/file.mp4')
  })
})

describe('getDownloadUrl', () => {
  it('builds URL with encoded token', () => {
    const url = getDownloadUrl('abc-123')
    expect(url).toContain('/api/download?token=abc-123')
    expect(url).toContain(BACKEND_URL)
  })

  it('URL-encodes special characters in token', () => {
    const url = getDownloadUrl('token with spaces')
    expect(url).toContain('token%20with%20spaces')
  })
})

describe('triggerBrowserDownload', () => {
  it('creates and clicks an anchor element', () => {
    const clickSpy = vi.fn()
    const appendSpy = vi.spyOn(document.body, 'appendChild').mockImplementation(() => document.createElement('a'))
    const removeSpy = vi.spyOn(document.body, 'removeChild').mockImplementation(() => document.createElement('a'))

    const mockAnchor = document.createElement('a')
    mockAnchor.click = clickSpy
    vi.spyOn(document, 'createElement').mockReturnValueOnce(mockAnchor)

    triggerBrowserDownload('https://example.com/file.mp4', 'video.mp4')

    expect(mockAnchor.href).toBe('https://example.com/file.mp4')
    expect(mockAnchor.download).toBe('video.mp4')
    expect(clickSpy).toHaveBeenCalledOnce()

    appendSpy.mockRestore()
    removeSpy.mockRestore()
  })
})

describe('extractMedia (handleResponse behavior)', () => {
  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('throws ApiClientError with detail.error on 422 response', async () => {
    const { extractMedia } = await import('@/lib/api')
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 422,
      json: async () => ({
        detail: { error: 'EXTRACTION_FAILED', message: 'Extraction failed' },
      }),
    } as Response)

    await expect(extractMedia({ url: 'https://tiktok.com/test' })).rejects.toMatchObject({
      code: 'EXTRACTION_FAILED',
      message: 'Extraction failed',
      status: 422,
    })
  })

  it('throws ApiClientError with top-level error when no detail', async () => {
    const { extractMedia } = await import('@/lib/api')
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ error: 'UNSUPPORTED_PLATFORM', message: 'Platform not supported' }),
    } as Response)

    await expect(extractMedia({ url: 'https://example.com' })).rejects.toMatchObject({
      code: 'UNSUPPORTED_PLATFORM',
      status: 400,
    })
  })

  it('throws ApiClientError with fallback message on non-JSON error body', async () => {
    const { extractMedia } = await import('@/lib/api')
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => { throw new SyntaxError('not json') },
    } as unknown as Response)

    await expect(extractMedia({ url: 'https://example.com' })).rejects.toMatchObject({
      code: 'UNKNOWN_ERROR',
      status: 500,
    })
  })

  it('returns parsed MediaResult on success', async () => {
    const { extractMedia } = await import('@/lib/api')
    const mockResult = {
      platform: 'tiktok',
      title: 'Test Video',
      thumbnail: null,
      thumbnails: [],
      author: 'user',
      duration: 30,
      formats: [{ id: '720p', label: 'HD', type: 'video/mp4', size_mb: 5.0, download_url: '/api/download?token=abc' }],
    }
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => mockResult,
    } as Response)

    const result = await extractMedia({ url: 'https://tiktok.com/test' })
    expect(result.platform).toBe('tiktok')
    expect(result.title).toBe('Test Video')
  })
})
