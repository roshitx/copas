# BACKEND/APP — LAYER GUIDE

## LAYER ORDER (strict)

```
routers/ → schemas/ → services/ → utils/
```

Routers call services. Services call utils. Schemas are used by routers for request/response validation. No cross-layer skipping.

## WHAT LIVES WHERE

| Layer | File | Responsibility |
|-------|------|----------------|
| `routers/` | `extract.py` | POST /api/extract — rate limiting, error mapping |
| `routers/` | `download.py` | GET /api/download?token= — token validation, streaming |
| `schemas/` | `extract.py` | Pydantic v2 request/response models |
| `services/` | `extractor.py` | yt-dlp invocation, platform handling, Format building |
| `services/` | `streamer.py` | httpx 32KB chunked streaming |
| `services/` | `token_store.py` | In-memory UUID4 token store, 5-min TTL |
| `utils/` | `platform.py` | URL normalization (x.com→twitter.com), platform detection |
| `main.py` | — | App factory: CORS, slowapi, lifespan, route registration |

## ANTI-PATTERNS

- No business logic in `routers/` — delegate to `services/`
- No direct yt-dlp calls outside `extractor.py`
- No token manipulation outside `token_store.py`
