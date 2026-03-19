# BACKEND — KNOWLEDGE BASE

**Stack:** FastAPI 0.115, Python, yt-dlp, httpx, slowapi, Pydantic v2, pytest

## STRUCTURE

```
backend/
├── app/
│   ├── main.py            # FastAPI entry: CORS, slowapi, lifespan, route registration
│   ├── routers/           # extract.py, download.py
│   ├── schemas/           # extract.py (Pydantic v2 request/response models)
│   ├── services/          # extractor.py, streamer.py, token_store.py
│   └── utils/             # platform.py (platform detection helpers)
├── tests/
│   ├── conftest.py
│   ├── contract/          # API contract tests
│   ├── fixtures/twitter/  # JSON fixtures (mirror of tests/ root + frontend/)
│   ├── integration/api/   # test_extract_twitter.py, test_download_twitter.py
│   ├── live/              # test_twitter_live.py (hits real APIs)
│   └── unit/services/     # test_extractor_helpers.py, test_token_store.py
├── .env.example
├── Dockerfile
├── pytest.ini
└── railway.toml
```

## WHERE TO LOOK

| Task | File |
|------|------|
| Request routing | `app/routers/extract.py`, `app/routers/download.py` |
| Pydantic schemas | `app/schemas/extract.py` |
| yt-dlp extraction | `app/services/extractor.py` |
| Download streaming | `app/services/streamer.py` |
| Token lifecycle | `app/services/token_store.py` |
| Platform normalization | `app/utils/platform.py` |
| App bootstrap | `app/main.py` |

## KEY BEHAVIORS

**extractor.py:** `extract_media_info(url)` → detect platform → normalize x.com→twitter.com → run yt-dlp in `asyncio` executor → handle playlist type (multi-media tweets) → return `Format` list.

**token_store.py:** In-memory `dict[UUID4 → metadata]`. 5-min TTL. Cleanup runs as background task started in `lifespan`. **Lost on restart** — no persistence.

**streamer.py:** httpx streaming, 32KB chunks. Used for proxied downloads.

**Rate limiting:** 10 req/min/IP on `POST /api/extract` via slowapi.

## ERROR MAPPING

| Raise | HTTP | Body code |
|-------|------|-----------|
| `ValueError` | 400 | `UNSUPPORTED_PLATFORM` |
| `PermissionError` | 403 | `ACCESS_DENIED` |
| `RuntimeError` | 422 | `EXTRACTION_FAILED` |
| `Exception` | 500 | — |

## CONVENTIONS

- All route handlers are `async`
- Schemas use Pydantic v2 (`.model_validate()`, not `.parse_obj()`)
- Tests use `asyncio_mode=auto` — no manual `@pytest.mark.asyncio` needed
- Test markers: `unit`, `integration`, `contract`, `live`, `smoke`, `timeout`
- x.com URLs always normalized to twitter.com before passing to yt-dlp

## ANTI-PATTERNS

- Do NOT add persistence to `token_store` without discussing data loss implications
- Do NOT add new platforms without updating `Platform` type in `frontend/types/index.ts`
- Do NOT use `jest` — backend tests are pytest only
- Do NOT run `live` tests in CI — they hit real external APIs

## COMMANDS

```bash
uvicorn app.main:app --reload   # dev server
pytest                          # all tests
pytest -m unit                  # unit only
pytest -m integration           # integration only
pytest -m live                  # live (hits real APIs — use sparingly)
pytest -m "not live"            # everything except live
```

## ENV VARS

```
ALLOWED_ORIGINS=   # comma-separated CORS origins
PORT=              # uvicorn port (Railway sets automatically)
YTDLP_COOKIE_FILE= # path to cookies.txt for age-restricted content
```

## NOTES

- Twitter test fixtures at `tests/fixtures/twitter/` must stay in sync with `tests/` (root) and `frontend/tests/fixtures/twitter/`
- `railway.toml` handles Railway deployment config — do not hardcode PORT
