import type { Format } from '@/types'

export interface VideoGroup {
  label: string
  formats: Format[]
}

export function groupVideoFormats(videoFormats: Format[]): VideoGroup[] {
  const groups = new Map<string, VideoGroup>()
  for (const fmt of videoFormats) {
    const match = fmt.label.match(/^Video (\d+) ·/)
    if (match) {
      const key = match[1]
      if (!groups.has(key)) {
        groups.set(key, { label: 'Video ' + key, formats: [] })
      }
      groups.get(key)!.formats.push(fmt)
    } else {
      if (!groups.has('default')) {
        groups.set('default', { label: 'Video', formats: [] })
      }
      groups.get('default')!.formats.push(fmt)
    }
  }
  return Array.from(groups.values())
}

export function categorizeFormats(formats: Format[]) {
  const videoFormats = formats.filter(
    (f) => f.type.toLowerCase().includes('video') || f.type.toLowerCase().includes('mp4')
  )
  const imageFormats = formats.filter((f) => f.type.toLowerCase().includes('image'))
  const audioFormats = formats.filter((f) => f.type.toLowerCase().includes('audio'))

  return { videoFormats, imageFormats, audioFormats }
}
