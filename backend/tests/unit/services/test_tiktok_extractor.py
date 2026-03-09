"""Unit tests for TikTok extractor."""

import pytest
import respx
import httpx
from httpx import Response
import respx
import httpx

from app.services.tiktok_extractor import (
    extract_tiktok_media,
    TikWMUnavailableError,
    TikWMContentError,
)


class TestExtractTiktokMedia:
    """Tests for extract_tiktok_media function."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_successful_video_extraction(self, mock_token_store):
        """Test successful extraction of TikTok video."""
        respx.post("https://www.tikwm.com/api/").mock(
            return_value=Response(
                200,
                json={
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "id": "123",
                        "title": "Test Video",
                        "play": "https://test.com/video.mp4",
                        "author": {"nickname": "testuser"},
                        "cover": "https://test.com/thumb.jpg",
                        "duration": 30,
                    },
                },
            )
        )

        result = await extract_tiktok_media("https://www.tiktok.com/@user/video/123")

        assert result.platform == "tiktok"
        assert result.title == "Test Video"
        assert result.author == "testuser"
        assert result.duration == 30
        assert len(result.formats) == 1
        assert result.formats[0].type == "video/mp4"

    @respx.mock
    @pytest.mark.asyncio
    async def test_photo_post_extraction(self, mock_token_store):
        """Test extraction of TikTok photo post."""
        respx.post("https://www.tikwm.com/api/").mock(
            return_value=Response(
                200,
                json={
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "id": "456",
                        "title": "Photo Post",
                        "images": [
                            "https://test.com/img1.jpg",
                            "https://test.com/img2.jpg",
                        ],
                        "author": {"nickname": "photouser"},
                    },
                },
            )
        )

        result = await extract_tiktok_media("https://www.tiktok.com/@user/photo/456")

        assert result.platform == "tiktok"
        assert result.duration is None
        assert len(result.formats) == 2
        assert all(f.type == "image/jpeg" for f in result.formats)

    @respx.mock
    @pytest.mark.asyncio
    async def test_api_error_content_not_found(self):
        """Test error handling for content not found."""
        respx.post("https://www.tikwm.com/api/").mock(
            return_value=Response(200, json={"code": -1, "msg": "Video not found"})
        )

        with pytest.raises(TikWMContentError):
            await extract_tiktok_media("https://www.tiktok.com/@user/video/999")

    @respx.mock
    @pytest.mark.asyncio
    async def test_api_unavailable(self):
        """Test error handling for API unavailable."""
        respx.post("https://www.tikwm.com/api/").mock(return_value=Response(503))

        with pytest.raises(TikWMUnavailableError):
            await extract_tiktok_media("https://www.tiktok.com/@user/video/123")

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test error handling for timeout."""
        respx.post("https://www.tikwm.com/api/").mock(side_effect=httpx.TimeoutException("Request timed out"))

        with pytest.raises(TikWMUnavailableError):
            await extract_tiktok_media("https://www.tiktok.com/@user/video/123")
