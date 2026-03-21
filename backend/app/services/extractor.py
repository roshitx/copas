"""Backwards-compatible re-export from refactored extractors module.

All functionality has been moved to app.services.extractors/.
This module provides re-exports so existing imports and test mocks continue to work.
"""

from app.services.extractors import extract_media_info
from app.services.extractors.base import (
    extract_info_sync as _extract_info_sync,
    create_format as _create_format,
    build_formats as _build_formats,
)
from app.services.extractors.twitter import _extract_tweet_id
from app.services.extractors.facebook import (
    extract_facebook_media as _extract_facebook_hybrid,
    _extract_info_sync_facebook,
    _build_media_result as _build_facebook_media_result,
)
from app.services.extractors.instagram import _extract_photos as _extract_instagram_photos
from app.services.facebook_fallback import extract_facebook_via_fallback
from app.utils.facebook_scope import classify_extraction_error
import app.services.token_store as _token_store_module

__all__ = [
    "extract_media_info",
    "_extract_info_sync",
    "_create_format",
    "_build_formats",
    "_extract_tweet_id",
    "_extract_facebook_hybrid",
    "_extract_info_sync_facebook",
    "_build_facebook_media_result",
    "_extract_instagram_photos",
    "extract_facebook_via_fallback",
    "classify_extraction_error",
    "_token_store_module",
]
