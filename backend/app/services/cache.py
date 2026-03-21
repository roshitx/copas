"""Extraction result cache with Redis backend and in-memory fallback."""

import hashlib
import json
import time
import logging
from typing import Any, Optional

from redis.asyncio import Redis

# Per-platform TTL (seconds) — defined inline to avoid circular imports with extractors
CACHE_TTL_BY_PLATFORM = {
    "youtube": 1800,    # 30 min — content rarely changes
    "tiktok": 1800,     # 30 min
    "facebook": 900,    # 15 min
    "instagram": 600,   # 10 min — stories/reels can expire
    "twitter": 600,     # 10 min
}
CACHE_TTL_DEFAULT = 300  # 5 min fallback

logger = logging.getLogger(__name__)


class ExtractionCache:
    """Cache for extraction results. Uses Redis if available, falls back to in-memory dict."""

    def __init__(self, redis: Optional[Redis] = None):
        self._redis = redis
        self._memory: dict[str, tuple[float, str]] = {}

    @staticmethod
    def _cache_key(url: str) -> str:
        url_hash = hashlib.sha256(url.strip().lower().encode()).hexdigest()[:16]
        return f"cache:extract:{url_hash}"

    @staticmethod
    def _get_ttl(data: Optional[dict[str, Any]] = None) -> int:
        """Get TTL based on platform from cached data."""
        if data:
            platform = data.get("platform", "")
            return CACHE_TTL_BY_PLATFORM.get(platform, CACHE_TTL_DEFAULT)
        return CACHE_TTL_DEFAULT

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
        ttl = self._get_ttl(data)

        if self._redis:
            await self._redis.setex(key, ttl, raw)
        else:
            self._memory[key] = (time.time() + ttl, raw)

    async def invalidate(self, url: str) -> None:
        key = self._cache_key(url)
        if self._redis:
            await self._redis.delete(key)
        else:
            self._memory.pop(key, None)


# Global instance — initialized during app startup
extraction_cache = ExtractionCache()
