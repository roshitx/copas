"""Facebook media extraction via yt-dlp (primary) + fallback provider."""

import asyncio
import logging

import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget

from app.schemas.extract import MediaResult
from app.services.cache import extraction_cache
from app.services.retry import with_retry, RetryableError
from app.services.facebook_fallback import extract_facebook_via_fallback
from app.utils.facebook_scope import is_facebook_url_in_scope, classify_extraction_error, ErrorClass
from .base import build_formats, extract_best_thumbnail
from .constants import (
    AUTH_KEYWORDS, EXTRACT_KEYWORDS, NETWORK_KEYWORDS,
    ERR_FACEBOOK_OUT_OF_SCOPE, ERR_FACEBOOK_AUTH,
    ERR_FACEBOOK_DUAL_FAILURE, ERR_FACEBOOK_NO_FORMATS,
    ERR_FACEBOOK_GENERIC, ERR_GENERIC_FAILURE,
)

logger = logging.getLogger(__name__)


async def extract_facebook_media(url: str) -> MediaResult:
    """Facebook hybrid extraction: primary yt-dlp -> fallback if allowed."""
    if not is_facebook_url_in_scope(url):
        logger.info("Facebook URL out of scope: %s", url)
        raise ValueError(ERR_FACEBOOK_OUT_OF_SCOPE)

    loop = asyncio.get_running_loop()
    primary_error: Exception | None = None

    try:
        async def _extract():
            return await loop.run_in_executor(None, _extract_info_sync_facebook, url)
        info = await with_retry(_extract, max_attempts=2, wait_seconds=2.0)
        logger.info("Facebook primary extraction succeeded: %s", url)

        result = await _build_media_result(info, url)
        await extraction_cache.set(url, result.model_dump())
        return result

    except Exception as e:
        primary_error = e
        logger.warning("Facebook primary extraction failed: %s", e)

    error_class = classify_extraction_error(primary_error)
    logger.info(
        "Facebook error classified: %s", error_class.value,
        extra={"platform": "facebook", "error_class": error_class.value}
    )

    if error_class == ErrorClass.NO_FALLBACK:
        raise primary_error

    if error_class == ErrorClass.TERMINAL_ACCESS:
        raise PermissionError(ERR_FACEBOOK_AUTH) from primary_error

    if error_class == ErrorClass.ALLOW_FALLBACK:
        logger.info("Facebook ALLOW_FALLBACK, attempting fallback for: %s", url)
        try:
            result = await extract_facebook_via_fallback(url)
            cache_data = result.model_dump() if hasattr(result, "model_dump") else result
            await extraction_cache.set(url, cache_data)
            return result
        except Exception as fallback_error:
            logger.error("Facebook fallback failed: %s", fallback_error)
            raise RuntimeError(ERR_FACEBOOK_DUAL_FAILURE) from fallback_error

    raise RuntimeError(ERR_FACEBOOK_GENERIC)


def _extract_info_sync_facebook(url: str) -> dict:
    """Synchronous yt-dlp extraction for Facebook (no cookies)."""
    ydl_opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.0 Mobile/15E148 Safari/604.1"
            ),
        },
        "socket_timeout": 30,
        "impersonate": ImpersonateTarget("chrome"),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            msg_lower = msg.lower()
            if any(k in msg_lower for k in AUTH_KEYWORDS):
                raise PermissionError("Konten memerlukan login atau tidak dapat diakses.") from e
            if any(k in msg_lower for k in EXTRACT_KEYWORDS):
                raise RuntimeError("Gagal mengekstrak media. Pastikan link valid.") from e
            if any(k in msg_lower for k in NETWORK_KEYWORDS):
                raise RetryableError(f"Transient extraction error: {msg}") from e
            raise RuntimeError(ERR_GENERIC_FAILURE.format(msg=msg)) from e

    return info


async def _build_media_result(info: dict, original_url: str) -> MediaResult:
    """Build MediaResult from successful Facebook yt-dlp extraction."""
    title = info.get("title", "Untitled")
    author = info.get("uploader_id") or info.get("uploader")
    thumbnail = extract_best_thumbnail(info)
    thumbnails = [thumbnail] if thumbnail else []
    duration = info.get("duration")
    formats = await build_formats(info, platform="facebook", author=author)

    if not formats:
        raise RuntimeError(ERR_FACEBOOK_NO_FORMATS)

    return MediaResult(
        platform="facebook",
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=thumbnails,
        duration=duration,
        formats=formats,
    )
