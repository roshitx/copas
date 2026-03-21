"""Shared extraction utilities: yt-dlp wrapper, format building, filename generation."""

import os
import logging
from typing import Optional

import yt_dlp

from app.schemas.extract import Format
import app.services.token_store as _token_store_module
from app.services.retry import RetryableError
from .constants import (
    AUTH_KEYWORDS, EXTRACT_KEYWORDS, NETWORK_KEYWORDS,
    QUALITY_LABELS,
    ERR_AUTH_REQUIRED, ERR_EXTRACTION_FAILED, ERR_GENERIC_FAILURE,
)

logger = logging.getLogger(__name__)


def build_filename(
    platform: str, author: Optional[str] = None, index: int = 0, ext: str = "mp4"
) -> str:
    """Build standardized filename: {platform}_{author}_copas_io[_{index}].{ext}"""
    sanitized_author = author.replace(" ", "_") if author else None
    parts = [p for p in [platform or "copas", sanitized_author] if p]
    parts.append("copas_io")
    if index > 0:
        parts.append(str(index))
    return "_".join(parts) + f".{ext}"


def classify_download_error(error: yt_dlp.utils.DownloadError) -> Exception:
    """Classify a yt-dlp DownloadError into the appropriate exception type."""
    msg = str(error)
    msg_lower = msg.lower()

    if any(k in msg_lower for k in AUTH_KEYWORDS):
        return PermissionError(ERR_AUTH_REQUIRED)
    if any(k in msg_lower for k in EXTRACT_KEYWORDS):
        return RuntimeError(ERR_EXTRACTION_FAILED)
    if any(k in msg_lower for k in NETWORK_KEYWORDS):
        return RetryableError(f"Transient extraction error: {msg}")
    return RuntimeError(ERR_GENERIC_FAILURE.format(msg=msg))


def extract_info_sync(url: str, use_cookies: bool = True) -> dict:
    """Synchronous yt-dlp extraction with platform-aware options."""
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
        "extractor_args": {
            "instagram": {"api": ["graphql"]},
            "twitter": {"api": ["graphql"]},
        },
        "socket_timeout": 30,
    }

    if use_cookies:
        cookie_file = os.environ.get("YTDLP_COOKIE_FILE")
        if cookie_file and os.path.isfile(cookie_file):
            ydl_opts["cookiefile"] = cookie_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            raise classify_download_error(e) from e

    return info


async def create_format(
    fmt: dict, label: str, content_type: str,
    platform: str = "", author: Optional[str] = None, index: int = 0,
) -> Format:
    """Create a Format with download token from a yt-dlp format dict."""
    url = fmt.get("url")
    if not url:
        url = fmt.get("manifest_url") or fmt.get("fragment_base_url")
    if not url:
        raise ValueError("Format URL is required")

    ext = fmt.get("ext", "mp4")
    filename = build_filename(platform, author, index, ext)
    token = await _token_store_module.token_store.create_token(url, filename, content_type)

    filesize = fmt.get("filesize")
    size_mb = round(filesize / (1024 * 1024), 2) if filesize else None

    return Format(
        id=fmt.get("format_id", "unknown"),
        label=label,
        type=content_type,
        size_mb=size_mb,
        download_url=f"/api/download?token={token}",
    )


async def build_formats(
    info: dict, video_index: int = 0, platform: str = "", author: Optional[str] = None
) -> list[Format]:
    """Build format list from yt-dlp info dict."""
    formats: list[Format] = []
    has_video_formats = any(f.get("vcodec") != "none" for f in info.get("formats", []))

    if has_video_formats:
        formats = await _build_video_formats(info, video_index, platform, author)
    else:
        formats = await _build_audio_formats(info, platform, author)

    return formats


async def _build_video_formats(
    info: dict, video_index: int, platform: str, author: Optional[str]
) -> list[Format]:
    """Extract and deduplicate video formats from yt-dlp info."""
    video_formats = []
    for fmt in info.get("formats", []):
        if fmt.get("vcodec") != "none" and fmt.get("acodec") != "none":
            video_formats.append(fmt)
        elif fmt.get("vcodec") != "none":
            video_formats.append(fmt)

    seen = set()
    unique_formats = []
    for fmt in video_formats:
        key = (fmt.get("height"), fmt.get("ext"))
        if key not in seen:
            seen.add(key)
            unique_formats.append(fmt)

    unique_formats.sort(key=lambda f: (-(f.get("height") or 0), 0 if f.get("ext") == "mp4" else 1))

    quality_map: dict = {}
    for fmt in unique_formats:
        height = fmt.get("height")
        if height and height not in quality_map:
            quality_map[height] = fmt

    formats: list[Format] = []
    for height in sorted(quality_map.keys(), reverse=True):
        fmt = quality_map[height]
        quality = QUALITY_LABELS.get(height, f"{height}p")
        label = f"Video {video_index} · {quality}" if video_index > 0 else f"Video {quality}"
        try:
            formats.append(await create_format(fmt, label, "video/mp4", platform=platform, author=author))
        except ValueError:
            pass

    if not formats and unique_formats:
        for best in unique_formats:
            try:
                height = best.get("height", "unknown")
                quality = QUALITY_LABELS.get(height, f"{height}p") if isinstance(height, int) else f"{height}p"
                fallback_label = f"Video {video_index} · {quality}" if video_index > 0 else f"Video {quality}"
                formats.append(await create_format(best, fallback_label, "video/mp4", platform=platform, author=author))
                break
            except ValueError:
                continue

    return formats


async def _build_audio_formats(
    info: dict, platform: str, author: Optional[str]
) -> list[Format]:
    """Extract best audio format from yt-dlp info."""
    audio_formats = [f for f in info.get("formats", []) if f.get("acodec") != "none"]
    if not audio_formats:
        return []

    audio_formats.sort(key=lambda f: f.get("abr", 0) or 0, reverse=True)
    best_audio = audio_formats[0]

    return [await create_format(best_audio, "Audio MP3", "audio/mp3", platform=platform, author=author)]


def extract_best_thumbnail(info: dict) -> Optional[str]:
    """Extract best thumbnail URL from yt-dlp info dict."""
    thumbnail = info.get("thumbnail")
    if not thumbnail:
        info_thumbs = info.get("thumbnails") or []
        for t in reversed(info_thumbs):
            if t.get("url"):
                return t["url"]
    return thumbnail
