import { Page, Route } from '@playwright/test'

export interface MockExtractOptions {
  page: Page
  fixtureData: any
  delay?: number
}

export interface MockDownloadOptions {
  page: Page
  filename?: string
  contentType?: string
  delay?: number
}

const BACKEND_URL = 'http://localhost:8000'

/**
 * Transform fixture format (camelCase) to API format (snake_case).
 */
function transformFormat(fixtureFormat: {
  id: string
  label: string
  type: string
  sizeMb: number | null
  downloadUrl: string
}): any {
  return {
    id: fixtureFormat.id,
    label: fixtureFormat.label,
    type: fixtureFormat.type,
    size_mb: fixtureFormat.sizeMb,
    download_url: fixtureFormat.downloadUrl,
  }
}

/**
 * Transform fixture data to API response format.
 */
function transformFixture(fixture: {
  expected_frontend_state: {
    platform: string
    author: string
    title: string
    formats: Array<{
      id: string
      label: string
      type: string
      sizeMb: number | null
      downloadUrl: string
    }>
    thumbnail: string | null
    thumbnails: string[]
    duration: number | null
  }
}): any {
  return {
    platform: fixture.expected_frontend_state.platform,
    author: fixture.expected_frontend_state.author,
    title: fixture.expected_frontend_state.title,
    thumbnail: fixture.expected_frontend_state.thumbnail,
    thumbnails: fixture.expected_frontend_state.thumbnails,
    duration: fixture.expected_frontend_state.duration,
    formats: fixture.expected_frontend_state.formats.map(transformFormat),
  }
}

export function mockExtractApi(options: MockExtractOptions): void {
  const { page, fixtureData, delay = 0 } = options

  page.route(`${BACKEND_URL}/api/extract`, async (route: Route) => {
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay))
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(transformFixture({ expected_frontend_state: fixtureData }))
    })
  })
}

export function mockDownloadApi(options: MockDownloadOptions): void {
  const { page, filename = 'download.bin', contentType = 'application/octet-stream', delay = 0 } = options

  page.route(`${BACKEND_URL}/api/download**`, async (route: Route, request) => {
    if (delay > 0) {
      await new Promise(resolve => setTimeout(resolve, delay))
    }

    const fakeBlob = Buffer.alloc(100, 0)

    await route.fulfill({
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Content-Length': '100'
      },
      body: fakeBlob
    })
  })
}

export function createDownloadInterceptor(page: Page): {
  wasCalled: () => boolean
  getToken: () => string | null
  reset: () => void
} {
  let called = false
  let capturedToken: string | null = null

  page.route(`${BACKEND_URL}/api/download**`, async (route: Route, request) => {
    called = true
    const url = request.url()
    const tokenMatch = url.match(/[?&]token=([^&]+)/)
    capturedToken = tokenMatch ? tokenMatch[1] : null

    await route.fulfill({
      status: 200,
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="download.bin"`,
        'Content-Length': '100'
      },
      body: Buffer.alloc(100, 0)
    })
  })

  return {
    wasCalled: () => called,
    getToken: () => capturedToken,
    reset: () => {
      called = false
      capturedToken = null
    }
  }
}

/**
 * Mock all external calls to ensure ZERO network calls to:
 * - X.com / Twitter
 * - fxtwitter / vxtwitter
 * - yt-dlp
 * - Any other external services
 */
export function mockAllExternalCalls(page: Page): void {
  page.route('**/*', async (route: Route, request) => {
    const url = request.url()

    // Allow frontend requests
    if (url.startsWith('http://localhost:3000')) {
      route.continue()
      return
    }

    // Block Twitter/X domains
    if (url.includes('x.com') || url.includes('twitter.com')) {
      await route.abort('blockedbyclient')
      return
    }

    // Block fxtwitter/vxtwitter
    if (url.includes('fxtwitter') || url.includes('vxtwitter')) {
      await route.abort('blockedbyclient')
      return
    }

    // Block yt-dlp related calls
    if (url.includes('yt-dlp') || url.includes('youtube.com') || url.includes('youtu.be')) {
      await route.abort('blockedbyclient')
      return
    }

    // Stub Twitter CDN images
    if (url.includes('pbs.twimg.com')) {
      await route.fulfill({
        status: 200,
        contentType: 'image/jpeg',
        body: Buffer.alloc(100, 0)
      })
      return
    }

    // Allow backend API (should be mocked by specific mock functions)
    if (url.startsWith(BACKEND_URL)) {
      route.continue()
      return
    }

    // Block everything else
    await route.abort('blockedbyclient')
  })
}
