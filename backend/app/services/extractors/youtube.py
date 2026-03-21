"""YouTube and generic platform extraction via yt-dlp."""

import asyncio
import logging

from app.schemas.extract import MediaResult, Format
from app.services.cache import extraction_cache
from app.services.retry import with_retry
from .base import extract_info_sync, build_formats, extract_best_thumbnail
from .constants import ERR_NO_FORMATS

logger = logging.getLogger(__name__)


async def extract_youtube_media(url: str, platform: str = "youtube") -> MediaResult:
    """Extract media from YouTube or generic platform URL."""
    loop = asyncio.get_running_loop()

    async def _extract():
        return await loop.run_in_executor(None, extract_info_sync, url)
    info = await with_retry(_extract, max_attempts=2, wait_seconds=2.0)

    info_type = info.get("_type")
    author: str | None = None

    if info_type == "playlist":
        entries = info.get("entries") or []
        title = info.get("title") or (entries[0].get("title") if entries else "Unknown")
        thumbnail = info.get("thumbnail")
        if not thumbnail and entries:
            thumbnail = entries[0].get("thumbnail")
        duration = info.get("duration") or (entries[0].get("duration") if entries else None)

        thumbnails: list[str] = []
        for e in entries:
            t = e.get("thumbnail")
            if not t:
                e_thumbs = e.get("thumbnails") or []
                for et in reversed(e_thumbs):
                    if et.get("url"):
                        t = et["url"]
                        break
            if t:
                thumbnails.append(t)

        formats: list[Format] = []
        for i, entry in enumerate(entries, start=1):
            entry_formats = await build_formats(
                entry, video_index=i if len(entries) > 1 else 0, platform=platform, author=author
            )
            formats.extend(entry_formats)

        author = (
            info.get("uploader_id") or info.get("uploader")
            or (entries[0].get("uploader_id") if entries else None)
            or (entries[0].get("uploader") if entries else None)
        )
    else:
        title = info.get("title", "Unknown")
        thumbnail = extract_best_thumbnail(info)
        thumbnails = [thumbnail] if thumbnail else []
        duration = info.get("duration")
        formats = await build_formats(info, platform=platform, author=author)
        author = info.get("uploader_id") or info.get("uploader")

    if not formats:
        raise RuntimeError(ERR_NO_FORMATS)

    result = MediaResult(
        platform=platform,
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=thumbnails,
        duration=duration,
        formats=formats,
    )
    await extraction_cache.set(url, result.model_dump())
    return result
