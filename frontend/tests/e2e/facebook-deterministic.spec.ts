import { test, expect, type Page } from '@playwright/test'
import { readFileSync } from 'fs'
import { join } from 'path'
import { mockExtractApi, mockDownloadApi } from './helpers/mock-api'
import { waitForResultCard, assertFormatButtonCount, assertMediaTypeBadges, submitUrl } from './helpers/assertions'

const BACKEND_URL = 'http://localhost:8000'
const FACEBOOK_FIXTURES_DIR = join(__dirname, '..', 'fixtures', 'facebook')

type FacebookSuccessFixture = {
  input_url: string
  expected_frontend_state: {
    title: string
    formats: Array<{ label: string }>
  }
}

type FacebookOutOfScopeFixture = {
  input_url: string
  expected_error_state: {
    error_code: string
    message: string
  }
}

function loadFacebookFixture<T>(filename: string): T {
  const content = readFileSync(join(FACEBOOK_FIXTURES_DIR, filename), 'utf-8')
  return JSON.parse(content) as T
}

const singleVideoFixture = loadFacebookFixture<FacebookSuccessFixture>('single-video-watch.json')
const singleImageFixture = loadFacebookFixture<FacebookSuccessFixture>('single-image-public.json')
const fallbackDeliveredFixture = loadFacebookFixture<FacebookSuccessFixture>('single-video-fb-watch.json')
const outOfScopeFixture = loadFacebookFixture<FacebookOutOfScopeFixture>('out-of-scope-share-v.json')

async function setupPage(browser: any): Promise<Page> {
  const page = await browser.newPage()
  await page.goto('/')
  await page.waitForSelector('input[placeholder*="Tempel"]', { timeout: 30_000 })
  return page
}

test.describe('Facebook Deterministic Scenario', () => {
  let page: Page

  test.afterEach(async () => {
    if (page && !page.isClosed()) {
      await page.close()
    }
  })

  test('single video success scenario (fixture): result card, VIDEO badge, download button visible', async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: singleVideoFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'facebook_watch_video_copas_io.mp4' })

    await submitUrl(page, singleVideoFixture.input_url)
    await waitForResultCard(page)

    await expect(page.getByText(singleVideoFixture.expected_frontend_state.title)).toBeVisible()
    await assertFormatButtonCount(page, 1)
    await assertMediaTypeBadges(page, ['VIDEO'])
    await expect(page.getByTestId('format-button').first()).toBeVisible()
  })

  test('single image success scenario (fixture): result card, IMAGE badge, download button visible', async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: singleImageFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'facebook_single_image_copas_io.jpg' })

    await submitUrl(page, singleImageFixture.input_url)
    await waitForResultCard(page)

    await expect(page.getByText(singleImageFixture.expected_frontend_state.title)).toBeVisible()
    await assertFormatButtonCount(page, 1)
    await assertMediaTypeBadges(page, ['IMAGE'])
    await expect(page.getByTestId('format-button').first()).toBeVisible()
  })

  test('out-of-scope error handling (share/v URL): shows error banner and hides result card', async ({ browser }) => {
    page = await setupPage(browser)

    await page.route(`${BACKEND_URL}/api/extract`, async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: outOfScopeFixture.expected_error_state.error_code,
          message: outOfScopeFixture.expected_error_state.message,
        }),
      })
    })

    await submitUrl(page, outOfScopeFixture.input_url)

    const errorBanner = page.locator('p.text-red-400').first()
    await expect(errorBanner).toBeVisible()
    await expect(errorBanner).toContainText(outOfScopeFixture.expected_error_state.message)
    await expect(page.getByTestId('result-card')).not.toBeVisible()
    await expect(page.getByTestId('format-button')).toHaveCount(0)
  })

  test('fallback-delivered format display: shows expected format label and download CTA', async ({ browser }) => {
    page = await setupPage(browser)
    mockExtractApi({ page, fixtureData: fallbackDeliveredFixture.expected_frontend_state })
    mockDownloadApi({ page, filename: 'facebook_fb_watch_fallback_copas_io.mp4' })

    await submitUrl(page, fallbackDeliveredFixture.input_url)
    await waitForResultCard(page)

    await assertFormatButtonCount(page, 1)
    await assertMediaTypeBadges(page, ['VIDEO'])
    await expect(page.getByText(fallbackDeliveredFixture.expected_frontend_state.formats[0].label)).toBeVisible()
    await expect(page.getByTestId('format-button').first()).toBeVisible()
  })
})
