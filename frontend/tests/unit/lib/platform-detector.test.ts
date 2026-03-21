import { describe, it, expect } from 'vitest'
import { detectPlatform, isValidUrl } from '@/lib/platform-detector'

describe('detectPlatform', () => {
  describe('TikTok', () => {
    it.each([
      'https://www.tiktok.com/@username/video/1234567890',
      'https://vm.tiktok.com/ZMabc123',
      'https://vt.tiktok.com/ZMabc123',
      'https://www.tiktok.com/t/ZTRabc123',
    ])('detects %s as tiktok', (url) => {
      expect(detectPlatform(url)).toBe('tiktok')
    })
  })

  describe('Instagram', () => {
    it.each([
      'https://www.instagram.com/p/ABC123def/',
      'https://www.instagram.com/reel/ABC123def/',
      'https://www.instagram.com/tv/ABC123def/',
      'https://www.instagram.com/stories/username/1234567890/',
      'https://instagr.am/p/ABC123def/',
    ])('detects %s as instagram', (url) => {
      expect(detectPlatform(url)).toBe('instagram')
    })
  })

  describe('YouTube', () => {
    it.each([
      'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      'https://youtu.be/dQw4w9WgXcQ',
      'https://www.youtube.com/shorts/dQw4w9WgXcQ',
      'https://music.youtube.com/watch?v=dQw4w9WgXcQ',
      'https://www.youtube.com/live/dQw4w9WgXcQ',
    ])('detects %s as youtube', (url) => {
      expect(detectPlatform(url)).toBe('youtube')
    })
  })

  describe('Twitter / X', () => {
    it.each([
      'https://twitter.com/user/status/1234567890',
      'https://x.com/user/status/1234567890',
      'https://t.co/AbCdEfGh',
    ])('detects %s as twitter', (url) => {
      expect(detectPlatform(url)).toBe('twitter')
    })
  })

  describe('Facebook', () => {
    it.each([
      'https://www.facebook.com/watch/?v=1234567890',
      'https://www.facebook.com/username/videos/1234567890',
      'https://www.facebook.com/reel/1234567890',
      'https://fb.watch/AbCdEfGh/',
      'https://www.facebook.com/share/v/AbCdEfGh',
    ])('detects %s as facebook', (url) => {
      expect(detectPlatform(url)).toBe('facebook')
    })
  })

  describe('Threads', () => {
    it.each([
      'https://www.threads.net/@username/post/AbCdEfGh',
      'https://www.threads.net/t/AbCdEfGh',
      'https://threads.com/@username/post/AbCdEfGh',
      'https://threads.com/t/AbCdEfGh',
    ])('detects %s as threads', (url) => {
      expect(detectPlatform(url)).toBe('threads')
    })
  })

  describe('unknown / edge cases', () => {
    it('returns unknown for unrecognized URL', () => {
      expect(detectPlatform('https://example.com/video/123')).toBe('unknown')
    })

    it('returns unknown for non-URL string', () => {
      expect(detectPlatform('not a url')).toBe('unknown')
    })

    it('returns unknown for empty string', () => {
      expect(detectPlatform('')).toBe('unknown')
    })

    it('is case-insensitive for TikTok', () => {
      expect(detectPlatform('HTTPS://WWW.TIKTOK.COM/@USER/VIDEO/123')).toBe('tiktok')
    })

    it('hostname fallback: bare tiktok.com URL', () => {
      expect(detectPlatform('https://tiktok.com')).toBe('tiktok')
    })

    it('hostname fallback: bare youtube.com URL', () => {
      expect(detectPlatform('https://youtube.com')).toBe('youtube')
    })

    it('hostname fallback: youtu.be without path', () => {
      expect(detectPlatform('https://youtu.be')).toBe('youtube')
    })
  })
})

describe('isValidUrl', () => {
  it('returns true for http URL', () => {
    expect(isValidUrl('http://example.com')).toBe(true)
  })

  it('returns true for https URL', () => {
    expect(isValidUrl('https://example.com/path')).toBe(true)
  })

  it('returns false for URL with no protocol', () => {
    expect(isValidUrl('example.com')).toBe(false)
  })

  it('returns false for plain text', () => {
    expect(isValidUrl('not a url at all')).toBe(false)
  })

  it('returns false for empty string', () => {
    expect(isValidUrl('')).toBe(false)
  })

  it('returns false for ftp:// URL', () => {
    expect(isValidUrl('ftp://example.com')).toBe(false)
  })

  it('strips leading/trailing whitespace', () => {
    expect(isValidUrl('  https://example.com  ')).toBe(true)
  })
})
