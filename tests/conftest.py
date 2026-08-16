"""Shared pytest fixtures and configuration for the Selenium QA framework.

Provides:
  * WebDriver session fixture with webdriver-manager auto-provisioning
  * Environment configuration fixture (URLs, credentials, browser targets)
  * Page Factory wiring helpers
  * Screenshot-on-failure hook and HTML reporting metadata
"""

from __future__ import annotations

import json
import logging
import os
import sys
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

# Make ``tests`` importable as a package root regardless of pytest invocation.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.factories.test_data_factory import (
    TestDataFactory,
    get_factory,
    reset_factory,
)
from tests.pages.base_page import BasePage
from tests.pages.page_factory import PageFactory

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------
def _load_env_config() -> dict[str, Any]:
    """Build a typed environment config from env vars (never hardcode secrets)."""
    return {
        "base_url": os.environ.get("APP_BASE_URL", "http://localhost:8000"),
        "admin_url": os.environ.get("APP_ADMIN_URL", "http://localhost:8000/admin"),
        "api_url": os.environ.get("APP_API_URL", "http://localhost:8000/api"),
        "browser": os.environ.get("APP_BROWSER", "chromium").lower(),
        "headless": os.environ.get("APP_HEADLESS", "true").lower()
        in {"1", "true", "yes"},
        "timeout": int(os.environ.get("APP_TIMEOUT", "15")),
        "implicit_wait": int(os.environ.get("APP_IMPLICIT_WAIT", "5")),
        "retry_count": int(os.environ.get("APP_RETRY_COUNT", "2")),
        "credentials": {
            "admin_user": os.environ.get("APP_ADMIN_USER", "admin"),
            "admin_pass": os.environ.get("APP_ADMIN_PASS", "ChangeMe123!"),
            "test_user": os.environ.get("APP_TEST_USER", "tester"),
            "test_pass": os.environ.get("APP_TEST_PASS", "TestPass123!"),
        },
        "viewport": {
            "width": int(os.environ.get("APP_VIEWPORT_WIDTH", "1366")),
            "height": int(os.environ.get("APP_VIEWPORT_HEIGHT", "768")),
        },
        "report_dir": Path(os.environ.get("APP_REPORT_DIR", "reports")),
    }


@pytest.fixture(scope="session")
def env_config() -> dict[str, Any]:
    """Session-scoped environment configuration."""
    return _load_env_config()


# ---------------------------------------------------------------------------
# WebDriver fixture
# ---------------------------------------------------------------------------
def _build_driver(browser: str, headless: bool, viewport: dict[str, int]):
    """Build a WebDriver instance using webdriver-manager."""
    from selenium import webdriver
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

    options = None
    if browser == "chromium" or browser == "chrome":
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument(f"--window-size={viewport['width']},{viewport['height']}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=options,
        )
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(
            service=webdriver.firefox.service.Service(GeckoDriverManager().install()),
            options=options,
        )
    elif browser == "edge":
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Edge(
            service=webdriver.edge.service.Service(
                EdgeChromiumDriverManager().install()
            ),
            options=options,
        )
    else:
        raise ValueError(f"Unsupported browser: {browser!r}")
    return driver


@pytest.fixture(scope="session")
def _session_driver(env_config: dict[str, Any]) -> Generator[Any, None, None]:
    """One WebDriver per xdist worker, reused across tests for speed."""
    driver_instance = _build_driver(
        browser=env_config["browser"],
        headless=env_config["headless"],
        viewport=env_config["viewport"],
    )
    driver_instance.set_window_size(
        env_config["viewport"]["width"], env_config["viewport"]["height"]
    )
    try:
        yield driver_instance
    finally:
        try:
            driver_instance.quit()
        except Exception:
            logger.exception("Error quitting WebDriver")


@pytest.fixture(scope="function")
def driver(_session_driver, env_config: dict[str, Any], live_server: str) -> Generator[Any, None, None]:
    """Per-test handle over the shared worker browser with clean state.

    Dismisses leftover alerts, navigates to the app origin so cookie
    deletion targets the app domain (Chrome scopes delete_all_cookies to
    the current origin), and resets implicit wait so one test's waits
    cannot leak into the next.
    """
    from selenium.common.exceptions import NoAlertPresentException

    try:
        _session_driver.switch_to.alert.dismiss()
    except NoAlertPresentException:
        pass  # no alert present is the common case
    try:
        _session_driver.get(live_server)
        _session_driver.delete_all_cookies()
    except Exception:
        logger.exception("Error clearing cookies before test")
    _session_driver.implicitly_wait(env_config["implicit_wait"])
    try:
        yield _session_driver
    finally:
        try:
            _session_driver.get("about:blank")
        except Exception:
            logger.exception("Error resetting browser after test")


@pytest.fixture(scope="session")
def browser_driver(_session_driver) -> Generator[Any, None, None]:
    """Session-scoped WebDriver for performance-critical suites."""
    yield _session_driver


# ---------------------------------------------------------------------------
# Page Object fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def base_page(driver, env_config: dict[str, Any]) -> BasePage:
    """Bare BasePage wired to the current driver and environment."""
    return BasePage(
        driver=driver,
        base_url=env_config["base_url"],
        timeout=env_config["timeout"],
    )


@pytest.fixture(scope="function")
def page_factory(driver, env_config: dict[str, Any]) -> PageFactory:
    """Return the PageFactory class with env-aware defaults."""
    PageFactory.clear()
    from tests.pages.about_page import AboutPage
    from tests.pages.dashboard_page import DashboardPage
    from tests.pages.home_page import HomePage
    from tests.pages.login_page import LoginPage
    from tests.pages.messages_page import MessagesPage
    from tests.pages.signup_page import SignupPage

    PageFactory.register_page("home", HomePage, "index", "root")
    PageFactory.register_page("login", LoginPage, "signin")
    PageFactory.register_page("signup", SignupPage, "register")
    PageFactory.register_page("dashboard", DashboardPage, "dashboard")
    PageFactory.register_page("messages", MessagesPage, "messages")
    PageFactory.register_page("about", AboutPage, "about")
    return PageFactory


# ---------------------------------------------------------------------------
# Test data fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="function")
def data_factory() -> TestDataFactory:
    """Function-scoped factory with a fresh seed for per-test uniqueness."""
    reset_factory()
    return get_factory()


@pytest.fixture(scope="session")
def shared_factory() -> TestDataFactory:
    """Session-scoped factory for read-only seed data."""
    reset_factory()
    return get_factory(seed=12345)


@pytest.fixture(scope="function")
def user_record(data_factory: TestDataFactory) -> dict[str, Any]:
    """Produce a unique user payload for a single test."""
    return data_factory.user().to_dict()


@pytest.fixture(scope="function")
def product_record(data_factory: TestDataFactory) -> dict[str, Any]:
    """Produce a unique product payload for a single test."""
    return data_factory.product().to_dict()


@pytest.fixture(scope="function")
def order_record(data_factory: TestDataFactory) -> dict[str, Any]:
    """Produce a unique order payload for a single test."""
    return data_factory.order().to_dict()


@pytest.fixture(scope="function")
def payment_record(data_factory: TestDataFactory) -> dict[str, Any]:
    """Produce a unique payment payload for a single test."""
    return data_factory.payment().to_dict()


# ---------------------------------------------------------------------------
# Reporting hooks
# ---------------------------------------------------------------------------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach screenshot-on-failure and write a per-test JSON report."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return

    test_id = item.nodeid.replace("::", "__").replace("/", "_")
    report_dir = Path(os.environ.get("APP_REPORT_DIR", "reports"))
    json_dir = report_dir / "per-test"
    json_dir.mkdir(parents=True, exist_ok=True)

    extra: dict[str, Any] = {"screenshot": None}

    if report.failed:
        driver_instance = item.funcargs.get("driver") or item.funcargs.get(
            "browser_driver"
        )
        if driver_instance is not None:
            screenshot_dir = report_dir / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            safe_id = "".join(c if c.isalnum() or c in "-_." else "_" for c in test_id)
            screenshot_path = screenshot_dir / f"{safe_id}.png"
            try:
                driver_instance.save_screenshot(str(screenshot_path))
                extra["screenshot"] = str(screenshot_path)
            except Exception:
                logger.exception("Failed to capture screenshot for %s", test_id)

    record = {
        "nodeid": item.nodeid,
        "outcome": report.outcome,
        "duration_s": round(report.duration, 4),
        "longrepr": str(report.longrepr) if report.longrepr else None,
        **extra,
    }
    record_path = json_dir / f"{test_id}.json"
    record_path.write_text(json.dumps(record, default=str, indent=2), encoding="utf-8")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options for the QA runner."""
    parser.addoption(
        "--qa-suite",
        action="store",
        default="all",
        choices=["all", "smoke", "functional", "regression", "e2e"],
        help="Which test suite bucket to run.",
    )
    parser.addoption(
        "--qa-bucket",
        action="store",
        default=None,
        help="Restrict to a specific bucket (e.g. 'login', 'checkout').",
    )


# ---------------------------------------------------------------------------
# Live server fixture (for real Selenium WebDriver tests)
# ---------------------------------------------------------------------------
import socket
import threading
import time

from werkzeug.serving import make_server


def _wait_for_port(host: str, port: int, timeout: float = 10.0) -> bool:
    """Wait until a TCP port is accepting connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)
    return False


@pytest.fixture(scope="session")
def live_server(env_config: dict[str, Any]):
    """Start the Flask demo app as a real HTTP server for Selenium tests.

    Spins up the demo app on 127.0.0.1:8000 in a background thread,
    waits for the port to be ready, then yields the base URL. Each xdist
    worker gets its own server instance; if port 8000 is already taken
    (e.g. by another worker), an ephemeral port is used instead.
    """
    from src.demo.app import create_app

    app = create_app()
    host = "127.0.0.1"

    server = None
    port = 8000
    try:
        server = make_server(host, port, app, threaded=True)
    except OSError:
        # Port 8000 taken (likely by another xdist worker) — use any free port.
        server = make_server(host, 0, app, threaded=True)
        port = server.server_port

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://{host}:{port}"
    if not _wait_for_port(host, port, timeout=10.0):
        raise RuntimeError(f"Live server did not start on {host}:{port}")

    yield base_url

    server.shutdown()


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Apply --qa-suite filtering at collection time."""
    suite = config.getoption("--qa-suite")
    bucket = config.getoption("--qa-bucket")

    keep: list[pytest.Item] = []
    for item in items:
        markers = {m.name for m in item.iter_markers()}
        if suite != "all" and suite not in markers and "all" not in markers:
            continue
        if bucket and bucket not in markers and bucket not in item.nodeid.lower():
            continue
        keep.append(item)

    items[:] = keep
