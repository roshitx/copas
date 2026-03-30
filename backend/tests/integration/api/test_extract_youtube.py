"""
Integration tests for /api/extract endpoint covering YouTube scenarios.

Tests YouTube content extraction with mocked upstream:
1. Standard video extraction
2. Shorts extraction
3. Music extraction

Also tests error mapping: 403, 422
And platform detection: youtube.com, youtu.be
"""

import json
import pytest
from unittest.mock import patch, AsyncMock

from app.schemas.extract import MediaResult, Format

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

# Load fixtures
FIXTURES_DIR = "tests/fixtures/youtube"


def load_fixture(filename: str) -> dict:
    """Load a JSON fixture file."""
    with open(f"{FIXTURES_DIR}/{filename}", "r") as f:
        return json.load(f)


# Load all YouTube fixtures
VIDEO_FIXTURE = load_fixture("video.json")
SHORTS_FIXTURE = load_fixture("shorts.json")
MUSIC_FIXTURE = load_fixture("music.json")


def create_expected_media_result(fixture: dict) -> MediaResult:
    """Create a MediaResult from fixture expected response."""
    expected = fixture["expected_backend_response"]
    mock_ytdlp = fixture["mock_ytdlp_response"]

    formats = []
    for i, fmt in enumerate(mock_ytdlp.get("formats", [])):
        # Determine if video or audio format
        is_audio_only = fmt.get("vcodec") == "none" or fmt.get("height") is None
        mime_type = "audio/webm" if is_audio_only else "video/mp4"

        formats.append(
            Format(
                id=fmt["format_id"],
                label=f"Video {fmt.get('height', 'audio')}p" if not is_audio_only else "Audio",
                type=mime_type,
                size_mb=fmt.get("filesize") / (1024 * 1024) if fmt.get("filesize") else None,
                download_url=f"/api/download?token=test-token-{fmt['format_id']}",
            )
        )

    return MediaResult(
        platform=expected["platform"],
        title=expected["title"],
        author=expected["author"],
        thumbnail=expected["thumbnail"],
        thumbnails=expected["thumbnails"],
        duration=expected.get("duration"),
        formats=formats,
    )


class TestYouTubeVideoExtraction:
    """Test YouTube standard video extraction."""

    async def test_video_returns_correct_structure(self, client, mock_token_store):
        """Test that video extraction returns correct response structure."""
        fixture = VIDEO_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify platform
            assert data["platform"] == expected["platform"]

            # Verify author
            assert data["author"] == expected["author"]

            # Verify title
            assert data["title"] == expected["title"]

            # Verify duration
            assert data["duration"] == expected["duration"]

            # Verify formats exist
            assert len(data["formats"]) >= expected["formats_count_min"]

    async def test_video_has_thumbnail(self, client, mock_token_store):
        """Test that video has correct thumbnail."""
        fixture = VIDEO_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )
            data = response.json()

            assert data["thumbnail"] == expected["thumbnail"]
            assert len(data["thumbnails"]) >= 1

    async def test_video_has_multiple_formats(self, client, mock_token_store):
        """Test that video has multiple quality formats available."""
        fixture = VIDEO_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )
            data = response.json()

            # Verify at least minimum formats
            assert len(data["formats"]) >= expected["formats_count_min"]

            # Verify video formats exist
            video_formats = [f for f in data["formats"] if f["type"] == "video/mp4"]
            assert len(video_formats) >= 1

            # Verify format has required fields
            for fmt in video_formats:
                assert "id" in fmt
                assert "label" in fmt
                assert "type" in fmt
                assert "download_url" in fmt


class TestYouTubeShortsExtraction:
    """Test YouTube Shorts extraction."""

    async def test_shorts_returns_correct_structure(self, client, mock_token_store):
        """Test that Shorts extraction returns correct response structure."""
        fixture = SHORTS_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify platform
            assert data["platform"] == expected["platform"]

            # Verify author
            assert data["author"] == expected["author"]

            # Verify title
            assert data["title"] == expected["title"]

            # Verify duration (shorts are short)
            assert data["duration"] == expected["duration"]

            # Verify formats exist
            assert len(data["formats"]) >= expected["formats_count_min"]

    async def test_shorts_short_url_works(self, client, mock_token_store):
        """Test that youtu.be short URL works for Shorts."""
        fixture = SHORTS_FIXTURE
        mock_result = create_expected_media_result(fixture)

        # Use youtu.be short URL format
        short_url = f"https://youtu.be/{fixture['mock_ytdlp_response']['id']}"

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": short_url}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"


class TestYouTubeMusicExtraction:
    """Test YouTube Music extraction."""

    async def test_music_returns_correct_structure(self, client, mock_token_store):
        """Test that Music extraction returns correct response structure."""
        fixture = MUSIC_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify platform
            assert data["platform"] == expected["platform"]

            # Verify author
            assert data["author"] == expected["author"]

            # Verify title
            assert data["title"] == expected["title"]

            # Verify duration (music can be long)
            assert data["duration"] == expected["duration"]

            # Verify formats exist
            assert len(data["formats"]) >= expected["formats_count_min"]

    async def test_music_url_detected(self, client, mock_token_store):
        """Test that music.youtube.com URL is detected correctly."""
        fixture = MUSIC_FIXTURE
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 200
            data = response.json()
            # Music URLs should still return youtube as platform
            assert data["platform"] == "youtube"


class TestYouTubeErrorHandling:
    """Test YouTube error response mapping."""

    async def test_private_video_returns_403(self, client, mock_token_store):
        """Test PermissionError -> 403 ACCESS_DENIED for private video."""
        fixture = VIDEO_FIXTURE

        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = PermissionError(
                "This video is private. Sign in to access."
            )

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 403
            data = response.json()
            assert data["error"] == "ACCESS_DENIED"
            assert "message" in data

    async def test_extraction_failure_returns_422(self, client, mock_token_store):
        """Test RuntimeError -> 422 EXTRACTION_FAILED."""
        fixture = VIDEO_FIXTURE

        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = RuntimeError("Failed to extract media")

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 422
            data = response.json()
            assert data["error"] == "EXTRACTION_FAILED"
            assert "message" in data

    async def test_age_restricted_returns_403(self, client, mock_token_store):
        """Test age restricted video -> 403 ACCESS_DENIED."""
        fixture = VIDEO_FIXTURE

        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = PermissionError(
                "Sign in to confirm your age. This video may be inappropriate for some users."
            )

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 403
            data = response.json()
            assert data["error"] == "ACCESS_DENIED"
            assert "message" in data


class TestYouTubePlatformDetection:
    """Test YouTube URL platform detection."""

    async def test_youtube_url_detected(self, client, mock_token_store):
        """Test that youtube.com URL is detected as platform: youtube."""
        fixture = VIDEO_FIXTURE
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"

    async def test_youtu_be_short_url_detected(self, client, mock_token_store):
        """Test that youtu.be URL is detected as platform: youtube."""
        fixture = VIDEO_FIXTURE
        mock_result = create_expected_media_result(fixture)

        # Convert to youtu.be short URL
        video_id = fixture["mock_ytdlp_response"]["id"]
        short_url = f"https://youtu.be/{video_id}"

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": short_url}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"