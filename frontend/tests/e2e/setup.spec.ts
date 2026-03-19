import { test, expect } from '@playwright/test'

test('setup verification', async ({ page }) => {
  await page.goto('/')
  expect(true).toBe(true)
})
