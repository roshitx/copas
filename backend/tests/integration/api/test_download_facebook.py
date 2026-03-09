import pytest
from fastapi.testclient import TestClient
from typing import Protocol, cast

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


class TokenStoreLike(Protocol):
    async def create_token(
        self, download_url: str, filename: str, content_type: str
    ) -> str: ...


class MockUpstreamMedia(Protocol):
    def __call__(
        self, url: str, content: bytes = b"", status_code: int = 200
    ) -> object: ...


class TestDownloadFacebookTokenizedFormats:
    async def test_valid_token_download_stream_primary_facebook_format(
        self,
        client: TestClient,
        mock_token_store: TokenStoreLike,
        mock_upstream_media: MockUpstreamMedia,
    ):
        token = await mock_token_store.create_token(
            download_url="https://video.xx.fbcdn.net/facebook_watch_primary_720.mp4",
            filename="facebook_watch_video.mp4",
            content_type="video/mp4",
        )

        video_bytes = b"facebook_primary_video_chunk_" * 80
        _ = mock_upstream_media(
            "https://video.xx.fbcdn.net/facebook_watch_primary_720.mp4",
            content=video_bytes,
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.content == video_bytes
        assert response.headers.get("content-type") == "video/mp4"
        assert 'filename="facebook_watch_video.mp4"' in response.headers.get(
            "Content-Disposition", ""
        )

    @pytest.mark.parametrize(
        "download_url,filename,content_type,payload",
        [
            (
                "https://video.xx.fbcdn.net/facebook_fallback_720.mp4",
                "facebook_fallback_video.mp4",
                "video/mp4",
                b"facebook_fallback_video_chunk_" * 64,
            ),
            (
                "https://audio.xx.fbcdn.net/facebook_fallback_audio.m4a",
                "facebook_fallback_audio.m4a",
                "audio/mp4",
                b"facebook_fallback_audio_chunk_" * 64,
            ),
        ],
    )
    async def test_valid_token_download_stream_fallback_facebook_format(
        self,
        client: TestClient,
        mock_token_store: TokenStoreLike,
        mock_upstream_media: MockUpstreamMedia,
        download_url: str,
        filename: str,
        content_type: str,
        payload: bytes,
    ):
        token = await mock_token_store.create_token(
            download_url=download_url,
            filename=filename,
            content_type=content_type,
        )

        _ = mock_upstream_media(download_url, content=payload)

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.content == payload
        assert response.headers.get("content-type") == content_type
        assert f'filename="{filename}"' in response.headers.get(
            "Content-Disposition", ""
        )

    async def test_expired_token_rejected(self, client: TestClient, expired_token: str):
        response = client.get(f"/api/download?token={expired_token}")

        assert response.status_code == 410
        error_detail = response.text.lower()
        assert (
            "expired" in error_detail
            or "invalid" in error_detail
            or "not found" in error_detail
        )

    async def test_invalid_token_rejected(self, client: TestClient):
        response = client.get("/api/download?token=invalid-facebook-token")

        assert response.status_code == 410
        error_detail = response.text.lower()
        assert (
            "expired" in error_detail
            or "invalid" in error_detail
            or "not found" in error_detail
        )

    async def test_filename_content_disposition_header_for_facebook_media(
        self,
        client: TestClient,
        mock_token_store: TokenStoreLike,
        mock_upstream_media: MockUpstreamMedia,
    ):
        token = await mock_token_store.create_token(
            download_url="https://video.xx.fbcdn.net/facebook_header_test_1080.mp4",
            filename="facebook_reel_61500112233445.mp4",
            content_type="video/mp4",
        )

        _ = mock_upstream_media(
            "https://video.xx.fbcdn.net/facebook_header_test_1080.mp4"
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        content_disp = cast(str, response.headers.get("Content-Disposition", ""))
        assert "attachment" in content_disp
        assert 'filename="facebook_reel_61500112233445.mp4"' in content_disp
