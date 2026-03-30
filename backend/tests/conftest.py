import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response
from unittest.mock import patch

from app.main import app
from app.services.token_store import TokenStore, TokenData


class MockTokenStore(TokenStore):
    def __init__(self, ttl_seconds: int = 5):
        super().__init__()
        self.TTL_SECONDS = ttl_seconds


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_token_store(monkeypatch):
    fresh_store = MockTokenStore(ttl_seconds=5)
    fresh_store._redis = None  # Force in-memory mode for tests
    monkeypatch.setattr("app.routers.download.token_store", fresh_store)
    monkeypatch.setattr("app.services.token_store.token_store", fresh_store)
    # Patch the token_store in extractor modules (accessed via _token_store_module)
    monkeypatch.setattr(
        "app.services.extractors.base._token_store_module.token_store", fresh_store
    )
    monkeypatch.setattr(
        "app.services.tiktok_extractor._token_store_module.token_store", fresh_store
    )
    monkeypatch.setattr(
        "app.services.facebook_fallback._token_store_module.token_store", fresh_store
    )
    return fresh_store


@pytest.fixture(autouse=True)
def reset_http_client_singleton():
    """Reset singleton httpx client before each test so respx.mock can intercept it."""
    import app.services.http_client as _http_client_module
    _http_client_module._client = None
    yield
    _http_client_module._client = None


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test to prevent 429 errors."""
    from app.routers.extract import limiter as extract_limiter
    from app.routers.download import limiter as download_limiter

    extract_limiter.reset()
    download_limiter.reset()
    yield


@pytest.fixture(autouse=True)
def reset_extraction_cache():
    """Clear extraction cache before each test to prevent cross-test contamination."""
    from app.services.cache import extraction_cache

    extraction_cache._memory.clear()
    yield
    extraction_cache._memory.clear()


@pytest.fixture
def mock_media_bytes():
    return b"\x00\x00\x00\x20ftypisom" + b"mock_video_data_" * 64


@pytest.fixture
def mock_upstream_media(mock_media_bytes):
    def _setup_mock(url: str, content: bytes = b"", status_code: int = 200):
        if not content:
            content = mock_media_bytes
        route = respx.route(method="GET", url=url).mock(
            return_value=Response(status_code=status_code, content=content)
        )
        return route

    with respx.mock:
        with patch("app.services.streamer.validate_public_url", side_effect=lambda url: url):
            yield _setup_mock


@pytest.fixture
def sample_twitter_video_token(mock_token_store):
    token = "test-token-twitter-video"
    mock_token_store._tokens[token] = TokenData(
        download_url="https://video.twimg.com/ext_tw_video/123/test.mp4",
        filename="twitter_video_123.mp4",
        content_type="video/mp4",
    )
    return token


@pytest.fixture
def sample_instagram_image_token(mock_token_store):
    token = "test-token-instagram-image"
    mock_token_store._tokens[token] = TokenData(
        download_url="https://scontent.cdninstagram.com/v/t51.123/image.jpg",
        filename="instagram_image_456.jpg",
        content_type="image/jpeg",
    )
    return token


@pytest.fixture
def expired_token(mock_token_store):
    import time

    token = "test-token-expired"
    mock_token_store._tokens[token] = TokenData(
        download_url="https://video.twimg.com/ext_tw_video/expired/test.mp4",
        filename="expired_video.mp4",
        content_type="video/mp4",
        created_at=time.time() - 400,
    )
    return token
