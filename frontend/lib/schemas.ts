import { z } from 'zod'

export const PlatformSchema = z.enum([
  'tiktok',
  'instagram',
  'youtube',
  'twitter',
  'facebook',
  'threads',
  'unknown',
])

export const FormatSchema = z.object({
  id: z.string(),
  label: z.string(),
  type: z.string(),
  size_mb: z.number().nullable(),
  download_url: z.string(),
})

export const MediaResultSchema = z.object({
  platform: PlatformSchema,
  title: z.string(),
  thumbnail: z.string().nullable(),
  thumbnails: z.array(z.string()),
  author: z.string().nullable(),
  duration: z.number().nullable(),
  formats: z.array(FormatSchema),
})

export const ApiErrorSchema = z.object({
  error: z.string(),
  message: z.string(),
})

export type Platform = z.infer<typeof PlatformSchema>
export type Format = z.infer<typeof FormatSchema>
export type MediaResult = z.infer<typeof MediaResultSchema>
export type ApiError = z.infer<typeof ApiErrorSchema>
