"""TikTok media extraction via TikWM API."""

from typing import Optional
import httpx
from app.schemas.extract import MediaResult, Format
import app.services.token_store as _token_store_module
from app.services.retry import with_retry
from app.services.http_client import get_http_client
from app.services.extractors.base import build_filename


class TikWMError(Exception):
    """Base exception for TikWM errors."""

    pass


class TikWMUnavailableError(TikWMError):
    """TikWM service is down or unreachable."""

    pass


class TikWMContentError(TikWMError):
    """Content not found, removed, or private."""

    pass


TIKWM_API_URL = "https://www.tikwm.com/api/"


async def extract_tiktok_media(url: str) -> MediaResult:
    """Extract media info from TikTok URL using TikWM API."""
    data = await with_retry(_fetch_tikwm_data, url, max_attempts=2, wait_seconds=1.0)
    return await _build_media_result(data)


async def _fetch_tikwm_data(url: str) -> dict:
    """Fetch data from TikWM API."""
    try:
        client = get_http_client()
        response = await client.post(
            TIKWM_API_URL,
            data={"url": url},
            headers={"User-Agent": "Mozilla/5.0 (compatible; CopasBot/1.0)"},
        )

        if response.status_code != 200:
            raise TikWMUnavailableError(
                "Layanan TikTok sedang tidak tersedia. Coba lagi nanti."
            )

        result = response.json()

        if result.get("code") != 0 or not result.get("data"):
            raise TikWMContentError(
                "Konten TikTok tidak ditemukan atau bersifat pribadi. "
                "Pastikan link dapat diakses publik."
            )

        return result["data"]

    except httpx.TimeoutException:
        raise TikWMUnavailableError("Layanan TikTok tidak merespons. Coba lagi nanti.")
    except httpx.RequestError:
        raise TikWMUnavailableError(
            "Gagal menghubungi layanan TikTok. Periksa koneksi Anda."
        )


async def _build_media_result(data: dict) -> MediaResult:
    """Build MediaResult from TikWM response data."""
    author = data.get("author", {}).get("nickname")
    title = data.get("title") or "Untitled"
    thumbnail = data.get("cover") or data.get("origin_cover")
    duration = data.get("duration")

    # Detect media type
    images = data.get("images", [])
    is_photo_mode = bool(images)

    if is_photo_mode:
        formats = await _build_photo_formats(data, author)
        thumbnails = (
            images[: len(formats)] if images else [thumbnail] if thumbnail else []
        )
    else:
        formats = await _build_video_formats(data, author)
        thumbnails = [thumbnail] if thumbnail else []

    if not formats:
        raise TikWMContentError(
            "Tidak ada format media yang tersedia untuk konten ini."
        )

    return MediaResult(
        platform="tiktok",
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=thumbnails,
        duration=duration,
        formats=formats,
    )


async def _build_video_formats(data: dict, author: Optional[str]) -> list[Format]:
    """Build video format options."""
    play_url = data.get("play")
    if not play_url:
        return []

    filename = build_filename("tiktok", author, ext="mp4")

    token = await _token_store_module.token_store.create_token(
        download_url=play_url, filename=filename, content_type="video/mp4"
    )

    size_mb = None
    if data.get("size"):
        size_mb = round(data["size"] / (1024 * 1024), 2)

    return [
        Format(
            id="tikwm-video",
            label="Video HD",
            type="video/mp4",
            size_mb=size_mb,
            download_url=f"/api/download?token={token}",
        )
    ]


async def _build_photo_formats(data: dict, author: Optional[str]) -> list[Format]:
    """Build photo format options for TikTok photo mode."""
    images = data.get("images", [])
    if not images:
        return []

    formats = []
    for i, img_url in enumerate(images, start=1):
        filename = build_filename("tiktok", author, index=i if len(images) > 1 else 0, ext="jpg")

        token = await _token_store_module.token_store.create_token(
            download_url=img_url, filename=filename, content_type="image/jpeg"
        )

        label = f"Foto {i}" if len(images) > 1 else "Foto"

        formats.append(
            Format(
                id=f"tikwm-photo-{i}",
                label=label,
                type="image/jpeg",
                size_mb=None,
                download_url=f"/api/download?token={token}",
            )
        )

    return formats
