import { test, expect, type Page } from '@playwright/test'
import { mockExtractApi, mockDownloadApi } from './helpers/mock-api'
import {
  waitForResultCard,
  assertMediaTypeBadges,
} from './helpers/assertions'
import { readFileSync } from 'fs'
import { join } from 'path'

const FIXTURES_DIR = join(__dirname, '..', 'fixtures', 'youtube')

function loadFixture(filename: string) {
  return JSON.parse(readFileSync(join(FIXTURES_DIR, filename), 'utf-8'))
}

const videoFixture = loadFixture('video.json')
const shortsFixture = loadFixture('shorts.json')

async function setupPage(browser: any): Promise<Page> {
  const page = await browser.newPage()
  await page.goto('/')
  await page.waitForSelector('input[placeholder*="Tempel"]', { timeout: 30_000 })
  return page
}

async function submitUrl(page: Page, url: string): Promise<void> {
  const urlInput = page.locator('input[placeholder*="Tempel"]')
  await urlInput.fill(url)
  await page.locator('button:has-text("Copas!")').click()
}

// ============================================================================
// 1) YouTube Standard Video
// ============================================================================

test.describe('YouTube Standard Video Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: videoFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'youtube_test_copas_io.mp4' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, videoFixture.input_url)
    await waitForResultCard(page)
    await expect(page.getByTestId('result-card')).toBeVisible()
  })

  test('happy path: shows format buttons with VIDEO badge', async () => {
    await submitUrl(page, videoFixture.input_url)
    await waitForResultCard(page)
    await assertMediaTypeBadges(page, ['VIDEO'])
  })

  test('happy path: shows multiple quality options', async () => {
    await submitUrl(page, videoFixture.input_url)
    await waitForResultCard(page)
    const buttons = page.getByTestId('format-button')
    const count = await buttons.count()
    expect(count).toBeGreaterThanOrEqual(1)
  })

  test('happy path: no "Download Semua" button for video-only', async () => {
    await submitUrl(page, videoFixture.input_url)
    await waitForResultCard(page)
    await expect(page.getByTestId('download-all-button')).not.toBeVisible()
  })

  test('happy path: format button is clickable', async () => {
    await submitUrl(page, videoFixture.input_url)
    await waitForResultCard(page)
    const formatButton = page.getByTestId('format-button').first()
    await expect(formatButton).toBeVisible()
    await expect(formatButton).toBeEnabled()
  })

  test('happy path: thumbnail visible in result card', async () => {
    await submitUrl(page, videoFixture.input_url)
    const resultCard = await waitForResultCard(page)
    await expect(resultCard.locator('img').first()).toBeVisible()
  })
})

// ============================================================================
// 2) YouTube Shorts
// ============================================================================

test.describe('YouTube Shorts Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: shortsFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'youtube_shorts_copas_io.mp4' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, shortsFixture.input_url)
    await waitForResultCard(page)
    await expect(page.getByTestId('result-card')).toBeVisible()
  })

  test('happy path: shows VIDEO badge', async () => {
    await submitUrl(page, shortsFixture.input_url)
    await waitForResultCard(page)
    await assertMediaTypeBadges(page, ['VIDEO'])
  })

  test('happy path: format button is clickable', async () => {
    await submitUrl(page, shortsFixture.input_url)
    await waitForResultCard(page)
    const formatButton = page.getByTestId('format-button').first()
    await expect(formatButton).toBeVisible()
    await expect(formatButton).toBeEnabled()
  })

  test('happy path: no "Download Semua" button for single video', async () => {
    await submitUrl(page, shortsFixture.input_url)
    await waitForResultCard(page)
    await expect(page.getByTestId('download-all-button')).not.toBeVisible()
  })
})

// ============================================================================
// Network Guard
// ============================================================================

test.describe('YouTube Network Guard', () => {
  test('no outbound calls to youtube.com or youtu.be from frontend', async ({ browser }) => {
    const page = await setupPage(browser)
    const forbiddenUrls: string[] = []
    const forbiddenPatterns = [/youtube\.com/, /youtu\.be/, /googlevideo\.com/]
    const trackedTypes = new Set(['fetch', 'xhr'])

    page.on('request', (request) => {
      const url = request.url()
      const type = request.resourceType()
      if (!trackedTypes.has(type)) return
      for (const pattern of forbiddenPatterns) {
        if (pattern.test(url)) forbiddenUrls.push(url)
      }
    })

    mockExtractApi({ page, fixtureData: videoFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'youtube_test.mp4' })

    await submitUrl(page, videoFixture.input_url)
    await waitForResultCard(page)
    await page.waitForTimeout(1000)

    expect(forbiddenUrls).toHaveLength(0)
    await page.close()
  })
})
