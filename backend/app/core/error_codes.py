"""Centralized error codes and messages for the API.

This module provides a single source of truth for all error codes
and their corresponding messages used throughout the application.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes for API responses."""

    # Platform errors (4xx)
    UNSUPPORTED_PLATFORM = "UNSUPPORTED_PLATFORM"
    ACCESS_DENIED = "ACCESS_DENIED"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    INVALID_URL = "INVALID_URL"

    # Service errors (5xx)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Token errors (4xx)
    TOKEN_INVALID = "TOKEN_INVALID"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"


# HTTP status code mapping for each error code
ERROR_STATUS_MAP = {
    ErrorCode.UNSUPPORTED_PLATFORM: 400,
    ErrorCode.ACCESS_DENIED: 403,
    ErrorCode.EXTRACTION_FAILED: 422,
    ErrorCode.INVALID_URL: 400,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.RATE_LIMIT_EXCEEDED: 429,
    ErrorCode.TOKEN_INVALID: 410,
    ErrorCode.TOKEN_EXPIRED: 410,
}


# Human-readable messages for each error code
ERROR_MESSAGES = {
    ErrorCode.UNSUPPORTED_PLATFORM: "Platform tidak didukung. Gunakan URL dari TikTok, Instagram, YouTube, X/Twitter, atau Facebook.",
    ErrorCode.ACCESS_DENIED: "Akses ditolak. Konten mungkin bersifat privat atau dibatasi.",
    ErrorCode.EXTRACTION_FAILED: "Gagal mengekstrak media. Pastikan URL valid dan coba lagi.",
    ErrorCode.INVALID_URL: "URL tidak valid. Pastikan URL adalah link publik yang dapat diakses.",
    ErrorCode.SERVICE_UNAVAILABLE: "Layanan暂时 tidak tersedia. Coba lagi nanti.",
    ErrorCode.INTERNAL_ERROR: "Terjadi kesalahan internal. Tim kami telah diberitahu.",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Terlalu banyak permintaan. Silakan tunggu beberapa saat.",
    ErrorCode.TOKEN_INVALID: "Token tidak valid atau sudah tidak ada.",
    ErrorCode.TOKEN_EXPIRED: "Token telah kadaluarsa. Silakan minta URL download baru.",
}


# Platform-specific error messages
PLATFORM_ERROR_MESSAGES = {
    "tiktok": {
        "private": "Video TikTok ini bersifat privat.",
        "unavailable": "Video TikTok tidak tersedia atau telah dihapus.",
        "content_error": "Gagal memproses konten TikTok.",
    },
    "instagram": {
        "private": "Akun Instagram ini bersifat privat.",
        "unavailable": "Konten Instagram tidak tersedia atau telah dihapus.",
    },
    "twitter": {
        "private": "Tweet ini berasal dari akun privat.",
        "unavailable": "Tweet tidak tersedia atau telah dihapus.",
    },
    "facebook": {
        "private": "Konten Facebook ini bersifat privat.",
        "unavailable": "Konten Facebook tidak tersedia atau telah dihapus.",
    },
    "youtube": {
        "private": "Video YouTube ini bersifat privat.",
        "unavailable": "Video YouTube tidak tersedia atau telah dihapus.",
        "age_restricted": "Video YouTube dibatasi usia dan memerlukan autentikasi.",
    },
}


def get_error_details(error_code: ErrorCode) -> dict[str, str | int]:
    """Get complete error details including status code and message.

    Args:
        error_code: The error code to get details for.

    Returns:
        Dictionary with 'error' and 'message' keys, plus 'status_code' for internal use.
    """
    return {
        "error": error_code.value,
        "message": ERROR_MESSAGES.get(
            error_code, "Terjadi kesalahan yang tidak diketahui."
        ),
        "status_code": ERROR_STATUS_MAP.get(error_code, 500),
    }


def create_error_response(
    error_code: ErrorCode, custom_message: str | None = None
) -> dict[str, str]:
    """Create an error response for API endpoints.

    Args:
        error_code: The error code to use.
        custom_message: Optional custom message to override the default.

    Returns:
        Dictionary with 'error' and 'message' keys suitable for API response.
    """
    return {
        "error": error_code.value,
        "message": custom_message
        or ERROR_MESSAGES.get(error_code, "Terjadi kesalahan yang tidak diketahui."),
    }
