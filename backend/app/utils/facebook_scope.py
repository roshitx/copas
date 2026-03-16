"""
Facebook scope policy and error classification for extraction pipeline.

SCOPE POLICY:
- Facebook public-core scope is intentionally limited to avoid authentication
  requirements and reduce failure surface area.
- In-scope patterns: watch, videos, reel, fb.watch (public video content)
- Out-of-scope patterns: share/v (redirect links, often private/expired)

ERROR CLASSIFICATION:
- NO_FALLBACK: URL validation failures (invalid, out-of-scope, unsupported)
  → Should raise ValueError (mapped to 400 UNSUPPORTED_PLATFORM)
- ALLOW_FALLBACK: Runtime extraction failures (network, format, transient)
  → Can retry with alternative extractor or raise RuntimeError (422)
- TERMINAL_ACCESS: Authentication/challenge/forbidden errors
  → Should raise PermissionError (mapped to 403 ACCESS_DENIED)

FALLBACK RULE:
When both primary extractor and fallback fail, raise RuntimeError so
router maps to 422 EXTRACTION_FAILED.
"""

import re
from enum import Enum


class ErrorClass(Enum):
    """Classification of extraction errors for fallback eligibility.

    NO_FALLBACK: Error is fundamental (invalid URL, out of scope) - no retry.
    ALLOW_FALLBACK: Error is recoverable (network, transient) - can retry.
    TERMINAL_ACCESS: Error requires authentication - no retry without credentials.
    """

    NO_FALLBACK = "no_fallback"
    ALLOW_FALLBACK = "allow_fallback"
    TERMINAL_ACCESS = "terminal_access"


# In-scope URL patterns for Facebook public-core extraction.
# These are URLs that yt-dlp can typically extract without authentication.
FACEBOOK_IN_SCOPE_PATTERNS: tuple[str, ...] = (
    r"facebook\.com/[^/]+/videos/",
    r"facebook\.com/watch",
    r"facebook\.com/watch/",
    r"facebook\.com/reel/",
    r"facebook\.com/video\.php",
    r"fb\.watch/",
)

# Out-of-scope URL patterns that should be rejected early.
# These patterns typically require authentication or are private content.
# share/v/ URLs are redirect links that are often private or expired.
FACEBOOK_OUT_OF_SCOPE_PATTERNS: tuple[str, ...] = (
    r"facebook\.com/share/v/",
)


def is_facebook_url_in_scope(url: str) -> bool:
    """
    Check if a Facebook URL falls within the public-core scope.

    A URL is in-scope if:
    1. It matches at least one in-scope pattern, AND
    2. It does NOT match any out-of-scope pattern.

    Args:
        url: The Facebook URL to validate.

    Returns:
        True if URL is within public-core scope, False otherwise.

    Examples:
        >>> is_facebook_url_in_scope("https://facebook.com/watch?v=123")
        True
        >>> is_facebook_url_in_scope("https://facebook.com/username/videos/456")
        True
        >>> is_facebook_url_in_scope("https://facebook.com/share/v/abc")
        False
    """
    url_lower = url.lower()

    # Check out-of-scope patterns first (denylist takes precedence)
    for pattern in FACEBOOK_OUT_OF_SCOPE_PATTERNS:
        if re.search(pattern, url_lower):
            return False

    # Check in-scope patterns
    for pattern in FACEBOOK_IN_SCOPE_PATTERNS:
        if re.search(pattern, url_lower):
            return True

    # Default to out-of-scope for unmatched Facebook URLs
    return False


# Error message keywords for classification
_AUTH_KEYWORDS: tuple[str, ...] = (
    "login",
    "private",
    "cookie",
    "sign in",
    "sign_in",
    "authenticate",
    "authentication",
    "forbidden",
    "403",
    "401",
    "unauthorized",
    "account",
    "session",
    "credentials",
    "not logged",
    "age-restricted",
    "age restricted",
)

_INVALID_URL_KEYWORDS: tuple[str, ...] = (
    "unsupported url",
    "invalid url",
    "url not found",
    "not a valid",
    "malformed",
)

_TRANSIENT_KEYWORDS: tuple[str, ...] = (
    "timeout",
    "connection",
    "network",
    "temporary",
    "rate limit",
    "too many requests",
    "503",
    "502",
)


def classify_extraction_error(error: Exception) -> ErrorClass:
    """
    Classify an extraction error to determine fallback eligibility.

    Classification rules:
    - NO_FALLBACK: URL validation errors (invalid, unsupported, out-of-scope)
    - TERMINAL_ACCESS: Authentication/authorization failures
    - ALLOW_FALLBACK: Transient/runtime failures that may succeed on retry

    Args:
        error: The exception from extraction attempt.

    Returns:
        ErrorClass enum indicating fallback eligibility.

    Examples:
        >>> classify_extraction_error(ValueError("Unsupported URL"))
        <ErrorClass.NO_FALLBACK: 'no_fallback'>
        >>> classify_extraction_error(PermissionError("Login required"))
        <ErrorClass.TERMINAL_ACCESS: 'terminal_access'>
    """
    msg = str(error).lower()

    # ValueError indicates URL validation failure - no fallback
    if isinstance(error, ValueError):
        return ErrorClass.NO_FALLBACK

    # PermissionError indicates auth failure - terminal
    if isinstance(error, PermissionError):
        return ErrorClass.TERMINAL_ACCESS

    # Check for auth-related keywords in message
    if any(k in msg for k in _AUTH_KEYWORDS):
        return ErrorClass.TERMINAL_ACCESS

    # Check for invalid URL keywords
    if any(k in msg for k in _INVALID_URL_KEYWORDS):
        return ErrorClass.NO_FALLBACK

    # Check for transient errors (may succeed on retry)
    if any(k in msg for k in _TRANSIENT_KEYWORDS):
        return ErrorClass.ALLOW_FALLBACK

    # Default: allow fallback for unclassified runtime errors
    # (network issues, format parsing, etc.)
    return ErrorClass.ALLOW_FALLBACK
