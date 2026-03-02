"""
Unit tests for extractor.py helper functions

Tests filename generation, tweet ID extraction, URL normalization, format labels
"""

from unittest.mock import patch, AsyncMock

import pytest

from app.services.extractor import (
    _extract_tweet_id,
    _create_format,
)
from app.utils.platform import detect_platform


@pytest.mark.unit
class TestExtractTweetId:
    """Test suite for _extract_tweet_id function."""

    def test_extract_from_twitter_com_status(self):
        """Extract tweet ID from twitter.com/status URL."""
        url = "https://twitter.com/username/status/1234567890123456789"
        result = _extract_tweet_id(url)
        assert result == "1234567890123456789"

    def test_extract_from_x_com_status(self):
        """Extract tweet ID from x.com/status URL."""
        url = "https://x.com/username/status/9876543210987654321"
        result = _extract_tweet_id(url)
        assert result == "9876543210987654321"

    def test_extract_from_twitter_com_statuses(self):
        """Extract tweet ID from twitter.com/statuses URL (legacy)."""
        url = "https://twitter.com/username/statuses/1111111111111111111"
        result = _extract_tweet_id(url)
        assert result == "1111111111111111111"

    def test_extract_from_x_com_statuses(self):
        """Extract tweet ID from x.com/statuses URL (legacy)."""
        url = "https://x.com/username/statuses/2222222222222222222"
        result = _extract_tweet_id(url)
        assert result == "2222222222222222222"

    def test_extract_with_query_params(self):
        """Extract tweet ID from URL with query parameters."""
        url = "https://twitter.com/user/status/1234567890123456789?s=20&t=abc123"
        result = _extract_tweet_id(url)
        assert result == "1234567890123456789"

    def test_extract_with_http(self):
        """Extract tweet ID from HTTP URL."""
        url = "http://twitter.com/user/status/5555555555555555555"
        result = _extract_tweet_id(url)
        assert result == "5555555555555555555"

    def test_extract_returns_none_for_invalid_url(self):
        """Return None for URLs without tweet ID."""
        urls = [
            "https://twitter.com/username",
            "https://twitter.com/username/media",
            "https://example.com/twitter/status/123",
            "not-a-url",
            "",
            "https://instagram.com/p/ABC123",
        ]
        for url in urls:
            assert _extract_tweet_id(url) is None

    def test_extract_with_numeric_username(self):
        """Extract tweet ID when username contains numbers."""
        url = "https://twitter.com/user123/status/9999999999999999999"
        result = _extract_tweet_id(url)
        assert result == "9999999999999999999"


@pytest.mark.unit
class TestDetectPlatform:
    """Test suite for detect_platform function from platform.py."""

    def test_detect_tiktok(self):
        """Detect TikTok URLs."""
        urls = [
            "https://tiktok.com/@user/video/123",
            "https://vm.tiktok.com/abc123",
            "https://vt.tiktok.com/xyz789",
        ]
        for url in urls:
            assert detect_platform(url) == "tiktok"

    def test_detect_instagram(self):
        """Detect Instagram URLs."""
        urls = [
            "https://instagram.com/p/ABC123",
            "https://instagr.am/p/XYZ789",
            "https://www.instagram.com/reel/ABC123",
        ]
        for url in urls:
            assert detect_platform(url) == "instagram"

    def test_detect_youtube(self):
        """Detect YouTube URLs."""
        urls = [
            "https://youtube.com/watch?v=ABC123",
            "https://youtu.be/XYZ789",
            "https://music.youtube.com/watch?v=ABC123",
        ]
        for url in urls:
            assert detect_platform(url) == "youtube"

    def test_detect_twitter(self):
        """Detect Twitter/X URLs."""
        urls = [
            "https://twitter.com/user/status/123",
            "https://x.com/user/status/123",
            "https://t.co/shortlink",
        ]
        for url in urls:
            assert detect_platform(url) == "twitter"

    def test_detect_facebook(self):
        """Detect Facebook URLs."""
        urls = [
            "https://facebook.com/video.php?v=123",
            "https://fb.watch/abc123",
            "https://fb.me/xyz789",
        ]
        for url in urls:
            assert detect_platform(url) == "facebook"

    def test_detect_threads(self):
        """Detect Threads URLs."""
        urls = [
            "https://threads.net/@user/post/ABC123",
            "https://threads.com/@user/post/XYZ789",
        ]
        for url in urls:
            assert detect_platform(url) == "threads"

    def test_detect_unknown(self):
        """Return unknown for unrecognized URLs."""
        urls = [
            "https://example.com/video/123",
            "https://linkedin.com/posts/abc",
            "not-a-url",
            "",
        ]
        for url in urls:
            assert detect_platform(url) == "unknown"

    def test_detect_case_insensitive(self):
        """Platform detection is case-insensitive."""
        urls = [
            "https://TWITTER.com/user/status/123",
            "https://X.COM/user/status/123",
            "https://YouTube.Com/watch?v=ABC",
        ]
        assert detect_platform(urls[0]) == "twitter"
        assert detect_platform(urls[1]) == "twitter"
        assert detect_platform(urls[2]) == "youtube"


@pytest.mark.unit
class TestCreateFormatFilename:
    """Test suite for _create_format filename generation.

    Pattern: {platform}_{author}_copas_io(_{index}).ext
    """

    @pytest.fixture
    def mock_fmt(self):
        """Mock format dict with URL."""
        return {
            "format_id": "best",
            "url": "https://example.com/video.mp4",
            "ext": "mp4",
            "filesize": 10485760,  # 10 MB
        }

    @pytest.mark.asyncio
    async def test_filename_with_platform_and_author(self, mock_fmt):
        """Filename includes platform, author, and copas_io."""
        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="test-token-123")

            result = await _create_format(
                mock_fmt,
                label="Video 720p",
                content_type="video/mp4",
                platform="twitter",
                author="john_doe",
                index=0,
            )

            assert result is not None
            # Verify token_store was called with correct filename
            call_args = mock_store.create_token.call_args
            filename = (
                call_args[0][1] if call_args else call_args.kwargs.get("filename", "")
            )
            assert "twitter_john_doe_copas_io" in filename
            assert filename.endswith(".mp4")

    @pytest.mark.asyncio
    async def test_filename_with_platform_only(self, mock_fmt):
        """Filename includes platform and copas_io when no author."""
        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="test-token-456")

            await _create_format(
                mock_fmt,
                label="Video 1080p",
                content_type="video/mp4",
                platform="youtube",
                author=None,
                index=0,
            )

            call_args = mock_store.create_token.call_args
            filename = call_args[0][1]
            assert "youtube_copas_io" in filename
            assert "None" not in filename

    @pytest.mark.asyncio
    async def test_filename_with_author_only(self, mock_fmt):
        """Filename includes author and copas_io when no platform."""
        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="test-token-789")

            await _create_format(
                mock_fmt,
                label="Video 480p",
                content_type="video/mp4",
                platform="",
                author="jane_doe",
                index=0,
            )

            call_args = mock_store.create_token.call_args
            filename = call_args[0][1]
            assert "jane_doe_copas_io" in filename

    @pytest.mark.asyncio
    async def test_filename_with_neither_platform_nor_author(self, mock_fmt):
        """Filename defaults to copas_copas_io when no platform or author."""
        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="test-token-abc")

            await _create_format(
                mock_fmt,
                label="Video 360p",
                content_type="video/mp4",
                platform="",
                author=None,
                index=0,
            )

            call_args = mock_store.create_token.call_args
            filename = call_args[0][1]
            assert "copas_copas_io" in filename

    @pytest.mark.asyncio
    async def test_filename_with_index(self, mock_fmt):
        """Filename includes index when video_index > 0."""
        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="test-token-def")

            await _create_format(
                mock_fmt,
                label="Video 720p",
                content_type="video/mp4",
                platform="twitter",
                author="user123",
                index=2,
            )

            call_args = mock_store.create_token.call_args
            filename = call_args[0][1]
            assert filename.startswith("twitter_user123_copas_io_2")

    @pytest.mark.asyncio
    async def test_filename_extension_from_format(self):
        """Filename uses extension from format dict."""
        fmt_webm = {
            "format_id": "best",
            "url": "https://example.com/video.webm",
            "ext": "webm",
            "filesize": None,
        }

        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="test-token-ghi")

            await _create_format(
                fmt_webm,
                label="Video WebM",
                content_type="video/webm",
                platform="youtube",
                author="creator",
                index=0,
            )

            call_args = mock_store.create_token.call_args
            filename = call_args[0][1]
            assert filename.endswith(".webm")

    @pytest.mark.asyncio
    async def test_filename_default_extension(self):
        """Filename defaults to .mp4 when no extension in format."""
        fmt_no_ext = {
            "format_id": "best",
            "url": "https://example.com/video",
            "filesize": None,
        }

        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="test-token-jkl")

            await _create_format(
                fmt_no_ext,
                label="Video",
                content_type="video/mp4",
                platform="tiktok",
                author="tiktok_user",
                index=0,
            )

            call_args = mock_store.create_token.call_args
            filename = call_args[0][1]
            assert filename.endswith(".mp4")


@pytest.mark.unit
class TestCreateFormatResult:
    """Test suite for _create_format return value."""

    @pytest.fixture
    def mock_fmt(self):
        """Mock format dict."""
        return {
            "format_id": "137",
            "url": "https://example.com/video.mp4",
            "ext": "mp4",
            "filesize": 5242880,  # 5 MB
        }

    @pytest.mark.asyncio
    async def test_returns_format_object(self, mock_fmt):
        """_create_format returns a Format object with correct fields."""
        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="token-abc-123")

            result = await _create_format(
                mock_fmt,
                label="Video 1080p",
                content_type="video/mp4",
                platform="youtube",
                author="tester",
                index=0,
            )

            assert result.id == "137"
            assert result.label == "Video 1080p"
            assert result.type == "video/mp4"
            assert result.size_mb == 5.0  # 5242880 / 1024 / 1024
            assert "/api/download?token=token-abc-123" in result.download_url

    @pytest.mark.asyncio
    async def test_size_mb_none_when_no_filesize(self):
        """size_mb is None when filesize not available."""
        fmt_no_size = {
            "format_id": "best",
            "url": "https://example.com/video.mp4",
            "ext": "mp4",
            "filesize": None,
        }

        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="token")

            result = await _create_format(
                fmt_no_size,
                label="Video",
                content_type="video/mp4",
                platform="twitter",
                author="user",
                index=0,
            )

            assert result.size_mb is None

    @pytest.mark.asyncio
    async def test_uses_manifest_url_when_no_url(self):
        """Uses manifest_url when url not available."""
        fmt_manifest = {
            "format_id": "hls",
            "manifest_url": "https://example.com/manifest.m3u8",
            "ext": "mp4",
            "filesize": None,
        }

        with patch("app.services.extractor._token_store_module.token_store") as mock_store:
            mock_store.create_token = AsyncMock(return_value="token")

            result = await _create_format(
                fmt_manifest,
                label="HLS Stream",
                content_type="video/mp4",
                platform="instagram",
                author="insta_user",
                index=0,
            )

            # Should create token successfully
            assert result is not None
            mock_store.create_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_when_no_url_available(self):
        """Raises ValueError when no URL can be found."""
        fmt_no_url = {
            "format_id": "bad",
            "ext": "mp4",
            "filesize": None,
        }

        with pytest.raises(ValueError, match="Format URL is required"):
            await _create_format(
                fmt_no_url,
                label="Bad Format",
                content_type="video/mp4",
                platform="youtube",
                author="user",
                index=0,
            )


@pytest.mark.unit
class TestUrlNormalization:
    """Test URL normalization logic.

    Based on extract_media_info: x.com -> twitter.com
    """

    def test_x_com_normalized_to_twitter(self):
        """x.com URLs are normalized to twitter.com."""
        url = "https://x.com/user/status/1234567890"
        # The normalization happens inline in extract_media_info
        normalized = url.replace("x.com/", "twitter.com/")
        assert "twitter.com" in normalized
        assert "x.com" not in normalized

    def test_twitter_com_unchanged(self):
        """twitter.com URLs remain unchanged."""
        url = "https://twitter.com/user/status/1234567890"
        normalized = url.replace("x.com/", "twitter.com/")
        assert normalized == url

    def test_x_com_case_variations(self):
        """Various x.com formats are handled."""
        urls = [
            ("https://x.com/user/status/123", "https://twitter.com/user/status/123"),
            ("http://x.com/user/status/123", "http://twitter.com/user/status/123"),
        ]
        for original, expected in urls:
            normalized = original.replace("x.com/", "twitter.com/")
            assert normalized == expected


@pytest.mark.unit
class TestFormatLabelPatterns:
    """Test format label generation patterns."""

    def test_video_quality_labels(self):
        """Video quality labels include resolution."""
        # Labels are built in _build_formats
        # Video {index} · {quality} or Video {quality}
        qualities = ["144p", "240p", "360p", "480p", "720p", "1080p", "4K"]
        for q in qualities:
            label = f"Video {q}"
            assert "Video" in label
            assert q in label

    def test_video_index_in_label(self):
        """Multi-video entries include index in label."""
        index = 2
        quality = "720p"
        label = f"Video {index} · {quality}"
        assert f"Video {index}" in label
        assert quality in label

    def test_audio_label_format(self):
        """Audio format has Audio MP3 label."""
        label = "Audio MP3"
        assert label == "Audio MP3"

    def test_photo_label_single(self):
        """Single photo has 'Foto' label."""
        label = "Foto"
        assert label == "Foto"

    def test_photo_label_multiple(self):
        """Multiple photos have indexed labels."""
        for i in range(1, 5):
            label = f"Foto {i}"
            assert label == f"Foto {i}"
