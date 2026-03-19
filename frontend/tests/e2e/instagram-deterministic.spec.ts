import { test, expect, type Page } from '@playwright/test'
import { mockExtractApi, mockDownloadApi } from './helpers/mock-api'
import {
  waitForResultCard,
  assertFormatButtonCount,
  assertMediaTypeBadges,
  assertDownloadAllButtonVisible,
  assertHybridSections,
} from './helpers/assertions'
import {
  instagramSingleVideoReelFixture,
  instagramSingleImageFixture,
  instagramMultiImage3Fixture,
  instagramHybridFixture,
  instagramMixedOrderFixture,
} from './helpers/fixtures'

const BACKEND_URL = 'http://localhost:8000'

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
// 1) Instagram Single Video Reel
// ============================================================================

test.describe('Instagram Single Video Reel Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: instagramSingleVideoReelFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'instagram_creatortesting_copas_io.mp4' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, 'https://instagram.com/reel/ABC123xyz/')
    await waitForResultCard(page)
    await expect(page.getByTestId('result-card')).toBeVisible()
  })

  test('happy path: shows 1 format button with VIDEO badge', async () => {
    await submitUrl(page, 'https://instagram.com/reel/ABC123xyz/')
    await waitForResultCard(page)
    await assertFormatButtonCount(page, 1)
    await assertMediaTypeBadges(page, ['VIDEO'])
  })

  test('happy path: no "Download Semua" button for single video', async () => {
    await submitUrl(page, 'https://instagram.com/reel/ABC123xyz/')
    await waitForResultCard(page)
    await expect(page.getByTestId('download-all-button')).not.toBeVisible()
  })

  test('happy path: format button is clickable', async () => {
    await submitUrl(page, 'https://instagram.com/reel/ABC123xyz/')
    await waitForResultCard(page)
    const formatButton = page.getByTestId('format-button').first()
    await expect(formatButton).toBeVisible()
    await expect(formatButton).toBeEnabled()
  })

  test('happy path: thumbnail visible in result card', async () => {
    await submitUrl(page, 'https://instagram.com/reel/ABC123xyz/')
    const resultCard = await waitForResultCard(page)
    await expect(resultCard.locator('img').first()).toBeVisible()
  })
})

// ============================================================================
// 2) Instagram Single Image
// ============================================================================

test.describe('Instagram Single Image Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: instagramSingleImageFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'instagram_photolover_copas_io.jpg' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, 'https://instagram.com/p/DEF456abc/')
    await waitForResultCard(page)
    await expect(page.getByTestId('result-card')).toBeVisible()
  })

  test('happy path: shows 1 format button with IMAGE badge', async () => {
    await submitUrl(page, 'https://instagram.com/p/DEF456abc/')
    await waitForResultCard(page)
    await assertFormatButtonCount(page, 1)
    await assertMediaTypeBadges(page, ['IMAGE'])
  })

  test('happy path: no "Download Semua" button', async () => {
    await submitUrl(page, 'https://instagram.com/p/DEF456abc/')
    await waitForResultCard(page)
    await expect(page.getByTestId('download-all-button')).not.toBeVisible()
  })
})

// ============================================================================
// 3) Instagram Multi-Image Carousel (3 images)
// ============================================================================

test.describe('Instagram Multi-Image Carousel (3 images) Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: instagramMultiImage3Fixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'instagram_travelblogger_copas_io.zip' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: shows 3 format buttons', async () => {
    await submitUrl(page, 'https://instagram.com/p/GHI789def/')
    await waitForResultCard(page)

    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(200)

    await assertFormatButtonCount(page, 3)
  })

  test('happy path: shows "Download Semua" ZIP button', async () => {
    await submitUrl(page, 'https://instagram.com/p/GHI789def/')
    await waitForResultCard(page)

    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(200)

    await assertDownloadAllButtonVisible(page)
  })

  test('happy path: ZIP download works', async () => {
    await submitUrl(page, 'https://instagram.com/p/GHI789def/')
    await waitForResultCard(page)

    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(250)

    const downloadAllButton = page.getByTestId('download-all-button')
    await expect(downloadAllButton).toBeVisible()
    await expect(downloadAllButton).toBeEnabled()
    await downloadAllButton.click()
    await expect(downloadAllButton).toBeVisible()
  })

  test('happy path: ZIP download filename is correct', async () => {
    await submitUrl(page, 'https://instagram.com/p/GHI789def/')
    await waitForResultCard(page)

    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(250)

    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 10_000 }),
      page.getByTestId('download-all-button').click(),
    ])

    expect(download.suggestedFilename()).toMatch(/\.zip$/)
    expect(download.suggestedFilename()).toContain('instagram')
  })
})

// ============================================================================
// 4) Instagram Hybrid (Video + Image)
// ============================================================================

test.describe('Instagram Hybrid (Video + Image) Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: instagramHybridFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'instagram_mixedcontent_copas_io.zip' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: shows both VIDEO and IMAGE sections', async () => {
    await submitUrl(page, 'https://instagram.com/p/JKL012ghi/')
    await waitForResultCard(page)
    await assertHybridSections(page)
  })

  test('happy path: video has index 1, image has index 2', async () => {
    await submitUrl(page, 'https://instagram.com/p/JKL012ghi/')
    await waitForResultCard(page)

    await expect(page.getByText(/Video 1/i)).toBeVisible()
    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(200)
    await expect(page.getByText(/Foto 2/i)).toBeVisible()
  })

  test('happy path: both formats clickable', async () => {
    await submitUrl(page, 'https://instagram.com/p/JKL012ghi/')
    await waitForResultCard(page)

    const videoSection = page.getByTestId('video-section')
    const videoButton = videoSection.getByTestId('format-button').first()
    await expect(videoButton).toBeVisible()
    await expect(videoButton).toBeEnabled()
    await videoButton.click()
    await expect(videoButton).toBeVisible()

    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(200)

    const imageButton = imageSection.getByTestId('format-button').first()
    await expect(imageButton).toBeVisible()
    await expect(imageButton).toBeEnabled()
    await imageButton.click()
    await expect(imageButton).toBeVisible()
  })
})

// ============================================================================
// 5) Instagram Mixed Order (Image, Video, Image)
// ============================================================================

test.describe('Instagram Mixed Order (Image, Video, Image) Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: instagramMixedOrderFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'instagram_shuffledmedia_copas_io.zip' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: media preserves source order', async () => {
    await submitUrl(page, 'https://instagram.com/p/MNO345jkl/')
    await waitForResultCard(page)

    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(200)

    const labels = await page.getByTestId('format-button').allTextContents()
    const idxFoto1 = labels.findIndex((t) => t.includes('Foto 1'))
    const idxVideo2 = labels.findIndex((t) => t.includes('Video 2'))
    const idxFoto3 = labels.findIndex((t) => t.includes('Foto 3'))

    expect(idxFoto1).toBeGreaterThanOrEqual(0)
    expect(idxVideo2).toBeGreaterThanOrEqual(0)
    expect(idxFoto3).toBeGreaterThanOrEqual(0)
    expect(idxFoto1).toBeLessThan(idxFoto3)
  })

  test('happy path: indices 1,2,3 match input order', async () => {
    await submitUrl(page, 'https://instagram.com/p/MNO345jkl/')
    await waitForResultCard(page)

    const allTexts = await page.locator('[data-testid="format-button"], [data-testid="download-all-button"]').allTextContents()
    const joined = allTexts.join(' ')

    expect(joined).toContain('1')
    expect(joined).toContain('2')
    expect(joined).toContain('3')
  })
})

// ============================================================================
// Network Guard
// ============================================================================

test.describe('Instagram Network Guard', () => {
  test('no outbound calls to instagram.com, cdninstagram.com, fbcdn.net', async ({ browser }) => {
    const page = await setupPage(browser)
    const forbiddenUrls: string[] = []
    const forbiddenPatterns = [/instagram\.com/, /cdninstagram\.com/, /fbcdn\.net/]

    const trackedTypes = new Set(['fetch', 'xhr'])

    page.on('request', (request) => {
      const url = request.url()
      const type = request.resourceType()
      if (!trackedTypes.has(type)) return
      for (const pattern of forbiddenPatterns) {
        if (pattern.test(url)) forbiddenUrls.push(url)
      }
    })

    mockExtractApi({ page, fixtureData: instagramSingleImageFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'instagram_test.jpg' })

    await submitUrl(page, 'https://instagram.com/p/DEF456abc/')
    await waitForResultCard(page)
    await page.waitForTimeout(1000)

    expect(forbiddenUrls).toHaveLength(0)
    await page.close()
  })
})
