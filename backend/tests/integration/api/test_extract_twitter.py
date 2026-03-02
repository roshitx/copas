"""
Integration tests for /api/extract endpoint covering Twitter scenarios.

Tests all 5 canonical Twitter URLs with mocked upstream (yt-dlp/fxtwitter):
1. Single image
2. Single video
3. Multi-video (2 videos)
4. Multi-image (2 photos)
5. Hybrid (video + image)

Also tests error mapping: 400, 403, 422, 500
"""

import json
import pytest
import respx
from httpx import Response
from unittest.mock import patch, MagicMock

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

# Load fixtures
FIXTURES_DIR = "tests/fixtures/twitter"


def load_fixture(filename: str) -> dict:
    """Load a JSON fixture file."""
    with open(f"{FIXTURES_DIR}/{filename}", "r") as f:
        return json.load(f)


# Load all Twitter fixtures
SINGLE_IMAGE_FIXTURE = load_fixture("single-image.json")
SINGLE_VIDEO_FIXTURE = load_fixture("single-video.json")
MULTI_VIDEO_FIXTURE = load_fixture("multi-video-2.json")
MULTI_IMAGE_FIXTURE = load_fixture("multi-image-2.json")
HYBRID_FIXTURE = load_fixture("hybrid-video-image.json")


def create_mock_ytdlp_info(fixture: dict, is_playlist: bool = False) -> dict:
    """Create a mock yt-dlp info dict from a fixture."""
    expected = fixture["expected_backend_response"]
    formats_data = expected.get("formats", [])

    if is_playlist:
        # Multi-item playlist structure
        entries = []
        for i, fmt in enumerate(formats_data):
            is_video = fmt["type"] == "video/mp4"
            entry = {
                "title": expected["title"],
                "thumbnail": expected["thumbnails"][i]
                if i < len(expected["thumbnails"])
                else expected["thumbnail"],
                "duration": expected.get("duration"),
                "uploader_id": expected.get("author"),
                "uploader": expected.get("author"),
                "formats": [
                    {
                        "format_id": fmt["id"],
                        "url": f"https://video.twimg.com/mock_video_{i}.mp4",
                        "ext": "mp4" if is_video else "jpg",
                        "vcodec": "h264" if is_video else "none",
                        "acodec": "aac" if is_video else "none",
                        "height": 720 if is_video else None,
                        "filesize": int(fmt["size_mb"] * 1024 * 1024)
                        if fmt.get("size_mb")
                        else None,
                    }
                ],
            }
            entries.append(entry)

        return {
            "_type": "playlist",
            "title": expected["title"],
            "thumbnail": expected["thumbnail"],
            "uploader_id": expected.get("author"),
            "uploader": expected.get("author"),
            "entries": entries,
        }
    else:
        # Single item structure
        fmt = formats_data[0] if formats_data else {}
        is_video = fmt.get("type") == "video/mp4"
        is_image = fmt.get("type") == "image/jpeg"

        # For videos, include multiple format options for quality selection
        if is_video:
            mock_formats = [
                {
                    "format_id": "720",
                    "url": "https://video.twimg.com/mock_video_720.mp4",
                    "ext": "mp4",
                    "vcodec": "h264",
                    "acodec": "aac",
                    "height": 720,
                    "filesize": int(fmt.get("size_mb", 15) * 1024 * 1024),
                },
                {
                    "format_id": "480",
                    "url": "https://video.twimg.com/mock_video_480.mp4",
                    "ext": "mp4",
                    "vcodec": "h264",
                    "acodec": "aac",
                    "height": 480,
                    "filesize": int(fmt.get("size_mb", 15) * 0.6 * 1024 * 1024),
                },
            ]
        else:
            mock_formats = []

        return {
            "title": expected["title"],
            "thumbnail": expected["thumbnail"],
            "uploader_id": expected.get("author"),
            "uploader": expected.get("author"),
            "duration": expected.get("duration"),
            "formats": mock_formats,
        }


def create_fxtwitter_response(fixture: dict) -> dict:
    """Create a mock fxtwitter API response from a fixture."""
    expected = fixture["expected_backend_response"]
    formats_data = expected.get("formats", [])

    photos = []
    for i, fmt in enumerate(formats_data):
        if fmt["type"] == "image/jpeg":
            photo_url = (
                expected["thumbnails"][i]
                if i < len(expected["thumbnails"])
                else f"https://pbs.twimg.com/media/photo_{i}.jpg"
            )
            photos.append({"url": photo_url})

    return {
        "tweet": {
            "text": expected["title"],
            "author": {
                "screen_name": expected.get("author"),
                "name": expected.get("author"),
            },
            "media": {
                "photos": photos,
            },
        }
    }


class TestExtractTwitterSingleImage:
    """Test single image Twitter extraction."""

    async def test_single_image_returns_correct_structure(
        self, client, mock_token_store
    ):
        """Test that single image extraction returns correct response structure."""
        fixture = SINGLE_IMAGE_FIXTURE
        expected = fixture["expected_backend_response"]

        # Mock yt-dlp to raise "no video could be found" for image-only tweets
        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.side_effect = RuntimeError("no video could be found")

            # Mock fxtwitter API
            fx_response = create_fxtwitter_response(fixture)
            with respx.mock:
                route = respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json=fx_response))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )

                assert response.status_code == 200
                assert route.called

                data = response.json()

                # Verify platform
                assert data["platform"] == expected["platform"]

                # Verify author
                assert data["author"] == expected["author"]

                # Verify title
                assert data["title"] == expected["title"]

                # Verify thumbnails
                assert len(data["thumbnails"]) == len(expected["thumbnails"])
                assert data["thumbnail"] == expected["thumbnail"]

                # Verify formats - should have 1 image format
                assert len(data["formats"]) == 1
                fmt = data["formats"][0]
                assert fmt["type"] == "image/jpeg"
                assert fmt["label"] == "Foto"
                assert fmt["id"] == "img-1"
                assert fmt["download_url"].startswith("/api/download?token=")

    async def test_single_image_tokenized_download_url(self, client, mock_token_store):
        """Test that download URLs are properly tokenized."""
        fixture = SINGLE_IMAGE_FIXTURE

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.side_effect = RuntimeError("no video could be found")

            fx_response = create_fxtwitter_response(fixture)
            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json=fx_response))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )
                data = response.json()

                # Extract token from download URL
                download_url = data["formats"][0]["download_url"]
                assert download_url.startswith("/api/download?token=")
                token = download_url.split("token=")[1]

                # Verify token is valid by checking it exists in token store
                assert token in mock_token_store._tokens


class TestExtractTwitterSingleVideo:
    """Test single video Twitter extraction."""

    async def test_single_video_returns_video_formats(self, client, mock_token_store):
        """Test that single video extraction returns video formats with quality labels."""
        fixture = SINGLE_VIDEO_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=False)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            # Mock fxtwitter (may return no photos for video tweets)
            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json={"tweet": {"media": {}}}))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )

                assert response.status_code == 200
                data = response.json()

                # Verify platform and metadata
                assert data["platform"] == expected["platform"]
                assert data["author"] == expected["author"]
                assert data["duration"] == expected["duration"]

                # Verify video formats exist
                video_formats = [f for f in data["formats"] if f["type"] == "video/mp4"]
                assert len(video_formats) >= 1

                # Verify format labels include quality
                for fmt in video_formats:
                    assert "Video" in fmt["label"]
                    assert fmt["download_url"].startswith("/api/download?token=")

    async def test_single_video_has_thumbnail(self, client, mock_token_store):
        """Test that single video has correct thumbnail."""
        fixture = SINGLE_VIDEO_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=False)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json={"tweet": {"media": {}}}))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )
                data = response.json()

                assert data["thumbnail"] == expected["thumbnail"]
                assert len(data["thumbnails"]) == len(expected["thumbnails"])


class TestExtractTwitterMultiVideo:
    """Test multi-video (2 videos) Twitter extraction."""

    async def test_multi_video_returns_indexed_labels(self, client, mock_token_store):
        """Test that multi-video extraction returns indexed labels like 'Video 1 · 720p'."""
        fixture = MULTI_VIDEO_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=True)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json={"tweet": {"media": {}}}))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )

                assert response.status_code == 200
                data = response.json()

                # Should have 2 formats (one for each video)
                video_formats = [f for f in data["formats"] if f["type"] == "video/mp4"]
                assert len(video_formats) == 2

                # Verify indexed labels
                labels = [f["label"] for f in video_formats]
                assert any("Video 1" in label for label in labels)
                assert any("Video 2" in label for label in labels)

    async def test_multi_video_has_multiple_thumbnails(self, client, mock_token_store):
        """Test that multi-video has thumbnails for each video."""
        fixture = MULTI_VIDEO_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=True)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json={"tweet": {"media": {}}}))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )
                data = response.json()

                assert len(data["thumbnails"]) == 2


class TestExtractTwitterMultiImage:
    """Test multi-image (2 photos) Twitter extraction."""

    async def test_multi_image_returns_multiple_formats(self, client, mock_token_store):
        """Test that multi-image extraction returns 2 image formats."""
        fixture = MULTI_IMAGE_FIXTURE
        expected = fixture["expected_backend_response"]

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.side_effect = RuntimeError("no video could be found")

            fx_response = create_fxtwitter_response(fixture)
            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json=fx_response))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )

                assert response.status_code == 200
                data = response.json()

                # Should have 2 image formats
                image_formats = [
                    f for f in data["formats"] if f["type"] == "image/jpeg"
                ]
                assert len(image_formats) == 2

                # Verify indexed labels
                labels = [f["label"] for f in image_formats]
                assert any("Foto 1" in label for label in labels)
                assert any("Foto 2" in label for label in labels)

    async def test_multi_image_all_have_tokenized_urls(self, client, mock_token_store):
        """Test that all images have tokenized download URLs."""
        fixture = MULTI_IMAGE_FIXTURE

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.side_effect = RuntimeError("no video could be found")

            fx_response = create_fxtwitter_response(fixture)
            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json=fx_response))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )
                data = response.json()

                # All formats should have tokenized URLs
                for fmt in data["formats"]:
                    assert fmt["download_url"].startswith("/api/download?token=")
                    token = fmt["download_url"].split("token=")[1]
                    assert token in mock_token_store._tokens


class TestExtractTwitterHybrid:
    """Test hybrid (video + image) Twitter extraction."""

    async def test_hybrid_returns_both_video_and_image(self, client, mock_token_store):
        """Test that hybrid extraction returns both video and image sections."""
        fixture = HYBRID_FIXTURE
        expected = fixture["expected_backend_response"]

        # Create mock info with video
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=False)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            # Mock fxtwitter to return the image
            fx_response = create_fxtwitter_response(fixture)
            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json=fx_response))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )

                assert response.status_code == 200
                data = response.json()

                # Should have both video and image formats
                video_formats = [f for f in data["formats"] if f["type"] == "video/mp4"]
                image_formats = [
                    f for f in data["formats"] if f["type"] == "image/jpeg"
                ]

                assert len(video_formats) >= 1, "Should have at least one video format"
                assert len(image_formats) == 1, "Should have one image format"

    async def test_hybrid_has_correct_author_and_thumbnails(
        self, client, mock_token_store
    ):
        """Test that hybrid extraction has correct author and thumbnails."""
        fixture = HYBRID_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=False)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            fx_response = create_fxtwitter_response(fixture)
            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json=fx_response))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )
                data = response.json()

                assert data["author"] == expected["author"]
                assert data["duration"] == expected["duration"]
                assert len(data["thumbnails"]) == 2


class TestExtractErrorMapping:
    """Test error response mapping from exceptions to HTTP status codes."""

    async def test_unsupported_platform_returns_400(self, client):
        """Test ValueError → 400 UNSUPPORTED_PLATFORM."""
        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = ValueError("Unsupported platform for URL")

            response = client.post(
                "/api/extract", json={"url": "https://unsupported.com/video"}
            )

            assert response.status_code == 400
            data = response.json()
            assert data["detail"]["error"] == "UNSUPPORTED_PLATFORM"
            assert "message" in data["detail"]

    async def test_private_content_returns_403(self, client):
        """Test PermissionError → 403 ACCESS_DENIED."""
        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = PermissionError(
                "Login required to access content"
            )

            response = client.post(
                "/api/extract", json={"url": "https://x.com/private/status/123"}
            )

            assert response.status_code == 403
            data = response.json()
            assert data["detail"]["error"] == "ACCESS_DENIED"
            assert "message" in data["detail"]

    async def test_extraction_failure_returns_422(self, client):
        """Test RuntimeError → 422 EXTRACTION_FAILED."""
        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = RuntimeError("Failed to extract media")

            response = client.post(
                "/api/extract", json={"url": "https://x.com/user/status/123"}
            )

            assert response.status_code == 422
            data = response.json()
            assert data["detail"]["error"] == "EXTRACTION_FAILED"
            assert "message" in data["detail"]

    async def test_internal_error_returns_500(self, client):
        """Test unexpected Exception → 500 INTERNAL_ERROR."""
        with patch("app.routers.extract.extract_media_info") as mock_extract:
            mock_extract.side_effect = Exception("Unexpected database error")

            response = client.post(
                "/api/extract", json={"url": "https://x.com/user/status/123"}
            )

            assert response.status_code == 500
            data = response.json()
            assert data["detail"]["error"] == "INTERNAL_ERROR"
            assert "message" in data["detail"]
            data = response.json()
            assert data["detail"]["error"] == "INTERNAL_ERROR"
            assert "message" in data["detail"]


class TestExtractResponseStructure:
    """Test overall response structure compliance with schema."""

    async def test_response_has_required_fields(self, client, mock_token_store):
        """Test that response includes all required MediaResult fields."""
        fixture = SINGLE_VIDEO_FIXTURE
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=False)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json={"tweet": {"media": {}}}))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )
                data = response.json()

                # Check all required fields
                assert "platform" in data
                assert "title" in data
                assert "author" in data
                assert "formats" in data
                assert "thumbnails" in data
                assert "thumbnail" in data
                assert "duration" in data

    async def test_format_has_required_fields(self, client, mock_token_store):
        """Test that each format includes all required Format fields."""
        fixture = SINGLE_VIDEO_FIXTURE
        mock_info = create_mock_ytdlp_info(fixture, is_playlist=False)

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.return_value = mock_info

            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json={"tweet": {"media": {}}}))

                response = client.post(
                    "/api/extract", json={"url": fixture["input_url"]}
                )
                data = response.json()

                for fmt in data["formats"]:
                    assert "id" in fmt
                    assert "label" in fmt
                    assert "type" in fmt
                    assert "download_url" in fmt
                    # size_mb may be null
                    assert "size_mb" in fmt

    async def test_twitter_platform_detection(self, client, mock_token_store):
        """Test that Twitter URLs are correctly detected."""
        fixture = SINGLE_IMAGE_FIXTURE

        with patch("app.services.extractor._extract_info_sync") as mock_ytdlp:
            mock_ytdlp.side_effect = RuntimeError("no video could be found")

            fx_response = create_fxtwitter_response(fixture)
            with respx.mock:
                respx.route(
                    method="GET",
                    url__regex=r"https://api\.fxtwitter\.com/status/\d+",
                ).mock(return_value=Response(200, json=fx_response))

                # Test both x.com and twitter.com domains
                for url in [
                    fixture["input_url"],
                    fixture["input_url"].replace("x.com", "twitter.com"),
                ]:
                    response = client.post("/api/extract", json={"url": url})
                    data = response.json()
                    assert data["platform"] == "twitter"
