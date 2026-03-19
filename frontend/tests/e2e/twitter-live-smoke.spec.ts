import { test, expect } from '@playwright/test'
import * as path from 'path'


/**
 * Twitter Live Smoke Tests (@live)
 *
 * These tests make REAL network calls to Twitter/X and the backend.
 * They are tagged with @live to allow separate execution:
 *   - Run live tests: npx playwright test --grep @live
 *   - Skip live tests: npx playwright test --grep-invert @live
 *
 * These tests verify end-to-end functionality with real upstream services.
 * They should be run on a schedule or manual dispatch, NOT on every PR.
 */

// Screenshots directory for failure artifacts (relative to frontend/)
const SCREENSHOTS_DIR = 'test-results/live-smoke'

// Canonical Twitter URLs for live testing (without query parameters)
const CANONICAL_URLS = {
  singleImage: 'https://x.com/rwhendry/status/2027767749695705372',
  singleVideo: 'https://x.com/sosmedkeras/status/2027955413753417803',
  multiVideo: 'https://x.com/mikuroQ/status/2027735620534358393',
  multiImage: 'https://x.com/IndonesiaGaruda/status/2027914018976108959',
  hybrid: 'https://x.com/Villgecrazylady/status/2027532953966825726',
}

// Test configuration for live network resilience
test.describe.configure({
  timeout: 60_000, // 60s per test (live network is slow)
  retries: 2, // 2 retries for flaky network
})

test.describe('@live Twitter Live Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to app
    await page.goto('/')

    // Wait for the main input to be visible
    await expect(page.locator('input[placeholder*="link"]')).toBeVisible({
      timeout: 10_000,
    })
  })

  test('Single image @live', async ({ page }) => {
    const url = CANONICAL_URLS.singleImage

    // Fill URL input
    await page.locator('input[placeholder*="link"]').fill(url)

    // Submit form
    await page.locator('button[type="submit"]').click()

    // Wait for result card to appear (up to 30s for live network)
    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    // Assert: at least 1 format button appears
    const formatButtons = page.locator('button').filter({ hasText: /DOWNLOAD/i })
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    // Capture screenshot for evidence
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `single-image-${Date.now()}.png`),
    })
  })

  test('Single video @live', async ({ page }) => {
    const url = CANONICAL_URLS.singleVideo

    // Fill URL input
    await page.locator('input[placeholder*="link"]').fill(url)

    // Submit form
    await page.locator('button[type="submit"]').click()

    // Wait for result card to appear
    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    // Assert: at least 1 format button appears
    const formatButtons = page.locator('button').filter({ hasText: /DOWNLOAD/i })
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    // Capture screenshot for evidence
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `single-video-${Date.now()}.png`),
    })
  })

  test('Multi-video @live', async ({ page }) => {
    const url = CANONICAL_URLS.multiVideo

    // Fill URL input
    await page.locator('input[placeholder*="link"]').fill(url)

    // Submit form
    await page.locator('button[type="submit"]').click()

    // Wait for result card to appear
    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    // Assert: at least 1 format button appears
    const formatButtons = page.locator('button').filter({ hasText: /DOWNLOAD/i })
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    // Capture screenshot for evidence
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `multi-video-${Date.now()}.png`),
    })
  })

  test('Multi-image @live', async ({ page }) => {
    const url = CANONICAL_URLS.multiImage

    // Fill URL input
    await page.locator('input[placeholder*="link"]').fill(url)

    // Submit form
    await page.locator('button[type="submit"]').click()

    // Wait for result card to appear
    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    // Assert: at least 1 format button appears
    const formatButtons = page.locator('button').filter({ hasText: /DOWNLOAD/i })
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    // Capture screenshot for evidence
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `multi-image-${Date.now()}.png`),
    })
  })

  test('Hybrid video+image @live', async ({ page }) => {
    const url = CANONICAL_URLS.hybrid

    // Fill URL input
    await page.locator('input[placeholder*="link"]').fill(url)

    // Submit form
    await page.locator('button[type="submit"]').click()

    // Wait for result card to appear
    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    // Assert: at least 1 format button appears
    const formatButtons = page.locator('button').filter({ hasText: /DOWNLOAD/i })
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    // Capture screenshot for evidence
    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `hybrid-${Date.now()}.png`),
    })
  })
})
