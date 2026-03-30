import { test, expect, type Page } from '@playwright/test'
import { mockExtractApi, mockDownloadApi, createDownloadInterceptor } from './helpers/mock-api'
import {
  waitForResultCard,
  assertFormatButtonCount,
  assertMediaTypeBadges,
  assertDownloadAllButtonVisible,
  assertVideoAccordionGroups,
  assertHybridSections,
  assertVideoSectionVisible,
  assertImageSectionVisible,
  assertFormatListVisible,
  assertAccordionContainerVisible,
  createNetworkInterceptor,
} from './helpers/assertions'
import {
  singleImageFixture,
  singleVideoFixture,
  multiVideoFixture,
  multiImageFixture,
  hybridFixture,
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
// Single Image Scenario
// ============================================================================

test.describe('Twitter Single Image Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: singleImageFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'twitter_rwhendry_copas_io.jpg' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    const networkInterceptor = createNetworkInterceptor(page)
    await submitUrl(page, singleImageFixture.input_url)
    const resultCard = await waitForResultCard(page)
    await expect(page.getByText(singleImageFixture.expected_frontend_state.title)).toBeVisible()
    const thumbnail = resultCard.locator('img').first()
    await expect(thumbnail).toBeVisible()
    networkInterceptor.assertNoForbiddenCalls()
  })

  test('happy path: shows 1 format button with IMAGE badge', async () => {
    await submitUrl(page, singleImageFixture.input_url)
    await waitForResultCard(page)
    await assertFormatButtonCount(page, 1)
    await assertMediaTypeBadges(page, ['IMAGE'])
    await expect(page.getByText('Foto')).toBeVisible()
  })

  test('happy path: no Download Semua button for single image', async () => {
    await submitUrl(page, singleImageFixture.input_url)
    await waitForResultCard(page)
    const downloadAllButton = page.getByTestId('download-all-button')
    await expect(downloadAllButton).not.toBeVisible()
  })

  test('happy path: no video section for image-only content', async () => {
    await submitUrl(page, singleImageFixture.input_url)
    await waitForResultCard(page)
    const videoSection = page.getByTestId('video-section')
    await expect(videoSection).not.toBeVisible()
    await assertFormatListVisible(page)
  })
})

// ============================================================================
// Single Video Scenario
// ============================================================================

test.describe('Twitter Single Video Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: singleVideoFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'twitter_sosmedkeras_copas_io.mp4' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, singleVideoFixture.input_url)
    const resultCard = await waitForResultCard(page)
    await expect(page.getByText(singleVideoFixture.expected_frontend_state.title)).toBeVisible()
  })

  test('happy path: shows format button with VIDEO badge', async () => {
    await submitUrl(page, singleVideoFixture.input_url)
    await waitForResultCard(page)
    await assertFormatButtonCount(page, singleVideoFixture.expected_frontend_state.formats.length)
    await assertMediaTypeBadges(page, ['VIDEO'])
    await expect(page.getByText('Video 720p')).toBeVisible()
  })

  test('happy path: shows duration badge', async () => {
    await submitUrl(page, singleVideoFixture.input_url)
    await waitForResultCard(page)
    const duration = page.locator('text=/0:30|30/')
    await expect(duration).toBeVisible()
  })

  test('happy path: no image section for video-only content', async () => {
    await submitUrl(page, singleVideoFixture.input_url)
    await waitForResultCard(page)
    const imageSection = page.getByTestId('image-section')
    await expect(imageSection).not.toBeVisible()
  })
})

// ============================================================================
// Multi Video Scenario (2 videos)
// ============================================================================

test.describe('Twitter Multi Video (2 videos) Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: multiVideoFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'twitter_mikuroQ_copas_io.zip' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, multiVideoFixture.input_url)
    const resultCard = await waitForResultCard(page)
    await expect(page.getByText(multiVideoFixture.expected_frontend_state.title)).toBeVisible()
    const thumbnails = resultCard.locator('img')
    await expect(thumbnails).toHaveCount(2)
  })

  test('happy path: shows 2 media badge', async () => {
    await submitUrl(page, multiVideoFixture.input_url)
    await waitForResultCard(page)
    const mediaBadge = page.getByText('2 media')
    await expect(mediaBadge).toBeVisible()
  })

  test('happy path: shows two accordion video groups', async () => {
    await submitUrl(page, multiVideoFixture.input_url)
    await waitForResultCard(page)
    await assertAccordionContainerVisible(page)
    await assertVideoAccordionGroups(page, 2)
    await assertVideoSectionVisible(page)
  })

  test('happy path: shows correct format labels for each video', async () => {
    await submitUrl(page, multiVideoFixture.input_url)
    await waitForResultCard(page)
    // video-section and video-group are both open by default
    const videoGroups = page.getByTestId('video-group')
    await expect(videoGroups.nth(0).getByTestId('format-button').first()).toBeVisible()
    await expect(videoGroups.nth(1).getByTestId('format-button').first()).toBeVisible()
  })


  test('happy path: each video group has VIDEO badge', async () => {
    await submitUrl(page, multiVideoFixture.input_url)
    await waitForResultCard(page)
    // video-section and video-group are both open by default
    await assertMediaTypeBadges(page, ['VIDEO'])
  })
})

// ============================================================================
// Multi Image Scenario (2 photos)
// ============================================================================

test.describe('Twitter Multi Image (2 photos) Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: multiImageFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'twitter_IndonesiaGaruda_copas_io.zip' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, multiImageFixture.input_url)
    const resultCard = await waitForResultCard(page)
    await expect(page.getByText(multiImageFixture.expected_frontend_state.title)).toBeVisible()
    const thumbnails = resultCard.locator('img')
    await expect(thumbnails).toHaveCount(2)
  })

  test('happy path: shows 2 media badge', async () => {
    await submitUrl(page, multiImageFixture.input_url)
    await waitForResultCard(page)
    const mediaBadge = page.getByText('2 media')
    await expect(mediaBadge).toBeVisible()
  })

  test('happy path: shows 2 image format buttons with IMAGE badges', async () => {
    await submitUrl(page, multiImageFixture.input_url)
    await waitForResultCard(page)
    // Expand image section
    const imageSection = page.getByTestId('image-section')
    const summary = imageSection.locator('summary').first()
    await summary.click()
    await page.waitForTimeout(200)
    await assertFormatButtonCount(page, 2)
    await assertMediaTypeBadges(page, ['IMAGE'])
    await expect(page.getByText('Foto 1')).toBeVisible()
    await expect(page.getByText('Foto 2')).toBeVisible()
  })

  test('happy path: shows Download Semua Foto button', async () => {
    await submitUrl(page, multiImageFixture.input_url)
    await waitForResultCard(page)
    // Expand image section
    const imageSection = page.getByTestId('image-section')
    const summary = imageSection.locator('summary').first()
    await summary.click()
    await page.waitForTimeout(200)
    await assertDownloadAllButtonVisible(page)
  })

  test('happy path: clicking Download Semua triggers ZIP download', async () => {
    await submitUrl(page, multiImageFixture.input_url)
    await waitForResultCard(page)
    // Expand image section
    const imageSection = page.getByTestId('image-section')
    const summary = imageSection.locator('summary').first()
    await summary.click()
    await page.waitForTimeout(300)
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 10_000 }),
      page.getByTestId('download-all-button').click(),
    ])
    const filename = download.suggestedFilename()
    expect(filename).toMatch(/\.zip$/)
    expect(filename).toContain('twitter')
  })

  test('happy path: ZIP download has correct entry count', async () => {
    await submitUrl(page, multiImageFixture.input_url)
    await waitForResultCard(page)
    let downloadUrls: string[] = []
    await page.route(`${BACKEND_URL}/api/download**`, async (route, request) => {
      downloadUrls.push(request.url())
      await route.fulfill({
        status: 200,
        headers: {
          'Content-Type': 'application/octet-stream',
          'Content-Disposition': 'attachment; filename="image.jpg"',
        },
        body: Buffer.alloc(100, 0),
      })
    })
    // Expand image section
    const imageSection = page.getByTestId('image-section')
    const summary = imageSection.locator('summary').first()
    await summary.click()
    await page.waitForTimeout(300)
    await page.getByTestId('download-all-button').click()
    await page.waitForTimeout(2000)
    expect(downloadUrls.length).toBe(2)
    expect(downloadUrls[0]).toContain('mock_token_multi_image_1')
    expect(downloadUrls[1]).toContain('mock_token_multi_image_2')
  })

  test('happy path: no video section for image-only content', async () => {
    await submitUrl(page, multiImageFixture.input_url)
    await waitForResultCard(page)
    await assertImageSectionVisible(page)
    const videoSection = page.getByTestId('video-section')
    await expect(videoSection).not.toBeVisible()
  })
})

// ============================================================================
// Hybrid Video + Image Scenario
// ============================================================================

test.describe('Twitter Hybrid Video + Image Scenario', () => {
  let page: Page

  test.beforeEach(async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: hybridFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'twitter_Villgecrazylady_copas_io.zip' })
  })

  test.afterEach(async () => {
    await page.close()
  })

  test('happy path: extracts and shows result card', async () => {
    await submitUrl(page, hybridFixture.input_url)
    const resultCard = await waitForResultCard(page)
    await expect(page.getByText(hybridFixture.expected_frontend_state.title)).toBeVisible()
    const thumbnails = resultCard.locator('img')
    await expect(thumbnails).toHaveCount(2)
  })

  test('happy path: shows 2 media badge', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    const mediaBadge = page.getByText('2 media')
    await expect(mediaBadge).toBeVisible()
  })

  test('happy path: both video AND image sections are visible', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    await assertHybridSections(page)
    await assertAccordionContainerVisible(page)
  })

  test('happy path: at least 1 video format + at least 1 image format button', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    // Expand both sections
    const videoSection = page.getByTestId('video-section')
    const videoSummary = videoSection.locator('summary').first()
    await videoSummary.click()
    const imageSection = page.getByTestId('image-section')
    const imageSummary = imageSection.locator('summary').first()
    await imageSummary.click()
    await page.waitForTimeout(300)
    await assertFormatButtonCount(page, hybridFixture.expected_frontend_state.formats.length)
  })

  test('happy path: shows duration badge for video', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    const duration = page.locator('text=/0:25|25/')
    await expect(duration).toBeVisible()
  })

  test('happy path: shows correct format labels', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    // video-section is already open by default — just open nested video-groups
    const videoGroups = page.getByTestId('video-group')
    const vgCount = await videoGroups.count()
    for (let i = 0; i < vgCount; i++) {
      await videoGroups.nth(i).locator('summary').click()
      await page.waitForTimeout(150)
    }
    await page.waitForTimeout(200)
    await expect(page.getByTestId('format-button').filter({ hasText: 'Video 1' }).first()).toBeVisible()
    // Expand image section (closed by default)
    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(200)
    await expect(page.getByTestId('format-button').filter({ hasText: 'Foto' }).first()).toBeVisible()
  })

  test('happy path: image section handles single image correctly', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    // Expand image section
    const imageSection = page.getByTestId('image-section')
    const summary = imageSection.locator('summary').first()
    await summary.click()
    await page.waitForTimeout(300)
    const downloadAllButton = page.getByTestId('download-all-button')
    const imageFormats = hybridFixture.expected_frontend_state.formats.filter(
      (f) => f.type.toLowerCase().includes('image')
    )
    if (imageFormats.length > 1) {
      await expect(downloadAllButton).toBeVisible()
    } else {
      await expect(downloadAllButton).not.toBeVisible()
    }
  })

  test('happy path: can download video format', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    // Hybrid: 1 video + 1 image. Video renders directly in video-section (not video-group)
    const videoSection = page.getByTestId('video-section')
    const videoFormatButton = videoSection.getByTestId('format-button').first()
    await expect(videoFormatButton).toBeVisible({ timeout: 8_000 })
    await expect(videoFormatButton).toBeEnabled()
  })
  test('happy path: can download image format', async () => {
    await submitUrl(page, hybridFixture.input_url)
    await waitForResultCard(page)
    const imageSection = page.getByTestId('image-section')
    await imageSection.locator('summary').first().click()
    await page.waitForTimeout(300)
    const imageFormatButton = imageSection.getByTestId('format-button').first()
    await expect(imageFormatButton).toBeVisible()
    await expect(imageFormatButton).toBeEnabled()
  })
  })


// ============================================================================
// Cross-Scenario Edge Cases
// ============================================================================

test.describe('Cross-Scenario Edge Cases', () => {
  test('no external network calls are made to Twitter/X domains', async ({ browser }) => {
    const page = await setupPage(browser)
    const networkInterceptor = createNetworkInterceptor(page)
    mockExtractApi({ page, fixtureData: singleImageFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'test.jpg' })
    await submitUrl(page, singleImageFixture.input_url)
    await waitForResultCard(page)
    await page.waitForTimeout(1000)
    networkInterceptor.assertNoForbiddenCalls()
    await page.close()
  })
})
