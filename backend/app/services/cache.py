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
        self._memory: dict[str, tuple[float, str]] = {}

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
