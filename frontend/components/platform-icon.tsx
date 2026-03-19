'use client'
import type { Platform } from '@/types'

// Import specific icons from simple-icons
import {
  siTiktok,
  siInstagram,
  siYoutube,
  siX,
  siFacebook,
  siThreads,
} from 'simple-icons'

const PLATFORM_ICONS: Record<string, typeof siTiktok> = {
  tiktok: siTiktok,
  instagram: siInstagram,
  youtube: siYoutube,
  twitter: siX,      // X (formerly Twitter)
  facebook: siFacebook,
  threads: siThreads,
}

interface PlatformIconProps {
  platform: Platform
  size?: number
  useColor?: boolean  // use brand color vs white
  className?: string
}

export function PlatformIcon({ platform, size = 16, useColor = false, className }: PlatformIconProps) {
  const icon = PLATFORM_ICONS[platform]
  if (!icon || platform === 'unknown') return null

  const color = useColor ? `#${icon.hex}` : 'currentColor'

  return (
    <svg
      role="img"
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill={color}
      aria-label={icon.title}
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <title>{icon.title}</title>
      <path d={icon.path} />
    </svg>
  )
}
