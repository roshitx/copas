"""
Twitter Live Smoke Tests

These tests make REAL network calls to Twitter/X.
They are marked with @pytest.mark.live to allow separate execution:
  - Run live tests: pytest -m live
  - Skip live tests: pytest -m "not live"

These tests verify extraction works with real upstream services.
They should be run on a schedule or manual dispatch, NOT on every PR.
"""

import pytest
from app.services.extractors import extract_media_info

pytestmark = pytest.mark.live

# Canonical Twitter URLs for live testing (from tests/shared/twitter-scenarios.json)
CANONICAL_URLS = {
    "single_image": "https://x.com/rwhendry/status/2027767749695705372?s=20",
    "single_video": "https://x.com/sosmedkeras/status/2027955413753417803?s=20",
    "multi_video": "https://x.com/mikuroQ/status/2027735620534358393?s=20",
    "multi_image": "https://x.com/IndonesiaGaruda/status/2027914018976108959?s=20",
    "hybrid": "https://x.com/Villgecrazylady/status/2027532953966825726?s=20",
}


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_single_image():
    """Live test: single image extraction from real Twitter."""
    url = CANONICAL_URLS["single_image"]
    result = await extract_media_info(url)

    # Assert: returns MediaResult with basic structure
    assert result.platform == "twitter"
    assert result.title is not None and len(result.title) > 0
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) > 0


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_single_video():
    """Live test: single video extraction from real Twitter."""
    url = CANONICAL_URLS["single_video"]
    result = await extract_media_info(url)

    # Assert: returns MediaResult with basic structure
    assert result.platform == "twitter"
    assert result.title is not None and len(result.title) > 0
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) > 0


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_multi_video():
    """Live test: multi-video extraction from real Twitter."""
    url = CANONICAL_URLS["multi_video"]
    result = await extract_media_info(url)

    # Assert: returns MediaResult with basic structure
    assert result.platform == "twitter"
    assert result.title is not None and len(result.title) > 0
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) > 0


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_multi_image():
    """Live test: multi-image extraction from real Twitter."""
    url = CANONICAL_URLS["multi_image"]
    result = await extract_media_info(url)

    # Assert: returns MediaResult with basic structure
    assert result.platform == "twitter"
    assert result.title is not None and len(result.title) > 0
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) > 0


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_hybrid():
    """Live test: hybrid video+image extraction from real Twitter."""
    url = CANONICAL_URLS["hybrid"]
    result = await extract_media_info(url)

    # Assert: returns MediaResult with basic structure
    assert result.platform == "twitter"
    assert result.title is not None and len(result.title) > 0
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) > 0
