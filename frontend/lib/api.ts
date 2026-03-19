import type { ExtractRequest, MediaResult, ApiError } from '@/types'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000'

class ApiClientError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly status?: number,
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorBody: ApiError | null = null
    let detailBody: ApiError | null = null
    try {
      const parsed = await res.json()
      if (parsed && typeof parsed === 'object') {
        const topLevel = parsed as Partial<ApiError>
        const detail = (parsed as { detail?: unknown }).detail
        if (topLevel.error || topLevel.message) {
          errorBody = {
            error: topLevel.error ?? 'UNKNOWN_ERROR',
            message: topLevel.message ?? '',
          }
        }
        if (detail && typeof detail === 'object') {
          const d = detail as Partial<ApiError>
          if (d.error || d.message) {
            detailBody = {
              error: d.error ?? 'UNKNOWN_ERROR',
              message: d.message ?? '',
            }
          }
        }
      }
    } catch {
      // Non-JSON error body
    }

    const resolvedError = detailBody?.error ?? errorBody?.error ?? 'UNKNOWN_ERROR'
    const resolvedMessage =
      detailBody?.message ??
      errorBody?.message ??
      `Request failed with status ${res.status}`

    throw new ApiClientError(
      resolvedError,
      resolvedMessage,
      res.status,
    )
  }
  return res.json() as Promise<T>
}

export async function extractMedia(request: ExtractRequest): Promise<MediaResult> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 30_000)

  try {
    const res = await fetch(`${BACKEND_URL}/api/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal,
    })
    return handleResponse<MediaResult>(res)
  } finally {
    clearTimeout(timeoutId)
  }
}

export function toBackendUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }

  return `${BACKEND_URL}${path}`
}

export function getDownloadUrl(token: string): string {
  return toBackendUrl(`/api/download?token=${encodeURIComponent(token)}`)
}

export async function validateDownloadToken(token: string): Promise<void> {
  const res = await fetch(
    toBackendUrl(`/api/download/validate?token=${encodeURIComponent(token)}`),
    { method: 'GET' }
  )

  await handleResponse<{ valid: boolean }>(res)
}

export function triggerBrowserDownload(downloadUrl: string, filename?: string): void {
  const a = document.createElement('a')
  a.href = downloadUrl
  if (filename) a.download = filename
  a.target = '_blank'
  a.rel = 'noopener noreferrer'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export { ApiClientError }
