"""
Facebook Live Smoke Tests

These tests make REAL network calls to Facebook.
They are marked with @pytest.mark.live to allow separate execution:
  - Run live tests: pytest -m live
  - Skip live tests: pytest -m "not live"

URLs sourced from docs/source-test-plan.md
"""

import pytest
from app.services.extractors import extract_media_info

pytestmark = pytest.mark.live

# Canonical Facebook URLs for live testing (from docs/source-test-plan.md)
CANONICAL_URLS = {
    "video": "https://www.facebook.com/share/r/18Rw4FA12F/",
}


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_live_video():
    """Live test: video extraction from real Facebook."""
    url = CANONICAL_URLS["video"]
    result = await extract_media_info(url)

    assert result.platform == "facebook"
    assert len(result.formats) >= 1
    video_formats = [f for f in result.formats if "video" in f.type]
    assert len(video_formats) >= 1
