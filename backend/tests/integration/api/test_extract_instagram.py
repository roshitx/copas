"""
Integration tests for /api/extract endpoint covering Instagram scenarios.

Tests Instagram content extraction with mocked upstream:
1. Reel extraction (vertical short video)
2. Post extraction (image)
3. Post extraction (video)

Also tests error mapping: 403, 422
And platform detection: instagram.com, instagr.am
"""

import json
import pytest
from unittest.mock import patch, AsyncMock

from app.schemas.extract import MediaResult, Format

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

# Load fixtures
FIXTURES_DIR = "tests/fixtures/instagram"


def load_fixture(filename: str) -> dict:
    """Load a JSON fixture file."""
    with open(f"{FIXTURES_DIR}/{filename}", "r") as f:
        return json.load(f)


# Load all Instagram fixtures
REEL_FIXTURE = load_fixture("reel.json")
POST_IMAGE_FIXTURE = load_fixture("post-image.json")
POST_VIDEO_FIXTURE = load_fixture("post-video.json")
MULTI_IMAGE_FIXTURE = load_fixture("multi-image.json")
MULTI_VIDEO_FIXTURE = load_fixture("multi-video.json")


def create_expected_media_result(fixture: dict) -> MediaResult:
    """Create a MediaResult from fixture expected response."""
    expected = fixture["expected_backend_response"]

    formats = []
    for fmt in expected.get("formats", []):
        formats.append(
            Format(
                id=fmt["id"],
                label=fmt["label"],
                type=fmt["type"],
                size_mb=fmt.get("size_mb"),
                download_url=f"/api/download?token=test-token-{fmt['id']}",
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


class TestInstagramReelExtraction:
    """Test Instagram Reel extraction."""

    async def test_reel_returns_correct_structure(self, client, mock_token_store):
        """Test that Reel extraction returns correct response structure."""
        fixture = REEL_FIXTURE
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

            # Verify formats - should have 1 video format
            assert len(data["formats"]) >= 1
            video_formats = [f for f in data["formats"] if f["type"] == "video/mp4"]
            assert len(video_formats) >= 1

            # Verify format has required fields
            fmt = video_formats[0]
            assert "id" in fmt
            assert "label" in fmt
            assert "type" in fmt
            assert "download_url" in fmt

    async def test_reel_has_thumbnail(self, client, mock_token_store):
        """Test that Reel has correct thumbnail."""
        fixture = REEL_FIXTURE
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


class TestInstagramPostExtraction:
    """Test Instagram Post extraction (image and video)."""

    async def test_post_image_returns_image_format(self, client, mock_token_store):
        """Test that image post extraction returns image format."""
        fixture = POST_IMAGE_FIXTURE
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

            # Verify duration is null for images
            assert data["duration"] is None

            # Verify formats - should have image format
            image_formats = [f for f in data["formats"] if f["type"] == "image/jpeg"]
            assert len(image_formats) >= 1

            # Verify image format has required fields
            fmt = image_formats[0]
            assert "id" in fmt
            assert "label" in fmt
            assert "download_url" in fmt

    async def test_post_video_returns_video_format(self, client, mock_token_store):
        """Test that video post extraction returns video format."""
        fixture = POST_VIDEO_FIXTURE
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

            # Verify duration is present for video
            assert data["duration"] == expected["duration"]

            # Verify formats - should have video format
            video_formats = [f for f in data["formats"] if f["type"] == "video/mp4"]
            assert len(video_formats) >= 1

            # Verify video format has required fields
            fmt = video_formats[0]
            assert "id" in fmt
            assert "label" in fmt
            assert "download_url" in fmt


class TestInstagramMultiImageExtraction:
    """Test Instagram multi-image carousel extraction."""

    async def test_multi_image_returns_multiple_image_formats(self, client, mock_token_store):
        """Test that multi-image carousel returns ≥2 image formats."""
        fixture = MULTI_IMAGE_FIXTURE
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

            assert data["platform"] == expected["platform"]
            assert data["author"] == expected["author"]
            assert data["duration"] is None

            image_formats = [f for f in data["formats"] if "image" in f["type"]]
            assert len(image_formats) >= 2

            for fmt in image_formats:
                assert "id" in fmt
                assert "label" in fmt
                assert "download_url" in fmt

    async def test_multi_image_has_thumbnails(self, client, mock_token_store):
        """Test that multi-image carousel returns thumbnails."""
        fixture = MULTI_IMAGE_FIXTURE
        mock_result = create_expected_media_result(fixture)

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )
            data = response.json()

            assert data["thumbnail"] is not None
            assert len(data["thumbnails"]) >= 1


class TestInstagramMultiVideoExtraction:
    """Test Instagram multi-video carousel extraction."""

    async def test_multi_video_returns_multiple_video_formats(self, client, mock_token_store):
        """Test that multi-video carousel returns ≥2 video formats."""
        fixture = MULTI_VIDEO_FIXTURE
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

            assert data["platform"] == expected["platform"]
            assert data["author"] == expected["author"]

            video_formats = [f for f in data["formats"] if "video" in f["type"]]
            assert len(video_formats) >= 2

            for fmt in video_formats:
                assert "id" in fmt
                assert "label" in fmt
                assert "download_url" in fmt

    async def test_multi_video_has_duration(self, client, mock_token_store):
        """Test that multi-video carousel has duration."""
        fixture = MULTI_VIDEO_FIXTURE
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

            assert data["duration"] == expected["duration"]


class TestInstagramErrorHandling:
    """Test Instagram error response mapping."""

    async def test_private_content_returns_403(self, client, mock_token_store):
        """Test PermissionError -> 403 ACCESS_DENIED."""
        fixture = REEL_FIXTURE

        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = PermissionError(
                "Konten ini memerlukan login atau tidak dapat diakses."
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
        fixture = REEL_FIXTURE

        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = RuntimeError("Failed to extract media")

            response = client.post(
                "/api/extract", json={"url": fixture["url"]}
            )

            assert response.status_code == 422
            data = response.json()
            assert data["error"] == "EXTRACTION_FAILED"
            assert "message" in data


class TestInstagramPlatformDetection:
    """Test Instagram URL platform detection."""

    async def test_instagram_url_detected(self, client, mock_token_store):
        """Test that instagram.com URL is detected as platform: instagram."""
        fixture = REEL_FIXTURE
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
            assert data["platform"] == "instagram"

    async def test_instagram_short_url_detected(self, client, mock_token_store):
        """Test that instagr.am URL is detected as platform: instagram."""
        # Use the post-image fixture but with instagr.am URL
        fixture = POST_IMAGE_FIXTURE
        mock_result = create_expected_media_result(fixture)

        # Convert URL to short form
        short_url = fixture["url"].replace("www.instagram.com", "instagr.am")

        with patch(
            "app.routers.extract.extract_media_info", new_callable=AsyncMock
        ) as mock_extract:
            mock_extract.return_value = mock_result

            response = client.post(
                "/api/extract", json={"url": short_url}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "instagram"