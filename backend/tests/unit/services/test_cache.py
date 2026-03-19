"""Unit tests for extraction cache."""

import pytest

from app.services.cache import ExtractionCache


@pytest.mark.unit
class TestExtractionCache:
    """Test suite for ExtractionCache."""

    @pytest.fixture
    def memory_cache(self):
        """Cache with no Redis (in-memory mode)."""
        return ExtractionCache(redis=None)

    @pytest.fixture
    def redis_cache(self):
        """Cache backed by fakeredis."""
        import fakeredis.aioredis
        fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
        return ExtractionCache(redis=fake)

    @pytest.mark.asyncio
    async def test_get_returns_none_on_miss_memory(self, memory_cache):
        result = await memory_cache.get("https://example.com/video")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_memory(self, memory_cache):
        data = {"platform": "youtube", "title": "Test"}
        await memory_cache.set("https://example.com/video", data)
        result = await memory_cache.get("https://example.com/video")
        assert result == data

    @pytest.mark.asyncio
    async def test_get_returns_none_on_miss_redis(self, redis_cache):
        result = await redis_cache.get("https://example.com/video")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_redis(self, redis_cache):
        data = {"platform": "youtube", "title": "Test"}
        await redis_cache.set("https://example.com/video", data)
        result = await redis_cache.get("https://example.com/video")
        assert result == data

    @pytest.mark.asyncio
    async def test_different_urls_different_keys(self, memory_cache):
        await memory_cache.set("https://example.com/a", {"title": "A"})
        await memory_cache.set("https://example.com/b", {"title": "B"})
        assert (await memory_cache.get("https://example.com/a"))["title"] == "A"
        assert (await memory_cache.get("https://example.com/b"))["title"] == "B"

    @pytest.mark.asyncio
    async def test_invalidate_memory(self, memory_cache):
        await memory_cache.set("https://example.com/video", {"title": "X"})
        await memory_cache.invalidate("https://example.com/video")
        result = await memory_cache.get("https://example.com/video")
        assert result is None

    @pytest.mark.asyncio
    async def test_invalidate_redis(self, redis_cache):
        await redis_cache.set("https://example.com/video", {"title": "X"})
        await redis_cache.invalidate("https://example.com/video")
        result = await redis_cache.get("https://example.com/video")
        assert result is None
