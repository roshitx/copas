import { readFileSync } from 'fs'
import { join } from 'path'

const FIXTURES_ROOT_DIR = join(__dirname, '..', '..', 'fixtures')
const TWITTER_FIXTURES_DIR = join(FIXTURES_ROOT_DIR, 'twitter')
const INSTAGRAM_FIXTURES_DIR = join(FIXTURES_ROOT_DIR, 'instagram')

/**
 * Load a fixture file from a specific directory and return the parsed JSON.
 */
function loadFixtureFromDir(fixturesDir: string, filename: string): {
  input_url: string
  expected_frontend_state: {
    platform: string
    author: string
    title: string | null
    formats: Array<{
      id: string
      label: string
      type: string
      sizeMb: number | null
      downloadUrl: string
    }>
    thumbnail: string | null
    thumbnails: string[]
    duration: number | null
  }
} {
  const filepath = join(fixturesDir, filename)
  const content = readFileSync(filepath, 'utf-8')
  return JSON.parse(content)
}

export function loadFixture(filename: string) {
  return loadFixtureFromDir(TWITTER_FIXTURES_DIR, filename)
}

export function loadInstagramFixture(filename: string) {
  return loadFixtureFromDir(INSTAGRAM_FIXTURES_DIR, filename)
}

// Export Twitter fixtures
export const singleImageFixture = loadFixture('single-image.json')
export const singleVideoFixture = loadFixture('single-video.json')
export const multiVideoFixture = loadFixture('multi-video-2.json')
export const multiImageFixture = loadFixture('multi-image-2.json')
export const hybridFixture = loadFixture('hybrid-video-image.json')

// Export Instagram fixtures
export const instagramSingleVideoReelFixture = loadInstagramFixture('single-video-reel.json')
export const instagramSingleImageFixture = loadInstagramFixture('single-image.json')
export const instagramMultiImage3Fixture = loadInstagramFixture('multi-image-3.json')
export const instagramHybridFixture = loadInstagramFixture('hybrid-video-image.json')
export const instagramMixedOrderFixture = loadInstagramFixture('mixed-order.json')