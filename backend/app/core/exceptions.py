"""Custom exception classes for the Copas.io API.

This module provides a hierarchy of exceptions for consistent error handling
across the application.
"""

from typing import Optional

from .error_codes import ERROR_MESSAGES, ERROR_STATUS_MAP, ErrorCode


class CopasException(Exception):
    """Base exception for all Copas.io API errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        self.error_code = error_code
        self.message = message or ERROR_MESSAGES.get(
            error_code, "Terjadi kesalahan yang tidak diketahui."
        )
        self.status_code = status_code or ERROR_STATUS_MAP.get(error_code, 500)
        super().__init__(self.message)

    def to_dict(self) -> dict[str, str]:
        """Convert exception to dictionary for API response."""
        return {
            "error": self.error_code.value,
            "message": self.message,
        }


class PlatformException(CopasException):
    """Exception raised for platform-related errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        platform: Optional[str] = None,
    ):
        super().__init__(error_code, message)
        self.platform = platform


class UnsupportedPlatformException(PlatformException):
    """Raised when the platform is not supported."""

    def __init__(self, message: Optional[str] = None, platform: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.UNSUPPORTED_PLATFORM,
            message=message or ERROR_MESSAGES[ErrorCode.UNSUPPORTED_PLATFORM],
            platform=platform,
        )


class AccessDeniedException(PlatformException):
    """Raised when access to content is denied (private, restricted, etc.)."""

    def __init__(self, message: Optional[str] = None, platform: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.ACCESS_DENIED,
            message=message or ERROR_MESSAGES[ErrorCode.ACCESS_DENIED],
            platform=platform,
        )


class ExtractionFailedException(PlatformException):
    """Raised when media extraction fails."""

    def __init__(self, message: Optional[str] = None, platform: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.EXTRACTION_FAILED,
            message=message or ERROR_MESSAGES[ErrorCode.EXTRACTION_FAILED],
            platform=platform,
        )


class InvalidURLException(CopasException):
    """Raised when the URL is invalid or malformed."""

    def __init__(self, message: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.INVALID_URL,
            message=message or ERROR_MESSAGES[ErrorCode.INVALID_URL],
        )


class ServiceUnavailableException(CopasException):
    """Raised when an external service is unavailable."""

    def __init__(self, message: Optional[str] = None, service: Optional[str] = None):
        self.service = service
        super().__init__(
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            message=message or ERROR_MESSAGES[ErrorCode.SERVICE_UNAVAILABLE],
        )


class TokenException(CopasException):
    """Base exception for token-related errors."""

    pass


class TokenInvalidException(TokenException):
    """Raised when a token is invalid or not found."""

    def __init__(self, message: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.TOKEN_INVALID,
            message=message or ERROR_MESSAGES[ErrorCode.TOKEN_INVALID],
        )


class TokenExpiredException(TokenException):
    """Raised when a token has expired."""

    def __init__(self, message: Optional[str] = None):
        super().__init__(
            error_code=ErrorCode.TOKEN_EXPIRED,
            message=message or ERROR_MESSAGES[ErrorCode.TOKEN_EXPIRED],
        )
