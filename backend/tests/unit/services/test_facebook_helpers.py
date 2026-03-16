"""
Unit tests for facebook_scope.py helper functions.

Tests scope validation and error classification for Facebook extraction.
"""

import pytest

from app.utils.facebook_scope import (
    ErrorClass,
    is_facebook_url_in_scope,
    classify_extraction_error,
)


@pytest.mark.unit
class TestIsFacebookUrlInScope:
    """Test suite for is_facebook_url_in_scope function."""

    def test_watch_url_in_scope(self):
        """facebook.com/watch URLs are in scope."""
        urls = [
            "https://facebook.com/watch?v=123456",
            "https://www.facebook.com/watch?v=abc",
            "https://m.facebook.com/watch?v=xyz",
        ]
        for url in urls:
            assert is_facebook_url_in_scope(url) is True

    def test_videos_url_in_scope(self):
        """facebook.com/{user}/videos/ URLs are in scope."""
        urls = [
            "https://facebook.com/username/videos/123456789/",
            "https://www.facebook.com/someuser/videos/987654321",
            "https://facebook.com/page.name/videos/111222333",
        ]
        for url in urls:
            assert is_facebook_url_in_scope(url) is True

    def test_reel_url_in_scope(self):
        """facebook.com/reel/ URLs are in scope."""
        urls = [
            "https://facebook.com/reel/123456789",
            "https://www.facebook.com/reel/abc123",
        ]
        for url in urls:
            assert is_facebook_url_in_scope(url) is True

    def test_video_php_in_scope(self):
        """facebook.com/video.php URLs are in scope."""
        urls = [
            "https://facebook.com/video.php?v=123456",
            "https://www.facebook.com/video.php?v=987654",
        ]
        for url in urls:
            assert is_facebook_url_in_scope(url) is True

    def test_fb_watch_short_url_in_scope(self):
        """fb.watch short URLs are in scope."""
        urls = [
            "https://fb.watch/abc123xyz",
            "https://fb.watch/video-slug-here",
        ]
        for url in urls:
            assert is_facebook_url_in_scope(url) is True

    def test_profile_url_out_of_scope(self):
        """Plain profile URLs are out of scope (no video pattern)."""
        urls = [
            "https://facebook.com/username",
            "https://facebook.com/username/",
            "https://facebook.com/username/photos",
            "https://facebook.com/username/posts",
        ]
        for url in urls:
            assert is_facebook_url_in_scope(url) is False

    def test_share_v_out_of_scope(self):
        """facebook.com/share/v/ URLs are out of scope (redirect links)."""
        urls = [
            "https://facebook.com/share/v/abc123",
            "https://www.facebook.com/share/v/xyz789",
            "https://m.facebook.com/share/v/test123",
        ]
        for url in urls:
            assert is_facebook_url_in_scope(url) is False

    def test_case_insensitive(self):
        """Scope check is case-insensitive."""
        urls = [
            ("HTTPS://FACEBOOK.COM/WATCH?V=123", True),
            ("https://Facebook.com/Username/Videos/123", True),
            ("https://FACEBOOK.COM/SHARE/V/ABC", False),  # share/v is out of scope
        ]
        for url, expected in urls:
            assert is_facebook_url_in_scope(url) is expected

    def test_out_of_scope_takes_precedence(self):
        """Out-of-scope patterns take precedence over in-scope."""
        url = "https://facebook.com/share/v/watch/123"
        assert is_facebook_url_in_scope(url) is False


@pytest.mark.unit
class TestErrorClass:
    """Test suite for ErrorClass enum."""

    def test_error_class_values(self):
        """ErrorClass has expected values."""
        assert ErrorClass.NO_FALLBACK.value == "no_fallback"
        assert ErrorClass.ALLOW_FALLBACK.value == "allow_fallback"
        assert ErrorClass.TERMINAL_ACCESS.value == "terminal_access"


@pytest.mark.unit
class TestClassifyExtractionError:
    """Test suite for classify_extraction_error function."""

    def test_value_error_is_no_fallback(self):
        """ValueError always maps to NO_FALLBACK."""
        error = ValueError("Some validation error")
        assert classify_extraction_error(error) == ErrorClass.NO_FALLBACK

    def test_permission_error_is_terminal_access(self):
        """PermissionError maps to TERMINAL_ACCESS."""
        error = PermissionError("Access denied")
        assert classify_extraction_error(error) == ErrorClass.TERMINAL_ACCESS

    def test_auth_keywords_are_terminal_access(self):
        """Errors with auth keywords map to TERMINAL_ACCESS."""
        auth_messages = [
            "Login required to view this content",
            "Private video - authentication needed",
            "Cookie file is missing",
            "Please sign in to continue",
            "403 Forbidden - access denied",
            "401 Unauthorized",
            "Account verification required",
            "Session expired",
            "Invalid credentials",
            "Not logged in",
            "Age-restricted content",
        ]
        for msg in auth_messages:
            error = RuntimeError(msg)
            assert classify_extraction_error(error) == ErrorClass.TERMINAL_ACCESS, msg

    def test_invalid_url_keywords_are_no_fallback(self):
        """Errors with invalid URL keywords map to NO_FALLBACK."""
        invalid_messages = [
            "Unsupported URL format",
            "Invalid URL provided",
            "URL not found in database",
            "Not a valid Facebook URL",
            "Malformed URL string",
        ]
        for msg in invalid_messages:
            error = RuntimeError(msg)
            assert classify_extraction_error(error) == ErrorClass.NO_FALLBACK, msg

    def test_transient_errors_allow_fallback(self):
        """Transient errors map to ALLOW_FALLBACK."""
        transient_messages = [
            "Connection timeout",
            "Network error occurred",
            "Temporary failure",
            "Rate limit exceeded",
            "Too many requests - try again later",
            "503 Service Unavailable",
            "502 Bad Gateway",
        ]
        for msg in transient_messages:
            error = RuntimeError(msg)
            assert classify_extraction_error(error) == ErrorClass.ALLOW_FALLBACK, msg

    def test_generic_runtime_error_allows_fallback(self):
        """Unclassified RuntimeError defaults to ALLOW_FALLBACK."""
        error = RuntimeError("Something went wrong during extraction")
        assert classify_extraction_error(error) == ErrorClass.ALLOW_FALLBACK

    def test_generic_exception_allows_fallback(self):
        """Unclassified exceptions default to ALLOW_FALLBACK."""
        error = Exception("Unknown error")
        assert classify_extraction_error(error) == ErrorClass.ALLOW_FALLBACK

    def test_error_message_case_insensitive(self):
        """Error classification is case-insensitive."""
        errors = [
            RuntimeError("LOGIN REQUIRED"),
            RuntimeError("Please Sign In"),
            RuntimeError("CONNECTION TIMEOUT"),
        ]
        assert classify_extraction_error(errors[0]) == ErrorClass.TERMINAL_ACCESS
        assert classify_extraction_error(errors[1]) == ErrorClass.TERMINAL_ACCESS
        assert classify_extraction_error(errors[2]) == ErrorClass.ALLOW_FALLBACK


@pytest.mark.unit
class TestFacebookScopeIntegration:
    """Integration tests for Facebook scope with extractor."""

    def test_scope_constants_defined(self):
        """Module has required constants exported."""
        from app.utils.facebook_scope import (
            FACEBOOK_IN_SCOPE_PATTERNS,
            FACEBOOK_OUT_OF_SCOPE_PATTERNS,
        )

        assert len(FACEBOOK_IN_SCOPE_PATTERNS) > 0
        assert len(FACEBOOK_OUT_OF_SCOPE_PATTERNS) > 0

    def test_in_scope_patterns_are_regex_compatible(self):
        """In-scope patterns compile as valid regex."""
        import re
        from app.utils.facebook_scope import FACEBOOK_IN_SCOPE_PATTERNS

        for pattern in FACEBOOK_IN_SCOPE_PATTERNS:
            _ = re.compile(pattern)  # Verify compilation

    def test_out_of_scope_patterns_are_regex_compatible(self):
        """Out-of-scope patterns compile as valid regex."""
        import re
        from app.utils.facebook_scope import FACEBOOK_OUT_OF_SCOPE_PATTERNS

        for pattern in FACEBOOK_OUT_OF_SCOPE_PATTERNS:
            _ = re.compile(pattern)  # Verify compilation
