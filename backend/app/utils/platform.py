import re


def detect_platform(url: str) -> str:
    """
    Detect the social media platform from a URL.

    Args:
        url: The URL to analyze

    Returns:
        Platform identifier: "tiktok" | "instagram" | "youtube" | "twitter" | "facebook" | "threads" | "unknown"
    """
    patterns = {
        "tiktok": r"(tiktok\.com|vm\.tiktok\.com|vt\.tiktok\.com)",
        "instagram": r"(instagram\.com|instagr\.am)",
        "youtube": r"(youtube\.com|youtu\.be|music\.youtube\.com)",
        "twitter": r"(twitter\.com|x\.com|t\.co)",
        "facebook": r"(facebook\.com|fb\.watch|fb\.me)",
        "threads": r"(threads\.net|threads\.com)",
    }

    url_lower = url.lower()

    for platform, pattern in patterns.items():
        if re.search(pattern, url_lower):
            return platform

    return "unknown"
