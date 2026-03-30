import asyncio
import logging
from contextlib import asynccontextmanager
from typing import cast

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response

from .core.config import settings
from .core.error_codes import create_error_response
from .core.exceptions import CopasException
from .core.logging_config import setup_logging
from .routers import download, extract, health
from .services.cache import extraction_cache
from .services.http_client import close_http_client
from .services.redis_client import close_redis, get_redis
from .services.token_store import start_cleanup_task, token_store

# Logger for startup/security configuration warnings
logger = logging.getLogger(__name__)

# Initialize structured logging
setup_logging()

# Initialize Sentry (no-op if SENTRY_DSN is empty)
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        traces_sample_rate=settings.sentry_traces_sample_rate,
        environment=settings.environment,
    )
    logger.info("Sentry initialized", extra={"environment": settings.environment})


# Initialize limiter — uses Redis for persistence when available
def _create_limiter() -> Limiter:
    if settings.redis_url:
        return Limiter(key_func=get_remote_address, storage_uri=settings.redis_url)
    return Limiter(key_func=get_remote_address)


limiter = _create_limiter()


def _parse_allowed_origins() -> list[str]:
    """Parse and validate CORS origins from settings.

    - Trims whitespace
    - Drops empty entries
    - Disallows wildcard in production
    - Uses strict localhost fallback only in development
    """
    localhost_fallback = ["http://localhost:3000", "http://127.0.0.1:3000"]

    raw_origins = settings.allowed_origins
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    if "*" in origins:
        if settings.is_development:
            logger.warning(
                "ALLOWED_ORIGINS contains wildcard '*'. Falling back to strict localhost list in development."
            )
            return localhost_fallback
        raise RuntimeError("Wildcard ALLOWED_ORIGINS is not allowed in production.")

    if origins:
        return origins

    if settings.is_development:
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

    # Shutdown: cancel cleanup task, close HTTP client, close Redis
    _ = cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

    await close_http_client()
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


@app.exception_handler(CopasException)
async def copas_exception_handler(
    request: Request, exc: CopasException
) -> JSONResponse:
    """Handle all CopasException subclasses with consistent error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.error_code, exc.message),
    )


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
app.include_router(health.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
