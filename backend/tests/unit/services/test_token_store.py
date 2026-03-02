"""
Unit tests for token_store.py

Tests token lifecycle: create, get, expire, cleanup
"""

import asyncio
import time
from unittest.mock import patch

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
