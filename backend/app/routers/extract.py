from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.error_codes import ErrorCode
from ..core.exceptions import (
    AccessDeniedException,
    CopasException,
    ExtractionFailedException,
    ServiceUnavailableException,
    UnsupportedPlatformException,
)
from ..schemas.extract import ExtractRequest, MediaResult
from ..services.extractors import extract_media_info
from ..services.tiktok_extractor import (
    TikWMContentError,
    TikWMUnavailableError,
)

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/api/extract", response_model=MediaResult)
@limiter.limit("10/minute")
async def extract_endpoint(request: Request, body: ExtractRequest) -> MediaResult:
    """
    Extract media information from a URL.

    Rate limited to 10 requests per minute per IP.

    Raises:
        UnsupportedPlatformException: If the platform is not supported.
        AccessDeniedException: If access to content is denied.
        ExtractionFailedException: If media extraction fails.
        ServiceUnavailableException: If external service is unavailable.
        CopasException: For other internal errors.
    """
    try:
        result = await extract_media_info(body.url)
        return result
    except ValueError as e:
        raise UnsupportedPlatformException(message=str(e))
    except PermissionError as e:
        raise AccessDeniedException(message=str(e))
    except RuntimeError as e:
        raise ExtractionFailedException(message=str(e))
    except TikWMUnavailableError as e:
        raise ServiceUnavailableException(message=str(e), service="TikWM")
    except TikWMContentError as e:
        raise ExtractionFailedException(message=str(e))
    except CopasException:
        # Re-raise custom exceptions as-is (already handled)
        raise
    except Exception:
        raise CopasException(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Terjadi kesalahan internal. Coba lagi nanti.",
        )
