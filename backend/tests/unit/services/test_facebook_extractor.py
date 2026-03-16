"""
Unit tests for Facebook hybrid extraction flow in extractor.py.

Tests the hybrid path: primary yt-dlp → fallback if allowed.
"""

from unittest.mock import patch, AsyncMock, MagicMock
import pytest

from app.services.extractor import extract_media_info, _extract_facebook_hybrid
from app.utils.facebook_scope import ErrorClass
from app.schemas.extract import MediaResult, Format


@pytest.mark.unit
class TestFacebookHybridExtraction:
    """Test suite for Facebook hybrid extraction flow."""

    @pytest.fixture
    def valid_facebook_url(self):
        """Valid in-scope Facebook URL."""
        return "https://facebook.com/watch?v=123456789"

    @pytest.fixture
    def out_of_scope_url(self):
        """Out-of-scope Facebook URL."""
        return "https://facebook.com/share/v/abc123"

    @pytest.fixture
    def mock_media_result(self):
        """Mock MediaResult from successful extraction."""
        return MediaResult(
            platform="facebook",
            title="Test Video",
            author="test_user",
            thumbnail="https://example.com/thumb.jpg",
            thumbnails=["https://example.com/thumb.jpg"],
            duration=120,
            formats=[
                Format(
                    id="video-720p",
                    label="Video 720p",
                    type="video/mp4",
                    size_mb=10.5,
                    download_url="/api/download?token=test-token",
                )
            ],
        )

    @pytest.mark.asyncio
    async def test_out_of_scope_raises_value_error(self, out_of_scope_url):
        """Out-of-scope URLs raise ValueError (400 UNSUPPORTED_PLATFORM)."""
        with pytest.raises(ValueError) as exc_info:
            await _extract_facebook_hybrid(out_of_scope_url)

        assert "tidak didukung" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_primary_success_returns_result(
        self, valid_facebook_url, mock_media_result
    ):
        """Successful primary extraction returns MediaResult."""
        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_extract,
            patch(
                "app.services.extractor._build_facebook_media_result",
                new_callable=AsyncMock,
            ) as mock_build,
        ):
            mock_extract.return_value = {"title": "Test"}
            mock_build.return_value = mock_media_result

            result = await _extract_facebook_hybrid(valid_facebook_url)

            assert result.platform == "facebook"
            assert result.title == "Test Video"
            mock_extract.assert_called_once_with(valid_facebook_url)
            mock_build.assert_called_once()

    @pytest.mark.asyncio
    async def test_primary_fail_terminal_access_raises_permission_error(
        self, valid_facebook_url
    ):
        """TERMINAL_ACCESS error raises PermissionError (403 ACCESS_DENIED)."""
        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_extract,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
        ):
            mock_extract.side_effect = PermissionError("Login required")
            mock_classify.return_value = ErrorClass.TERMINAL_ACCESS

            with pytest.raises(PermissionError) as exc_info:
                await _extract_facebook_hybrid(valid_facebook_url)

            assert "memerlukan login" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_primary_fail_no_fallback_raises_original_error(
        self, valid_facebook_url
    ):
        """NO_FALLBACK error raises original error without fallback attempt."""
        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_extract,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
            patch(
                "app.services.extractor.extract_facebook_via_fallback"
            ) as mock_fallback,
        ):
            original_error = ValueError("Invalid URL format")
            mock_extract.side_effect = original_error
            mock_classify.return_value = ErrorClass.NO_FALLBACK

            with pytest.raises(ValueError, match="Invalid URL format"):
                await _extract_facebook_hybrid(valid_facebook_url)

            mock_fallback.assert_not_called()

    @pytest.mark.asyncio
    async def test_primary_fail_allow_fallback_success(
        self, valid_facebook_url, mock_media_result
    ):
        """ALLOW_FALLBACK triggers fallback and returns result on success."""
        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_extract,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
            patch(
                "app.services.extractor.extract_facebook_via_fallback",
                new_callable=AsyncMock,
            ) as mock_fallback,
        ):
            mock_extract.side_effect = RuntimeError("Network timeout")
            mock_classify.return_value = ErrorClass.ALLOW_FALLBACK
            mock_fallback.return_value = mock_media_result

            result = await _extract_facebook_hybrid(valid_facebook_url)

            assert result.platform == "facebook"
            mock_fallback.assert_called_once_with(valid_facebook_url)

    @pytest.mark.asyncio
    async def test_dual_failure_raises_runtime_error(self, valid_facebook_url):
        """Both primary and fallback failure raises RuntimeError (422 EXTRACTION_FAILED)."""
        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_extract,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
            patch(
                "app.services.extractor.extract_facebook_via_fallback",
                new_callable=AsyncMock,
            ) as mock_fallback,
        ):
            mock_extract.side_effect = RuntimeError("Primary failed")
            mock_classify.return_value = ErrorClass.ALLOW_FALLBACK
            mock_fallback.side_effect = RuntimeError("Fallback failed")

            with pytest.raises(RuntimeError) as exc_info:
                await _extract_facebook_hybrid(valid_facebook_url)

            assert "gagal" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_no_cookies_used_for_facebook(self, valid_facebook_url):
        """Facebook extraction does NOT use cookies (intentional design)."""
        with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
            mock_ydl = MagicMock()
            mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)
            mock_ydl.extract_info.return_value = {"title": "Test"}

            from app.services.extractor import _extract_info_sync_facebook

            _extract_info_sync_facebook(valid_facebook_url)

            mock_ydl_class.assert_called_once()
            call_kwargs = mock_ydl_class.call_args[1]

            assert "cookiefile" not in call_kwargs


@pytest.mark.unit
class TestFacebookPlatformRouting:
    """Test that Facebook URLs are correctly routed through hybrid flow."""

    @pytest.mark.asyncio
    async def test_facebook_url_routes_to_hybrid_extractor(self):
        """Facebook platform detection routes to hybrid extractor."""
        facebook_url = "https://facebook.com/watch?v=123"

        with patch(
            "app.services.extractor._extract_facebook_hybrid",
            new_callable=AsyncMock,
        ) as mock_hybrid:
            mock_hybrid.return_value = MediaResult(
                platform="facebook",
                title="Test",
                author=None,
                thumbnail=None,
                thumbnails=[],
                duration=None,
                formats=[],
            )

            await extract_media_info(facebook_url)

            mock_hybrid.assert_called_once_with(facebook_url)

    @pytest.mark.asyncio
    async def test_non_facebook_urls_not_routed_to_hybrid(self):
        """Non-Facebook URLs are NOT routed to hybrid extractor."""
        twitter_url = "https://twitter.com/user/status/123"

        with (
            patch(
                "app.services.extractor._extract_facebook_hybrid",
                new_callable=AsyncMock,
            ) as mock_hybrid,
            patch("app.services.extractor._extract_info_sync") as mock_sync,
            patch(
                "app.services.extractor._build_formats",
                new_callable=AsyncMock,
            ) as mock_build,
        ):
            mock_sync.return_value = {
                "title": "Test",
                "formats": [],
            }
            mock_build.return_value = []

            try:
                await extract_media_info(twitter_url)
            except RuntimeError:
                pass

            mock_hybrid.assert_not_called()
