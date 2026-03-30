"""Core module exports for Copas.io API.

This module provides centralized access to all core components
including configuration, error handling, and logging.
"""

from .config import settings
from .error_codes import (
    ERROR_MESSAGES,
    ERROR_STATUS_MAP,
    ErrorCode,
    create_error_response,
    get_error_details,
)
from .exceptions import (
    AccessDeniedException,
    CopasException,
    ExtractionFailedException,
    InvalidURLException,
    ServiceUnavailableException,
    TokenException,
    TokenExpiredException,
    TokenInvalidException,
    UnsupportedPlatformException,
)

__all__ = [
    # Settings
    "settings",
    # Error codes
    "ErrorCode",
    "ERROR_MESSAGES",
    "ERROR_STATUS_MAP",
    "create_error_response",
    "get_error_details",
    # Exceptions
    "CopasException",
    "UnsupportedPlatformException",
    "AccessDeniedException",
    "ExtractionFailedException",
    "InvalidURLException",
    "ServiceUnavailableException",
    "TokenException",
    "TokenInvalidException",
    "TokenExpiredException",
]
