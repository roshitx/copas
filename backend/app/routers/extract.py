from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas.extract import ExtractRequest, MediaResult
from app.services.extractor import extract_media_info

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/api/extract", response_model=MediaResult)
@limiter.limit("10/minute")
async def extract_endpoint(request: Request, body: ExtractRequest) -> MediaResult:
    """
    Extract media information from a URL.

    Rate limited to 10 requests per minute per IP.
    """
    try:
        result = await extract_media_info(body.url)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail={
            "error": "UNSUPPORTED_PLATFORM",
            "message": str(e),
        })
    except PermissionError as e:
        raise HTTPException(status_code=403, detail={
            "error": "ACCESS_DENIED",
            "message": str(e),
        })
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail={
            "error": "EXTRACTION_FAILED",
            "message": str(e),
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": "INTERNAL_ERROR",
            "message": "Terjadi kesalahan internal. Coba lagi nanti.",
        })
