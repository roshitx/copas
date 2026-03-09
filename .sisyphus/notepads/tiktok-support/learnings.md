# TikTok Support Implementation - Learnings

**Date**: 2026-03-09
**Plan**: tiktok-support

## Key Learnings

### 1. Async/Sync Pattern Critical
**Issue**: ThinkDeep identified critical bug in original plan - async functions calling sync helpers.
**Fix**: All format-building functions must be async to properly await `token_store.create_token()`.
**Pattern**: When any function in a call chain needs to await, the entire chain must be async.

### 2. TikWM API Behavior
- Endpoint: `POST https://www.tikwm.com/api/` with `url` form data
- Response: `{"code": 0, "msg": "success", "data": {...}}`
- Video posts have `play` field
- Photo posts have `images` array
- Error indicated by `code: -1`

### 3. Error Code Mapping
| Exception | HTTP Code | When to Use |
|-----------|-----------|-------------|
| TikWMUnavailableError | 503 | Service down, timeout, network error |
| TikWMContentError | 422 | Content not found, private, removed |

### 4. Test Mocking with respx
- Use `respx.post()` to mock TikWM API calls
- Use `httpx.TimeoutException` for timeout testing
- Fixture `mock_token_store` needs monkeypatch for `_token_store_module`

### 5. Token Store Integration
- Must mock `app.services.tiktok_extractor._token_store_module.token_store`
- Follows same pattern as `extractor.py` module
- Token creation happens in async format builders

## Successful Patterns

### Async Chain
```python
async def extract_tiktok_media(url: str) -> MediaResult:
    data = await _fetch_tikwm_data(url)
    return await _build_media_result(data)  # Must await!

async def _build_media_result(data: dict) -> MediaResult:
    formats = await _build_video_formats(data, author)  # Must await!
    ...

async def _build_video_formats(...) -> list[Format]:
    token = await _token_store_module.token_store.create_token(...)  # Must await!
```

### Indonesian Error Messages
Consistent pattern for user-facing errors:
- Service unavailable: "Layanan TikTok sedang tidak tersedia. Coba lagi nanti."
- Content error: "Konten TikTok tidak ditemukan atau bersifat pribadi."
- Network error: "Gagal menghubungi layanan TikTok. Periksa koneksi Anda."

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| backend/app/services/tiktok_extractor.py | CREATE | 169 |
| backend/app/services/extractor.py | MODIFY | +6 |
| backend/app/routers/extract.py | MODIFY | +12 |
| backend/tests/conftest.py | MODIFY | +4 |
| backend/tests/unit/services/test_tiktok_extractor.py | CREATE | 106 |

## Test Results
- 5/5 unit tests passed
- 52/52 total service tests passed
- All error paths covered

## Architecture Decisions

1. **Separate module**: Created `tiktok_extractor.py` instead of adding to `extractor.py` to keep concerns separated
2. **No fallback**: TikWM is the primary method; no automatic fallback to yt-dlp (would require cookies)
3. **HTTP POST**: TikWM uses POST not GET (discovered during testing)
4. **Token reuse**: Same token store module pattern as existing code

## References
- Momus review: Critical bugs identified and fixed
- ThinkDeep analysis: Async/sync mismatch caught pre-implementation
- Manual review: Verified against existing extractor.py patterns
