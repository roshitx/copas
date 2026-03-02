# Copas.io MVP — Handoff Document

## Status: Phase 1 MVP Complete

---

## Architecture Summary

```
[User Browser]
      │ paste URL
      ▼
[Next.js 14 — Vercel]
  app/page.tsx → LandingPage
      │ POST /api/extract
      ▼
[FastAPI Backend — Railway]
  routers/extract.py → services/extractor.py
      │ yt-dlp Python API
      ▼
  token_store.py creates token → returns formats with /api/download?token=
      │
[User clicks Download]
      │ GET /api/download?token=
      ▼
  routers/download.py → services/streamer.py → httpx → remote media URL
      │ StreamingResponse (32KB chunks)
      ▼
[Browser saves file]
```

---

## Key Design Decisions

### 1. No File Storage
Media is never stored on the server. The backend:
1. Extracts media URLs via yt-dlp
2. Creates short-lived tokens mapping to those URLs
3. On download request, proxies the stream from the origin to the browser

### 2. Token System (In-Memory, MVP Only)
- Tokens are UUID4 strings stored in a Python dict
- 5-minute TTL enforced at read time
- Background cleanup task runs every 5 minutes
- **Single-instance limitation**: tokens don't survive restarts or scale horizontally
- **Phase 2 upgrade path**: Replace with Redis (key already in place via `ALLOWED_ORIGINS` env pattern)

### 3. Dark-Mode-Only
- `<html className="dark">` is hardcoded in layout.tsx
- No toggle, no system preference detection — always dark
- Simplifies CSS — only dark CSS vars needed

### 4. Platform Detection
Runs in two places:
- **Frontend** (`lib/platform-detector.ts`): Immediate UI feedback (badge) before API call
- **Backend** (`app/utils/platform.py`): Authoritative detection for yt-dlp routing

---

## Environment Variables

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000  # dev
# NEXT_PUBLIC_BACKEND_URL=https://your-app.up.railway.app  # prod
```

### Backend (`backend/.env`)
```
ALLOWED_ORIGINS=*          # restrict in prod
PORT=8000                  # Railway sets this automatically
```

---

## Running Locally

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local: set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev   # → http://localhost:3000
```

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
# Health check: GET http://localhost:8000/health
```

---

## Deployment

### Frontend → Vercel
1. Push `frontend/` to GitHub
2. Import in Vercel → set **Root Directory** = `frontend`
3. Add env var: `NEXT_PUBLIC_BACKEND_URL=https://your-railway-app.up.railway.app`

### Backend → Railway
1. Push `backend/` to GitHub
2. Import in Railway → Dockerfile detected automatically
3. Railway sets `$PORT` — no config needed
4. Health check path: `/health`

---

## Known Limitations (Phase 1)

| Limitation | Impact | Phase 2 Fix |
|-----------|--------|-------------|
| Token store in-memory | Single instance, no horizontal scaling | Redis |
| No yt-dlp cookies | TikTok/Instagram may fail for private/login-required content | Cookie rotation |
| No retry logic | Transient yt-dlp failures surface as errors | Retry middleware |
| No caching | Same URL re-extracts every time | Redis cache by URL hash |
| No rate limit persistence | Restarts reset rate limit counters | Redis-backed slowapi |

---

## Phase 2 Roadmap

Per PRD section 4.2 and section 11:

1. **Batch download** — multiple URLs in one session
2. **Download history** — localStorage-based, no auth needed
3. **Redis integration** — for token store + rate limiting + caching
4. **Cookie management** — for TikTok no-watermark + Instagram private
5. **Monitoring** — Sentry error tracking + Plausible analytics
6. **Rate limit tightening** — `ALLOWED_ORIGINS` to specific domains

---

## File Structure Reference

```
copas.io/
├── docs/
│   ├── api-contract.md
│   └── mvp-handoff.md
├── CHANGELOG.md
├── prd.md
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/           (shadcn/ui)
│   │   ├── landing-page.tsx
│   │   ├── url-input.tsx
│   │   ├── result-card.tsx
│   │   ├── format-button.tsx
│   │   ├── platform-badge.tsx
│   │   └── skeleton-result.tsx
│   ├── hooks/use-download.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── platform-detector.ts
│   │   └── utils.ts
│   ├── store/download-store.ts
│   ├── types/index.ts
│   └── [config files]
└── backend/
    ├── app/
    │   ├── main.py
    │   ├── routers/{extract,download}.py
    │   ├── services/{extractor,token_store,streamer}.py
    │   ├── schemas/extract.py
    │   └── utils/platform.py
    ├── Dockerfile
    ├── railway.toml
    └── requirements.txt
```
