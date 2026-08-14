"""Environment configuration for the Selenium QA framework.

Loads runtime settings from environment variables with sane defaults so the
suite can run locally, in CI, or against a staging environment without code
changes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class EnvironmentConfig:
    """Resolved configuration for a single test run."""

    base_url: str
    browser: str
    headless: bool
    implicit_wait: int
    explicit_wait: int
    workers: int
    reruns: int
    screenshot_dir: str
    log_dir: str
    credentials: dict = field(default_factory=dict)

    @staticmethod
    def _bool(value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _int(value: str | None, default: int) -> int:
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    @classmethod
    def from_env(cls, env: dict | None = None) -> "EnvironmentConfig":
        """Build a config from os.environ (or an injected mapping for tests)."""
        src = os.environ if env is None else env
        creds = {
            "username": src.get("QA_USERNAME", "tester@example.com"),
            "password": src.get("QA_PASSWORD", "ChangeMe!123"),
        }
        browsers_raw = src.get("QA_BROWSERS", src.get("QA_BROWSER", "chromium"))
        browser = browsers_raw.split(",")[0].strip().lower() or "chromium"
        return cls(
            base_url=src.get("QA_BASE_URL", "http://localhost:8000").rstrip("/"),
            browser=browser,
            headless=cls._bool(src.get("QA_HEADLESS"), default=True),
            implicit_wait=cls._int(src.get("QA_IMPLICIT_WAIT"), 0),
            explicit_wait=cls._int(src.get("QA_EXPLICIT_WAIT"), 10),
            workers=cls._int(src.get("QA_WORKERS"), 4),
            reruns=cls._int(src.get("QA_RERUNS"), 2),
            screenshot_dir=src.get("QA_SCREENSHOT_DIR", "reports/screenshots"),
            log_dir=src.get("QA_LOG_DIR", "reports/logs"),
            credentials=creds,
        )

    @property
    def supported_browsers(self) -> List[str]:
        return ["chromium", "firefox", "edge"]
