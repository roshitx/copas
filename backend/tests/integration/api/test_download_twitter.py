import pytest
import respx
from httpx import Response

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TestDownloadTokenValidation:
    async def test_valid_token_returns_200_with_streaming_body(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://video.twimg.com/test_video.mp4",
            filename="test_video.mp4",
            content_type="video/mp4",
        )

        mock_video_data = b"mock_video_content_" * 100
        mock_upstream_media(
            "https://video.twimg.com/test_video.mp4",
            content=mock_video_data,
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.content == mock_video_data

    async def test_expired_token_returns_410(self, client, expired_token):
        response = client.get(f"/api/download?token={expired_token}")

        assert response.status_code == 410
        error_detail = response.json()["detail"].lower()
        assert (
            "expired" in error_detail
            or "invalid" in error_detail
            or "not found" in error_detail
        )

    async def test_invalid_token_returns_410(self, client):
        response = client.get("/api/download?token=invalid-token-12345")

        assert response.status_code == 410
        error_detail = response.json()["detail"].lower()
        assert (
            "expired" in error_detail
            or "invalid" in error_detail
            or "not found" in error_detail
        )

    async def test_missing_token_query_param(self, client):
        response = client.get("/api/download")

        assert response.status_code == 422


class TestDownloadHeaders:
    async def test_content_disposition_header_matches_filename(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://video.twimg.com/test.mp4",
            filename="my_custom_video.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media("https://video.twimg.com/test.mp4")

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp
        assert 'filename="my_custom_video.mp4"' in content_disp

    async def test_content_type_matches_media_type(
        self, client, mock_token_store, mock_upstream_media
    ):
        video_token = await mock_token_store.create_token(
            download_url="https://video.twimg.com/test.mp4",
            filename="video.mp4",
            content_type="video/mp4",
        )
        mock_upstream_media("https://video.twimg.com/test.mp4")

        response = client.get(f"/api/download?token={video_token}")
        assert response.headers.get("content-type") == "video/mp4"

    async def test_content_type_jpeg_image(
        self, client, mock_token_store, mock_upstream_media
    ):
        image_token = await mock_token_store.create_token(
            download_url="https://pbs.twimg.com/media/test.jpg",
            filename="image.jpg",
            content_type="image/jpeg",
        )
        mock_upstream_media("https://pbs.twimg.com/media/test.jpg")

        response = client.get(f"/api/download?token={image_token}")
        assert response.headers.get("content-type") == "image/jpeg"

    async def test_content_type_png_image(
        self, client, mock_token_store, mock_upstream_media
    ):
        image_token = await mock_token_store.create_token(
            download_url="https://pbs.twimg.com/media/test.png",
            filename="image.png",
            content_type="image/png",
        )
        mock_upstream_media("https://pbs.twimg.com/media/test.png")

        response = client.get(f"/api/download?token={image_token}")
        assert response.headers.get("content-type") == "image/png"


class TestDownloadStreaming:
    async def test_streaming_response_chunks(
        self, client, mock_token_store, mock_upstream_media
    ):
        large_content = b"x" * (32768 * 3)

        token = await mock_token_store.create_token(
            download_url="https://video.twimg.com/large.mp4",
            filename="large_video.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media(
            "https://video.twimg.com/large.mp4",
            content=large_content,
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert len(response.content) == len(large_content)
        assert response.content == large_content


class TestDownloadRepeatedAccess:
    async def test_repeated_download_with_same_token_works(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://video.twimg.com/shared.mp4",
            filename="shared_video.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media("https://video.twimg.com/shared.mp4")

        response1 = client.get(f"/api/download?token={token}")
        assert response1.status_code == 200

        mock_upstream_media("https://video.twimg.com/shared.mp4")
        response2 = client.get(f"/api/download?token={token}")
        assert response2.status_code == 200

        mock_upstream_media("https://video.twimg.com/shared.mp4")
        response3 = client.get(f"/api/download?token={token}")
        assert response3.status_code == 200

    async def test_token_expires_after_ttl(
        self, client, mock_token_store, mock_upstream_media
    ):
        import time

        token = await mock_token_store.create_token(
            download_url="https://video.twimg.com/temp.mp4",
            filename="temp_video.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media("https://video.twimg.com/temp.mp4")
        response1 = client.get(f"/api/download?token={token}")
        assert response1.status_code == 200

        time.sleep(6)

        response2 = client.get(f"/api/download?token={token}")
        assert response2.status_code == 410


class TestDownloadPlatformSpecific:
    async def test_twitter_video_download(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://video.twimg.com/ext_tw_video/123/twitter_video.mp4",
            filename="twitter_123_video.mp4",
            content_type="video/mp4",
        )

        route = mock_upstream_media(
            "https://video.twimg.com/ext_tw_video/123/twitter_video.mp4"
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert route.called

    async def test_instagram_image_download(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://scontent-ams2-1.cdninstagram.com/v/t51.2885-15/insta_image.jpg",
            filename="instagram_image.jpg",
            content_type="image/jpeg",
        )

        mock_upstream_media(
            "https://scontent-ams2-1.cdninstagram.com/v/t51.2885-15/insta_image.jpg"
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.headers.get("content-type") == "image/jpeg"
        content_disp = response.headers.get("Content-Disposition", "")
        assert 'filename="instagram_image.jpg"' in content_disp
