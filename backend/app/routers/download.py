from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..services.streamer import stream_media
from ..services.token_store import token_store

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.get("/api/download/validate")
@limiter.limit("30/minute")
async def validate_download_token(request: Request, token: str):
    """Validate a download token without streaming media."""
    token_data = await token_store.get_token(token)

    if not token_data:
        raise HTTPException(
            status_code=410, detail="Token expired, invalid, or not found"
        )

    return {"valid": True}


@router.get("/api/download")
@limiter.limit("30/minute")
async def download_endpoint(request: Request, token: str):
    """
    Download media using a signed token.

    Rate limited to 30 requests per minute per IP.
    Tokens expire after 5 minutes.
    """
    token_data = await token_store.get_token(token)

    if not token_data:
        raise HTTPException(
            status_code=410, detail="Token expired, invalid, or not found"
        )

    return await stream_media(
        token_data.download_url, token_data.filename, token_data.content_type
    )
