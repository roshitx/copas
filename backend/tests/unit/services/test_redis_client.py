"""Unit tests for Redis client module."""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.unit
class TestGetRedis:
    """Test Redis client initialization."""

    @pytest.fixture(autouse=True)
    def reset_module_state(self):
        """Reset module-level state before each test."""
        from app.services import redis_client
        redis_client._redis = None
        redis_client._initialized = False
        yield
        redis_client._redis = None
        redis_client._initialized = False

    @pytest.mark.asyncio
    async def test_returns_none_when_no_redis_url(self):
        """Returns None when REDIS_URL is not configured."""
        with patch.dict("os.environ", {}, clear=True):
            from app.services.redis_client import get_redis
            client = await get_redis()
            assert client is None

    @pytest.mark.asyncio
    async def test_returns_client_when_redis_url_set(self):
        """Returns a Redis client when REDIS_URL is configured."""
        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
            with patch("app.services.redis_client.Redis.from_url") as mock_from_url:
                mock_client = AsyncMock()
                mock_client.ping = AsyncMock(return_value=True)
                mock_from_url.return_value = mock_client
                from app.services.redis_client import get_redis
                client = await get_redis()
                assert client is not None

    @pytest.mark.asyncio
    async def test_caches_redis_connection(self):
        """Subsequent calls return the same client instance."""
        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
            with patch("app.services.redis_client.Redis.from_url") as mock_from_url:
                mock_client = AsyncMock()
                mock_client.ping = AsyncMock(return_value=True)
                mock_from_url.return_value = mock_client
                from app.services.redis_client import get_redis
                client1 = await get_redis()
                client2 = await get_redis()
                assert client1 is client2
                mock_from_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_none_on_connection_failure(self):
        """Returns None when Redis connection fails."""
        with patch.dict("os.environ", {"REDIS_URL": "redis://badhost:6379/0"}):
            with patch("app.services.redis_client.Redis.from_url") as mock_from_url:
                mock_client = AsyncMock()
                mock_client.ping = AsyncMock(side_effect=ConnectionError("refused"))
                mock_from_url.return_value = mock_client
                from app.services.redis_client import get_redis
                client = await get_redis()
                assert client is None
