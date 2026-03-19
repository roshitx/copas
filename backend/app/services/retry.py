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

    Non-retryable exceptions are raised immediately.
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
