"""
Self-hosted fallback adapter for Facebook media extraction.

Provides an alternative extraction path when yt-dlp primary extraction fails
with ALLOW_FALLBACK error class. Uses configurable self-hosted providers.

ENV CONFIG:
- FACEBOOK_FALLBACK_ENABLED: Enable/disable fallback (default: false)
- FACEBOOK_FALLBACK_BASE_URL: Base URL for fallback provider
- FACEBOOK_FALLBACK_TIMEOUT_SECONDS: Request timeout (default: 30)

FEATURES:
- Provider healthcheck with 60s cache
- Structured logging for observability
- In-memory metrics counters
- Kill-switch via feature flag
"""

import os
import time
import logging
from typing import Optional
from dataclasses import dataclass, field
import httpx
import asyncio

from app.schemas.extract import MediaResult, Format
from app.utils.facebook_scope import ErrorClass, classify_extraction_error
import app.services.token_store as _token_store_module
from app.services.extractors.base import build_filename


# Configure logger
logger = logging.getLogger(__name__)


# In-memory metrics counters
@dataclass
class FallbackMetrics:
    """Simple in-memory metrics for fallback extraction."""

    facebook_primary_success: int = 0
    facebook_fallback_attempt: int = 0
    facebook_fallback_success: int = 0
    facebook_dual_failure: int = 0

    def to_dict(self) -> dict:
        return {
            "facebook_primary_success": self.facebook_primary_success,
            "facebook_fallback_attempt": self.facebook_fallback_attempt,
            "facebook_fallback_success": self.facebook_fallback_success,
            "facebook_dual_failure": self.facebook_dual_failure,
        }


metrics = FallbackMetrics()


# Healthcheck cache
@dataclass
class HealthCache:
    """Cache for provider health status."""

    is_healthy: bool = False
    last_check: float = 0.0
    ttl_seconds: int = 60


health_cache = HealthCache()


class FacebookFallbackError(Exception):
    """Base exception for Facebook fallback errors."""

    def __init__(
        self, message: str, error_class: ErrorClass = ErrorClass.ALLOW_FALLBACK
    ):
        super().__init__(message)
        self.error_class = error_class


class FacebookFallbackDisabledError(FacebookFallbackError):
    """Fallback adapter is disabled via config."""

    def __init__(self):
        super().__init__(
            "Facebook fallback adapter is disabled", error_class=ErrorClass.NO_FALLBACK
        )


class FacebookFallbackTimeoutError(FacebookFallbackError):
    """Fallback request timed out."""

    def __init__(self, message: str = "Fallback request timed out"):
        super().__init__(message, error_class=ErrorClass.ALLOW_FALLBACK)


class FacebookFallbackProviderError(FacebookFallbackError):
    """Fallback provider returned an error (5xx, network issues)."""

    def __init__(self, message: str):
        super().__init__(message, error_class=ErrorClass.ALLOW_FALLBACK)


class FacebookFallbackContentError(FacebookFallbackError):
    """Content not found, private, or inaccessible."""

    def __init__(self, message: str):
        super().__init__(message, error_class=ErrorClass.TERMINAL_ACCESS)


class FacebookFallbackUnhealthyError(FacebookFallbackError):
    """Fallback provider is unhealthy."""

    def __init__(self):
        super().__init__(
            "Fallback provider is unhealthy", error_class=ErrorClass.NO_FALLBACK
        )


# Configuration from environment
def _get_config() -> dict:
    """Load fallback configuration from environment."""
    enabled_str = os.getenv("FACEBOOK_FALLBACK_ENABLED", "false").lower()
    return {
        "enabled": enabled_str in ("true", "1", "yes"),
        "base_url": os.getenv("FACEBOOK_FALLBACK_BASE_URL", ""),
        "timeout_seconds": int(os.getenv("FACEBOOK_FALLBACK_TIMEOUT_SECONDS", "30")),
        "max_retries": 2,
        "retry_base_delay": 1.0,  # seconds
        "healthcheck_timeout": 5,  # seconds
    }


async def check_fallback_health() -> bool:
    """
    Check if fallback provider is healthy.

    Uses cached result if within TTL (60 seconds).
    Performs lightweight healthcheck with short timeout (5s).

    Returns:
        True if provider is healthy, False otherwise.
    """
    global health_cache

    now = time.time()

    # Return cached result if still valid
    if now - health_cache.last_check < health_cache.ttl_seconds:
        logger.debug(
            "fallback_healthcheck_cached",
            extra={
                "is_healthy": health_cache.is_healthy,
                "cache_age_seconds": now - health_cache.last_check,
            },
        )
        return health_cache.is_healthy

    config = _get_config()

    # Cannot check health without base URL
    if not config["base_url"]:
        logger.warning("fallback_healthcheck_no_base_url")
        return False

    # Cannot check health if disabled
    if not config["enabled"]:
        logger.debug("fallback_healthcheck_disabled")
        return False

    # Perform healthcheck
    timeout = httpx.Timeout(config["healthcheck_timeout"])

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                f"{config['base_url']}/health",
                headers={"User-Agent": "CopasBot/1.0 (healthcheck)"},
            )

            is_healthy = response.status_code == 200

            # Update cache
            health_cache.is_healthy = is_healthy
            health_cache.last_check = now

            logger.info(
                "fallback_healthcheck_complete",
                extra={
                    "is_healthy": is_healthy,
                    "status_code": response.status_code,
                },
            )

            return is_healthy

    except httpx.TimeoutException:
        logger.warning("fallback_healthcheck_timeout")
        health_cache.is_healthy = False
        health_cache.last_check = now
        return False

    except httpx.RequestError as e:
        logger.warning("fallback_healthcheck_error", extra={"error": str(e)})
        health_cache.is_healthy = False
        health_cache.last_check = now
        return False


def get_metrics() -> dict:
    """Get current metrics snapshot."""
    return metrics.to_dict()


def reset_metrics() -> None:
    """Reset all metrics counters (useful for testing)."""
    global metrics
    metrics = FallbackMetrics()


def clear_health_cache() -> None:
    """Clear health cache (useful for testing)."""
    global health_cache
    health_cache = HealthCache()


async def extract_facebook_via_fallback(url: str) -> MediaResult:
    """
    Extract Facebook media using self-hosted fallback provider.

    Args:
        url: Facebook video/reel URL to extract.

    Returns:
        MediaResult with normalized data compatible with primary extractor.

    Raises:
        FacebookFallbackDisabledError: Fallback is disabled in config.
        FacebookFallbackUnhealthyError: Provider is unhealthy.
        FacebookFallbackTimeoutError: Request timed out after retries.
        FacebookFallbackProviderError: Provider error after retries exhausted.
        FacebookFallbackContentError: Content not found/private.

    Kill-switch: Returns disabled status when FACEBOOK_FALLBACK_ENABLED=false
    Healthcheck: Skips fallback if provider is unhealthy.
    """
    config = _get_config()

    # Log extraction start
    logger.info(
        "facebook_extraction_start",
        extra={
            "url": url,
            "fallback_enabled": config["enabled"],
        },
    )

    # Kill-switch check
    if not config["enabled"]:
        logger.info(
            "facebook_fallback_path",
            extra={"path": "disabled", "reason": "kill_switch"},
        )
        raise FacebookFallbackDisabledError()

    if not config["base_url"]:
        logger.warning(
            "facebook_fallback_path",
            extra={"path": "disabled", "reason": "no_base_url"},
        )
        raise FacebookFallbackError(
            "FACEBOOK_FALLBACK_BASE_URL not configured",
            error_class=ErrorClass.NO_FALLBACK,
        )

    # Healthcheck before attempting extraction
    is_healthy = await check_fallback_health()
    if not is_healthy:
        logger.warning(
            "facebook_fallback_path",
            extra={"path": "skipped", "reason": "unhealthy_provider"},
        )
        raise FacebookFallbackUnhealthyError()

    # Increment attempt counter
    metrics.facebook_fallback_attempt += 1

    logger.info(
        "facebook_fallback_path",
        extra={"path": "fallback", "provider": config["base_url"]},
    )

    try:
        # Fetch with retry logic
        data = await _fetch_with_retry(url, config)

        # Normalize response to MediaResult
        result = await _build_media_result(data, url)

        # Increment success counter
        metrics.facebook_fallback_success += 1

        logger.info(
            "facebook_extraction_success",
            extra={
                "title": result.title,
                "formats_count": len(result.formats),
            },
        )

        return result

    except FacebookFallbackContentError as e:
        # Content errors are expected, log at info level
        logger.info(
            "facebook_extraction_error",
            extra={
                "error_class": "content_error",
                "error_message": str(e),
            },
        )
        raise

    except (FacebookFallbackTimeoutError, FacebookFallbackProviderError) as e:
        # Provider errors - log at warning level
        logger.warning(
            "facebook_extraction_error",
            extra={
                "error_class": "provider_error",
                "error_message": str(e),
            },
        )
        # Increment dual failure counter if this was the last resort
        metrics.facebook_dual_failure += 1
        raise

    except Exception as e:
        # Unexpected errors - log at error level
        logger.error(
            "facebook_extraction_error",
            extra={
                "error_class": "unexpected",
                "error_type": type(e).__name__,
                "error_message": str(e),
            },
        )
        metrics.facebook_dual_failure += 1
        raise


async def _fetch_with_retry(url: str, config: dict) -> dict:
    """
    Fetch from fallback provider with exponential backoff retry.

    Max 2 attempts with 1s, 2s delays.
    """
    last_error: Optional[Exception] = None

    for attempt in range(config["max_retries"]):
        try:
            return await _fetch_from_provider(url, config)
        except (FacebookFallbackTimeoutError, FacebookFallbackProviderError) as e:
            last_error = e
            logger.warning(
                "facebook_fallback_retry",
                extra={
                    "attempt": attempt + 1,
                    "max_attempts": config["max_retries"],
                    "error": str(e),
                },
            )
            if attempt < config["max_retries"] - 1:
                # Exponential backoff: 1s, 2s
                delay = config["retry_base_delay"] * (2**attempt)
                await asyncio.sleep(delay)
        except FacebookFallbackContentError:
            # Don't retry content errors (private, not found)
            raise

    # Retries exhausted
    raise last_error or FacebookFallbackProviderError("Unknown error after retries")


async def _fetch_from_provider(url: str, config: dict) -> dict:
    """Make HTTP request to fallback provider."""
    timeout = httpx.Timeout(config["timeout_seconds"])

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{config['base_url']}/api/extract",
                json={"url": url},
                headers={
                    "User-Agent": "CopasBot/1.0 (fallback-adapter)",
                    "Accept": "application/json",
                },
            )

            if response.status_code >= 500:
                raise FacebookFallbackProviderError(
                    f"Fallback provider error: HTTP {response.status_code}"
                )

            if response.status_code == 404:
                raise FacebookFallbackContentError(
                    "Konten tidak ditemukan atau telah dihapus"
                )

            if response.status_code == 403:
                raise FacebookFallbackContentError(
                    "Konten bersifat pribadi atau memerlukan login"
                )

            if response.status_code != 200:
                raise FacebookFallbackProviderError(
                    f"Fallback provider returned HTTP {response.status_code}"
                )

            result = response.json()

            if result.get("error"):
                error_msg = result.get("message", "Unknown error")
                # Classify error for proper handling
                if any(
                    k in error_msg.lower()
                    for k in ["private", "login", "forbidden", "403"]
                ):
                    raise FacebookFallbackContentError(error_msg)
                raise FacebookFallbackProviderError(error_msg)

            if not result.get("data"):
                raise FacebookFallbackContentError(
                    "Tidak ada data media yang ditemukan"
                )

            return result["data"]

    except httpx.TimeoutException:
        raise FacebookFallbackTimeoutError(
            f"Fallback request timed out after {config['timeout_seconds']}s"
        )
    except httpx.RequestError as e:
        raise FacebookFallbackProviderError(
            f"Gagal menghubungi fallback provider: {str(e)}"
        )


async def _build_media_result(data: dict, original_url: str) -> MediaResult:
    """
    Build MediaResult from fallback provider response.

    Expected data structure:
    {
        "title": str,
        "thumbnail": str,
        "author": str,
        "duration": int,
        "video_url": str,
        "audio_url": str (optional),
    }
    """
    title = data.get("title") or "Untitled"
    thumbnail = data.get("thumbnail")
    author = data.get("author")
    duration = data.get("duration")

    formats = await _build_formats(data, author)

    if not formats:
        raise FacebookFallbackContentError("Tidak ada format media yang tersedia")

    return MediaResult(
        platform="facebook",
        title=title,
        thumbnail=thumbnail,
        thumbnails=[thumbnail] if thumbnail else [],
        author=author,
        duration=duration,
        formats=formats,
    )


async def _build_formats(data: dict, author: Optional[str]) -> list[Format]:
    """Build format list from fallback response."""
    formats = []

    # Video format
    video_url = data.get("video_url")
    if video_url:
        filename = build_filename("facebook", author, ext="mp4")

        token = await _token_store_module.token_store.create_token(
            download_url=video_url, filename=filename, content_type="video/mp4"
        )

        size_mb = None
        if data.get("size"):
            size_mb = round(data["size"] / (1024 * 1024), 2)

        formats.append(
            Format(
                id="fallback-video",
                label="Video HD",
                type="video/mp4",
                size_mb=size_mb,
                download_url=f"/api/download?token={token}",
            )
        )

    # Audio format (optional)
    audio_url = data.get("audio_url")
    if audio_url:
        filename = build_filename("facebook", author, ext="mp3")

        token = await _token_store_module.token_store.create_token(
            download_url=audio_url, filename=filename, content_type="audio/mp3"
        )

        formats.append(
            Format(
                id="fallback-audio",
                label="Audio MP3",
                type="audio/mp3",
                size_mb=None,
                download_url=f"/api/download?token={token}",
            )
        )

    return formats
