# COPAS.IO — PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-02
**Project:** Copas.io — all-in-one social media content downloader
**Stack:** Next.js 14 (frontend, Vercel) + FastAPI (backend, Railway)

---

## OVERVIEW

Paste any social media URL → auto-detect platform → download media in chosen format.
Supports: TikTok, Instagram, YouTube, X/Twitter, Facebook, Threads. Indonesia-first market.

## STRUCTURE

```
copas.io/
├── frontend/          # Next.js 14 App Router, TypeScript, Tailwind, shadcn/ui
├── backend/           # FastAPI, yt-dlp, Pydantic v2, slowapi
├── tests/             # Shared test fixtures + scenario schemas
├── docs/              # api-contract.md, mvp-handoff.md, testing-platform-expansion.md
├── brief/             # Product briefs
├── prd.md             # Product requirements doc
├── CHANGELOG.md       # Version history
└── package.json       # Root-level UI deps (lucide-react, zustand, etc.)
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| URL extraction logic | `backend/app/services/extractor.py` |
| Download streaming | `backend/app/services/streamer.py` |
| Token management (TTL) | `backend/app/services/token_store.py` |
| Platform detection (FE) | `frontend/lib/platform-detector.ts` |
| API client + errors | `frontend/lib/api.ts` |
| Zustand state | `frontend/store/download-store.ts` |
| TypeScript types | `frontend/types/index.ts` |
| Shared test fixtures | `tests/` (shared JSON scenarios) |
| API contract spec | `docs/api-contract.md` |
| Supported platforms | `frontend/types/index.ts` → `Platform` type |

## ARCHITECTURE

```
[User] → [Next.js FE] → POST /api/extract → [FastAPI BE]
                                              ↓
                                          yt-dlp → token_store (UUID4, 5min TTL)
                                              ↓
           [User] ← download URL (token) ← [FE]
           [User] → GET /api/download?token=… → [BE streams via httpx 32KB chunks]
```

**Backend layers:** `routers/` → `schemas/` → `services/` → `utils/`
**Frontend layers:** `app/` → `components/` → `hooks/` → `lib/` → `store/` → `types/`

## KEY TYPES (frontend/types/index.ts)

- `Platform` — `'tiktok'|'instagram'|'youtube'|'twitter'|'facebook'|'threads'|'unknown'`
- `DownloadStatus` — `'idle'|'loading'|'success'|'error'`
- `Format` — `{id, label, type, size_mb, download_url}`
- `MediaResult` — `{platform, title, thumbnail, thumbnails[], author, duration, formats[]}`
- `ApiError` — `{error, message}`

## BACKEND ERROR CODES

| Exception | HTTP | Code |
|-----------|------|------|
| `ValueError` | 400 | `UNSUPPORTED_PLATFORM` |
| `PermissionError` | 403 | `ACCESS_DENIED` |
| `RuntimeError` | 422 | `EXTRACTION_FAILED` |
| `Exception` | 500 | — |

## CONVENTIONS

- Backend: async FastAPI, Pydantic v2 schemas, `asyncio_mode=auto` in pytest
- Frontend: strict TypeScript (`strict: true`), path alias `@/*` → `./`, no src/ dir
- Rate limit: 10 req/min/IP on `/api/extract`
- x.com URLs normalized → twitter.com before yt-dlp
- Token store is **in-memory** (no persistence, lost on restart)
- API client uses 30s timeout, throws `ApiClientError(code, message, status)`

## ANTI-PATTERNS

- Do NOT use `as any` or `@ts-ignore`
- Do NOT add database persistence to token_store without discussing state loss implications
- Do NOT add new platforms without updating `Platform` type in `frontend/types/index.ts`
- Do NOT hardcode `NEXT_PUBLIC_BACKEND_URL` — always from env
- Do NOT use `jest` — frontend uses Playwright, backend uses pytest

## ENVIRONMENT VARS

```
# Backend (.env)
ALLOWED_ORIGINS=        # comma-separated CORS origins
PORT=                   # uvicorn port
YTDLP_COOKIE_FILE=      # path to cookies.txt for age-restricted content

# Frontend (.env.local)
NEXT_PUBLIC_BACKEND_URL=  # full URL of backend (e.g. https://api.copas.io)
```

## COMMANDS

```bash
# Frontend
cd frontend && npm run dev          # dev server
cd frontend && npm run build        # production build
cd frontend && npm run test:e2e     # Playwright tests

# Backend
cd backend && uvicorn app.main:app --reload   # dev server
cd backend && pytest                          # all tests
cd backend && pytest -m unit                  # unit only
cd backend && pytest -m integration           # integration only
cd backend && pytest -m live                  # live (hits real APIs)

# Root (UI deps)
npm install                         # installs root-level deps
```

## TEST MARKERS (backend)

`unit`, `integration`, `contract`, `live`, `smoke`, `timeout`

## NOTES

- `.sisyphus/` — AI agent state/plans (boulder.json). Ignore in code changes.
- `.opencode/skills/` — AI skill definitions. Ignore in code changes.
- Shared Twitter test fixtures live in BOTH `tests/` AND `frontend/tests/fixtures/twitter/` AND `backend/tests/fixtures/twitter/` — keep in sync.
- `jszip` dep exists at root level — used in frontend for bundling multi-image downloads.

---

## Kombinasi Skills Optimal Per Skenario

| Skenario | Load Skills |
|---|---|
| Buat React component baru | `coding-standards` + `frontend-patterns` + `web-design-guidelines` |
| Polish / transform existing UI | `frontend-ui-ux-engineer` + `ui-ux-pro-max` + `web-design-guidelines` |
| Tambah animasi/micro-interaction | `animation-designer` + `frontend-patterns` |
| Setup design system | `design-foundation` + `ui-ux-pro-max` |
| Implement shadcn component | `shadcn-ui-expert` + `coding-standards` + `web-design-guidelines` |
| Build Next.js page baru | `vercel-react-best-practices` + `frontend-patterns` + `coding-standards` |
| Buat API endpoint | `backend-patterns` + `tdd-workflow` |
| Full UI feature (end-to-end) | `frontend-ui-ux-engineer` + `animation-designer` + `shadcn-ui-expert` + `coding-standards` + `frontend-patterns` + `web-design-guidelines` |
| Ship MVP cepat | `mvp-builder` + `design-foundation` + `shadcn-ui-expert` |
| Bug fix | `tdd-workflow` + `backend-patterns` (atau `frontend-patterns`) |

---

## Anti-Patterns yang Dilarang (Global)

- Jangan pakai emoji sebagai icon — gunakan SVG dari Lucide atau Simple Icons
- Jangan animasi `width`/`height` — gunakan `transform` (GPU)
- Jangan `as any` atau `@ts-ignore`
- Jangan `div` untuk elemen interaktif — gunakan `button`
- Jangan `outline: none` — gunakan `:focus-visible`
- Jangan barrel file (`index.ts` re-export semua) — import langsung
- Jangan hardcode warna inline — pakai CSS variables / Tailwind tokens
- Jangan layout-shift saat hover — animasikan `transform` bukan layout properties
- Jangan `placeholder` sebagai pengganti `label`
- Jangan `tabindex > 0`
