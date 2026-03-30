import { Page, Locator, expect } from '@playwright/test'
import type { MediaResult } from '@/types'

/**
 * Wait for the result card to be rendered.
 */
export async function waitForResultCard(page: Page): Promise<Locator> {
  const resultCard = page.getByTestId('result-card')
  await expect(resultCard).toBeVisible({ timeout: 10000 })
  return resultCard
}

/**
 * Assert that the correct number of format buttons are visible.
 */
export async function assertFormatButtonCount(page: Page, expectedCount: number): Promise<void> {
  const buttons = page.getByTestId('format-button')
  await expect(buttons).toHaveCount(expectedCount)
}

/**
 * Assert that media type badges are present with correct labels.
 * Checks for VIDEO, IMAGE, and AUDIO badges.
 */
export async function assertMediaTypeBadges(
  page: Page,
  expectedTypes: Array<'VIDEO' | 'IMAGE' | 'AUDIO'>
): Promise<void> {
  for (const type of expectedTypes) {
    // Badge is inside the format button, look for the uppercase label
    const badge = page.locator('span').filter({ hasText: new RegExp(`^${type}$`) })
    await expect(badge.first()).toBeVisible()
  }
}

/**
 * Assert that the "Download Semua" button is visible.
 */
export async function assertDownloadAllButtonVisible(page: Page): Promise<void> {
  const downloadAllButton = page.getByTestId('download-all-button')
  await expect(downloadAllButton).toBeVisible()
}

/**
 * Assert that accordion groups are visible for multi-video content.
 */
export async function assertVideoAccordionGroups(
  page: Page,
  expectedGroupCount: number
): Promise<void> {
  const videoSection = page.getByTestId('video-section')
  await expect(videoSection).toBeVisible()
  
  // Check for video groups (nested details elements)
  const videoGroups = page.getByTestId('video-group')
  await expect(videoGroups).toHaveCount(expectedGroupCount)
}

/**
 * Assert that both video and image sections are present (hybrid content).
 */
export async function assertHybridSections(page: Page): Promise<void> {
  const videoSection = page.getByTestId('video-section')
  const imageSection = page.getByTestId('image-section')
  
  await expect(videoSection).toBeVisible()
  await expect(imageSection).toBeVisible()
}

/**
 * Assert that the video section is visible.
 */
export async function assertVideoSectionVisible(page: Page): Promise<void> {
  const videoSection = page.getByTestId('video-section')
  await expect(videoSection).toBeVisible()
}

/**
 * Assert that the image section is visible.
 */
export async function assertImageSectionVisible(page: Page): Promise<void> {
  const imageSection = page.getByTestId('image-section')
  await expect(imageSection).toBeVisible()
}

/**
 * Assert that the audio section is visible.
 */
export async function assertAudioSectionVisible(page: Page): Promise<void> {
  const audioSection = page.getByTestId('audio-section')
  await expect(audioSection).toBeVisible()
}

/**
 * Assert that the flat format list is visible (non-accordion mode).
 */
export async function assertFormatListVisible(page: Page): Promise<void> {
  const formatList = page.getByTestId('format-list')
  await expect(formatList).toBeVisible()
}

/**
 * Assert that the accordion container is visible (accordion mode).
 */
export async function assertAccordionContainerVisible(page: Page): Promise<void> {
  const accordionContainer = page.locator('.divide-y.divide-border').first()
  await expect(accordionContainer).toBeVisible()
}

/**
 * Assert that the URL input is visible and ready for input.
 */
export async function assertUrlInputReady(page: Page): Promise<Locator> {
  // URL input is the text input with placeholder
  const urlInput = page.locator('input[type="text"][placeholder*="link"]')
  await expect(urlInput).toBeVisible()
  await expect(urlInput).toBeEnabled()
  return urlInput
}

/**
 * Type a URL into the input and submit the form.
 */
export async function submitUrl(page: Page, url: string): Promise<void> {
  const urlInput = await assertUrlInputReady(page)
  await urlInput.fill(url)
  
  // Click the submit button
  const submitButton = page.locator('button[type="submit"]')
  await submitButton.click()
}

/**
 * Comprehensive assertion for single image scenario.
 */
export async function assertSingleImageScenario(
  page: Page,
  mediaResult: MediaResult
): Promise<void> {
  await waitForResultCard(page)
  await assertFormatListVisible(page)
  await assertFormatButtonCount(page, mediaResult.formats.length)
  await assertMediaTypeBadges(page, ['IMAGE'])
  
  // Single image should not have download all button in flat view
  const downloadAllButton = page.getByTestId('download-all-button')
  await expect(downloadAllButton).not.toBeVisible()
}

/**
 * Comprehensive assertion for single video scenario.
 */
export async function assertSingleVideoScenario(
  page: Page,
  mediaResult: MediaResult
): Promise<void> {
  await waitForResultCard(page)
  await assertFormatListVisible(page)
  await assertFormatButtonCount(page, mediaResult.formats.length)
  await assertMediaTypeBadges(page, ['VIDEO'])
  
  // Single video should show video section in accordion
  await assertVideoSectionVisible(page)
}

/**
 * Comprehensive assertion for multi-video scenario.
 */
export async function assertMultiVideoScenario(
  page: Page,
  mediaResult: MediaResult,
  expectedVideoCount: number
): Promise<void> {
  await waitForResultCard(page)
  await assertAccordionContainerVisible(page)
  await assertVideoAccordionGroups(page, expectedVideoCount)
  await assertFormatButtonCount(page, mediaResult.formats.length)
  await assertMediaTypeBadges(page, ['VIDEO'])
}

/**
 * Comprehensive assertion for multi-image scenario.
 */
export async function assertMultiImageScenario(
  page: Page,
  mediaResult: MediaResult
): Promise<void> {
  await waitForResultCard(page)
  await assertImageSectionVisible(page)
  await assertDownloadAllButtonVisible(page)
  await assertFormatButtonCount(page, mediaResult.formats.length)
  await assertMediaTypeBadges(page, ['IMAGE'])
}

/**
 * Comprehensive assertion for hybrid (video + image) scenario.
 */
export async function assertHybridScenario(
  page: Page,
  mediaResult: MediaResult
): Promise<void> {
  await waitForResultCard(page)
  await assertAccordionContainerVisible(page)
  await assertHybridSections(page)
  await assertFormatButtonCount(page, mediaResult.formats.length)
  await assertMediaTypeBadges(page, ['VIDEO', 'IMAGE'])
  await assertDownloadAllButtonVisible(page)
}

/**
 * Verify that no external network calls are made to Twitter/X domains.
 * This is a safety check to ensure mocking is working.
 */
export function createNetworkInterceptor(page: Page): {
  forbiddenUrls: string[]
  clear: () => void
  assertNoForbiddenCalls: () => void
} {
  const forbiddenUrls: string[] = []
  const forbiddenPatterns = [
    /x\.com/,
    /twitter\.com/,
    /fxtwitter/,
    /vxtwitter/,
    /yt-dlp/,
  ]

  page.on('request', (request) => {
    const url = request.url()
    for (const pattern of forbiddenPatterns) {
      if (pattern.test(url)) {
        forbiddenUrls.push(url)
      }
    }
  })

  return {
    forbiddenUrls,
    clear: () => {
      forbiddenUrls.length = 0
    },
    assertNoForbiddenCalls: () => {
      if (forbiddenUrls.length > 0) {
        throw new Error(
          `Forbidden network calls detected: ${forbiddenUrls.join(', ')}`
        )
      }
    },
  }
}
