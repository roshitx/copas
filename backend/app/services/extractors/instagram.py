"""Instagram media extraction via yt-dlp + og:image scraping fallback."""

import asyncio
import html
import re
import logging
from typing import Optional

from app.schemas.extract import MediaResult, Format
from app.services.cache import extraction_cache
from app.services.retry import with_retry
from app.services.http_client import get_http_client
from .base import extract_info_sync, build_formats, create_format, extract_best_thumbnail
from .constants import ERR_INSTAGRAM_PRIVATE, ERR_NO_FORMATS

logger = logging.getLogger(__name__)


async def extract_instagram_media(url: str) -> MediaResult:
    """Extract media from Instagram URL."""
    loop = asyncio.get_running_loop()

    try:
        async def _extract():
            return await loop.run_in_executor(None, extract_info_sync, url)
        info = await with_retry(_extract, max_attempts=2, wait_seconds=2.0)
    except RuntimeError as e:
        if "there is no video in this post" in str(e).lower():
            return await _extract_photos(url)
        raise

    title = info.get("title", "Unknown")
    author = info.get("uploader_id") or info.get("uploader")
    thumbnail = extract_best_thumbnail(info)
    thumbnails = [thumbnail] if thumbnail else []
    duration = info.get("duration")
    formats = await build_formats(info, platform="instagram", author=author)

    # Instagram carousel/photo posts: yt-dlp returns playlist but no video formats
    if not formats:
        return await _extract_photos(
            url, ytdlp_title=title if title != "Unknown" else None, ytdlp_author=author,
        )

    result = MediaResult(
        platform="instagram",
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=thumbnails,
        duration=duration,
        formats=formats,
    )
    await extraction_cache.set(url, result.model_dump())
    return result


async def _extract_photos(
    url: str,
    ytdlp_title: Optional[str] = None,
    ytdlp_author: Optional[str] = None,
) -> MediaResult:
    """Fallback for Instagram photo-only posts. Scrapes og:image from the page."""
    shortcode = _extract_shortcode(url)
    if not shortcode:
        raise RuntimeError(ERR_INSTAGRAM_PRIVATE)

    photo_urls: list[str] = []
    title = ytdlp_title or "Instagram Post"
    author = ytdlp_author

    try:
        client = get_http_client()

        # Method 1: Instagram oEmbed API
        try:
            oembed_url = f"https://api.instagram.com/oembed/?url=https://www.instagram.com/p/{shortcode}/"
            resp = await client.get(oembed_url)
            if resp.status_code == 200 and "json" in resp.headers.get("content-type", ""):
                data = resp.json()
                raw_title = data.get("title") or ""
                title = html.unescape(raw_title) if raw_title else "Instagram Post"
                author = data.get("author_name")
                thumb = data.get("thumbnail_url")
                if thumb:
                    photo_urls.append(thumb)
        except Exception:
            pass

        # Method 2: Scrape og:image
        if not photo_urls:
            page_resp = await client.get(f"https://www.instagram.com/p/{shortcode}/")
            if page_resp.status_code == 200:
                body = page_resp.text
                og_matches = re.findall(
                    r'<meta\s+[^>]*?property="og:image"[^>]*?content="([^"]+)"', body,
                )
                if not og_matches:
                    og_matches = re.findall(
                        r'<meta\s+[^>]*?content="([^"]+)"[^>]*?property="og:image"', body,
                    )
                for img_url in og_matches:
                    clean_url = img_url.replace("&amp;", "&")
                    if clean_url not in photo_urls:
                        photo_urls.append(clean_url)

                if title == "Instagram Post":
                    og_title = re.search(
                        r'<meta\s+[^>]*?property="og:title"[^>]*?content="([^"]+)"', body
                    )
                    if not og_title:
                        og_title = re.search(
                            r'<meta\s+[^>]*?content="([^"]+)"[^>]*?property="og:title"', body
                        )
                    if og_title:
                        title = html.unescape(og_title.group(1))[:100]

    except Exception as e:
        logger.warning("Instagram photo extraction failed: %s", e)

    if not photo_urls:
        raise RuntimeError(ERR_INSTAGRAM_PRIVATE)

    formats: list[Format] = []
    for i, img_url in enumerate(photo_urls, start=1):
        label = f"Foto {i}" if len(photo_urls) > 1 else "Foto"
        fake_fmt = {"format_id": f"ig-photo-{i}", "url": img_url, "ext": "jpg", "filesize": None}
        try:
            fmt = await create_format(
                fake_fmt, label, "image/jpeg",
                platform="instagram", author=author,
                index=i if len(photo_urls) > 1 else 0,
            )
            formats.append(fmt)
        except Exception:
            continue

    if not formats:
        raise RuntimeError(ERR_INSTAGRAM_PRIVATE)

    thumbnail = photo_urls[0]
    result = MediaResult(
        platform="instagram",
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=photo_urls,
        duration=None,
        formats=formats,
    )
    await extraction_cache.set(url, result.model_dump())
    return result


def _extract_shortcode(url: str) -> Optional[str]:
    match = re.search(r"instagram\.com/(?:p|reel|reels)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None
