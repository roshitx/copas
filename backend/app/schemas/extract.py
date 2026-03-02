from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import math


class ExtractRequest(BaseModel):
    url: str = Field(..., description="The URL of the media to extract")


class Format(BaseModel):
    id: str = Field(..., description="Format identifier for yt-dlp")
    label: str = Field(..., description="Human-readable format label")
    type: str = Field(..., description="MIME type: video/mp4 or audio/mp3")
    size_mb: Optional[float] = Field(None, description="File size in megabytes")
    download_url: str = Field(..., description="Download URL with signed token")


class MediaResult(BaseModel):
    platform: str = Field(
        ...,
        description="Platform name: tiktok, instagram, youtube, twitter, facebook, threads",
    )
    title: str = Field(..., description="Media title")
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")
    thumbnails: List[str] = Field(default_factory=list, description="All media thumbnail URLs for bento grid")
    author: Optional[str] = Field(None, description="Content author/uploader username")
    duration: Optional[int] = Field(None, description="Duration in seconds")

    @field_validator("duration", mode="before")
    @classmethod
    def coerce_duration(cls, v: object) -> Optional[int]:
        if v is None:
            return None
        try:
            return int(math.floor(float(v)))
        except (TypeError, ValueError):
            return None
    formats: List[Format] = Field(
        default_factory=list, description="Available download formats"
    )


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
