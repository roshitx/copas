import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from .routers import extract, download
from .services.redis_client import get_redis, close_redis
from .services.token_store import token_store, start_cleanup_task
from .services.cache import extraction_cache

# Logger for startup/security configuration warnings
logger = logging.getLogger(__name__)

# Initialize limiter — uses Redis for persistence when available
def _create_limiter() -> Limiter:
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return Limiter(key_func=get_remote_address, storage_uri=redis_url)
    return Limiter(key_func=get_remote_address)


limiter = _create_limiter()


def _parse_allowed_origins() -> list[str]:
    """Parse and validate CORS origins from environment.

    - Trims whitespace
    - Drops empty entries
    - Disallows wildcard in production
    - Uses strict localhost fallback only in development
    """
    env = os.getenv("ENV", "development").strip().lower()
    dev_envs = {"dev", "development", "local"}
    localhost_fallback = ["http://localhost:3000", "http://127.0.0.1:3000"]

    raw_origins = os.getenv("ALLOWED_ORIGINS", "")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    if "*" in origins:
        if env in dev_envs:
            logger.warning(
                "ALLOWED_ORIGINS contains wildcard '*'. Falling back to strict localhost list in development."
            )
            return localhost_fallback
        raise RuntimeError("Wildcard ALLOWED_ORIGINS is not allowed in production.")

    if origins:
        return origins

    if env in dev_envs:
        logger.warning(
            "ALLOWED_ORIGINS is empty. Falling back to strict localhost list in development."
        )
        return localhost_fallback

    raise RuntimeError(
        "ALLOWED_ORIGINS must be set to explicit origins in non-development environments."
    )


def _rate_limit_handler(request: Request, exc: Exception) -> Response:
    """Typed wrapper to satisfy FastAPI exception handler signature."""
    return _rate_limit_exceeded_handler(request, cast(RateLimitExceeded, exc))


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


# Create FastAPI app
app = FastAPI(
    title="Copas.io API",
    description="Social media content downloader",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limit exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# CORS middleware
allowed_origins = _parse_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(extract.router)
app.include_router(download.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
