# Copas.io Frontend

Social media content downloader web app. Paste any URL → auto-detect platform → download media.

**Supported platforms:** TikTok, Instagram, YouTube, X/Twitter, Facebook, Threads

## Features

### Core
- **URL auto-detection** — Platform detected from URL, shows preview icon before extraction
- **Multi-format download** — Video (MP4), audio (MP3), image formats with size info
- **Carousel support** — Multi-image Instagram posts bundled as ZIP

### UX Enhancements
- **Dark mode** — Toggle between Light/Dark/System preference (persisted)
- **Download progress** — Real-time percentage, ETA estimate, cancel button
- **Skeleton loading** — Shimmer animation while extracting media info
- **Error states** — Styled error card with retry button
- **Keyboard shortcuts** — `Ctrl+V` to paste, `Esc` to cancel
- **Mobile bottom sheet** — Native-feel format selection on mobile

### Pages
- `/` — Main download page
- `/faq` — Frequently asked questions with accordion

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS + shadcn/ui
- **State:** Zustand
- **Icons:** Lucide React + Simple Icons
- **Testing:** Playwright (E2E)

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout with theme provider
│   ├── page.tsx            # Main route
│   ├── globals.css         # CSS variables, dark mode, animations
│   └── faq/
│       └── page.tsx        # FAQ page
├── components/
│   ├── landing-page.tsx    # Main page layout + URL input
│   ├── url-input.tsx       # Input with platform detection
│   ├── result-card.tsx     # Media result + format selection
│   ├── download-progress.tsx  # Progress bar + cancel
│   ├── error-card.tsx      # Error state + retry
│   ├── skeleton-result.tsx # Loading skeleton
│   ├── theme-toggle.tsx    # Dark mode toggle
│   ├── format-button.tsx   # Format button (desktop/mobile)
│   ├── format-sheet.tsx    # Mobile bottom sheet
│   ├── platform-badge.tsx  # Platform icon chip
│   └── ui/                 # shadcn/ui primitives
├── hooks/
│   ├── use-download.ts     # Download orchestration
│   └── use-keyboard-shortcuts.ts  # Keyboard handlers
├── lib/
│   ├── api.ts              # Backend API client
│   ├── platform-detector.ts # URL → platform mapping
│   └── utils.ts            # Shared utilities
├── store/
│   └── download-store.ts   # Zustand state
├── types/
│   └── index.ts            # All TypeScript types
└── tests/
    ├── e2e/                # Playwright specs
    └── fixtures/           # Test fixtures
```

## Getting Started

### Prerequisites

- Node.js 18+
- Backend API running (see `../backend/`)

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### Install & Run

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Start production server |
| `npm run lint` | ESLint check |
| `npm run test:e2e` | Playwright tests (headless) |
| `npm run test:e2e:headed` | Playwright tests (with browser) |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+V` | Paste URL from clipboard |
| `Esc` | Cancel download / reset |

## State Management

Zustand store (`store/download-store.ts`):

```typescript
interface DownloadStore {
  url: string
  platform: Platform
  status: DownloadStatus
  progress: number           // 0-100
  result: MediaResult | null
  error: string | null
  // Actions
  setUrl, setPlatform, setStatus, setProgress, setResult, setError, reset
}
```

## API Integration

Backend API client (`lib/api.ts`):

```typescript
// Extract media info
const result = await extractMedia({ url: 'https://tiktok.com/...' })

// Get download URL
const downloadUrl = getDownloadUrl(token)

// Trigger browser download
triggerBrowserDownload(downloadUrl, 'video.mp4')
```

Error handling via `ApiClientError` with codes: `UNSUPPORTED_PLATFORM`, `ACCESS_DENIED`, `EXTRACTION_FAILED`

## Adding New Platforms

1. Add platform to `Platform` type in `types/index.ts`
2. Add detection pattern to `lib/platform-detector.ts`
3. Add icon mapping in `components/platform-badge.tsx`
4. Update backend extractor (see `../backend/`)

## Deployment

Configured for Vercel:

```bash
npm run build  # Verify build passes
```

Deploy via Vercel CLI or GitHub integration.

## License

Private project — All rights reserved.