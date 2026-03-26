import { test, expect } from '@playwright/test'
import * as path from 'path'

/**
 * YouTube Live Smoke Tests (@live)
 *
 * These tests make REAL network calls to YouTube and the backend.
 * They are tagged with @live to allow separate execution:
 *   - Run live tests: npx playwright test --grep @live
 *   - Skip live tests: npx playwright test --grep-invert @live
 *
 * URLs sourced from docs/source-test-plan.md
 */

const SCREENSHOTS_DIR = 'test-results/live-smoke'

const CANONICAL_URLS = {
  video: 'https://youtu.be/Q1I0ny09g5A',
}

test.describe.configure({
  timeout: 60_000,
  retries: 2,
})

test.describe('@live YouTube Live Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('input[placeholder*="Tempel"]')).toBeVisible({
      timeout: 10_000,
    })
  })

  test('Standard video @live', async ({ page }) => {
    await page.locator('input[placeholder*="Tempel"]').fill(CANONICAL_URLS.video)
    await page.locator('button:has-text("Copas!")').click()

    const resultCard = page.locator('[data-testid="result-card"]')
    await expect(resultCard).toBeVisible({ timeout: 30_000 })

    const formatButtons = page.getByTestId('format-button')
    const count = await formatButtons.count()
    expect(count).toBeGreaterThanOrEqual(1)

    await page.screenshot({
      path: path.join(SCREENSHOTS_DIR, `youtube-video-${Date.now()}.png`),
    })
  })
})
