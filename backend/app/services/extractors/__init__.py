"""Platform-specific media extractors with unified entry point."""

from ...schemas.extract import MediaResult
from ...utils.platform import detect_platform
from ..cache import extraction_cache
from ..tiktok_extractor import extract_tiktok_media
from .constants import ERR_THREADS_NOT_SUPPORTED, ERR_UNSUPPORTED_PLATFORM
from .facebook import extract_facebook_media
from .instagram import extract_instagram_media
from .twitter import extract_twitter_media


async def extract_media_info(url: str) -> MediaResult:
    """Extract media info from URL, routing to the appropriate platform extractor."""
    platform = detect_platform(url)

    if platform == "unknown":
        raise ValueError(ERR_UNSUPPORTED_PLATFORM)

    if platform == "threads":
        raise ValueError(ERR_THREADS_NOT_SUPPORTED)

    cached = await extraction_cache.get(url)
    if cached:
        return MediaResult(**cached)

    if platform == "tiktok":
        return await extract_tiktok_media(url)
    if platform == "facebook":
        return await extract_facebook_media(url)
    if platform == "twitter":
        return await extract_twitter_media(url)
    if platform == "instagram":
        return await extract_instagram_media(url)

    # Generic extraction (YouTube, etc.) via yt-dlp
    from .youtube import extract_youtube_media

    return await extract_youtube_media(url, platform)
