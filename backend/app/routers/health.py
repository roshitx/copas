"""Health check router for monitoring and diagnostics."""

from fastapi import APIRouter

from ..services.cache import extraction_cache

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint with Redis connectivity status.

    Returns:
        Dictionary with status and Redis connectivity information.
    """
    redis_ok = False
    if extraction_cache._redis:
        try:
            await extraction_cache._redis.ping()
            redis_ok = True
        except Exception:
            pass

    return {
        "status": "ok",
        "redis": "connected" if redis_ok else "unavailable",
    }
