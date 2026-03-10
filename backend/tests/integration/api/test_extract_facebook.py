import json
from typing import Protocol, TypedDict, cast
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.utils.facebook_scope import ErrorClass

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

FIXTURES_DIR = "tests/fixtures/facebook"


class ExpectedFormat(TypedDict):
    id: str
    label: str
    type: str
    size_mb: float
    download_url: str


class ExpectedBackendResponse(TypedDict):
    platform: str
    author: str
    title: str
    formats: list[ExpectedFormat]
    thumbnails: list[str]
    thumbnail: str
    duration: int


class FacebookSuccessFixture(TypedDict):
    input_url: str
    expected_backend_response: ExpectedBackendResponse


class FacebookErrorFixture(TypedDict):
    input_url: str


class TokenStoreLike(Protocol):
    _tokens: dict[str, object]

    async def create_token(
        self, download_url: str, filename: str, content_type: str
    ) -> str: ...

    async def get_token(self, token: str) -> object | None: ...


def load_fixture(filename: str) -> dict[str, object]:
    with open(f"{FIXTURES_DIR}/{filename}", "r") as f:
        return cast(dict[str, object], json.load(f))


WATCH_FIXTURE = cast(
    FacebookSuccessFixture,
    cast(object, load_fixture("single-video-watch.json")),
)



def create_mock_facebook_info(fixture: FacebookSuccessFixture) -> dict[str, object]:
    expected = fixture["expected_backend_response"]
    fmt = expected["formats"][0]
    return {
        "title": expected["title"],
        "thumbnail": expected["thumbnail"],
        "thumbnails": [{"url": expected["thumbnail"]}],
        "uploader_id": expected["author"],
        "uploader": expected["author"],
        "duration": expected["duration"],
        "formats": [
            {
                "format_id": fmt["id"],
                "url": "https://video.xx.fbcdn.net/mock_watch_720.mp4",
                "ext": "mp4",
                "vcodec": "h264",
                "acodec": "aac",
                "height": 720,
                "filesize": int(fmt["size_mb"] * 1024 * 1024),
            }
        ],
    }


async def create_fallback_result_with_token(
    mock_token_store: TokenStoreLike,
) -> dict[str, object]:
    token = await mock_token_store.create_token(
        "https://video.xx.fbcdn.net/mock_fallback_720.mp4",
        "facebook_fallback_copas_io.mp4",
        "video/mp4",
    )
    return {
        "platform": "facebook",
        "title": "Fallback Facebook Video",
        "author": "fallbackcreator",
        "thumbnail": "https://scontent.xx.fbcdn.net/fallback-thumb.jpg",
        "thumbnails": ["https://scontent.xx.fbcdn.net/fallback-thumb.jpg"],
        "duration": 35,
        "formats": [
            {
                "id": "720",
                "label": "Video 720p",
                "type": "video/mp4",
                "size_mb": 18.2,
                "download_url": f"/api/download?token={token}",
            }
        ],
    }


class TestExtractFacebookHybridMatrix:
    async def test_primary_success_path_returns_tokenized_format(
        self, client: TestClient, mock_token_store: TokenStoreLike
    ):
        fixture = WATCH_FIXTURE
        expected = fixture["expected_backend_response"]
        mock_info = create_mock_facebook_info(fixture)

        with patch(
            "app.services.extractor._extract_info_sync_facebook"
        ) as mock_primary:
            mock_primary.return_value = mock_info

            response = client.post("/api/extract", json={"url": fixture["input_url"]})

            assert response.status_code == 200
            data = cast(dict[str, object], response.json())
            assert cast(str, data["platform"]) == expected["platform"]
            assert cast(str, data["author"]) == expected["author"]
            assert cast(str, data["title"]) == expected["title"]

            formats = cast(list[dict[str, object]], data["formats"])
            assert len(formats) == 1
            assert cast(str, formats[0]["type"]) == "video/mp4"

            download_url = cast(str, formats[0]["download_url"])
            assert download_url.startswith("/api/download?token=")
            token = download_url.split("token=")[1]
            token_data = await mock_token_store.get_token(token)
            assert token_data is not None

    async def test_primary_fail_allow_fallback_success_path(
        self, client: TestClient, mock_token_store: TokenStoreLike
    ):
        fixture = WATCH_FIXTURE
        fallback_result = await create_fallback_result_with_token(mock_token_store)

        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_primary,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
            patch(
                "app.services.extractor.extract_facebook_via_fallback",
                new_callable=AsyncMock,
            ) as mock_fallback,
        ):
            mock_primary.side_effect = RuntimeError("Primary extractor timeout")
            mock_classify.return_value = ErrorClass.ALLOW_FALLBACK
            mock_fallback.return_value = fallback_result

            response = client.post("/api/extract", json={"url": fixture["input_url"]})

            assert response.status_code == 200
            data = cast(dict[str, object], response.json())
            assert cast(str, data["platform"]) == "facebook"
            assert cast(str, data["title"]) == "Fallback Facebook Video"

            formats = cast(list[dict[str, object]], data["formats"])
            download_url = cast(str, formats[0]["download_url"])
            assert download_url.startswith("/api/download?token=")
            mock_fallback.assert_called_once_with(fixture["input_url"])

            token = download_url.split("token=")[1]
            token_data = await mock_token_store.get_token(token)
            assert token_data is not None

    async def test_primary_fail_fallback_fail_returns_422_extraction_failed(
        self, client: TestClient
    ):
        fixture = WATCH_FIXTURE

        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_primary,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
            patch(
                "app.services.extractor.extract_facebook_via_fallback",
                new_callable=AsyncMock,
            ) as mock_fallback,
        ):
            mock_primary.side_effect = RuntimeError("Primary extractor timeout")
            mock_classify.return_value = ErrorClass.ALLOW_FALLBACK
            mock_fallback.side_effect = RuntimeError("Fallback provider down")

            response = client.post("/api/extract", json={"url": fixture["input_url"]})

            assert response.status_code == 422
            data = cast(dict[str, object], response.json())
            detail = cast(dict[str, object], data["detail"])
            assert cast(str, detail["error"]) == "EXTRACTION_FAILED"



    async def test_error_code_terminal_access_returns_403_access_denied(
        self, client: TestClient
    ):
        fixture = WATCH_FIXTURE

        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_primary,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
        ):
            mock_primary.side_effect = PermissionError("Login required")
            mock_classify.return_value = ErrorClass.TERMINAL_ACCESS

            response = client.post("/api/extract", json={"url": fixture["input_url"]})

            assert response.status_code == 403
            data = cast(dict[str, object], response.json())
            detail = cast(dict[str, object], data["detail"])
            assert cast(str, detail["error"]) == "ACCESS_DENIED"

    async def test_error_code_no_fallback_immediate_failure_without_fallback_attempt(
        self, client: TestClient
    ):
        fixture = WATCH_FIXTURE

        with (
            patch("app.services.extractor._extract_info_sync_facebook") as mock_primary,
            patch("app.services.extractor.classify_extraction_error") as mock_classify,
            patch(
                "app.services.extractor.extract_facebook_via_fallback",
                new_callable=AsyncMock,
            ) as mock_fallback,
        ):
            mock_primary.side_effect = ValueError("Invalid Facebook URL")
            mock_classify.return_value = ErrorClass.NO_FALLBACK

            response = client.post("/api/extract", json={"url": fixture["input_url"]})

            assert response.status_code == 400
            data = cast(dict[str, object], response.json())
            detail = cast(dict[str, object], data["detail"])
            assert cast(str, detail["error"]) == "UNSUPPORTED_PLATFORM"
            mock_fallback.assert_not_called()
