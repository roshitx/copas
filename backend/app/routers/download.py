from fastapi import APIRouter, HTTPException

from ..services.streamer import stream_media
from ..services.token_store import token_store

router = APIRouter()


@router.get("/api/download/validate")
async def validate_download_token(token: str):
    """
    Validate a download token without streaming media.
    """
    token_data = await token_store.get_token(token)

    if not token_data:
        raise HTTPException(
            status_code=410, detail="Token expired, invalid, or not found"
        )

    return {"valid": True}


@router.get("/api/download")
async def download_endpoint(token: str):
    """
    Download media using a signed token.

    Tokens expire after 5 minutes.
    """
    # Validate token
    token_data = await token_store.get_token(token)

    if not token_data:
        raise HTTPException(
            status_code=410, detail="Token expired, invalid, or not found"
        )

    # Stream the media
    return await stream_media(
        token_data.download_url, token_data.filename, token_data.content_type
    )
