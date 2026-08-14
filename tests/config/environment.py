"""Environment configuration loader for the Selenium QA framework.

Reads environment variables for target URLs, browser selection, credentials, and
execution mode (headless/visible). Falls back to safe defaults so the framework
can boot even when no .env is present.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - dotenv is optional
    def load_dotenv(*_args, **_kwargs):  # type: ignore[no-redef]
        return False


# Load .env if present at the project root.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=False)


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


class EnvironmentConfig:
    """Single source of truth for runtime configuration."""

    BASE_URL: str = os.getenv("QA_BASE_URL", "http://localhost:8000")
    ADMIN_URL: str = os.getenv("QA_ADMIN_URL", "http://localhost:8000/admin")
    API_URL: str = os.getenv("QA_API_URL", "http://localhost:8000/api")

    BROWSER: str = os.getenv("QA_BROWSER", "chromium").lower()
    HEADLESS: bool = _get_bool("QA_HEADLESS", True)
    WINDOW_WIDTH: int = _get_int("QA_WINDOW_WIDTH", 1440)
    WINDOW_HEIGHT: int = _get_int("QA_WINDOW_HEIGHT", 900)

    IMPLICIT_WAIT: int = _get_int("QA_IMPLICIT_WAIT", 5)
    EXPLICIT_WAIT: int = _get_int("QA_EXPLICIT_WAIT", 15)
    PAGE_LOAD_TIMEOUT: int = _get_int("QA_PAGE_LOAD_TIMEOUT", 30)

    MAX_RETRIES: int = _get_int("QA_MAX_RETRIES", 2)
    PARALLEL_WORKERS: int = _get_int("QA_PARALLEL_WORKERS", 4)
    TEST_TIMEOUT: int = _get_int("QA_TEST_TIMEOUT", 60)

    USERNAME: Optional[str] = os.getenv("QA_USERNAME")
    PASSWORD: Optional[str] = os.getenv("QA_PASSWORD")

    REPORTS_DIR: Path = Path(os.getenv("QA_REPORTS_DIR", "reports")).resolve()
    SCREENSHOTS_DIR: Path = Path(os.getenv("QA_SCREENSHOTS_DIR", "reports/screenshots")).resolve()
    LOGS_DIR: Path = Path(os.getenv("QA_LOGS_DIR", "reports/logs")).resolve()

    @classmethod
    def ensure_dirs(cls) -> None:
        for d in (cls.REPORTS_DIR, cls.SCREENSHOTS_DIR, cls.LOGS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def is_ci(cls) -> bool:
        return _get_bool("CI", False) or _get_bool("GITHUB_ACTIONS", False)

    @classmethod
    def summary(cls) -> dict:
        return {
            "base_url": cls.BASE_URL,
            "browser": cls.BROWSER,
            "headless": cls.HEADLESS,
            "parallel_workers": cls.PARALLEL_WORKERS,
            "max_retries": cls.MAX_RETRIES,
            "explicit_wait": cls.EXPLICIT_WAIT,
            "is_ci": cls.is_ci(),
        }


def get_config() -> EnvironmentConfig:
    """Return the singleton-style configuration object."""
    return EnvironmentConfig
