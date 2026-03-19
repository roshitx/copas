import { test, expect } from '@playwright/test'
import * as path from 'path'

const KNOWN_ERROR_CLASSES = new Set([
  'UNSUPPORTED_PLATFORM',
  'ACCESS_DENIED',
  'EXTRACTION_FAILED',
  'UNKNOWN_ERROR',
])

const SCREENSHOTS_DIR = 'test-results/live-smoke'

const CANONICAL_URLS = [
  {
    label: 'facebook-watch',
    url: 'https://www.facebook.com/watch/?v=10153728912901749',
  },
  {
    label: 'facebook-videos',
    url: 'https://www.facebook.com/facebook/videos/-enjoy-a-variety-of-video-content-all-in-one-place-with-facebooks-updated-full-s/1626418958299031/',
  },
  {
    label: 'facebook-fb-watch',
    url: 'https://fb.watch/9B_Bu_lk76/',
  },
] as const

type ExtractResponseLog = {
  status: number
  code: string | null
  message: string | null
  url: string
}

function normalizeKnownErrorClass(
  extractLog: ExtractResponseLog | undefined,
  uiErrorMessage: string,
): string | null {
  if (extractLog?.code) return extractLog.code

  if (extractLog && extractLog.status >= 400) return 'UNKNOWN_ERROR'

  if (uiErrorMessage.toLowerCase().includes('request failed with status')) {
    return 'UNKNOWN_ERROR'
  }

  return null
}

function extractKnownErrorCode(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') return null

  const root = payload as { error?: unknown; detail?: unknown }
  if (typeof root.error === 'string') return root.error

  if (root.detail && typeof root.detail === 'object') {
    const detail = root.detail as { error?: unknown }
    if (typeof detail.error === 'string') return detail.error
  }

  return null
}

function extractKnownErrorMessage(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') return null

  const root = payload as { message?: unknown; detail?: unknown }
  if (typeof root.message === 'string') return root.message

  if (root.detail && typeof root.detail === 'object') {
    const detail = root.detail as { message?: unknown }
    if (typeof detail.message === 'string') return detail.message
  }

  return null
}

test.describe.configure({
  timeout: 90_000,
  retries: 2,
})

test.describe('@live Facebook Live Smoke Tests', () => {
  for (const scenario of CANONICAL_URLS) {
    test(`${scenario.label} @live`, async ({ page }, testInfo) => {
      const consoleLogs: string[] = []
      const failedRequests: string[] = []
      const extractResponses: ExtractResponseLog[] = []

      page.on('console', (msg) => {
        consoleLogs.push(`[${msg.type()}] ${msg.text()}`)
      })

      page.on('requestfailed', (request) => {
        const failure = request.failure()
        const reason = failure?.errorText ?? 'unknown'
        failedRequests.push(`${request.method()} ${request.url()} :: ${reason}`)
      })

      page.on('response', async (response) => {
        const request = response.request()
        if (!response.url().includes('/api/extract') || request.method() !== 'POST') {
          return
        }

        let payload: unknown = null
        try {
          payload = await response.json()
        } catch {
          payload = null
        }

        extractResponses.push({
          status: response.status(),
          code: extractKnownErrorCode(payload),
          message: extractKnownErrorMessage(payload),
          url: response.url(),
        })
      })

      await page.goto('/')
      const urlInput = page.locator('input[placeholder*="link"]')
      await expect(urlInput).toBeVisible({ timeout: 10_000 })

      await urlInput.fill(scenario.url)
      await page.locator('button[type="submit"]').click()

      const resultCard = page.getByTestId('result-card')
      const errorText = page.locator('p.text-red-400').first()

      const outcome = await Promise.race([
        resultCard
          .waitFor({ state: 'visible', timeout: 45_000 })
          .then(() => 'success' as const),
        errorText
          .waitFor({ state: 'visible', timeout: 45_000 })
          .then(() => 'controlled_failure' as const),
      ])

      if (outcome === 'success') {
        const formatButtons = page.getByTestId('format-button')
        await expect(formatButtons.first()).toBeVisible({ timeout: 10_000 })
      } else {
        await expect(errorText).toBeVisible({ timeout: 10_000 })
        await expect(errorText).not.toHaveText(/^\s*$/)

        const uiErrorMessage = (await errorText.textContent())?.trim() ?? ''
        const latestExtract = extractResponses.at(-1)
        const normalizedErrorClass = normalizeKnownErrorClass(latestExtract, uiErrorMessage)

        if (latestExtract) {
          expect(latestExtract.status).toBeGreaterThanOrEqual(400)
        }

        expect(
          normalizedErrorClass,
          `unable to classify controlled failure. ui="${uiErrorMessage}" extractCode="${latestExtract?.code ?? 'null'}"`,
        ).not.toBeNull()
        expect(
          KNOWN_ERROR_CLASSES.has(normalizedErrorClass ?? ''),
          `unexpected backend error class: ${normalizedErrorClass ?? 'null'}`,
        ).toBe(true)
      }

      const screenshotPath = testInfo.outputPath(`${scenario.label}-${Date.now()}.png`)
      await page.screenshot({
        path: screenshotPath,
        fullPage: true,
      })

      await testInfo.attach('extract-response-log', {
        body: Buffer.from(JSON.stringify(extractResponses, null, 2), 'utf-8'),
        contentType: 'application/json',
      })

      await testInfo.attach('browser-console-log', {
        body: Buffer.from(consoleLogs.join('\n') || '(empty)', 'utf-8'),
        contentType: 'text/plain',
      })

      await testInfo.attach('failed-request-log', {
        body: Buffer.from(failedRequests.join('\n') || '(empty)', 'utf-8'),
        contentType: 'text/plain',
      })

      await testInfo.attach('smoke-screenshot', {
        path: screenshotPath,
        contentType: 'image/png',
      })

      await page.screenshot({
        path: path.join(SCREENSHOTS_DIR, `${scenario.label}-${Date.now()}.png`),
        fullPage: true,
      })
    })
  }
})
