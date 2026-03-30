"""Application configuration using Pydantic Settings.

Centralized configuration management with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Server
    port: int = Field(default=8000, description="Port to run the server on")
    environment: str = Field(default="development", description="Environment name")

    # CORS
    allowed_origins: str = Field(
        default="",
        description="Comma-separated list of allowed CORS origins",
    )

    # Redis
    redis_url: str | None = Field(
        default=None,
        description="Redis connection URL",
    )

    # Sentry
    sentry_dsn: str | None = Field(
        default=None,
        description="Sentry DSN for error tracking",
    )
    sentry_traces_sample_rate: float = Field(
        default=0.1,
        description="Sentry traces sample rate",
    )

    # yt-dlp
    ytdlp_cookie_file: str | None = Field(
        default=None,
        description="Path to cookies.txt for age-restricted content",
    )

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Normalize environment name to lowercase."""
        return v.strip().lower()

    @field_validator("sentry_traces_sample_rate")
    @classmethod
    def validate_sample_rate(cls, v: float) -> float:
        """Ensure sample rate is between 0 and 1."""
        if not (0 <= v <= 1):
            raise ValueError("sentry_traces_sample_rate must be between 0 and 1")
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment in {"dev", "development", "local"}

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return not self.is_development

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()
