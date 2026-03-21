"""Centralized error messages and constants for extraction services."""

# User-facing error messages (Indonesian)
ERR_UNSUPPORTED_PLATFORM = "Platform tidak didukung untuk URL ini."
ERR_THREADS_NOT_SUPPORTED = (
    "Platform Threads belum didukung. "
    "Coba download manual dari aplikasi Threads."
)
ERR_AUTH_REQUIRED = (
    "Konten ini memerlukan login atau tidak dapat diakses. "
    "Pastikan cookie sudah dikonfigurasi untuk platform ini."
)
ERR_EXTRACTION_FAILED = (
    "Gagal mengekstrak media. "
    "Pastikan link valid dan konten bisa diakses publik."
)
ERR_NO_FORMATS = (
    "Tidak ada format media yang tersedia untuk link ini. "
    "Konten mungkin memerlukan autentikasi atau tidak didukung."
)
ERR_INSTAGRAM_PRIVATE = (
    "Gagal memproses postingan Instagram. "
    "Postingan mungkin dari akun privat atau telah dihapus."
)
ERR_FACEBOOK_OUT_OF_SCOPE = (
    "URL Facebook tidak didukung. "
    "Hanya video publik (watch, reel, videos) yang dapat diunduh."
)
ERR_FACEBOOK_AUTH = (
    "Konten Facebook memerlukan login atau tidak dapat diakses. "
    "Pastikan konten bersifat publik."
)
ERR_FACEBOOK_DUAL_FAILURE = (
    "Gagal mengekstrak media Facebook. "
    "Coba lagi atau gunakan URL lain."
)
ERR_FACEBOOK_NO_FORMATS = "Tidak ada format media yang tersedia untuk video Facebook ini."
ERR_FACEBOOK_GENERIC = "Ekstraksi Facebook gagal tanpa alasan spesifik"
ERR_GENERIC_FAILURE = "Ekstraksi gagal: {msg}"

# yt-dlp error classification keywords
AUTH_KEYWORDS = (
    "login", "private", "cookie", "sign in", "sign_in",
    "empty media", "not logged", "authenticate", "authentication",
    "forbidden", "403", "401", "unauthorized", "unprocessable",
    "account", "session", "credentials",
)
EXTRACT_KEYWORDS = (
    "unable to extract", "video url",
    "no video formats", "unsupported url", "not a valid",
)
NETWORK_KEYWORDS = (
    "timed out", "connection", "network", "reset", "refused", "unavailable",
)

# Video quality labels
QUALITY_LABELS = {
    144: "144p",
    240: "240p",
    360: "360p",
    480: "480p",
    574: "574p",
    640: "640p",
    720: "720p",
    960: "960p",
    1080: "1080p",
    1440: "1440p",
    2160: "4K",
}


# NOTE: Cache TTL per-platform is defined in app/services/cache.py to avoid circular imports
