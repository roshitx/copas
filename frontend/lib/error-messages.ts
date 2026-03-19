import type { ErrorCode, Platform, PlatformErrorConfig } from '@/types'

export const ERROR_CODES: ErrorCode[] = [
  'UNSUPPORTED_PLATFORM',
  'ACCESS_DENIED',
  'EXTRACTION_FAILED',
  'RATE_LIMITED',
  'NETWORK_ERROR',
  'TIMEOUT',
  'UNKNOWN_ERROR',
]

export const SUGGESTED_ACTIONS = {
  checkUrl: 'Periksa kembali URL yang Anda masukkan',
  tryAgain: 'Coba lagi dalam beberapa saat',
  differentContent: 'Coba dengan konten lain yang tidak dibatasi',
  checkInternet: 'Pastikan koneksi internet Anda stabil',
  contactSupport: 'Hubungi dukungan jika masalah berlanjut',
} as const

export const PLATFORM_ERROR_MESSAGES: Record<Platform, PlatformErrorConfig> = {
  tiktok: {
    platform: 'tiktok',
    displayName: 'TikTok',
    messages: {
      UNSUPPORTED_PLATFORM: 'URL TikTok tidak valid atau formatnya tidak didukung',
      ACCESS_DENIED: 'Video TikTok mungkin privat atau telah dihapus',
      EXTRACTION_FAILED: 'Gagal mengambil informasi video TikTok',
      RATE_LIMITED: 'Terlalu banyak permintaan. Tunggu sebentar sebelum mencoba lagi',
      NETWORK_ERROR: 'Gagal terhubung ke TikTok. Periksa koneksi internet Anda',
      TIMEOUT: 'Permintaan ke TikTok terlalu lama. Coba lagi nanti',
      UNKNOWN_ERROR: 'Terjadi kesalahan saat memproses video TikTok',
    },
    genericMessage: 'Gagal memproses video TikTok. Video mungkin privat, dihapus, atau tidak tersedia',
    suggestedActions: [
      'Pastikan video tidak diatur sebagai privat',
      'Pastikan video belum dihapus oleh pemiliknya',
      'Coba salin ulang URL dari aplikasi TikTok',
    ],
  },
  instagram: {
    platform: 'instagram',
    displayName: 'Instagram',
    messages: {
      UNSUPPORTED_PLATFORM: 'URL Instagram tidak valid atau formatnya tidak didukung',
      ACCESS_DENIED: 'Postingan Instagram tidak tersedia atau akun privat',
      EXTRACTION_FAILED: 'Gagal mengambil informasi postingan Instagram',
      RATE_LIMITED: 'Terlalu banyak permintaan. Tunggu sebentar sebelum mencoba lagi',
      NETWORK_ERROR: 'Gagal terhubung ke Instagram. Periksa koneksi internet Anda',
      TIMEOUT: 'Permintaan ke Instagram terlalu lama. Coba lagi nanti',
      UNKNOWN_ERROR: 'Terjadi kesalahan saat memproses postingan Instagram',
    },
    genericMessage: 'Gagal memproses postingan Instagram. Postingan mungkin dari akun privat atau telah dihapus',
    suggestedActions: [
      'Pastikan postingan berasal dari akun publik',
      'Pastikan postingan belum dihapus',
      'Untuk multi-post, pastikan semua konten masih tersedia',
    ],
  },
  youtube: {
    platform: 'youtube',
    displayName: 'YouTube',
    messages: {
      UNSUPPORTED_PLATFORM: 'URL YouTube tidak valid atau formatnya tidak didukung',
      ACCESS_DENIED: 'Video YouTube mungkin dibatasi usia, dibatasi wilayah, atau dihapus',
      EXTRACTION_FAILED: 'Gagal mengambil informasi video YouTube',
      RATE_LIMITED: 'Terlalu banyak permintaan. Tunggu sebentar sebelum mencoba lagi',
      NETWORK_ERROR: 'Gagal terhubung ke YouTube. Periksa koneksi internet Anda',
      TIMEOUT: 'Permintaan ke YouTube terlalu lama. Coba lagi nanti',
      UNKNOWN_ERROR: 'Terjadi kesalahan saat memproses video YouTube',
    },
    genericMessage: 'Gagal memproses video YouTube. Video mungkin dibatasi usia, dibatasi wilayah, atau telah dihapus',
    suggestedActions: [
      'Pastikan video tidak dibatasi usia atau wilayah',
      'Video live stream yang sedang berlangsung tidak dapat diunduh',
      'Coba dengan video lain yang bersifat publik',
    ],
  },
  twitter: {
    platform: 'twitter',
    displayName: 'X (Twitter)',
    messages: {
      UNSUPPORTED_PLATFORM: 'URL X/Twitter tidak valid atau formatnya tidak didukung',
      ACCESS_DENIED: 'Tweet mungkin dari akun privat atau telah dihapus',
      EXTRACTION_FAILED: 'Gagal mengambil informasi tweet',
      RATE_LIMITED: 'Terlalu banyak permintaan. Tunggu sebentar sebelum mencoba lagi',
      NETWORK_ERROR: 'Gagal terhubung ke X/Twitter. Periksa koneksi internet Anda',
      TIMEOUT: 'Permintaan ke X/Twitter terlalu lama. Coba lagi nanti',
      UNKNOWN_ERROR: 'Terjadi kesalahan saat memproses tweet',
    },
    genericMessage: 'Gagal memproses tweet. Tweet mungkin dari akun privat atau telah dihapus',
    suggestedActions: [
      'Pastikan tweet berasal dari akun publik',
      'Pastikan tweet belum dihapus oleh pemiliknya',
      'Coba salin ulang URL dari aplikasi X/Twitter',
    ],
  },
  facebook: {
    platform: 'facebook',
    displayName: 'Facebook',
    messages: {
      UNSUPPORTED_PLATFORM: 'URL Facebook tidak valid atau formatnya tidak didukung',
      ACCESS_DENIED: 'Konten Facebook mungkin memerlukan login, dibatasi, atau privat',
      EXTRACTION_FAILED: 'Gagal mengambil informasi konten Facebook',
      RATE_LIMITED: 'Terlalu banyak permintaan. Tunggu sebentar sebelum mencoba lagi',
      NETWORK_ERROR: 'Gagal terhubung ke Facebook. Periksa koneksi internet Anda',
      TIMEOUT: 'Permintaan ke Facebook terlalu lama. Coba lagi nanti',
      UNKNOWN_ERROR: 'Terjadi kesalahan saat memproses konten Facebook',
    },
    genericMessage: 'Gagal memproses konten Facebook. Konten mungkin memerlukan login, dibatasi, atau bersifat privat',
    suggestedActions: [
      'Pastikan konten berasal dari akun/halaman publik',
      'Konten yang memerlukan login tidak dapat diunduh',
      'Coba dengan video atau postingan publik lainnya',
    ],
  },
  threads: {
    platform: 'threads',
    displayName: 'Threads',
    messages: {
      UNSUPPORTED_PLATFORM: 'URL Threads tidak valid atau formatnya tidak didukung',
      ACCESS_DENIED: 'Thread tidak tersedia atau akun privat',
      EXTRACTION_FAILED: 'Gagal mengambil informasi thread',
      RATE_LIMITED: 'Terlalu banyak permintaan. Tunggu sebentar sebelum mencoba lagi',
      NETWORK_ERROR: 'Gagal terhubung ke Threads. Periksa koneksi internet Anda',
      TIMEOUT: 'Permintaan ke Threads terlalu lama. Coba lagi nanti',
      UNKNOWN_ERROR: 'Terjadi kesalahan saat memproses thread',
    },
    genericMessage: 'Gagal memproses thread. Thread mungkin dari akun privat atau telah dihapus',
    suggestedActions: [
      'Pastikan thread berasal dari akun publik',
      'Pastikan thread belum dihapus oleh pemiliknya',
      'Coba salin ulang URL dari aplikasi Threads',
    ],
  },
  unknown: {
    platform: 'unknown',
    displayName: 'Platform',
    messages: {
      UNSUPPORTED_PLATFORM: 'Platform tidak didukung atau URL tidak dikenali',
      ACCESS_DENIED: 'Tidak dapat mengakses konten dari platform ini',
      EXTRACTION_FAILED: 'Gagal mengambil informasi dari URL yang diberikan',
      RATE_LIMITED: 'Terlalu banyak permintaan. Tunggu sebentar sebelum mencoba lagi',
      NETWORK_ERROR: 'Gagal terhubung. Periksa koneksi internet Anda',
      TIMEOUT: 'Permintaan terlalu lama. Coba lagi nanti',
      UNKNOWN_ERROR: 'Terjadi kesalahan yang tidak diketahui',
    },
    genericMessage: 'Gagal memproses URL. Platform mungkin tidak didukung atau konten tidak tersedia',
    suggestedActions: [
      'Pastikan URL berasal dari platform yang didukung (TikTok, Instagram, YouTube, X/Twitter, Facebook, Threads)',
      'Periksa kembali URL yang Anda salin',
      'Coba dengan URL lain',
    ],
  },
}

export function getPlatformErrorMessage(
  platform: Platform,
  code?: string
): string {
  const config = PLATFORM_ERROR_MESSAGES[platform]

  if (!code) {
    return config.genericMessage
  }

  const normalizedCode = code.toUpperCase() as ErrorCode
  return config.messages[normalizedCode] ?? config.genericMessage
}

export function getPlatformErrorConfig(platform: Platform): PlatformErrorConfig {
  return PLATFORM_ERROR_MESSAGES[platform]
}

export function getErrorWithSuggestions(
  platform: Platform,
  code?: string
): { message: string; actions: string[] } {
  const config = PLATFORM_ERROR_MESSAGES[platform]
  const message = getPlatformErrorMessage(platform, code)

  return {
    message,
    actions: config.suggestedActions,
  }
}

export function isValidErrorCode(code: string): code is ErrorCode {
  return ERROR_CODES.includes(code as ErrorCode)
}
