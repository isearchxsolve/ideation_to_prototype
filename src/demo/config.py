"""Application configuration using Pydantic Settings.

All runtime configuration is read from environment variables (optionally
via a `.env` file) and validated at startup, so misconfiguration fails
fast instead of surfacing as runtime errors.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_BROWSERS = {"chromium", "firefox", "edge"}


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Flask app
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # QA suite
    APP_BASE_URL: str | None = None
    APP_BROWSER: str = "chromium"
    APP_HEADLESS: bool = True
    APP_TIMEOUT: int = 15
    APP_IMPLICIT_WAIT: int = 5
    APP_VIEWPORT_WIDTH: int = 1366
    APP_VIEWPORT_HEIGHT: int = 768
    APP_REPORT_DIR: str = "reports"

    # Credentials (never hardcoded; read from the environment)
    APP_ADMIN_USER: str | None = None
    APP_ADMIN_PASS: str | None = None
    APP_TEST_USER: str | None = None
    APP_TEST_PASS: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("APP_BROWSER")
    @classmethod
    def browser_must_be_supported(cls, v: str) -> str:
        if v.lower() not in SUPPORTED_BROWSERS:
            raise ValueError(f"APP_BROWSER must be one of {sorted(SUPPORTED_BROWSERS)}")
        return v.lower()

    @field_validator("APP_PORT")
    @classmethod
    def port_must_be_valid(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("APP_PORT must be between 1 and 65535")
        return v


@lru_cache
def get_settings() -> Settings:
    """Return a cached, validated settings instance."""
    return Settings()


def get_config_dict() -> dict[str, Any]:
    """Return settings as a plain dictionary."""
    return get_settings().model_dump()
