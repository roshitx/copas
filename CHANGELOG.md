# CHANGELOG

## [0.1.0] — 2026-03-01

### Added

#### Frontend (Next.js 14 App Router)
- Project scaffold: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, Zustand
- Dark-mode-first theme (hardcoded `dark` class on `<html>`, no toggle)
- `types/index.ts` — shared TypeScript types matching API contract
- `lib/platform-detector.ts` — regex-based platform detection for TikTok, Instagram, YouTube, X/Twitter, Facebook, Threads (incl. short URLs)
- `lib/api.ts` — typed API client with `extractMedia()`, `getDownloadUrl()`, `triggerBrowserDownload()`, `ApiClientError`
- `store/download-store.ts` — Zustand store: url, platform, status, result, error
- `hooks/use-download.ts` — encapsulates extract + download logic
- `components/landing-page.tsx` — main page composition (hero + input + result)
- `components/url-input.tsx` — URL paste input with live platform detection, Copas! button, loading state
- `components/result-card.tsx` — media preview card with thumbnail, title, duration, format buttons
- `components/format-button.tsx` — individual download format button with type badge + file size
- `components/platform-badge.tsx` — animated platform indicator badge
- `components/skeleton-result.tsx` — skeleton loading state for result card
- `app/page.tsx` — root page with SEO metadata
- `.env.local.example` — `NEXT_PUBLIC_BACKEND_URL` env var

#### Backend (FastAPI)
- Project scaffold: FastAPI, yt-dlp, httpx, slowapi, Pydantic v2
- `app/main.py` — FastAPI app with CORS, slowapi rate limiting (10 req/min/IP), `/health` endpoint, lifespan
- `app/routers/extract.py` — `POST /api/extract` endpoint
- `app/routers/download.py` — `GET /api/download?token=` streaming endpoint
- `app/services/extractor.py` — async yt-dlp media info extractor, format builder (360p/720p/1080p + MP3)
- `app/services/token_store.py` — in-memory UUID4 token store, 5-min TTL, background cleanup
- `app/services/streamer.py` — httpx-based streaming response (32KB chunks)
- `app/schemas/extract.py` — Pydantic v2 models: ExtractRequest, Format, MediaResult, ErrorResponse
- `app/utils/platform.py` — URL regex-based platform detection
- `Dockerfile`, `railway.toml`, `.env.example`

#### Documentation
- `docs/api-contract.md` — full API contract specification
- `docs/mvp-handoff.md` — architecture notes, known limitations, next steps
