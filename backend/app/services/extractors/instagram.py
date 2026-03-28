"""Instagram media extraction via GraphQL API (curl_cffi) + yt-dlp fallback."""

import asyncio
import json
import logging
import os
import re
from typing import Optional
from urllib.parse import quote

from curl_cffi.requests import AsyncSession

from app.schemas.extract import MediaResult, Format
from app.services.cache import extraction_cache
from app.services.extractors.base import (
    extract_info_sync,
    build_formats,
    build_filename,
    extract_best_thumbnail,
)
from app.services.extractors.constants import ERR_INSTAGRAM_PRIVATE
import app.services.token_store as _token_store_module

logger = logging.getLogger(__name__)

IG_APP_ID = "936619743392459"
IG_GRAPHQL_URL = "https://www.instagram.com/graphql/query"
IG_DEFAULT_DOC_ID = "8845758582119845"

_GRAPHQL_HEADERS = {
    "x-ig-app-id": IG_APP_ID,
    "x-requested-with": "XMLHttpRequest",
    "x-csrftoken": "missing",
    "referer": "https://www.instagram.com/",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.instagram.com",
}


async def extract_instagram_media(url: str) -> MediaResult:
    """Extract media from Instagram URL.

    Strategy:
    1. GraphQL API via curl_cffi (handles carousel, photo, video)
    2. yt-dlp fallback (reels, single video)
    3. Embed page scraping (last resort)
    """
    shortcode = _extract_shortcode(url)

    # Primary: GraphQL API
    if shortcode:
        try:
            result = await _extract_via_graphql(shortcode, url)
            if result:
                return result
        except Exception as e:
            logger.warning("GraphQL extraction failed for %s: %s", shortcode, e)

    # Fallback: yt-dlp (good for reels/single videos)
    try:
        return await _extract_via_ytdlp(url)
    except Exception as e:
        logger.warning("yt-dlp extraction failed: %s", e)

    raise RuntimeError(ERR_INSTAGRAM_PRIVATE)


async def _extract_via_graphql(shortcode: str, original_url: str) -> Optional[MediaResult]:
    """Extract media using Instagram's GraphQL API with curl_cffi for TLS impersonation."""
    doc_id = os.environ.get("IG_GRAPHQL_DOC_ID", IG_DEFAULT_DOC_ID)

    variables = json.dumps(
        {
            "shortcode": shortcode,
            "fetch_tagged_user_count": None,
            "hoisted_comment_id": None,
            "hoisted_reply_id": None,
        },
        separators=(",", ":"),
    )
    body = f"variables={quote(variables)}&doc_id={doc_id}"

    async with AsyncSession(impersonate="chrome") as session:
        resp = await session.post(
            IG_GRAPHQL_URL,
            data=body,
            headers=_GRAPHQL_HEADERS,
            timeout=15,
        )

    if resp.status_code != 200:
        logger.debug("GraphQL returned %d for %s", resp.status_code, shortcode)
        return None

    data = resp.json()

    media = (
        data.get("data", {}).get("xdt_shortcode_media")
        or data.get("data", {}).get("shortcode_media")
    )
    if not media:
        logger.debug("No media in GraphQL response for %s", shortcode)
        return None

    return await _parse_graphql_media(media, original_url)


async def _parse_graphql_media(media: dict, original_url: str) -> MediaResult:
    """Parse Instagram GraphQL media response into MediaResult."""
    typename = media.get("__typename", "")
    owner = media.get("owner", {})
    author = owner.get("username") or owner.get("full_name")

    # Extract title from caption
    caption_edges = media.get("edge_media_to_caption", {}).get("edges", [])
    title = "Instagram Post"
    if caption_edges:
        raw_caption = caption_edges[0].get("node", {}).get("text", "")
        if raw_caption:
            title = raw_caption[:100]

    is_carousel = typename in ("XDTGraphSidecar", "GraphSidecar") or "edge_sidecar_to_children" in media
    is_video = media.get("is_video", False)

    all_formats: list[Format] = []
    thumbnails: list[str] = []

    if is_carousel:
        edges = media.get("edge_sidecar_to_children", {}).get("edges", [])
        for i, edge in enumerate(edges, start=1):
            node = edge.get("node", {})
            display_url = node.get("display_url")
            if display_url:
                thumbnails.append(display_url)

            if node.get("is_video") and node.get("video_url"):
                # Video slide
                video_url = node["video_url"]
                token = await _token_store_module.token_store.create_token(
                    download_url=video_url,
                    filename=build_filename("instagram", author, index=i, ext="mp4"),
                    content_type="video/mp4",
                )
                all_formats.append(Format(
                    id=f"ig-video-{i}",
                    label=f"Video {i}",
                    type="video/mp4",
                    size_mb=None,
                    download_url=f"/api/download?token={token}",
                ))
            elif display_url:
                # Photo slide
                token = await _token_store_module.token_store.create_token(
                    download_url=display_url,
                    filename=build_filename("instagram", author, index=i, ext="jpg"),
                    content_type="image/jpeg",
                )
                all_formats.append(Format(
                    id=f"ig-photo-{i}",
                    label=f"Foto {i}",
                    type="image/jpeg",
                    size_mb=None,
                    download_url=f"/api/download?token={token}",
                ))

    elif is_video:
        # Single video
        video_url = media.get("video_url")
        display_url = media.get("display_url")
        if display_url:
            thumbnails.append(display_url)
        if video_url:
            token = await _token_store_module.token_store.create_token(
                download_url=video_url,
                filename=build_filename("instagram", author, ext="mp4"),
                content_type="video/mp4",
            )
            all_formats.append(Format(
                id="ig-video",
                label="Video",
                type="video/mp4",
                size_mb=None,
                download_url=f"/api/download?token={token}",
            ))

    else:
        # Single photo
        display_url = media.get("display_url")
        if display_url:
            thumbnails.append(display_url)
            token = await _token_store_module.token_store.create_token(
                download_url=display_url,
                filename=build_filename("instagram", author, ext="jpg"),
                content_type="image/jpeg",
            )
            all_formats.append(Format(
                id="ig-photo",
                label="Foto",
                type="image/jpeg",
                size_mb=None,
                download_url=f"/api/download?token={token}",
            ))

    if not all_formats:
        raise RuntimeError(ERR_INSTAGRAM_PRIVATE)

    duration = media.get("video_duration") if is_video else None

    result = MediaResult(
        platform="instagram",
        title=title,
        author=author,
        thumbnail=thumbnails[0] if thumbnails else None,
        thumbnails=thumbnails,
        duration=int(duration) if duration else None,
        formats=all_formats,
    )
    await extraction_cache.set(original_url, result.model_dump())
    return result


async def _extract_via_ytdlp(url: str) -> MediaResult:
    """Fallback extraction using yt-dlp (works well for reels/single videos)."""
    loop = asyncio.get_running_loop()

    info = await loop.run_in_executor(None, extract_info_sync, url)

    # Handle playlist (multi-entry) from yt-dlp
    if info.get("_type") == "playlist" or "entries" in info:
        entries = [e for e in (info.get("entries") or []) if e is not None]
        title = info.get("title") or "Instagram Post"
        author = info.get("uploader_id") or info.get("uploader")
        all_formats: list[Format] = []
        thumbnails: list[str] = []

        for i, entry in enumerate(entries, start=1):
            thumb = extract_best_thumbnail(entry)
            if thumb:
                thumbnails.append(thumb)
            entry_formats = await build_formats(
                entry, video_index=i if len(entries) > 1 else 0,
                platform="instagram", author=author,
            )
            if entry_formats:
                all_formats.extend(entry_formats)

        if all_formats:
            result = MediaResult(
                platform="instagram",
                title=title,
                author=author,
                thumbnail=thumbnails[0] if thumbnails else None,
                thumbnails=thumbnails,
                duration=None,
                formats=all_formats,
            )
            await extraction_cache.set(url, result.model_dump())
            return result

    # Single entry
    title = info.get("title", "Unknown")
    author = info.get("uploader_id") or info.get("uploader")
    thumbnail = extract_best_thumbnail(info)
    duration = info.get("duration")
    formats = await build_formats(info, platform="instagram", author=author)

    if not formats:
        raise RuntimeError("No formats found via yt-dlp")

    result = MediaResult(
        platform="instagram",
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=[thumbnail] if thumbnail else [],
        duration=duration,
        formats=formats,
    )
    await extraction_cache.set(url, result.model_dump())
    return result


def _extract_shortcode(url: str) -> Optional[str]:
    match = re.search(r"instagram\.com/(?:p|reel|reels)/([A-Za-z0-9_-]+)", url)
    return match.group(1) if match else None
