# Copas.io API Contract
Version: 1.0.0 | Phase: MVP

---

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.copas.io` (Railway)

Frontend accesses backend via `NEXT_PUBLIC_BACKEND_URL` env var.

---

## POST /api/extract

Extract media metadata from a social media URL.

### Request
```json
{
  "url": "https://www.tiktok.com/@user/video/1234567890"
}
```

### Response 200 OK
```json
{
  "platform": "tiktok",
  "title": "Video title here",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "duration": 30,
  "formats": [
    {
      "id": "video_720p",
      "label": "Video 720p",
      "type": "video/mp4",
      "size_mb": 12.4,
      "download_url": "/api/download?token=uuid4-here"
    },
    {
      "id": "video_360p",
      "label": "Video 360p",
      "type": "video/mp4",
      "size_mb": 5.2,
      "download_url": "/api/download?token=uuid4-here"
    },
    {
      "id": "audio_mp3",
      "label": "Audio MP3",
      "type": "audio/mp3",
      "size_mb": 2.1,
      "download_url": "/api/download?token=uuid4-here"
    }
  ]
}
```

### Response 400 Bad Request
```json
{
  "error": "UNSUPPORTED_PLATFORM",
  "message": "Platform tidak didukung atau URL tidak valid."
}
```

### Response 422 Unprocessable Entity
```json
{
  "error": "EXTRACTION_FAILED",
  "message": "Gagal mengekstrak media. Coba lagi nanti."
}
```

---

## GET /api/download?token={token}

Stream media file to browser.

### Query Params
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | yes | UUID4 token from format.download_url |

### Response 200 OK
- `Content-Type: video/mp4` (or audio/mpeg, etc.)
- `Content-Disposition: attachment; filename="video.mp4"`
- Body: streaming binary

### Response 410 Gone
```json
{
  "error": "TOKEN_EXPIRED",
  "message": "Link download sudah kadaluarsa. Proses ulang URL."
}
```

---

## GET /health

Health check for Railway deployment.

### Response 200
```json
{ "status": "ok" }
```

---

## Rate Limiting
- 10 requests/minute per IP
- Applied to: POST /api/extract
- 429 response when exceeded

---

## Token Lifecycle
- Created by: POST /api/extract (per format)
- TTL: 5 minutes from creation
- Consumed by: GET /api/download (single-use or TTL expiry)
- Storage: In-memory (single instance — documented limitation)

---

## Platform Values
| Value | Platform |
|-------|----------|
| `tiktok` | TikTok |
| `instagram` | Instagram |
| `youtube` | YouTube |
| `twitter` | X / Twitter |
| `facebook` | Facebook |
| `threads` | Threads |
| `unknown` | Undetected |

---

## Supported Platforms (MVP)
| Platform | Video | Audio | Image |
|----------|-------|-------|-------|
| TikTok | ✅ | ✅ | ✅ |
| Instagram | ✅ | ✅ | ✅ |
| YouTube | ✅ | ✅ | ❌ |
| X/Twitter | ✅ | ✅ | ✅ |
| Facebook | ✅ | ✅ | ✅ |
| Threads | ✅ | ❌ | ✅ |
