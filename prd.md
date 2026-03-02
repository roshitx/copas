# PRD — Copas.io
**Product Requirements Document**
Version: 1.0.0
Date: March 2026
Author: Muhammad Aulia Rasyid

---

## 1. Overview

### 1.1 Product Summary
Copas.io adalah web app all-in-one social media content downloader.
User cukup paste satu link dari platform apapun, sistem akan otomatis
mendeteksi platform dan mengunduh media (video/gambar/audio) tanpa perlu
pilih-pilih menu atau platform terlebih dahulu.

### 1.2 Problem Statement
Saat ini downloader tersebar di banyak website berbeda — satu untuk TikTok,
satu untuk Instagram, satu untuk YouTube. User harus buka tab berbeda tiap
platform. Copas.io menyelesaikan ini dengan satu input box untuk semua platform.

### 1.3 Target User
- Konten kreator yang butuh referensi konten
- User biasa yang ingin simpan video/gambar dari sosmed
- Editor video yang butuh raw footage cepat
- Indonesia-first market, tapi tidak region-locked

---

## 2. Goals & Success Metrics

### 2.1 Goals
- Satu input untuk semua platform (zero friction)
- Download berhasil dalam < 10 detik
- Support video (MP4), audio (MP3), dan gambar (JPG/PNG/WebP)
- Bisa diakses gratis tanpa login

### 2.2 Success Metrics (KPI)
| Metrik | Target 3 Bulan |
|---|---|
| Monthly Active Users | 5,000+ |
| Download success rate | > 90% |
| Average download time | < 10 detik |
| Bounce rate | < 40% |
| Page load time | < 2 detik |

---

## 3. Supported Platforms

| Platform | Video | Audio | Gambar | Stories/Reels |
|---|---|---|---|---|
| TikTok | ✅ | ✅ | ✅ | ✅ |
| Instagram | ✅ | ✅ | ✅ | ✅ |
| YouTube | ✅ | ✅ | ❌ | ❌ |
| X (Twitter) | ✅ | ✅ | ✅ | ❌ |
| Facebook | ✅ | ✅ | ✅ | ❌ |
| Threads | ✅ | ❌ | ✅ | ❌ |

---

## 4. Features

### 4.1 Core Features (MVP)

#### F-01: Smart URL Detection
- Sistem otomatis mendeteksi platform dari URL yang di-paste
- Tidak perlu user pilih platform manual
- Support semua format URL termasuk short URL (e.g. vm.tiktok.com)

#### F-02: One-Click Download
- Satu tombol "Copas!" untuk trigger download
- Progress bar saat proses berlangsung
- File langsung ter-download ke device user

#### F-03: Format Selector
- Setelah URL diproses, user bisa pilih format:
  - Video: MP4 (360p / 720p / 1080p)
  - Audio: MP3
  - Gambar: JPG / PNG (untuk carousel Instagram, semua gambar di-zip)

#### F-04: Preview Media
- Tampilkan thumbnail/preview media sebelum download
- Tampilkan metadata: judul, durasi, resolusi, ukuran file

#### F-05: No Watermark (Best Effort)
- Download versi tanpa watermark bila tersedia (terutama TikTok)

### 4.2 Nice-to-Have (Post-MVP)

#### F-06: Batch Download
- User paste multiple URL sekaligus (maks 5 link)

#### F-07: Download History (LocalStorage)
- Simpan history download di browser, tanpa perlu akun

#### F-08: Browser Extension
- Chrome/Firefox extension untuk download langsung dari halaman sosmed

---

## 5. Tech Stack

### 5.1 Frontend
| Layer | Tech |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS + shadcn/ui |
| State Management | Zustand |
| HTTP Client | Axios / fetch native |
| Deployment | Vercel |

### 5.2 Backend
| Layer | Tech |
|---|---|
| API Framework | FastAPI (Python) |
| Download Engine | yt-dlp (Python) |
| Task Queue | Background tasks via FastAPI |
| Rate Limiting | slowapi (Redis-backed) |
| Deployment | Railway / Render |

### 5.3 Infrastructure
| Layer | Tech |
|---|---|
| CDN / Proxy | Cloudflare |
| Cache | Redis (opsional, fase 2) |
| Monitoring | Sentry (error tracking) |
| Analytics | Plausible / Umami (privacy-first) |

---

## 6. System Architecture
[User Browser]
|
| paste URL
↓
[Next.js Frontend - Vercel]
|
| POST /api/download { url }
↓
[Next.js API Route] ← deteksi platform via regex
|
| forward ke backend
↓
[FastAPI Backend - Railway]
|
| panggil yt-dlp
↓
[yt-dlp Engine]
|
| ekstrak media URL / stream file
↓
[Response balik ke user → trigger download]

---

## 7. API Specification

### POST /api/extract
**Request:**
```json
{
  "url": "https://www.tiktok.com/@user/video/1234567890"
}
```
**Response (200 OK):**
```
{
  "platform": "tiktok",
  "title": "Judul video",
  "thumbnail": "https://...",
  "duration": 30,
  "formats": [
    {
      "id": "video_720p",
      "label": "Video 720p",
      "type": "video/mp4",
      "size_mb": 12.4,
      "download_url": "/api/download?token=xxx"
    },
    {
      "id": "audio_mp3",
      "label": "Audio MP3",
      "type": "audio/mp3",
      "size_mb": 2.1,
      "download_url": "/api/download?token=xxx"
    }
  ]
}
```
**Response (400 Bad Request):**
```json
{
  "error": "UNSUPPORTED_PLATFORM",
  "message": "Platform tidak didukung atau URL tidak valid."
}
```
GET /api/download?token={token}

    Stream file langsung ke browser

    Token valid selama 5 menit (TTL)

    Response header: Content-Disposition: attachment

## 8. UI/UX Flow
```
[Landing Page]
  → Hero section: besar, fokus ke input box
  → User paste URL → tombol "Copas!" aktif
  → Loading state: progress bar + teks "Lagi diproses..."
  → Result card muncul:
       - Thumbnail preview
       - Judul & metadata
       - Tombol download per format
  → User klik format → file langsung diunduh
```
Design Principles
 - Mobile-first (mayoritas user akses via HP)
 - Dark mode by default
 - Minimal — tidak ada ads, tidak ada login wall
 - Fast perceived performance (skeleton loading)

 ## 9. Non-Functional Requirements
 | Requirement       | Target                          |
 | ----------------- | ------------------------------- |
 | Response time API | < 8 detik per request           |
 | Uptime            | > 99%                           |
 | Concurrent users  | 100 simultaneous request        |
 | Security          | Rate limit: 10 req/menit per IP |
 | SEO               | Meta tags lengkap, sitemap.xml  |
 | Accessibility     | WCAG 2.1 AA                     |

## 10. Constraints & Risks
| Risiko                        | Dampak          | Mitigasi                                              |
| ----------------------------- | --------------- | ----------------------------------------------------- |
| Platform update anti-scraping | Download gagal  | Update yt-dlp rutin, monitor error rate               |
| Server cost membengkak        | Finansial       | Rate limiting ketat, pakai Cloudflare cache           |
| DMCA / Legal                  | Takedown        | Tidak host file di server kita, direct stream ke user |
| yt-dlp cookies expired        | TikTok/IG gagal | Rotate cookies / pakai headless browser fallback      |
## 11. Development Milestones
| Phase                   | Scope                                     | Estimasi |
| ----------------------- | ----------------------------------------- | -------- |
| Phase 1 — MVP           | Landing page + core download (TikTok, YT) | 2 minggu |
| Phase 2 — Full Platform | Tambah IG, X, FB, Threads                 | 2 minggu |
| Phase 3 — Polish        | Preview, format selector, mobile polish   | 1 minggu |
| Phase 4 — Infra         | Rate limiting, monitoring, Cloudflare     | 1 minggu |
| Phase 5 — Post-MVP      | Batch download, history, extension        | TBD      |
## 12. Out of Scope (Explicitly)
- User login / akun
- Penyimpanan file di server
- Monetisasi (fase pertama)
- Mobile app (native iOS/Android)
- Platform: Pinterest, LinkedIn, Snapchat (fase berikutnya)

## 13. Prompt Context untuk AI
Jika kamu adalah AI yang membantu develop project ini, berikut konteksnya:

- Project name: Copas.io
- Goal: All-in-one social media downloader

- Frontend: Next.js 14 App Router + Tailwind CSS + shadcn/ui

- Backend: FastAPI + yt-dlp

- Core flow: User paste URL → detect platform → extract media → user download

- Design: Mobile-first, dark mode, minimal, no ads, no login

- Priority: Working download > beautiful UI > extra features

- Language preference: TypeScript untuk frontend, Python untuk backend
----
Dokumen ini adalah living document. Update sesuai perkembangan project.
