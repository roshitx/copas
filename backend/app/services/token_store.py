import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from uuid import uuid4

from redis.asyncio import Redis


@dataclass
class TokenData:
    download_url: str
    filename: str
    content_type: str
    created_at: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps({
            "download_url": self.download_url,
            "filename": self.filename,
            "content_type": self.content_type,
            "created_at": self.created_at,
        })

    @classmethod
    def from_json(cls, raw: str) -> "TokenData":
        data = json.loads(raw)
        return cls(
            download_url=data["download_url"],
            filename=data["filename"],
            content_type=data["content_type"],
            created_at=data["created_at"],
        )


class TokenStore:
    """Token store with Redis backend and in-memory fallback."""

    TTL_SECONDS = 300  # 5 minutes

    def __init__(self):
        self._tokens: Dict[str, TokenData] = {}
        self._lock = asyncio.Lock()
        self._redis: Optional[Redis] = None

    async def init_redis(self, redis_client: Optional[Redis]) -> None:
        """Set Redis client. Call during app startup."""
        self._redis = redis_client

    async def create_token(
        self, download_url: str, filename: str, content_type: str
    ) -> str:
        token = str(uuid4())
        data = TokenData(
            download_url=download_url, filename=filename, content_type=content_type
        )

        if self._redis:
            await self._redis.setex(
                f"token:{token}", self.TTL_SECONDS, data.to_json()
            )
        else:
            async with self._lock:
                self._tokens[token] = data

        return token

    async def get_token(self, token: str) -> Optional[TokenData]:
        if self._redis:
            raw = await self._redis.get(f"token:{token}")
            if not raw:
                return None
            return TokenData.from_json(raw)

        async with self._lock:
            data = self._tokens.get(token)
            if not data:
                return None
            if time.time() - data.created_at > self.TTL_SECONDS:
                del self._tokens[token]
                return None
            return data

    async def cleanup_expired(self) -> None:
        """Remove expired tokens from in-memory store. No-op when using Redis."""
        if self._redis:
            return

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
        await asyncio.sleep(60)
        await token_store.cleanup_expired()
