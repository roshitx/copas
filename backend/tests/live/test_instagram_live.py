"""
Instagram Live Smoke Tests

These tests make REAL network calls to Instagram.
They are marked with @pytest.mark.live to allow separate execution:
  - Run live tests: pytest -m live
  - Skip live tests: pytest -m "not live"

URLs sourced from docs/source-test-plan.md
"""

import pytest
from app.services.extractors import extract_media_info

pytestmark = pytest.mark.live

# Canonical Instagram URLs for live testing (from docs/source-test-plan.md)
CANONICAL_URLS = {
    "photo_only": "https://www.instagram.com/p/DWJRVycEZu3/",
    "video_reel": "https://www.instagram.com/reel/DWJHJLYTN7d/",
    "multiphoto": "https://www.instagram.com/p/DWGlvZVkyh5/",
    "multivideo": "https://www.instagram.com/p/DVXiyNHE78b/",
}


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_photo_only():
    """Live test: single photo extraction from real Instagram."""
    url = CANONICAL_URLS["photo_only"]
    result = await extract_media_info(url)

    assert result.platform == "instagram"
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) >= 1
    image_formats = [f for f in result.formats if "image" in f.type]
    assert len(image_formats) >= 1


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_video_reel():
    """Live test: reel extraction from real Instagram."""
    url = CANONICAL_URLS["video_reel"]
    result = await extract_media_info(url)

    assert result.platform == "instagram"
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) >= 1
    video_formats = [f for f in result.formats if "video" in f.type]
    assert len(video_formats) >= 1


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_multiphoto():
    """Live test: multi-photo carousel extraction from real Instagram."""
    url = CANONICAL_URLS["multiphoto"]
    result = await extract_media_info(url)

    assert result.platform == "instagram"
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) >= 2
    image_formats = [f for f in result.formats if "image" in f.type]
    assert len(image_formats) >= 2


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_multivideo():
    """Live test: multi-video carousel extraction from real Instagram."""
    url = CANONICAL_URLS["multivideo"]
    result = await extract_media_info(url)

    assert result.platform == "instagram"
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) >= 2
