import httpx
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator


async def stream_media(url: str, filename: str, content_type: str) -> StreamingResponse:

    # Determine appropriate headers based on the CDN being accessed
    def _build_headers(target_url: str) -> dict:
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

    async def generate() -> AsyncGenerator[bytes, None]:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream("GET", url, headers=_build_headers(url)) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes(chunk_size=32768):
                    yield chunk

    return StreamingResponse(
        generate(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
