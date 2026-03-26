import { test, expect } from '@playwright/test'
import * as path from 'path'

/**
 * Instagram Live Smoke Tests (@live)
 *
 * These tests make REAL network calls to Instagram and the backend.
 * They are tagged with @live to allow separate execution:
 *   - Run live tests: npx playwright test --grep @live
 *   - Skip live tests: npx playwright test --grep-invert @live
 *
 * URLs sourced from docs/source-test-plan.md
 */

const SCREENSHOTS_DIR = 'test-results/live-smoke'

const CANONICAL_URLS = {
  photoOnly: 'https://www.instagram.com/p/DWJRVycEZu3/',
  videoReel: 'https://www.instagram.com/reel/DWJHJLYTN7d/',
  multiphoto: 'https://www.instagram.com/p/DWGlvZVkyh5/',
  multivideo: 'https://www.instagram.com/p/DVXiyNHE78b/',
}

test.describe.configure({
  timeout: 60_000,
  retries: 2,
})

test.describe('@live Instagram Live Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('input[placeholder*="Tempel"]')).toBeVisible({
      timeout: 10_000,
    })
  })

  test('Photo-only post @live', async ({ page }) => {
    await page.locator('input[placeholder*="Tempel"]').fill(CANONICAL_URLS.photoOnly)
    await page.locator('button:has-text("Copas!")').click()

    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    const formatButtons = page.getByTestId('format-button')
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `instagram-photo-only-${Date.now()}.png`),
    })
  })

  test('Video reel @live', async ({ page }) => {
    await page.locator('input[placeholder*="Tempel"]').fill(CANONICAL_URLS.videoReel)
    await page.locator('button:has-text("Copas!")').click()

    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    const formatButtons = page.getByTestId('format-button')
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `instagram-video-reel-${Date.now()}.png`),
    })
  })

  test('Multiphoto carousel @live', async ({ page }) => {
    await page.locator('input[placeholder*="Tempel"]').fill(CANONICAL_URLS.multiphoto)
    await page.locator('button:has-text("Copas!")').click()

    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    const formatButtons = page.getByTestId('format-button')
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `instagram-multiphoto-${Date.now()}.png`),
    })
  })

  test('Multivideo carousel @live', async ({ page }) => {
    await page.locator('input[placeholder*="Tempel"]').fill(CANONICAL_URLS.multivideo)
    await page.locator('button:has-text("Copas!")').click()

    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    const formatButtons = page.getByTestId('format-button')
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `instagram-multivideo-${Date.now()}.png`),
    })
  })
})
