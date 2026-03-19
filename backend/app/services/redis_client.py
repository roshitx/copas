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
