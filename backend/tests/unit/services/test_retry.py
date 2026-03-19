"""Unit tests for retry logic."""

import pytest
from unittest.mock import AsyncMock

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
