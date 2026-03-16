"""Unit tests for Facebook fallback adapter."""

import pytest
import respx
import httpx
from httpx import Response
from unittest.mock import patch

from app.services.facebook_fallback import (
    extract_facebook_via_fallback,
    check_fallback_health,
    get_metrics,
    reset_metrics,
    clear_health_cache,
    FacebookFallbackError,
    FacebookFallbackDisabledError,
    FacebookFallbackUnhealthyError,
    FacebookFallbackTimeoutError,
    FacebookFallbackProviderError,
    FacebookFallbackContentError,
)


class TestExtractFacebookViaFallback:
    """Tests for extract_facebook_via_fallback function."""

    @pytest.mark.asyncio
    async def test_fallback_disabled_by_default(self, mock_token_store):
        """Test that fallback is disabled when FACEBOOK_FALLBACK_ENABLED not set."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(FacebookFallbackDisabledError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            assert "disabled" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_fallback_disabled_explicitly(self, mock_token_store):
        """Test that fallback returns disabled when FACEBOOK_FALLBACK_ENABLED=false."""
        with patch.dict("os.environ", {"FACEBOOK_FALLBACK_ENABLED": "false"}):
            with pytest.raises(FacebookFallbackDisabledError):
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

    @respx.mock
    @pytest.mark.asyncio
    async def test_successful_normalization(self, mock_token_store):
        """Test successful extraction and normalization to MediaResult."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
                "FACEBOOK_FALLBACK_TIMEOUT_SECONDS": "30",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            # Mock extraction
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(
                    200,
                    json={
                        "data": {
                            "title": "Test Facebook Video",
                            "thumbnail": "https://example.com/thumb.jpg",
                            "author": "testuser",
                            "duration": 120,
                            "video_url": "https://example.com/video.mp4",
                            "size": 10485760,  # 10MB
                        }
                    },
                )
            )

            result = await extract_facebook_via_fallback(
                "https://facebook.com/watch?v=123"
            )

            assert result.platform == "facebook"
            assert result.title == "Test Facebook Video"
            assert result.author == "testuser"
            assert result.duration == 120
            assert result.thumbnail == "https://example.com/thumb.jpg"
            assert len(result.formats) == 1
            assert result.formats[0].type == "video/mp4"
            assert result.formats[0].label == "Video HD"
            assert result.formats[0].size_mb == 10.0

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeout_with_retry(self, mock_token_store):
        """Test timeout handling with retry logic."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
                "FACEBOOK_FALLBACK_TIMEOUT_SECONDS": "5",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            # All requests timeout
            respx.post("https://fallback.example.com/api/extract").mock(
                side_effect=httpx.TimeoutException("Request timed out")
            )

            with pytest.raises(FacebookFallbackTimeoutError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            assert "timed out" in str(exc_info.value).lower()

    @respx.mock
    @pytest.mark.asyncio
    async def test_provider_5xx_retry_exhaustion(self, mock_token_store):
        """Test provider 5xx error with retry exhaustion."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            # Provider returns 500 error
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(500, json={"error": "Internal server error"})
            )

            with pytest.raises(FacebookFallbackProviderError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            assert "500" in str(exc_info.value)

    @respx.mock
    @pytest.mark.asyncio
    async def test_content_not_found_404(self, mock_token_store):
        """Test 404 response - content not found."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(404, json={"error": "Not found"})
            )

            with pytest.raises(FacebookFallbackContentError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=999")

            assert "tidak ditemukan" in str(exc_info.value).lower()

    @respx.mock
    @pytest.mark.asyncio
    async def test_content_private_403(self, mock_token_store):
        """Test 403 response - private content."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(403, json={"error": "Forbidden"})
            )

            with pytest.raises(FacebookFallbackContentError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            assert (
                "pribadi" in str(exc_info.value).lower()
                or "login" in str(exc_info.value).lower()
            )

    @respx.mock
    @pytest.mark.asyncio
    async def test_no_formats_available(self, mock_token_store):
        """Test error when no formats returned."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(
                    200,
                    json={
                        "data": {
                            "title": "No Media",
                            "author": "testuser",
                        }
                    },
                )
            )

            with pytest.raises(FacebookFallbackContentError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            assert "tidak ada format" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_missing_base_url(self, mock_token_store):
        """Test error when base URL not configured."""
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                # No FACEBOOK_FALLBACK_BASE_URL
            },
        ):
            with pytest.raises(FacebookFallbackError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            assert "BASE_URL" in str(exc_info.value)

    @respx.mock
    @pytest.mark.asyncio
    async def test_retry_succeeds_on_second_attempt(self, mock_token_store):
        """Test that retry succeeds on second attempt after first failure."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )

            call_count = 0

            def mock_response(request):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return Response(
                        503, json={"error": "Service temporarily unavailable"}
                    )
                return Response(
                    200,
                    json={
                        "data": {
                            "title": "Success on Retry",
                            "video_url": "https://example.com/video.mp4",
                        }
                    },
                )

            respx.post("https://fallback.example.com/api/extract").mock(
                side_effect=mock_response
            )

            result = await extract_facebook_via_fallback(
                "https://facebook.com/watch?v=123"
            )

            assert result.title == "Success on Retry"
            assert call_count == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_audio_format_included(self, mock_token_store):
        """Test that audio format is included when available."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(
                    200,
                    json={
                        "data": {
                            "title": "Video with Audio",
                            "video_url": "https://example.com/video.mp4",
                            "audio_url": "https://example.com/audio.mp3",
                        }
                    },
                )
            )

            result = await extract_facebook_via_fallback(
                "https://facebook.com/watch?v=123"
            )

            assert len(result.formats) == 2
            assert result.formats[0].type == "video/mp4"
            assert result.formats[1].type == "audio/mp3"
            assert result.formats[1].label == "Audio MP3"


class TestFallbackHealthcheck:
    """Tests for provider healthcheck functionality."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_healthcheck_healthy_provider(self, mock_token_store):
        """Test healthcheck returns True for healthy provider."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )

            is_healthy = await check_fallback_health()
            assert is_healthy is True
    @pytest.mark.asyncio
    async def test_healthcheck_unhealthy_provider_5xx(self, mock_token_store):
        """Test healthcheck returns False for unhealthy provider (5xx)."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(503, json={"error": "Service unavailable"})
            )

            is_healthy = await check_fallback_health()
            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_healthcheck_timeout_returns_false(self, mock_token_store):
        """Test healthcheck returns False on timeout."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            respx.get("https://fallback.example.com/health").mock(
                side_effect=httpx.TimeoutException("Healthcheck timeout")
            )

            is_healthy = await check_fallback_health()
            assert is_healthy is False

    @respx.mock
    @pytest.mark.asyncio
    async def test_healthcheck_cache_within_ttl(self, mock_token_store):
        """Test healthcheck uses cached result within TTL."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            call_count = 0

            def mock_health(request):
                nonlocal call_count
                call_count += 1
                return Response(200, json={"status": "ok"})

            respx.get("https://fallback.example.com/health").mock(
                side_effect=mock_health
            )

            # First call hits provider
            result1 = await check_fallback_health()
            assert result1 is True
            assert call_count == 1

            # Second call uses cache (no new HTTP request)
            result2 = await check_fallback_health()
            assert result2 is True
            assert call_count == 1  # Still 1, not incremented

    @pytest.mark.asyncio
    async def test_healthcheck_no_base_url(self, mock_token_store):
        """Test healthcheck returns False when base URL not configured."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                # No base URL
            },
        ):
            is_healthy = await check_fallback_health()
            assert is_healthy is False

    @pytest.mark.asyncio
    async def test_healthcheck_disabled_fallback(self, mock_token_store):
        """Test healthcheck returns False when fallback is disabled."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "false",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            is_healthy = await check_fallback_health()
            assert is_healthy is False


class TestFallbackMetrics:
    """Tests for metrics counters."""

    @pytest.mark.asyncio
    async def test_metrics_initial_state(self, mock_token_store):
        """Test metrics start at zero."""
        reset_metrics()
        metrics = get_metrics()
        assert metrics["facebook_primary_success"] == 0
        assert metrics["facebook_fallback_attempt"] == 0
        assert metrics["facebook_fallback_success"] == 0
        assert metrics["facebook_dual_failure"] == 0

    @respx.mock
    @pytest.mark.asyncio
    async def test_metrics_fallback_attempt_and_success(self, mock_token_store):
        """Test metrics increment on successful fallback."""
        reset_metrics()
        clear_health_cache()

        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            # Mock extraction
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(
                    200,
                    json={
                        "data": {
                            "title": "Test Video",
                            "video_url": "https://example.com/video.mp4",
                        }
                    },
                )
            )

            await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            metrics = get_metrics()
            assert metrics["facebook_fallback_attempt"] == 1
            assert metrics["facebook_fallback_success"] == 1
            assert metrics["facebook_dual_failure"] == 0

    @respx.mock
    @pytest.mark.asyncio
    async def test_metrics_dual_failure_on_provider_error(self, mock_token_store):
        """Test metrics increment dual_failure on provider error."""
        reset_metrics()
        clear_health_cache()

        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            # Mock extraction failure
            respx.post("https://fallback.example.com/api/extract").mock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            with pytest.raises(FacebookFallbackTimeoutError):
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            metrics = get_metrics()
            assert metrics["facebook_fallback_attempt"] == 1
            assert metrics["facebook_dual_failure"] == 1


class TestKillSwitchBehavior:
    """Tests for kill-switch functionality."""

    @pytest.mark.asyncio
    async def test_kill_switch_prevents_fallback(self, mock_token_store):
        """Test that FACEBOOK_FALLBACK_ENABLED=false prevents fallback."""
        reset_metrics()
        with patch.dict("os.environ", {"FACEBOOK_FALLBACK_ENABLED": "false"}):
            with pytest.raises(FacebookFallbackDisabledError):
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            # Metrics should not be incremented
            metrics = get_metrics()
            assert metrics["facebook_fallback_attempt"] == 0

    @pytest.mark.asyncio
    async def test_kill_switch_default_disabled(self, mock_token_store):
        """Test that fallback is disabled by default (no env var)."""
        reset_metrics()
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(FacebookFallbackDisabledError):
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            metrics = get_metrics()
            assert metrics["facebook_fallback_attempt"] == 0

    @respx.mock
    @pytest.mark.asyncio
    async def test_unhealthy_provider_skips_fallback(self, mock_token_store):
        """Test that unhealthy provider raises error without attempting extraction."""
        reset_metrics()
        clear_health_cache()

        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock unhealthy healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(503, json={"error": "Service unavailable"})
            )

            with pytest.raises(FacebookFallbackUnhealthyError) as exc_info:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")

            assert "unhealthy" in str(exc_info.value).lower()

            # Metrics should not be incremented (never attempted)
            metrics = get_metrics()
            assert metrics["facebook_fallback_attempt"] == 0


class TestFallbackErrorClassification:
    """Tests for error classification in fallback adapter."""

    @pytest.mark.asyncio
    async def test_disabled_error_classification(self, mock_token_store):
        """Test that disabled error has correct classification."""
        with patch.dict("os.environ", {}, clear=True):
            try:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")
            except FacebookFallbackDisabledError as e:
                from app.utils.facebook_scope import ErrorClass

                assert e.error_class == ErrorClass.NO_FALLBACK

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeout_error_classification(self, mock_token_store):
        """Test that timeout error has correct classification."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            respx.post("https://fallback.example.com/api/extract").mock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            try:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")
            except FacebookFallbackTimeoutError as e:
                from app.utils.facebook_scope import ErrorClass

                assert e.error_class == ErrorClass.ALLOW_FALLBACK

    @respx.mock
    @pytest.mark.asyncio
    async def test_content_error_classification(self, mock_token_store):
        """Test that content error has correct classification."""
        clear_health_cache()
        with patch.dict(
            "os.environ",
            {
                "FACEBOOK_FALLBACK_ENABLED": "true",
                "FACEBOOK_FALLBACK_BASE_URL": "https://fallback.example.com",
            },
        ):
            # Mock healthcheck
            respx.get("https://fallback.example.com/health").mock(
                return_value=Response(200, json={"status": "ok"})
            )
            respx.post("https://fallback.example.com/api/extract").mock(
                return_value=Response(403, json={"error": "Private"})
            )

            try:
                await extract_facebook_via_fallback("https://facebook.com/watch?v=123")
            except FacebookFallbackContentError as e:
                from app.utils.facebook_scope import ErrorClass

                assert e.error_class == ErrorClass.TERMINAL_ACCESS
