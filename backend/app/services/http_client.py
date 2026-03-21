"""Shared httpx.AsyncClient pool for reuse across extractors."""

import httpx

_client: httpx.AsyncClient | None = None

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Mobile/15E148 Safari/604.1"
    ),
}


def get_http_client() -> httpx.AsyncClient:
    """Get or create the shared httpx client. Must be closed via close_http_client()."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            headers=_DEFAULT_HEADERS,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )
    return _client


async def close_http_client() -> None:
    """Close the shared client. Call during app shutdown."""
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None
