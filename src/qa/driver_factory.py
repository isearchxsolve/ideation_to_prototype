"""WebDriver factory for the Selenium QA framework.

Provides centralized WebDriver provisioning with webdriver-manager
for Chromium, Firefox, and Edge. Supports headless mode and
custom browser options.
"""

from __future__ import annotations

import logging
from typing import Any

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger(__name__)

# Container-compatibility flags for Chromium-based browsers (Chrome/Edge):
# --no-sandbox is required inside unprivileged CI containers, and
# --disable-dev-shm-usage prevents crashes from the small default /dev/shm.
CHROMIUM_HARDENING_FLAGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
]

# Flags that trim per-process memory/background work so several parallel
# workers fit on CI runners and dev machines without OOM-killing a renderer.
CHROMIUM_MEMORY_FLAGS = [
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-renderer-backgrounding",
    "--metrics-recording-only",
    "--no-first-run",
    "--mute-audio",
    "--hide-scrollbars",
]


def create_driver(
    browser: str = "chromium",
    headless: bool = True,
    viewport: dict[str, int] | None = None,
    extra_options: list | None = None,
) -> Any:
    """Create and return a WebDriver instance.

    Parameters
    ----------
    browser : str
        One of: chromium, chrome, firefox, edge
    headless : bool
        Run in headless mode (default: True)
    viewport : dict
        Dict with 'width' and 'height' keys for window size
    extra_options : list
        Additional browser-specific options to add

    Returns
    -------
    selenium.webdriver.WebDriver
    """
    options = None
    service = None
    viewport = viewport or {"width": 1366, "height": 768}
    extra_options = extra_options or []

    if browser in ("chromium", "chrome"):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={viewport['width']},{viewport['height']}")
        for opt in CHROMIUM_HARDENING_FLAGS + CHROMIUM_MEMORY_FLAGS + extra_options:
            options.add_argument(opt)
        service = webdriver.chrome.service.Service(ChromeDriverManager().install())

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        for opt in extra_options:
            options.add_argument(opt)
        service = webdriver.firefox.service.Service(GeckoDriverManager().install())

    elif browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={viewport['width']},{viewport['height']}")
        for opt in CHROMIUM_HARDENING_FLAGS + CHROMIUM_MEMORY_FLAGS + extra_options:
            options.add_argument(opt)
        service = webdriver.edge.service.Service(EdgeChromiumDriverManager().install())

    else:
        raise ValueError(f"Unsupported browser: {browser!r}")

    driver = (
        webdriver.Chrome(service=service, options=options)
        if browser in ("chromium", "chrome")
        else (
            webdriver.Firefox(service=service, options=options)
            if browser == "firefox"
            else webdriver.Edge(service=service, options=options)
        )
    )

    driver.set_window_size(viewport["width"], viewport["height"])
    logger.info("Created %s WebDriver (headless=%s)", browser, headless)
    return driver
