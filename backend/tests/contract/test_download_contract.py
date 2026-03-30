import pytest
import respx
from httpx import Response

pytestmark = [pytest.mark.contract, pytest.mark.asyncio]


class TestDownloadContractSuccess:
    async def test_valid_token_returns_streaming_response_with_headers(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/media.mp4",
            filename="contract_test_video.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media(
            "https://cdn.example.com/media.mp4",
            content=b"mock_media_data",
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert "Content-Disposition" in response.headers
        assert response.headers.get("content-type") == "video/mp4"

    async def test_content_disposition_format_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/file.mp4",
            filename="my_file.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media("https://cdn.example.com/file.mp4")

        response = client.get(f"/api/download?token={token}")

        content_disp = response.headers.get("Content-Disposition", "")
        assert content_disp.startswith("attachment")
        assert 'filename="my_file.mp4"' in content_disp

    async def test_repeated_download_preserves_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/reusable.mp4",
            filename="reusable.mp4",
            content_type="video/mp4",
        )

        for _ in range(3):
            mock_upstream_media("https://cdn.example.com/reusable.mp4")
            response = client.get(f"/api/download?token={token}")

            assert response.status_code == 200
            assert response.headers.get("content-type") == "video/mp4"
            assert "Content-Disposition" in response.headers


class TestDownloadContractFailure:
    async def test_expired_token_returns_410_with_error_detail(
        self, client, mock_token_store
    ):
        import time

        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/expired.mp4",
            filename="expired.mp4",
            content_type="video/mp4",
        )

        mock_token_store._tokens[token].created_at = time.time() - 400

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 410
        json_response = response.json()
        assert "error" in json_response
        assert isinstance(json_response["message"], str)

    async def test_invalid_token_returns_410_schema(self, client):
        response = client.get("/api/download?token=nonexistent-token-xyz")

        assert response.status_code == 410
        json_response = response.json()
        assert "error" in json_response

    async def test_missing_token_returns_422_validation_error(self, client):
        response = client.get("/api/download")

        assert response.status_code == 422
        json_response = response.json()
        assert "detail" in json_response


class TestDownloadContractMediaTypes:
    async def test_video_mp4_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/video.mp4",
            filename="video.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media("https://cdn.example.com/video.mp4")

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.headers.get("content-type") == "video/mp4"
        assert 'filename="video.mp4"' in response.headers.get("Content-Disposition", "")

    async def test_image_jpeg_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/image.jpg",
            filename="image.jpg",
            content_type="image/jpeg",
        )

        mock_upstream_media("https://cdn.example.com/image.jpg")

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.headers.get("content-type") == "image/jpeg"

    async def test_image_png_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/image.png",
            filename="image.png",
            content_type="image/png",
        )

        mock_upstream_media("https://cdn.example.com/image.png")

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.headers.get("content-type") == "image/png"


class TestDownloadContractStreaming:
    async def test_streaming_response_content_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        content = b"streaming_content_data_" * 50

        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/stream.mp4",
            filename="stream.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media(
            "https://cdn.example.com/stream.mp4",
            content=content,
        )

        response = client.get(f"/api/download?token={token}")

        assert response.status_code == 200
        assert response.content == content


class TestDownloadContractTokenBehavior:
    async def test_token_ttl_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        import time

        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/ttl.mp4",
            filename="ttl.mp4",
            content_type="video/mp4",
        )

        mock_upstream_media("https://cdn.example.com/ttl.mp4")
        response1 = client.get(f"/api/download?token={token}")
        assert response1.status_code == 200

        time.sleep(6)

        response2 = client.get(f"/api/download?token={token}")
        assert response2.status_code == 410

    async def test_token_reuse_within_ttl_contract(
        self, client, mock_token_store, mock_upstream_media
    ):
        token = await mock_token_store.create_token(
            download_url="https://cdn.example.com/multi.mp4",
            filename="multi.mp4",
            content_type="video/mp4",
        )

        for i in range(5):
            mock_upstream_media("https://cdn.example.com/multi.mp4")
            response = client.get(f"/api/download?token={token}")

            assert response.status_code == 200, f"Failed on iteration {i}"
            assert response.headers.get("content-type") == "video/mp4"
