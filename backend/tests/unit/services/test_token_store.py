"""
Unit tests for token_store.py

Tests token lifecycle: create, get, expire, cleanup
"""

import asyncio
import time

import pytest

from app.services.token_store import TokenStore, TokenData


@pytest.mark.unit
class TestTokenStore:
    """Test suite for TokenStore class."""

    @pytest.fixture
    def store(self):
        """Fresh TokenStore instance for each test."""
        return TokenStore()

    @pytest.mark.asyncio
    async def test_create_token_returns_valid_uuid(self, store):
        """Token creation returns a valid UUID4 string."""
        token = await store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test_video.mp4",
            content_type="video/mp4",
        )

        assert isinstance(token, str)
        assert len(token) == 36  # UUID4 length
        assert token.count("-") == 4  # UUID4 format

    @pytest.mark.asyncio
    async def test_create_token_stores_data(self, store):
        """Token creation stores correct data."""
        url = "https://example.com/video.mp4"
        filename = "my_video.mp4"
        content_type = "video/mp4"

        token = await store.create_token(url, filename, content_type)
        data = await store.get_token(token)

        assert data is not None
        assert data.download_url == url
        assert data.filename == filename
        assert data.content_type == content_type
        assert isinstance(data.created_at, float)

    @pytest.mark.asyncio
    async def test_get_token_returns_none_for_missing(self, store):
        """Getting non-existent token returns None."""
        result = await store.get_token("non-existent-token-12345")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_token_returns_none_for_expired(self, store):
        """Expired tokens are deleted and None is returned."""
        # Create token normally
        token = await store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )

        # Manually set created_at to past time (more than TTL ago)
        async with store._lock:
            store._tokens[token].created_at = time.time() - 400  # 400 seconds ago

        result = await store.get_token(token)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_token_valid_within_ttl(self, store):
        """Tokens within TTL are returned successfully."""
        token = await store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )

        # Manually set created_at to recent time (within TTL)
        async with store._lock:
            store._tokens[token].created_at = time.time() - 100  # 100 seconds ago

        result = await store.get_token(token)
        assert result is not None
        assert result.download_url == "https://example.com/video.mp4"

    @pytest.mark.asyncio
    async def test_get_token_exactly_at_ttl_boundary(self, store):
        """Tokens exactly at TTL boundary are considered expired."""
        token = await store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )

        # Manually set created_at to exactly at TTL boundary
        async with store._lock:
            store._tokens[token].created_at = (
                time.time() - 300
            )  # Exactly 300 seconds ago

        result = await store.get_token(token)
        assert result is None

    @pytest.mark.asyncio
    async def test_cleanup_expired_removes_only_expired(self, store):
        """Cleanup only removes expired tokens, keeps valid ones."""
        # Create two tokens
        expired_token = await store.create_token(
            download_url="https://example.com/old.mp4",
            filename="old.mp4",
            content_type="video/mp4",
        )

        valid_token = await store.create_token(
            download_url="https://example.com/new.mp4",
            filename="new.mp4",
            content_type="video/mp4",
        )

        # Manually set created_at times
        async with store._lock:
            store._tokens[expired_token].created_at = time.time() - 400  # Expired
            store._tokens[valid_token].created_at = time.time() - 100  # Valid

        await store.cleanup_expired()

        # Check results - expired should be removed, valid should remain
        assert await store.get_token(expired_token) is None
        assert await store.get_token(valid_token) is not None

    @pytest.mark.asyncio
    async def test_cleanup_expired_empty_store(self, store):
        """Cleanup on empty store does not raise errors."""
        await store.cleanup_expired()  # Should not raise
        assert len(store._tokens) == 0

    @pytest.mark.asyncio
    async def test_concurrent_access(self, store):
        """Token store handles concurrent access safely."""
        tokens = []

        async def create_multiple():
            for i in range(10):
                token = await store.create_token(
                    download_url=f"https://example.com/video{i}.mp4",
                    filename=f"video{i}.mp4",
                    content_type="video/mp4",
                )
                tokens.append(token)

        # Run multiple creators concurrently
        await asyncio.gather(create_multiple(), create_multiple(), create_multiple())

        # All tokens should be retrievable
        assert len(tokens) == 30
        for token in tokens:
            data = await store.get_token(token)
            assert data is not None

    @pytest.mark.asyncio
    async def test_token_ttl_constant(self):
        """TTL is configured to 300 seconds (5 minutes)."""
        assert TokenStore.TTL_SECONDS == 300


@pytest.mark.unit
class TestTokenData:
    """Test suite for TokenData dataclass."""

    def test_token_data_creation(self):
        """TokenData can be created with all fields."""
        data = TokenData(
            download_url="https://example.com/file.mp4",
            filename="file.mp4",
            content_type="video/mp4",
            created_at=1234567890.0,
        )

        assert data.download_url == "https://example.com/file.mp4"
        assert data.filename == "file.mp4"
        assert data.content_type == "video/mp4"
        assert data.created_at == 1234567890.0

    def test_token_data_default_timestamp(self):
        """TokenData uses current time as default for created_at."""
        before = time.time()
        data = TokenData(
            download_url="https://example.com/file.mp4",
            filename="file.mp4",
            content_type="video/mp4",
        )
        after = time.time()

        assert before <= data.created_at <= after


@pytest.mark.unit
class TestRedisTokenStore:
    """Tests for Redis-backed token store behavior."""

    @pytest.fixture
    def redis_store(self):
        """TokenStore backed by fakeredis."""
        import fakeredis.aioredis
        fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        store = TokenStore()
        store._redis = fake_redis
        return store

    @pytest.mark.asyncio
    async def test_create_token_stores_in_redis(self, redis_store):
        """Token is stored in Redis when Redis is available."""
        token = await redis_store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )
        assert isinstance(token, str)
        assert len(token) == 36
        data = await redis_store.get_token(token)
        assert data is not None
        assert data.download_url == "https://example.com/video.mp4"

    @pytest.mark.asyncio
    async def test_redis_token_not_in_memory_dict(self, redis_store):
        """When Redis is available, tokens should NOT be in the in-memory dict."""
        token = await redis_store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )
        assert token not in redis_store._tokens

    @pytest.mark.asyncio
    async def test_redis_token_expiry(self, redis_store):
        """Redis token respects TTL — expired tokens return None."""
        token = await redis_store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )
        await redis_store._redis.delete(f"token:{token}")
        result = await redis_store.get_token(token)
        assert result is None

    @pytest.mark.asyncio
    async def test_fallback_to_memory_when_redis_none(self):
        """Falls back to in-memory when Redis is None."""
        store = TokenStore()
        store._redis = None
        token = await store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )
        assert token in store._tokens
        data = await store.get_token(token)
        assert data is not None

    @pytest.mark.asyncio
    async def test_cleanup_noop_with_redis(self, redis_store):
        """cleanup_expired is a no-op when Redis is available."""
        token = await redis_store.create_token(
            download_url="https://example.com/video.mp4",
            filename="test.mp4",
            content_type="video/mp4",
        )
        await redis_store.cleanup_expired()
        data = await redis_store.get_token(token)
        assert data is not None


@pytest.mark.unit
class TestTokenDataSerialization:
    """Test TokenData JSON serialization round-trip."""

    def test_to_json_and_from_json(self):
        original = TokenData(
            download_url="https://example.com/file.mp4",
            filename="file.mp4",
            content_type="video/mp4",
            created_at=1234567890.0,
        )
        json_str = original.to_json()
        restored = TokenData.from_json(json_str)
        assert restored.download_url == original.download_url
        assert restored.filename == original.filename
        assert restored.content_type == original.content_type
        assert restored.created_at == original.created_at
