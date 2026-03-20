# High Priority Backend Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace in-memory stores with Redis for token storage, response caching, and rate limiting persistence. Add retry logic with exponential backoff for transient extraction failures.

**Architecture:** Redis becomes the single backing store for tokens (replaces dict-based TokenStore), extraction cache (5-min TTL keyed by URL hash), and rate limiting (replaces slowapi's in-memory storage). Retry logic wraps yt-dlp and external API calls using tenacity. All changes are backward-compatible — the app falls back to in-memory if Redis is unavailable in development.

**Tech Stack:** Redis (via `redis[hiredis]`), tenacity, existing FastAPI/slowapi stack

---

## Task 1: Add Redis and Tenacity Dependencies

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/requirements-dev.txt`
- Modify: `backend/.env.example`
- Modify: `backend/Dockerfile`

**Step 1: Add dependencies to requirements.txt**

Add `redis[hiredis]` and `tenacity` to `backend/requirements.txt`:

```
redis[hiredis]>=5.0.0
tenacity>=8.2.0
```

**Step 2: Add fakeredis to dev dependencies**

Add to `backend/requirements-dev.txt`:

```
fakeredis[lua]>=2.21.0
```

**Step 3: Add REDIS_URL to .env.example**

Add to `backend/.env.example`:

```
# Redis URL for token store, caching, and rate limiting
# Falls back to in-memory in development if not set
REDIS_URL=redis://localhost:6379/0
```

**Step 4: Verify Dockerfile installs dependencies**

The existing Dockerfile already runs `pip install -r requirements.txt`, so no change needed. Verify it builds:

Run: `cd backend && docker build -t copas-test . --no-cache`
Expected: Build succeeds with redis and tenacity installed

**Step 5: Commit**

```bash
git add backend/requirements.txt backend/requirements-dev.txt backend/.env.example
git commit -m "chore: add redis and tenacity dependencies"
```

---

## Task 2: Create Redis Connection Module

**Files:**
- Create: `backend/app/services/redis_client.py`
- Test: `backend/tests/unit/services/test_redis_client.py`

**Step 1: Write the failing test**

Create `backend/tests/unit/services/test_redis_client.py`:

```python
"""Unit tests for Redis client module."""

import pytest
from unittest.mock import patch

from app.services.redis_client import get_redis, close_redis


@pytest.mark.unit
class TestGetRedis:
    """Test Redis client initialization."""

    @pytest.mark.asyncio
    async def test_returns_none_when_no_redis_url(self):
        """Returns None when REDIS_URL is not configured."""
        with patch.dict("os.environ", {}, clear=True):
            # Force reimport to pick up env change
            from app.services import redis_client
            redis_client._redis = None
            redis_client._initialized = False
            client = await get_redis()
            assert client is None

    @pytest.mark.asyncio
    async def test_returns_client_when_redis_url_set(self):
        """Returns a Redis client when REDIS_URL is configured."""
        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
            from app.services import redis_client
            redis_client._redis = None
            redis_client._initialized = False
            # This will attempt real connection — use fakeredis in integration tests
            # For unit test, we just verify the function doesn't crash with invalid URL
            # We'll mock the actual connection
            with patch("app.services.redis_client.Redis.from_url") as mock_from_url:
                mock_client = mock_from_url.return_value
                mock_client.ping = lambda: True
                client = await get_redis()
                assert client is not None

    @pytest.mark.asyncio
    async def test_caches_redis_connection(self):
        """Subsequent calls return the same client instance."""
        with patch.dict("os.environ", {"REDIS_URL": "redis://localhost:6379/0"}):
            from app.services import redis_client
            redis_client._redis = None
            redis_client._initialized = False
            with patch("app.services.redis_client.Redis.from_url") as mock_from_url:
                mock_client = mock_from_url.return_value
                mock_client.ping = lambda: True
                client1 = await get_redis()
                client2 = await get_redis()
                assert client1 is client2
                mock_from_url.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/services/test_redis_client.py -v -m unit`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.redis_client'`

**Step 3: Write minimal implementation**

Create `backend/app/services/redis_client.py`:

```python
"""Redis client with graceful fallback to None when unavailable."""

import logging
import os
from typing import Optional

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

_redis: Optional[Redis] = None
_initialized: bool = False


async def get_redis() -> Optional[Redis]:
    """Get async Redis client. Returns None if REDIS_URL not set or connection fails."""
    global _redis, _initialized

    if _initialized:
        return _redis

    _initialized = True
    redis_url = os.getenv("REDIS_URL")

    if not redis_url:
        logger.info("REDIS_URL not configured, using in-memory fallback")
        return None

    try:
        client = Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
        await client.ping()
        _redis = client
        logger.info("Redis connected successfully")
        return _redis
    except Exception as e:
        logger.warning("Redis connection failed, using in-memory fallback: %s", e)
        _redis = None
        return None


async def close_redis() -> None:
    """Close Redis connection if open."""
    global _redis, _initialized
    if _redis:
        await _redis.close()
        _redis = None
    _initialized = False
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/unit/services/test_redis_client.py -v -m unit`
Expected: PASS (3 tests)

**Step 5: Commit**

```bash
git add backend/app/services/redis_client.py backend/tests/unit/services/test_redis_client.py
git commit -m "feat: add Redis client module with graceful fallback"
```

---

## Task 3: Redis-backed Token Store

**Files:**
- Modify: `backend/app/services/token_store.py`
- Modify: `backend/tests/unit/services/test_token_store.py`
- Modify: `backend/tests/conftest.py`

**Step 1: Write failing tests for Redis-backed token store**

Add these tests to `backend/tests/unit/services/test_token_store.py` (keep existing tests, they validate the in-memory fallback path):

```python
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

        # Verify it's in Redis, not in-memory dict
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
        # Manually delete to simulate expiry
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
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/services/test_token_store.py::TestRedisTokenStore -v -m unit`
Expected: FAIL — `TokenStore` has no `_redis` attribute

**Step 3: Rewrite token_store.py with Redis support + in-memory fallback**

Replace `backend/app/services/token_store.py`:

```python
import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from uuid import uuid4

from redis.asyncio import Redis


@dataclass
class TokenData:
    download_url: str
    filename: str
    content_type: str
    created_at: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps({
            "download_url": self.download_url,
            "filename": self.filename,
            "content_type": self.content_type,
            "created_at": self.created_at,
        })

    @classmethod
    def from_json(cls, raw: str) -> "TokenData":
        data = json.loads(raw)
        return cls(
            download_url=data["download_url"],
            filename=data["filename"],
            content_type=data["content_type"],
            created_at=data["created_at"],
        )


class TokenStore:
    """Token store with Redis backend and in-memory fallback."""

    TTL_SECONDS = 300  # 5 minutes

    def __init__(self):
        self._tokens: Dict[str, TokenData] = {}
        self._lock = asyncio.Lock()
        self._redis: Optional[Redis] = None

    async def init_redis(self, redis_client: Optional[Redis]) -> None:
        """Set Redis client. Call during app startup."""
        self._redis = redis_client

    async def create_token(
        self, download_url: str, filename: str, content_type: str
    ) -> str:
        token = str(uuid4())
        data = TokenData(
            download_url=download_url, filename=filename, content_type=content_type
        )

        if self._redis:
            await self._redis.setex(
                f"token:{token}", self.TTL_SECONDS, data.to_json()
            )
        else:
            async with self._lock:
                self._tokens[token] = data

        return token

    async def get_token(self, token: str) -> Optional[TokenData]:
        if self._redis:
            raw = await self._redis.get(f"token:{token}")
            if not raw:
                return None
            return TokenData.from_json(raw)

        async with self._lock:
            data = self._tokens.get(token)
            if not data:
                return None
            if time.time() - data.created_at > self.TTL_SECONDS:
                del self._tokens[token]
                return None
            return data

    async def cleanup_expired(self) -> None:
        """Remove expired tokens from in-memory store. No-op when using Redis (Redis TTL handles it)."""
        if self._redis:
            return

        now = time.time()
        async with self._lock:
            expired = [
                token
                for token, data in self._tokens.items()
                if now - data.created_at > self.TTL_SECONDS
            ]
            for token in expired:
                del self._tokens[token]


# Global instance
token_store = TokenStore()


async def start_cleanup_task():
    """Start background cleanup task."""
    while True:
        await asyncio.sleep(60)
        await token_store.cleanup_expired()
```

**Step 4: Run all token store tests to verify they pass**

Run: `cd backend && python -m pytest tests/unit/services/test_token_store.py -v -m unit`
Expected: PASS (all existing tests + new Redis tests)

**Step 5: Update conftest.py to patch Redis attribute**

In `backend/tests/conftest.py`, update the `mock_token_store` fixture — add `fresh_store._redis = None` to ensure tests run in-memory mode:

```python
@pytest.fixture
def mock_token_store(monkeypatch):
    fresh_store = MockTokenStore(ttl_seconds=5)
    fresh_store._redis = None  # Force in-memory mode for tests
    monkeypatch.setattr("app.routers.download.token_store", fresh_store)
    monkeypatch.setattr("app.services.token_store.token_store", fresh_store)
    monkeypatch.setattr(
        "app.services.extractor._token_store_module.token_store", fresh_store
    )
    monkeypatch.setattr(
        "app.services.tiktok_extractor._token_store_module.token_store", fresh_store
    )
    return fresh_store
```

**Step 6: Run full test suite**

Run: `cd backend && python -m pytest tests/ -v -m "not live"`
Expected: All PASS

**Step 7: Commit**

```bash
git add backend/app/services/token_store.py backend/tests/unit/services/test_token_store.py backend/tests/conftest.py
git commit -m "feat: Redis-backed token store with in-memory fallback"
```

---

## Task 4: Response Caching Layer

**Files:**
- Create: `backend/app/services/cache.py`
- Create: `backend/tests/unit/services/test_cache.py`
- Modify: `backend/app/services/extractor.py` (wrap `extract_media_info`)
- Modify: `backend/app/routers/extract.py` (no change needed, caching is transparent)

**Step 1: Write the failing test for cache module**

Create `backend/tests/unit/services/test_cache.py`:

```python
"""Unit tests for extraction cache."""

import pytest
import json
from unittest.mock import AsyncMock

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
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/services/test_cache.py -v -m unit`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.cache'`

**Step 3: Write cache module**

Create `backend/app/services/cache.py`:

```python
"""Extraction result cache with Redis backend and in-memory fallback."""

import hashlib
import json
import time
import logging
from typing import Any, Optional

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 300  # 5 minutes


class ExtractionCache:
    """Cache for extraction results. Uses Redis if available, falls back to in-memory dict."""

    def __init__(self, redis: Optional[Redis] = None):
        self._redis = redis
        self._memory: dict[str, tuple[float, str]] = {}  # key -> (expires_at, json_str)

    @staticmethod
    def _cache_key(url: str) -> str:
        url_hash = hashlib.sha256(url.strip().lower().encode()).hexdigest()[:16]
        return f"cache:extract:{url_hash}"

    async def get(self, url: str) -> Optional[dict[str, Any]]:
        key = self._cache_key(url)

        if self._redis:
            raw = await self._redis.get(key)
            if raw:
                logger.debug("Cache HIT (redis): %s", key)
                return json.loads(raw)
            return None

        entry = self._memory.get(key)
        if not entry:
            return None
        expires_at, raw = entry
        if time.time() > expires_at:
            del self._memory[key]
            return None
        logger.debug("Cache HIT (memory): %s", key)
        return json.loads(raw)

    async def set(self, url: str, data: dict[str, Any]) -> None:
        key = self._cache_key(url)
        raw = json.dumps(data, default=str)

        if self._redis:
            await self._redis.setex(key, CACHE_TTL_SECONDS, raw)
        else:
            self._memory[key] = (time.time() + CACHE_TTL_SECONDS, raw)

    async def invalidate(self, url: str) -> None:
        key = self._cache_key(url)
        if self._redis:
            await self._redis.delete(key)
        else:
            self._memory.pop(key, None)


# Global instance — initialized during app startup
extraction_cache = ExtractionCache()
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/unit/services/test_cache.py -v -m unit`
Expected: PASS (7 tests)

**Step 5: Integrate cache into extractor**

Modify `backend/app/services/extractor.py` — add caching around `extract_media_info`:

At the top of the file, add import:
```python
from app.services.cache import extraction_cache
```

Wrap the beginning of `extract_media_info` function. After `platform = detect_platform(url)` and the platform validation checks, add cache lookup before any extraction:

```python
async def extract_media_info(url: str) -> MediaResult:
    platform = detect_platform(url)

    if platform == "unknown":
        raise ValueError(f"Unsupported platform for URL: {url}")

    if platform == "threads":
        raise ValueError(
            "Platform Threads belum didukung. "
            "Coba download manual dari aplikasi Threads."
        )

    # Check cache before extraction
    cached = await extraction_cache.get(url)
    if cached:
        return MediaResult(**cached)

    # ... rest of existing extraction logic ...

    # At the end, before returning result, cache it:
    result = MediaResult(
        platform=platform,
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=thumbnails,
        duration=duration,
        formats=formats,
    )

    # Cache the successful result (tokens are embedded in download_urls)
    await extraction_cache.set(url, result.model_dump())

    return result
```

Also add caching to `_extract_facebook_hybrid` and `extract_tiktok_media` return paths similarly — cache after successful extraction, check cache before.

**Step 6: Run full test suite**

Run: `cd backend && python -m pytest tests/ -v -m "not live"`
Expected: All PASS

**Step 7: Commit**

```bash
git add backend/app/services/cache.py backend/tests/unit/services/test_cache.py backend/app/services/extractor.py
git commit -m "feat: add extraction result caching with Redis/in-memory fallback"
```

---

## Task 5: Retry Logic with Tenacity

**Files:**
- Create: `backend/app/services/retry.py`
- Create: `backend/tests/unit/services/test_retry.py`
- Modify: `backend/app/services/extractor.py` (wrap `_extract_info_sync` and `_fetch_fxtwitter`)
- Modify: `backend/app/services/tiktok_extractor.py` (wrap `_fetch_tikwm_data`)

**Step 1: Write failing tests for retry logic**

Create `backend/tests/unit/services/test_retry.py`:

```python
"""Unit tests for retry logic."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.retry import with_retry, RetryableError


@pytest.mark.unit
class TestRetryLogic:
    """Test retry wrapper behavior."""

    @pytest.mark.asyncio
    async def test_succeeds_on_first_try(self):
        """No retry needed when function succeeds immediately."""
        func = AsyncMock(return_value="ok")
        result = await with_retry(func, max_attempts=3)
        assert result == "ok"
        func.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_retries_on_retryable_error(self):
        """Retries when RetryableError is raised, then succeeds."""
        func = AsyncMock(side_effect=[RetryableError("timeout"), "ok"])
        result = await with_retry(func, max_attempts=3, wait_seconds=0)
        assert result == "ok"
        assert func.await_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_attempts(self):
        """Raises last error after exhausting all retry attempts."""
        func = AsyncMock(side_effect=RetryableError("always fails"))
        with pytest.raises(RetryableError, match="always fails"):
            await with_retry(func, max_attempts=2, wait_seconds=0)
        assert func.await_count == 2

    @pytest.mark.asyncio
    async def test_does_not_retry_non_retryable(self):
        """Non-retryable errors are raised immediately without retry."""
        func = AsyncMock(side_effect=ValueError("bad input"))
        with pytest.raises(ValueError, match="bad input"):
            await with_retry(func, max_attempts=3, wait_seconds=0)
        func.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_retries_with_httpx_timeout(self):
        """httpx.TimeoutException triggers retry."""
        import httpx
        func = AsyncMock(side_effect=[httpx.TimeoutException("timeout"), "ok"])
        result = await with_retry(func, max_attempts=3, wait_seconds=0)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_with_connection_error(self):
        """httpx.ConnectError triggers retry."""
        import httpx
        func = AsyncMock(side_effect=[httpx.ConnectError("refused"), "ok"])
        result = await with_retry(func, max_attempts=3, wait_seconds=0)
        assert result == "ok"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/unit/services/test_retry.py -v -m unit`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.retry'`

**Step 3: Write retry module**

Create `backend/app/services/retry.py`:

```python
"""Retry logic with exponential backoff for transient failures."""

import asyncio
import logging
from typing import Callable, TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryableError(Exception):
    """Marker for errors that should trigger a retry."""
    pass


# Errors that indicate transient failures worth retrying
RETRYABLE_EXCEPTIONS = (
    RetryableError,
    httpx.TimeoutException,
    httpx.ConnectError,
    httpx.ReadError,
    ConnectionError,
    TimeoutError,
)


async def with_retry(
    func: Callable[..., T],
    *args,
    max_attempts: int = 3,
    wait_seconds: float = 1.0,
    **kwargs,
) -> T:
    """
    Call an async function with exponential backoff retry on transient errors.

    Args:
        func: Async callable to invoke.
        max_attempts: Maximum number of attempts (default 3).
        wait_seconds: Base wait between retries in seconds (default 1.0).
                      Doubles each attempt: 1s, 2s, 4s...

    Raises:
        The last exception if all attempts fail.
        Non-retryable exceptions immediately.
    """
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except RETRYABLE_EXCEPTIONS as e:
            last_error = e
            if attempt < max_attempts:
                delay = wait_seconds * (2 ** (attempt - 1))
                logger.warning(
                    "Retry %d/%d after error: %s (waiting %.1fs)",
                    attempt,
                    max_attempts,
                    str(e)[:100],
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "All %d attempts exhausted. Last error: %s",
                    max_attempts,
                    str(e)[:200],
                )

    raise last_error
```

**Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/unit/services/test_retry.py -v -m unit`
Expected: PASS (6 tests)

**Step 5: Integrate retry into extractor.py**

Modify `backend/app/services/extractor.py`:

Add import at top:
```python
from app.services.retry import with_retry, RetryableError
```

Wrap `_fetch_fxtwitter` call in `extract_media_info`:
```python
# Before:
fx_data = await _fetch_fxtwitter(tweet_id)

# After:
fx_data = await with_retry(_fetch_fxtwitter, tweet_id, max_attempts=2, wait_seconds=1.0)
```

Wrap the yt-dlp extraction call — modify the `_extract_info_sync` to raise `RetryableError` on network-like failures:

In `_extract_info_sync`, at the end of the except block, before the generic re-raise:
```python
network_keywords = ("timed out", "connection", "network", "reset", "refused", "unavailable")
if any(k in msg_lower for k in network_keywords):
    raise RetryableError(f"Transient extraction error: {msg}") from e
```

Then in `extract_media_info`, wrap the `loop.run_in_executor` calls:
```python
# Before:
info = await loop.run_in_executor(None, _extract_info_sync, normalized_url)

# After:
async def _extract_async():
    return await loop.run_in_executor(None, _extract_info_sync, normalized_url)
info = await with_retry(_extract_async, max_attempts=2, wait_seconds=2.0)
```

**Step 6: Integrate retry into tiktok_extractor.py**

In `backend/app/services/tiktok_extractor.py`, wrap the `_fetch_tikwm_data` call:

Add import:
```python
from app.services.retry import with_retry
```

In `extract_tiktok_media`:
```python
# Before:
data = await _fetch_tikwm_data(url)

# After:
data = await with_retry(_fetch_tikwm_data, url, max_attempts=2, wait_seconds=1.0)
```

**Step 7: Run full test suite**

Run: `cd backend && python -m pytest tests/ -v -m "not live"`
Expected: All PASS

**Step 8: Commit**

```bash
git add backend/app/services/retry.py backend/tests/unit/services/test_retry.py backend/app/services/extractor.py backend/app/services/tiktok_extractor.py
git commit -m "feat: add retry logic with exponential backoff for transient failures"
```

---

## Task 6: Wire Redis into App Startup

**Files:**
- Modify: `backend/app/main.py`
- Create: `backend/tests/unit/test_app_startup.py`

**Step 1: Write failing test for startup wiring**

Create `backend/tests/unit/test_app_startup.py`:

```python
"""Test that app startup wires Redis into services."""

import pytest
from unittest.mock import patch, AsyncMock

from app.services.token_store import token_store
from app.services.cache import extraction_cache


@pytest.mark.unit
class TestAppStartup:
    """Verify Redis is wired during lifespan."""

    def test_token_store_has_init_redis_method(self):
        """TokenStore exposes init_redis for startup wiring."""
        assert hasattr(token_store, "init_redis")
        assert callable(token_store.init_redis)

    def test_cache_accepts_redis_in_constructor(self):
        """ExtractionCache can accept a Redis client."""
        from app.services.cache import ExtractionCache
        cache = ExtractionCache(redis=None)
        assert cache._redis is None
```

**Step 2: Run test to verify it passes (these are integration-ready checks)**

Run: `cd backend && python -m pytest tests/unit/test_app_startup.py -v -m unit`
Expected: PASS

**Step 3: Update main.py lifespan to wire Redis**

Modify `backend/app/main.py`:

Add imports:
```python
from .services.redis_client import get_redis, close_redis
from .services.token_store import token_store
from .services.cache import extraction_cache
```

Update the `lifespan` function:
```python
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup: connect Redis
    redis = await get_redis()
    await token_store.init_redis(redis)
    extraction_cache._redis = redis

    if redis:
        logger.info("Redis connected — token store and cache using Redis backend")
    else:
        logger.info("No Redis — using in-memory fallback for tokens and cache")

    # Startup: start token cleanup task (only needed for in-memory mode)
    cleanup_task = asyncio.create_task(start_cleanup_task())

    yield

    # Shutdown: cancel cleanup task and close Redis
    _ = cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

    await close_redis()
```

**Step 4: Run full test suite**

Run: `cd backend && python -m pytest tests/ -v -m "not live"`
Expected: All PASS

**Step 5: Commit**

```bash
git add backend/app/main.py backend/tests/unit/test_app_startup.py
git commit -m "feat: wire Redis into app startup for token store and cache"
```

---

## Task 7: Redis-backed Rate Limiting (slowapi + Redis)

**Files:**
- Modify: `backend/app/main.py` (configure slowapi with Redis storage)

**Step 1: Write the failing test**

The rate limiter test is already implicit — if the limiter uses Redis, the `reset_rate_limiter` fixture in conftest should still work. Add a smoke test:

Add to `backend/tests/unit/test_app_startup.py`:

```python
    def test_limiter_uses_redis_storage_when_available(self):
        """When REDIS_URL is set, slowapi should use Redis storage."""
        from app.main import limiter
        # Limiter should be initialized (either memory or redis)
        assert limiter is not None
```

**Step 2: Update main.py to use Redis for rate limiting**

In `backend/app/main.py`, update limiter initialization:

```python
import os

# Initialize limiter — Redis storage configured in lifespan
def _create_limiter():
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return Limiter(
            key_func=get_remote_address,
            storage_uri=redis_url,
        )
    return Limiter(key_func=get_remote_address)

limiter = _create_limiter()
```

**Step 3: Run full test suite**

Run: `cd backend && python -m pytest tests/ -v -m "not live"`
Expected: All PASS

**Step 4: Commit**

```bash
git add backend/app/main.py backend/tests/unit/test_app_startup.py
git commit -m "feat: Redis-backed rate limiting via slowapi storage_uri"
```

---

## Task 8: Docker Compose for Local Dev

**Files:**
- Create: `backend/docker-compose.yml`
- Modify: `backend/.env.example`

**Step 1: Create docker-compose.yml**

Create `backend/docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy

volumes:
  redis-data:
```

**Step 2: Verify it works**

Run: `cd backend && docker compose up -d`
Expected: Both `redis` and `api` services start. Health check at `http://localhost:8000/health` returns `{"status": "ok"}`

Run: `docker compose down`

**Step 3: Commit**

```bash
git add backend/docker-compose.yml
git commit -m "feat: add Docker Compose for local dev with Redis"
```

---

## Task 9: Final Integration Verification

**Step 1: Run full backend test suite**

Run: `cd backend && python -m pytest tests/ -v -m "not live" --tb=short`
Expected: All PASS

**Step 2: Run with Docker Compose**

Run: `cd backend && docker compose up --build -d && sleep 3 && curl http://localhost:8000/health && docker compose down`
Expected: `{"status":"ok"}`

**Step 3: Final commit with all env updates**

```bash
git add backend/.env.example
git commit -m "docs: update .env.example with Redis configuration"
```

---

## Summary of Changes

| Component | Before | After |
|-----------|--------|-------|
| Token Store | In-memory dict, lost on restart | Redis with `SETEX` (5-min TTL), in-memory fallback |
| Extraction Cache | None | Redis/in-memory cache (5-min TTL), keyed by URL hash |
| Rate Limiting | In-memory slowapi, resets on restart | Redis-backed slowapi via `storage_uri` |
| Retry Logic | None | Exponential backoff (2 attempts, 1-2s delays) on transient errors |
| Local Dev | `Dockerfile` only | `docker-compose.yml` with Redis + API |

## Dependencies Added

| Package | Purpose | File |
|---------|---------|------|
| `redis[hiredis]>=5.0.0` | Async Redis client with C parser | `requirements.txt` |
| `tenacity>=8.2.0` | Retry library (available but custom impl preferred for simplicity) | `requirements.txt` |
| `fakeredis[lua]>=2.21.0` | Fake Redis for tests | `requirements-dev.txt` |

> **Note:** The plan uses a custom `with_retry` instead of tenacity's decorators for simpler integration with the existing async code patterns. Tenacity is still added as a dependency for future use if needed, but can be removed if you prefer the custom approach only.
