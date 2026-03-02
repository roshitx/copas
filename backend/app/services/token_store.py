import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from uuid import uuid4


@dataclass
class TokenData:
    download_url: str
    filename: str
    content_type: str
    created_at: float = field(default_factory=time.time)


class TokenStore:
    """In-memory token store for download links."""

    TTL_SECONDS = 300  # 5 minutes

    def __init__(self):
        self._tokens: Dict[str, TokenData] = {}
        self._lock = asyncio.Lock()

    async def create_token(
        self, download_url: str, filename: str, content_type: str
    ) -> str:
        """
        Create a new token for a download URL.

        Args:
            download_url: The direct URL to download from
            filename: The filename to use for the download
            content_type: The MIME type of the content

        Returns:
            A UUID4 token string
        """
        token = str(uuid4())
        data = TokenData(
            download_url=download_url, filename=filename, content_type=content_type
        )

        async with self._lock:
            self._tokens[token] = data

        return token

    async def get_token(self, token: str) -> Optional[TokenData]:
        """
        Retrieve token data if valid and not expired.

        Args:
            token: The token string to retrieve

        Returns:
            TokenData if valid, None if expired or not found
        """
        async with self._lock:
            data = self._tokens.get(token)

            if not data:
                return None

            # Check if expired
            if time.time() - data.created_at > self.TTL_SECONDS:
                del self._tokens[token]
                return None

            return data

    async def cleanup_expired(self) -> None:
        """Remove all expired tokens."""
        now = time.time()

        async with self._lock:
            expired = [
                token
                for token, data in self._tokens.items()
                if now - data.created_at > self.TTL_SECONDS
            ]

            for token in expired:
                del self._tokens[token]


# Global instance
token_store = TokenStore()


async def start_cleanup_task():
    """Start background cleanup task."""
    while True:
        await asyncio.sleep(60)  # Run every minute
        await token_store.cleanup_expired()
