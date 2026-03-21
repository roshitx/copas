"""Twitter/X media extraction via yt-dlp + fxtwitter API."""

import asyncio
import re
import logging
from typing import Optional

from app.schemas.extract import MediaResult, Format
from app.services.cache import extraction_cache
from app.services.retry import with_retry
from app.services.http_client import get_http_client
from .base import extract_info_sync, build_formats, create_format, extract_best_thumbnail
from .constants import ERR_NO_FORMATS

logger = logging.getLogger(__name__)


async def extract_twitter_media(url: str) -> MediaResult:
    """Extract media from Twitter/X URL."""
    normalized_url = url.replace("x.com/", "twitter.com/")
    loop = asyncio.get_running_loop()

    info: dict | None = None
    no_video_error = False

    try:
        async def _extract():
            return await loop.run_in_executor(None, extract_info_sync, normalized_url)
        info = await with_retry(_extract, max_attempts=2, wait_seconds=2.0)
    except RuntimeError as e:
        if "no video could be found" in str(e).lower():
            no_video_error = True
        else:
            raise

    title = "Unknown"
    author: str | None = None
    thumbnail: str | None = None
    thumbnails: list[str] = []
    duration: int | None = None
    formats: list[Format] = []

    if info is not None:
        title, author, thumbnail, thumbnails, duration, formats = await _parse_ytdlp_info(info)

    # Always fetch images via fxtwitter (yt-dlp excludes photos)
    tweet_id = _extract_tweet_id(url)
    if tweet_id:
        fx_data = await with_retry(_fetch_fxtwitter, tweet_id, max_attempts=2, wait_seconds=1.0)
        image_formats = await _build_image_formats(fx_data, author=author)
        formats.extend(image_formats)

        # Collect photo thumbnails
        photos = fx_data.get("tweet", {}).get("media", {}).get("photos", []) if fx_data else []
        if photos:
            photo_urls = [p["url"] for p in photos if p.get("url")]
            if photo_urls:
                if len(photo_urls) > 1:
                    thumbnails = photo_urls
                else:
                    existing = set(thumbnails)
                    for photo_url in photo_urls:
                        if photo_url not in existing:
                            thumbnails.append(photo_url)
                if not thumbnail:
                    thumbnail = photo_urls[0]

        # Image-only tweets: populate title/thumbnail from fxtwitter
        if no_video_error and fx_data:
            tweet = fx_data.get("tweet", {})
            title = tweet.get("text", "Unknown")[:100] or "Unknown"
            tweet_photos = tweet.get("media", {}).get("photos", [])
            if tweet_photos:
                thumbnail = tweet_photos[0].get("url")

        # Video-only tweets: fall back to fxtwitter video thumbnail
        if not thumbnail and fx_data:
            fx_videos = fx_data.get("tweet", {}).get("media", {}).get("videos", [])
            for fx_vid in fx_videos:
                vid_thumb = fx_vid.get("thumbnail_url")
                if vid_thumb:
                    thumbnail = vid_thumb
                    thumbnails = [vid_thumb]
                    break

        # Author from fxtwitter
        if fx_data and not author:
            tweet_author = fx_data.get("tweet", {}).get("author", {})
            author = tweet_author.get("screen_name") or tweet_author.get("name")

    if not formats:
        raise RuntimeError(ERR_NO_FORMATS)

    result = MediaResult(
        platform="twitter",
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=thumbnails,
        duration=duration,
        formats=formats,
    )
    await extraction_cache.set(url, result.model_dump())
    return result


async def _parse_ytdlp_info(info: dict) -> tuple:
    """Parse yt-dlp info dict into components."""
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
                entry, video_index=i if len(entries) > 1 else 0, platform="twitter", author=author
            )
            formats.extend(entry_formats)

        author = (
            info.get("uploader_id") or info.get("uploader")
            or (entries[0].get("uploader_id") if entries else None)
            or (entries[0].get("uploader") if entries else None)
        )
        return title, author, thumbnail, thumbnails, duration, formats
    else:
        title = info.get("title", "Unknown")
        thumbnail = extract_best_thumbnail(info)
        thumbnails = [thumbnail] if thumbnail else []
        duration = info.get("duration")
        formats = await build_formats(info, platform="twitter", author=author)
        author = info.get("uploader_id") or info.get("uploader")
        return title, author, thumbnail, thumbnails, duration, formats


def _extract_tweet_id(url: str) -> Optional[str]:
    match = re.search(r"(?:twitter\.com|x\.com)/[^/]+/status(?:es)?/(\d+)", url)
    return match.group(1) if match else None


async def _fetch_fxtwitter(tweet_id: str) -> dict:
    try:
        client = get_http_client()
        resp = await client.get(
            f"https://api.fxtwitter.com/status/{tweet_id}",
            headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"},
        )
        if resp.status_code != 200:
            return {}
        return resp.json()
    except Exception:
        return {}


async def _build_image_formats(
    fx_data: dict, platform: str = "twitter", author: Optional[str] = None
) -> list[Format]:
    if not fx_data:
        return []

    photos = fx_data.get("tweet", {}).get("media", {}).get("photos", [])
    image_formats: list[Format] = []

    for i, photo in enumerate(photos, start=1):
        image_url = photo.get("url")
        if not image_url:
            continue
        label = f"Foto {i}" if len(photos) > 1 else "Foto"
        fake_fmt = {"format_id": f"img-{i}", "url": image_url, "ext": "jpg", "filesize": None}
        try:
            fmt = await create_format(
                fake_fmt, label, "image/jpeg",
                platform=platform, author=author,
                index=i if len(photos) > 1 else 0,
            )
            image_formats.append(fmt)
        except Exception:
            continue

    return image_formats
