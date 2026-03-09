import asyncio
import os
import re
from typing import Optional

import httpx
import yt_dlp
from app.schemas.extract import MediaResult, Format
import app.services.token_store as _token_store_module
from app.utils.platform import detect_platform
from app.services.tiktok_extractor import extract_tiktok_media

async def extract_media_info(url: str) -> MediaResult:

    platform = detect_platform(url)

    if platform == "unknown":
        raise ValueError(f"Unsupported platform for URL: {url}")

    if platform == "threads":
        raise ValueError(
            "Platform Threads belum didukung. "
            "Coba download manual dari aplikasi Threads."
        )

    # Route TikTok to TikWM extractor
    if platform == "tiktok":
        return await extract_tiktok_media(url)


    # Normalize x.com -> twitter.com for better yt-dlp compatibility
    normalized_url = url.replace("x.com/", "twitter.com/") if platform == "twitter" else url

    loop = asyncio.get_event_loop()

    # For Twitter: yt-dlp may fail on image-only tweets ('no video could be found').
    # We catch that specific error and fall through to image extraction.
    info: dict | None = None
    no_video_error: bool = False

    if platform == "twitter":
        try:
            info = await loop.run_in_executor(None, _extract_info_sync, normalized_url)
        except RuntimeError as e:
            if "no video could be found" in str(e).lower():
                no_video_error = True
            else:
                raise
    else:
        info = await loop.run_in_executor(None, _extract_info_sync, normalized_url)

    title = "Unknown"
    author: str | None = None
    thumbnail: str | None = None
    thumbnails: list[str] = []
    duration: int | None = None
    formats: list[Format] = []

    if info is not None:
        # Handle playlist (multi-video tweet or gallery)
        info_type = info.get("_type")
        if info_type == "playlist":
            entries = info.get("entries") or []
            title = info.get("title") or (entries[0].get("title") if entries else "Unknown")
            thumbnail = info.get("thumbnail")
            if not thumbnail and entries:
                thumbnail = entries[0].get("thumbnail")
            duration = info.get("duration") or (entries[0].get("duration") if entries else None)
            thumbnails: list[str] = []
            for e in entries:
                t = e.get("thumbnail")
                if not t:
                    e_thumbs = e.get("thumbnails") or []
                    for et in reversed(e_thumbs):
                        if et.get("url"):
                            t = et["url"]
                            break
                if t:
                    thumbnails.append(t)
            for i, entry in enumerate(entries, start=1):
                entry_formats = await _build_formats(entry, video_index=i if len(entries) > 1 else 0, platform=platform, author=author)
                formats.extend(entry_formats)
            # Author from playlist or first entry
            author = (
                info.get("uploader_id")
                or info.get("uploader")
                or (entries[0].get("uploader_id") if entries else None)
                or (entries[0].get("uploader") if entries else None)
            )
        else:
            title = info.get("title", "Unknown")

            # Fall back to thumbnails[] array if thumbnail key is None (Instagram Reels, etc.)
            thumbnail = info.get("thumbnail")
            thumbnails: list[str] = []
            if not thumbnail:
                info_thumbs = info.get("thumbnails") or []
                for t in reversed(info_thumbs):
                    if t.get("url"):
                        thumbnail = t["url"]
                        break
            if thumbnail:
                thumbnails = [thumbnail]

            duration = info.get("duration")
            formats = await _build_formats(info, platform=platform, author=author)
            # Author from single video info
            author = info.get("uploader_id") or info.get("uploader")

    # For Twitter: always fetch images via fxtwitter (yt-dlp explicitly excludes photos)
    if platform == "twitter":
        tweet_id = _extract_tweet_id(url)
        if tweet_id:
            fx_data = await _fetch_fxtwitter(tweet_id)
            image_formats = await _build_twitter_image_formats(fx_data, platform=platform, author=author)
            formats.extend(image_formats)

            # Collect photo thumbnails for bento grid
            photos = fx_data.get("tweet", {}).get("media", {}).get("photos", []) if fx_data else []
            if photos:
                photo_urls = [p["url"] for p in photos if p.get("url")]
                if photo_urls:
                    # Merge photo URLs with existing thumbnails, avoiding duplicates
                    existing_urls = set(thumbnails)
                    for url in photo_urls:
                        if url not in existing_urls:
                            thumbnails.append(url)
                            existing_urls.add(url)
                    if not thumbnail:
                        thumbnail = photo_urls[0]
            photos = fx_data.get("tweet", {}).get("media", {}).get("photos", []) if fx_data else []
            if photos:
                photo_urls = [p["url"] for p in photos if p.get("url")]
                if photo_urls:
                    if not thumbnails or len(photo_urls) > 1:
                        thumbnails = photo_urls
                    if not thumbnail:
                        thumbnail = photo_urls[0]

            # For image-only tweets: populate title/thumbnail from fxtwitter
            if no_video_error and fx_data:
                tweet = fx_data.get("tweet", {})
                title = tweet.get("text", "Unknown")[:100] or "Unknown"
                tweet_photos = tweet.get("media", {}).get("photos", [])
                if tweet_photos:
                    thumbnail = tweet_photos[0].get("url")

            # Always try to get Twitter author from fxtwitter
            if fx_data and not author:
                tweet_author = fx_data.get("tweet", {}).get("author", {})
                author = tweet_author.get("screen_name") or tweet_author.get("name")
    if not formats:
        raise RuntimeError(
            "Tidak ada format media yang tersedia untuk link ini. "
            "Konten mungkin memerlukan autentikasi atau tidak didukung."
        )

    return MediaResult(
        platform=platform,
        title=title,
        author=author,
        thumbnail=thumbnail,
        thumbnails=thumbnails,
        duration=duration,
        formats=formats,
    )




def _extract_info_sync(url: str) -> dict:
    """Synchronous yt-dlp extraction with platform-aware options."""
    ydl_opts: dict = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/17.0 Mobile/15E148 Safari/604.1"
            ),
        },
        "extractor_args": {
            "instagram": {"api": ["graphql"]},
            "twitter": {"api": ["graphql"]},
        },
        "socket_timeout": 30,
    }

    # Load cookies from file if configured (required for Instagram/TikTok)
    cookie_file = os.environ.get("YTDLP_COOKIE_FILE")
    if cookie_file and os.path.isfile(cookie_file):
        ydl_opts["cookiefile"] = cookie_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            msg_lower = msg.lower()
            auth_keywords = (
                "login", "private", "cookie", "sign in", "sign_in",
                "empty media", "not logged", "authenticate", "authentication",
                "forbidden", "403", "401", "unauthorized", "unprocessable",
                "account", "session", "credentials",
            )
            extract_keywords = (
                "unable to extract", "video url",
                "no video formats", "unsupported url",
            )
            if any(k in msg_lower for k in auth_keywords):
                raise PermissionError(
                    "Konten ini memerlukan login atau tidak dapat diakses. "
                    "Pastikan cookie sudah dikonfigurasi untuk platform ini."
                ) from e
            if any(k in msg_lower for k in extract_keywords):
                raise RuntimeError(
                    "Gagal mengekstrak media. "
                    "Pastikan link valid dan konten bisa diakses publik."
                ) from e
            raise RuntimeError(f"Ekstraksi gagal: {msg}") from e

    return info


async def _build_formats(info: dict, video_index: int = 0, platform: str = "", author: str | None = None) -> list[Format]:
    formats = []


    # Check if video has audio and video formats
    has_video_formats = any(f.get("vcodec") != "none" for f in info.get("formats", []))

    if has_video_formats:
        # Video formats: filter for video+audio or best available
        video_formats = []
        for fmt in info.get("formats", []):
            # Prefer formats with both video and audio
            if fmt.get("vcodec") != "none" and fmt.get("acodec") != "none":
                video_formats.append(fmt)
            elif fmt.get("vcodec") != "none":
                video_formats.append(fmt)

        # Deduplicate and prioritize by quality
        seen = set()
        unique_formats = []
        for fmt in video_formats:
            key = (fmt.get("height"), fmt.get("ext"))
            if key not in seen:
                seen.add(key)
                unique_formats.append(fmt)

        # Sort by height descending, then by format preference
        def sort_key(f):
            height = f.get("height") or 0
            ext = f.get("ext", "")
            # Prefer mp4 over webm
            ext_priority = 0 if ext == "mp4" else 1
            return (-height, ext_priority)

        unique_formats.sort(key=sort_key)

        QUALITY_LABELS = {
            144: "144p",
            240: "240p",
            360: "360p",
            480: "480p",
            574: "574p",
            640: "640p",
            720: "720p",
            960: "960p",
            1080: "1080p",
            1440: "1440p",
            2160: "4K",
        }
        quality_map: dict = {}
        for fmt in unique_formats:
            height = fmt.get("height")
            if height and height not in quality_map:
                quality_map[height] = fmt

        for height in sorted(quality_map.keys(), reverse=True):
            fmt = quality_map[height]
            quality = QUALITY_LABELS.get(height, f"{height}p")
            label = f"Video {video_index} \u00b7 {quality}" if video_index > 0 else f"Video {quality}"
            try:
                formats.append(
                    await _create_format(
                        fmt, label, "video/mp4", info.get("title", "video"),
                    )
                )
            except ValueError:
                pass
            except ValueError:
                pass

        # Fallback: best available if nothing mapped
        if not formats and unique_formats:
            for best in unique_formats:
                try:
                    height = best.get("height", "unknown")
                    quality = QUALITY_LABELS.get(height, f"{height}p") if isinstance(height, int) else f"{height}p"
                    fallback_label = f"Video {video_index} \u00b7 {quality}" if video_index > 0 else f"Video {quality}"
                    formats.append(
                        await _create_format(
                            best, fallback_label, "video/mp4", info.get("title", "video")
                        )
                    )
                    break
                except ValueError:
                    continue
    else:
        # Audio only - extract audio format
        audio_formats = [
            f for f in info.get("formats", []) if f.get("acodec") != "none"
        ]


        if audio_formats:
            audio_formats.sort(key=lambda f: f.get("abr", 0) or 0, reverse=True)
            best_audio = audio_formats[0]
            formats.append(
                await _create_format(
                    best_audio, "Audio MP3", "audio/mp3", platform=platform, author=author,
                )
            )

    return formats


async def _create_format(
    fmt: dict, label: str, content_type: str,
    platform: str = "", author: str | None = None, index: int = 0,
) -> Format:
    url = fmt.get("url")
    if not url:
        url = fmt.get("manifest_url") or fmt.get("fragment_base_url")
    if not url:
        raise ValueError("Format URL is required")

    # Build filename: {platform}_{author}_copas_io[_{index}].{ext}
    ext = fmt.get("ext", "mp4")
    parts = [p for p in [platform or "copas", author] if p]
    parts.append("copas_io")
    if index > 0:
        parts.append(str(index))
    filename = "_".join(parts) + f".{ext}"

    # Create token
    token = await _token_store_module.token_store.create_token(url, filename, content_type)

    # Calculate size in MB if available
    filesize = fmt.get("filesize")
    size_mb = None
    if filesize:
        size_mb = round(filesize / (1024 * 1024), 2)

    return Format(
        id=fmt.get("format_id", "unknown"),
        label=label,
        type=content_type,
        size_mb=size_mb,
        download_url=f"/api/download?token={token}",
    )



def _extract_tweet_id(url: str) -> Optional[str]:
    """Extract tweet ID from any X/Twitter URL format."""
    match = re.search(r"(?:twitter\.com|x\.com)/[^/]+/status(?:es)?/(\d+)", url)
    return match.group(1) if match else None


async def _fetch_fxtwitter(tweet_id: str) -> dict:
    """Fetch tweet data from fxtwitter public API. Returns {} on failure."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(
                f"https://api.fxtwitter.com/status/{tweet_id}",
                headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"},
            )
            if resp.status_code != 200:
                return {}
            return resp.json()
    except Exception:
        return {}


async def _build_twitter_image_formats(fx_data: dict, platform: str = "twitter", author: str | None = None) -> list[Format]:
    if not fx_data:
        return []

    photos = fx_data.get("tweet", {}).get("media", {}).get("photos", [])
    image_formats: list[Format] = []

    for i, photo in enumerate(photos, start=1):
        image_url = photo.get("url")
        if not image_url:
            continue
        label = f"Foto {i}" if len(photos) > 1 else "Foto"
        fake_fmt = {
            "format_id": f"img-{i}",
            "url": image_url,
            "ext": "jpg",
            "filesize": None,
        }
        try:
            fmt = await _create_format(
                fake_fmt, label, "image/jpeg",
                platform=platform, author=author,
                index=i if len(photos) > 1 else 0,
            )
            image_formats.append(fmt)
        except Exception:
            continue

    return image_formats