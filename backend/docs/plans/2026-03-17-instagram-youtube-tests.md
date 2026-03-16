# Instagram & YouTube Test Coverage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add comprehensive unit and integration tests for Instagram and YouTube platforms using yt-dlp extraction.

**Architecture:** Instagram and YouTube use the generic yt-dlp extraction path via `_extract_info_sync()`. Tests will mock yt-dlp responses and verify the MediaResult structure matches expected output.

**Tech Stack:** pytest, pytest-asyncio, respx (HTTP mocking), unittest.mock

---

## Task 1: Create Instagram Test Fixtures

**Files:**
- Create: `tests/fixtures/instagram/reel.json`
- Create: `tests/fixtures/instagram/post-image.json`
- Create: `tests/fixtures/instagram/post-video.json`

**Step 1: Create fixtures directory**

Run: `mkdir -p tests/fixtures/instagram`
Expected: Directory created

**Step 2: Create Instagram Reel fixture**

Create `tests/fixtures/instagram/reel.json`:

```json
{
  "description": "Instagram Reel - vertical short video",
  "url": "https://www.instagram.com/reel/abc123xyz/",
  "mock_ytdlp_response": {
    "id": "abc123xyz",
    "title": "Test Instagram Reel",
    "uploader": "testuser",
    "uploader_id": "testuser",
    "duration": 15,
    "thumbnail": "https://scontent.cdninstagram.com/thumb.jpg",
    "thumbnails": [{"url": "https://scontent.cdninstagram.com/thumb.jpg"}],
    "formats": [
      {
        "format_id": "0",
        "url": "https://scontent.cdninstagram.com/video.mp4",
        "ext": "mp4",
        "vcodec": "h264",
        "acodec": "aac",
        "height": 1280,
        "width": 720,
        "filesize": 2500000
      }
    ]
  },
  "expected_backend_response": {
    "platform": "instagram",
    "title": "Test Instagram Reel",
    "author": "testuser",
    "duration": 15,
    "thumbnail": "https://scontent.cdninstagram.com/thumb.jpg",
    "thumbnails": ["https://scontent.cdninstagram.com/thumb.jpg"],
    "formats": [
      {
        "id": "instagram-video",
        "label": "Video 720x1280",
        "type": "video/mp4",
        "size_mb": 2.38
      }
    ]
  }
}
```

**Step 3: Create Instagram Post (image) fixture**

Create `tests/fixtures/instagram/post-image.json`:

```json
{
  "description": "Instagram Post - single image",
  "url": "https://www.instagram.com/p/xyz789/",
  "mock_ytdlp_response": {
    "id": "xyz789",
    "title": "Beautiful sunset",
    "uploader": "photouser",
    "uploader_id": "photouser",
    "duration": null,
    "thumbnail": "https://scontent.cdninstagram.com/photo.jpg",
    "thumbnails": [{"url": "https://scontent.cdninstagram.com/photo.jpg"}],
    "formats": [
      {
        "format_id": "0",
        "url": "https://scontent.cdninstagram.com/photo.jpg",
        "ext": "jpg",
        "vcodec": "none",
        "acodec": "none",
        "height": 1080,
        "width": 1080,
        "filesize": 500000
      }
    ]
  },
  "expected_backend_response": {
    "platform": "instagram",
    "title": "Beautiful sunset",
    "author": "photouser",
    "duration": null,
    "thumbnail": "https://scontent.cdninstagram.com/photo.jpg",
    "thumbnails": ["https://scontent.cdninstagram.com/photo.jpg"],
    "formats": [
      {
        "id": "instagram-image",
        "label": "Image 1080x1080",
        "type": "image/jpeg",
        "size_mb": 0.48
      }
    ]
  }
}
```

**Step 4: Create Instagram Post (video) fixture**

Create `tests/fixtures/instagram/post-video.json`:

```json
{
  "description": "Instagram Post - video",
  "url": "https://www.instagram.com/p/video123/",
  "mock_ytdlp_response": {
    "id": "video123",
    "title": "My vacation video",
    "uploader": "traveluser",
    "uploader_id": "traveluser",
    "duration": 60,
    "thumbnail": "https://scontent.cdninstagram.com/video_thumb.jpg",
    "thumbnails": [{"url": "https://scontent.cdninstagram.com/video_thumb.jpg"}],
    "formats": [
      {
        "format_id": "0",
        "url": "https://scontent.cdninstagram.com/video.mp4",
        "ext": "mp4",
        "vcodec": "h264",
        "acodec": "aac",
        "height": 1080,
        "width": 1080,
        "filesize": 15000000
      }
    ]
  },
  "expected_backend_response": {
    "platform": "instagram",
    "title": "My vacation video",
    "author": "traveluser",
    "duration": 60,
    "thumbnail": "https://scontent.cdninstagram.com/video_thumb.jpg",
    "thumbnails": ["https://scontent.cdninstagram.com/video_thumb.jpg"],
    "formats": [
      {
        "id": "instagram-video",
        "label": "Video 1080x1080",
        "type": "video/mp4",
        "size_mb": 14.31
      }
    ]
  }
}
```

**Step 5: Commit fixtures**

```bash
git add tests/fixtures/instagram/
git commit -m "test: add Instagram extraction fixtures"
```

---

## Task 2: Create YouTube Test Fixtures

**Files:**
- Create: `tests/fixtures/youtube/video.json`
- Create: `tests/fixtures/youtube/shorts.json`
- Create: `tests/fixtures/youtube/music.json`

**Step 1: Create fixtures directory**

Run: `mkdir -p tests/fixtures/youtube`
Expected: Directory created

**Step 2: Create YouTube video fixture**

Create `tests/fixtures/youtube/video.json`:

```json
{
  "description": "YouTube Standard Video",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "mock_ytdlp_response": {
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "uploader": "Rick Astley",
    "uploader_id": "RickAstleyVEVO",
    "duration": 212,
    "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "thumbnails": [{"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"}],
    "formats": [
      {
        "format_id": "22",
        "url": "https://rr3---sn-q4flrne7.googlevideo.com/videoplayback.mp4",
        "ext": "mp4",
        "vcodec": "avc1.64001F",
        "acodec": "mp4a.40.2",
        "height": 720,
        "width": 1280,
        "filesize": null,
        "tbr": 1500
      },
      {
        "format_id": "18",
        "url": "https://rr3---sn-q4flrne7.googlevideo.com/videoplayback_360.mp4",
        "ext": "mp4",
        "vcodec": "avc1.42001E",
        "acodec": "mp4a.40.2",
        "height": 360,
        "width": 640,
        "filesize": null,
        "tbr": 500
      }
    ]
  },
  "expected_backend_response": {
    "platform": "youtube",
    "title": "Rick Astley - Never Gonna Give You Up",
    "author": "RickAstleyVEVO",
    "duration": 212,
    "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "thumbnails": ["https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"],
    "formats_count_min": 1
  }
}
```

**Step 3: Create YouTube Shorts fixture**

Create `tests/fixtures/youtube/shorts.json`:

```json
{
  "description": "YouTube Shorts - vertical short video",
  "url": "https://www.youtube.com/shorts/abc123shorts",
  "mock_ytdlp_response": {
    "id": "abc123shorts",
    "title": "Quick Tutorial #shorts",
    "uploader": "TechCreator",
    "uploader_id": "TechCreator",
    "duration": 45,
    "thumbnail": "https://i.ytimg.com/vi/abc123shorts/maxresdefault.jpg",
    "thumbnails": [{"url": "https://i.ytimg.com/vi/abc123shorts/maxresdefault.jpg"}],
    "formats": [
      {
        "format_id": "18",
        "url": "https://rr3---sn-q4flrne7.googlevideo.com/shorts.mp4",
        "ext": "mp4",
        "vcodec": "avc1.42001E",
        "acodec": "mp4a.40.2",
        "height": 1280,
        "width": 720,
        "filesize": null,
        "tbr": 800
      }
    ]
  },
  "expected_backend_response": {
    "platform": "youtube",
    "title": "Quick Tutorial #shorts",
    "author": "TechCreator",
    "duration": 45,
    "thumbnail": "https://i.ytimg.com/vi/abc123shorts/maxresdefault.jpg",
    "thumbnails": ["https://i.ytimg.com/vi/abc123shorts/maxresdefault.jpg"],
    "formats_count_min": 1
  }
}
```

**Step 4: Create YouTube music fixture**

Create `tests/fixtures/youtube/music.json`:

```json
{
  "description": "YouTube Music video",
  "url": "https://music.youtube.com/watch?v=music123",
  "mock_ytdlp_response": {
    "id": "music123",
    "title": "Chill Lofi Beats",
    "uploader": "Lofi Girl",
    "uploader_id": "LofiGirl",
    "duration": 3600,
    "thumbnail": "https://i.ytimg.com/vi/music123/maxresdefault.jpg",
    "thumbnails": [{"url": "https://i.ytimg.com/vi/music123/maxresdefault.jpg"}],
    "formats": [
      {
        "format_id": "251",
        "url": "https://rr3---sn-q4flrne7.googlevideo.com/audio.webm",
        "ext": "webm",
        "vcodec": "none",
        "acodec": "opus",
        "height": null,
        "width": null,
        "filesize": null,
        "tbr": 160,
        "abr": 160
      },
      {
        "format_id": "22",
        "url": "https://rr3---sn-q4flrne7.googlevideo.com/video.mp4",
        "ext": "mp4",
        "vcodec": "avc1.64001F",
        "acodec": "mp4a.40.2",
        "height": 720,
        "width": 1280,
        "filesize": null,
        "tbr": 1500
      }
    ]
  },
  "expected_backend_response": {
    "platform": "youtube",
    "title": "Chill Lofi Beats",
    "author": "LofiGirl",
    "duration": 3600,
    "thumbnail": "https://i.ytimg.com/vi/music123/maxresdefault.jpg",
    "thumbnails": ["https://i.ytimg.com/vi/music123/maxresdefault.jpg"],
    "formats_count_min": 1
  }
}
```

**Step 5: Commit fixtures**

```bash
git add tests/fixtures/youtube/
git commit -m "test: add YouTube extraction fixtures"
```

---

## Task 3: Create Instagram Integration Tests

**Files:**
- Create: `tests/integration/api/test_extract_instagram.py`

**Step 1: Write the test file**

Create `tests/integration/api/test_extract_instagram.py`:

```python
"""
Integration tests for /api/extract endpoint covering Instagram scenarios.

Tests Instagram extraction via yt-dlp mocking:
1. Reel extraction
2. Post with image
3. Post with video
4. Private content (403)
5. Extraction failure (422)
"""

import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

from app.main import app

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

FIXTURES_DIR = "tests/fixtures/instagram"


def load_fixture(filename: str) -> dict:
    """Load a JSON fixture file."""
    with open(f"{FIXTURES_DIR}/{filename}", "r") as f:
        return json.load(f)


REEL_FIXTURE = load_fixture("reel.json")
POST_IMAGE_FIXTURE = load_fixture("post-image.json")
POST_VIDEO_FIXTURE = load_fixture("post-video.json")


def create_mock_ytdlp_info(fixture: dict) -> dict:
    """Create a mock yt-dlp info dict from a fixture."""
    return fixture["mock_ytdlp_response"]


class TestInstagramReelExtraction:
    """Tests for Instagram Reel extraction."""

    async def test_reel_returns_correct_structure(self, mock_token_store):
        """Instagram Reel returns MediaResult with video format."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(REEL_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": REEL_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "instagram"
            assert data["title"] == REEL_FIXTURE["expected_backend_response"]["title"]
            assert data["author"] == REEL_FIXTURE["expected_backend_response"]["author"]
            assert data["duration"] == REEL_FIXTURE["expected_backend_response"]["duration"]
            assert len(data["formats"]) >= 1
            assert data["formats"][0]["type"] == "video/mp4"

    async def test_reel_has_thumbnail(self, mock_token_store):
        """Instagram Reel includes thumbnail URL."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(REEL_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": REEL_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["thumbnail"] is not None
            assert len(data["thumbnails"]) >= 1


class TestInstagramPostExtraction:
    """Tests for Instagram Post extraction."""

    async def test_post_image_returns_image_format(self, mock_token_store):
        """Instagram Post with image returns image format."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(POST_IMAGE_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": POST_IMAGE_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "instagram"
            assert data["duration"] is None
            assert len(data["formats"]) >= 1
            assert data["formats"][0]["type"] == "image/jpeg"

    async def test_post_video_returns_video_format(self, mock_token_store):
        """Instagram Post with video returns video format."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(POST_VIDEO_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": POST_VIDEO_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "instagram"
            assert data["duration"] == POST_VIDEO_FIXTURE["expected_backend_response"]["duration"]
            assert len(data["formats"]) >= 1
            assert data["formats"][0]["type"] == "video/mp4"


class TestInstagramErrorHandling:
    """Tests for Instagram error handling."""

    async def test_private_content_returns_403(self, mock_token_store):
        """Private Instagram content returns 403 ACCESS_DENIED."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.side_effect = PermissionError(
                "Konten ini memerlukan login atau tidak dapat diakses."
            )

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://www.instagram.com/p/private123/"}
                )

            assert response.status_code == 403
            data = response.json()
            assert data["error"] == "ACCESS_DENIED"

    async def test_extraction_failure_returns_422(self, mock_token_store):
        """Extraction failure returns 422 EXTRACTION_FAILED."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.side_effect = RuntimeError("Gagal mengekstrak media.")

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://www.instagram.com/p/invalid/"}
                )

            assert response.status_code == 422
            data = response.json()
            assert data["error"] == "EXTRACTION_FAILED"


class TestInstagramPlatformDetection:
    """Tests for Instagram platform detection."""

    async def test_instagram_url_detected(self, mock_token_store):
        """Instagram URL is correctly identified."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(REEL_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://www.instagram.com/reel/test/"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "instagram"

    async def test_instagram_short_url_detected(self, mock_token_store):
        """instagr.am short URL is correctly identified."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(REEL_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://instagr.am/reel/test/"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "instagram"
```

**Step 2: Run tests to verify they pass**

Run: `PYTHONPATH=. uv run pytest tests/integration/api/test_extract_instagram.py -v --tb=short -p no:mcp_eval`
Expected: All tests pass

**Step 3: Commit Instagram tests**

```bash
git add tests/integration/api/test_extract_instagram.py
git commit -m "test: add Instagram integration tests"
```

---

## Task 4: Create YouTube Integration Tests

**Files:**
- Create: `tests/integration/api/test_extract_youtube.py`

**Step 1: Write the test file**

Create `tests/integration/api/test_extract_youtube.py`:

```python
"""
Integration tests for /api/extract endpoint covering YouTube scenarios.

Tests YouTube extraction via yt-dlp mocking:
1. Standard video
2. YouTube Shorts
3. YouTube Music
4. Private video (403)
5. Extraction failure (422)
"""

import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock

from app.main import app

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

FIXTURES_DIR = "tests/fixtures/youtube"


def load_fixture(filename: str) -> dict:
    """Load a JSON fixture file."""
    with open(f"{FIXTURES_DIR}/{filename}", "r") as f:
        return json.load(f)


VIDEO_FIXTURE = load_fixture("video.json")
SHORTS_FIXTURE = load_fixture("shorts.json")
MUSIC_FIXTURE = load_fixture("music.json")


def create_mock_ytdlp_info(fixture: dict) -> dict:
    """Create a mock yt-dlp info dict from a fixture."""
    return fixture["mock_ytdlp_response"]


class TestYouTubeVideoExtraction:
    """Tests for YouTube standard video extraction."""

    async def test_video_returns_correct_structure(self, mock_token_store):
        """YouTube video returns MediaResult with video format."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(VIDEO_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": VIDEO_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"
            assert data["title"] == VIDEO_FIXTURE["expected_backend_response"]["title"]
            assert data["author"] == VIDEO_FIXTURE["expected_backend_response"]["author"]
            assert data["duration"] == VIDEO_FIXTURE["expected_backend_response"]["duration"]
            assert len(data["formats"]) >= 1

    async def test_video_has_thumbnail(self, mock_token_store):
        """YouTube video includes thumbnail URL."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(VIDEO_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": VIDEO_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["thumbnail"] is not None
            assert len(data["thumbnails"]) >= 1

    async def test_video_has_multiple_formats(self, mock_token_store):
        """YouTube video may have multiple quality formats."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(VIDEO_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": VIDEO_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            min_formats = VIDEO_FIXTURE["expected_backend_response"]["formats_count_min"]
            assert len(data["formats"]) >= min_formats


class TestYouTubeShortsExtraction:
    """Tests for YouTube Shorts extraction."""

    async def test_shorts_returns_correct_structure(self, mock_token_store):
        """YouTube Shorts returns MediaResult with video format."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(SHORTS_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": SHORTS_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"
            assert data["title"] == SHORTS_FIXTURE["expected_backend_response"]["title"]
            assert data["duration"] == SHORTS_FIXTURE["expected_backend_response"]["duration"]

    async def test_shorts_short_url_works(self, mock_token_store):
        """youtu.be short URL works for Shorts."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(SHORTS_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://youtu.be/abc123shorts"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"


class TestYouTubeMusicExtraction:
    """Tests for YouTube Music extraction."""

    async def test_music_returns_correct_structure(self, mock_token_store):
        """YouTube Music returns MediaResult with formats."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(MUSIC_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": MUSIC_FIXTURE["url"]}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"
            assert data["duration"] == MUSIC_FIXTURE["expected_backend_response"]["duration"]

    async def test_music_url_detected(self, mock_token_store):
        """music.youtube.com URL is correctly identified."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(MUSIC_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://music.youtube.com/watch?v=test123"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"


class TestYouTubeErrorHandling:
    """Tests for YouTube error handling."""

    async def test_private_video_returns_403(self, mock_token_store):
        """Private YouTube video returns 403 ACCESS_DENIED."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.side_effect = PermissionError(
                "Konten ini memerlukan login atau tidak dapat diakses."
            )

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://www.youtube.com/watch?v=private123"}
                )

            assert response.status_code == 403
            data = response.json()
            assert data["error"] == "ACCESS_DENIED"

    async def test_extraction_failure_returns_422(self, mock_token_store):
        """Extraction failure returns 422 EXTRACTION_FAILED."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.side_effect = RuntimeError("Gagal mengekstrak media.")

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://www.youtube.com/watch?v=invalid"}
                )

            assert response.status_code == 422
            data = response.json()
            assert data["error"] == "EXTRACTION_FAILED"

    async def test_age_restricted_returns_403(self, mock_token_store):
        """Age-restricted video returns 403 ACCESS_DENIED."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.side_effect = PermissionError(
                "Age-restricted content requires login."
            )

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://www.youtube.com/watch?v=agerestricted"}
                )

            assert response.status_code == 403
            data = response.json()
            assert data["error"] == "ACCESS_DENIED"


class TestYouTubePlatformDetection:
    """Tests for YouTube platform detection."""

    async def test_youtube_url_detected(self, mock_token_store):
        """youtube.com URL is correctly identified."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(VIDEO_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://www.youtube.com/watch?v=test123"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"

    async def test_youtu_be_short_url_detected(self, mock_token_store):
        """youtu.be short URL is correctly identified."""
        with patch("app.services.extractor._extract_info_sync") as mock_extract:
            mock_extract.return_value = create_mock_ytdlp_info(VIDEO_FIXTURE)

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/extract",
                    json={"url": "https://youtu.be/test123"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "youtube"
```

**Step 2: Run tests to verify they pass**

Run: `PYTHONPATH=. uv run pytest tests/integration/api/test_extract_youtube.py -v --tb=short -p no:mcp_eval`
Expected: All tests pass

**Step 3: Commit YouTube tests**

```bash
git add tests/integration/api/test_extract_youtube.py
git commit -m "test: add YouTube integration tests"
```

---

## Task 5: Run Full Test Suite and Verify

**Step 1: Run all new tests**

Run: `PYTHONPATH=. uv run pytest tests/integration/api/test_extract_instagram.py tests/integration/api/test_extract_youtube.py -v --tb=short -p no:mcp_eval`
Expected: All tests pass

**Step 2: Run full test suite**

Run: `PYTHONPATH=. uv run pytest tests/ -v --tb=short -p no:mcp_eval --ignore=tests/live/`
Expected: All tests pass

**Step 3: Final commit if any fixes needed**

```bash
git add -A
git commit -m "test: complete Instagram and YouTube test coverage"
```

---

## Summary

**Files Created:**
- `tests/fixtures/instagram/reel.json`
- `tests/fixtures/instagram/post-image.json`
- `tests/fixtures/instagram/post-video.json`
- `tests/fixtures/youtube/video.json`
- `tests/fixtures/youtube/shorts.json`
- `tests/fixtures/youtube/music.json`
- `tests/integration/api/test_extract_instagram.py`
- `tests/integration/api/test_extract_youtube.py`

**Test Coverage Added:**
- Instagram: 10 tests (Reel, Post image, Post video, Error handling, Platform detection)
- YouTube: 13 tests (Video, Shorts, Music, Error handling, Platform detection)

**Total New Tests: 23**