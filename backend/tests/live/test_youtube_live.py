"""
YouTube Live Smoke Tests

These tests make REAL network calls to YouTube via yt-dlp.
They are marked with @pytest.mark.live to allow separate execution:
  - Run live tests: pytest -m live
  - Skip live tests: pytest -m "not live"

URLs sourced from docs/source-test-plan.md
"""

import pytest
from app.services.extractors import extract_media_info

pytestmark = pytest.mark.live

# Canonical YouTube URLs for live testing (from docs/source-test-plan.md)
CANONICAL_URLS = {
    "video": "https://youtu.be/Q1I0ny09g5A",
}


@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_live_video():
    """Live test: standard video extraction from real YouTube."""
    url = CANONICAL_URLS["video"]
    result = await extract_media_info(url)

    assert result.platform == "youtube"
    assert result.title is not None and len(result.title) > 0
    assert result.author is not None and len(result.author) > 0
    assert len(result.formats) >= 1
    video_formats = [f for f in result.formats if "video" in f.type]
    assert len(video_formats) >= 1
