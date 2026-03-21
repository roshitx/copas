import httpx
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from urllib.parse import quote

from app.utils.url_validator import validate_public_url


def _build_content_disposition(filename: str) -> str:
    cleaned_filename = filename.replace("\r", "").replace("\n", "").replace('"', "")
    if not cleaned_filename:
        cleaned_filename = "download"

    latin1_fallback = cleaned_filename.encode("latin-1", errors="ignore").decode(
        "latin-1"
    )
    if not latin1_fallback:
        latin1_fallback = "download"

    if latin1_fallback == cleaned_filename:
        return f'attachment; filename="{latin1_fallback}"'

    encoded_utf8_filename = quote(cleaned_filename, safe="")
    return (
        f'attachment; filename="{latin1_fallback}"; '
        f"filename*=UTF-8''{encoded_utf8_filename}"
    )


def _build_headers(target_url: str) -> dict[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    if "twimg.com" in target_url or "twitter.com" in target_url:
        headers["Referer"] = "https://twitter.com/"
    elif "cdninstagram.com" in target_url or "fbcdn.net" in target_url:
        headers["Referer"] = "https://www.instagram.com/"
    elif "tiktokcdn" in target_url or "tiktok.com" in target_url:
        headers["Referer"] = "https://www.tiktok.com/"
    return headers


async def stream_media(url: str, filename: str, content_type: str) -> StreamingResponse:
    validate_public_url(url)

    async def generate() -> AsyncGenerator[bytes, None]:
        # Streaming requires a dedicated client (can't use shared pool for long-lived streams)
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream(
                "GET", url, headers=_build_headers(url)
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes(chunk_size=32768):
                    yield chunk

    return StreamingResponse(
        generate(),
        media_type=content_type,
        headers={
            "Content-Disposition": _build_content_disposition(filename),
        },
    )
