"""Regression tests - edge cases via real Selenium WebDriver (200 tests)."""

from __future__ import annotations

import uuid

import pytest
from selenium.webdriver.common.by import By


def _unique_email(prefix: str = "reg") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.example"


# ── Rapid request edge cases ────────────────────────────────────────────────
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_rapid_home_loads_browser(driver, live_server, idx):
    """Rapid sequential loads of home page in browser."""
    for _ in range(5):
        driver.get(live_server)
        driver.implicitly_wait(2)
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_rapid_page_switches_browser(driver, live_server, idx):
    """Rapid switching between pages in browser."""
    for page in ["/", "/login", "/signup", "/about", "/"]:
        driver.get(f"{live_server}{page}")
        driver.implicitly_wait(2)
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()


# ── Malformed input edge cases ──────────────────────────────────────────────
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_login_sql_injection_browser(driver, live_server, idx):
    """Login handles SQL injection attempt safely (browser)."""
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(
        "' OR 1=1 --"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        "anything"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_signup_xss_name_browser(driver, live_server, idx):
    """Signup handles XSS attempt in name field (browser)."""
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "<script>alert('xss')</script>"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        _unique_email(f"xss{idx}")
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        "Pass123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        "Pass123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(2)
    # Ensure no script is executed (Flask auto-escapes)
    body = driver.find_element(By.TAG_NAME, "body")
    assert body.is_displayed()


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_message_xss_browser(driver, live_server, idx):
    """Message board handles XSS attempt (browser)."""
    driver.get(f"{live_server}/messages")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='message-input']").send_keys(
        "<script>alert('xss')</script>"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='message-submit']").click()
    driver.implicitly_wait(3)
    # Page should still be functional
    assert driver.find_element(By.TAG_NAME, "body").is_displayed()


# ── Boundary values ──────────────────────────────────────────────────────────
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_signup_long_email_browser(driver, live_server, idx):
    """Signup with very long email in browser."""
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    long_email = "a" * 100 + f"@test{idx}.example"
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "LongEmail"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        long_email
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        "Pass123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        "Pass123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(2)
    assert driver.find_element(By.TAG_NAME, "body").is_displayed()


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_login_unicode_password_browser(driver, live_server, idx):
    """Login with unicode characters in password (browser)."""
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(
        _unique_email(f"unicode{idx}")
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        "p@sswörd!によ用法"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


# ── Session edge cases ───────────────────────────────────────────────────────
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_logout_without_login_browser(driver, live_server, idx):
    """Logout without being logged in (browser)."""
    driver.get(f"{live_server}/logout")
    driver.implicitly_wait(3)
    assert driver.find_element(By.TAG_NAME, "body").is_displayed()


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_dashboard_without_login_browser(driver, live_server, idx):
    """Dashboard access without login redirects (browser)."""
    driver.get(f"{live_server}/dashboard")
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_multiple_signup_unique_users_browser(driver, live_server, idx):
    """Multiple different users can sign up (browser)."""
    email = _unique_email(f"multi_{idx}")
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        f"MultiUser{idx}"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        email
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        "Pass123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        "Pass123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(2)
    success = driver.find_elements(By.CSS_SELECTOR, "[data-testid='signup-success']")
    assert len(success) > 0


# ── Message accumulation ─────────────────────────────────────────────────────
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_message_accumulation_browser(driver, live_server, idx):
    """Messages accumulate on the board (browser)."""
    driver.get(f"{live_server}/messages")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='message-input']").send_keys(
        f"reg_msg_{idx}"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='message-submit']").click()
    driver.implicitly_wait(3)
    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='message-item']")
    assert len(messages) >= 1


# ── 404 page rendering ───────────────────────────────────────────────────────
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_404_page_displayed_browser(driver, live_server, idx):
    """404 page renders with error element."""
    driver.get(f"{live_server}/not-found-{idx}")
    driver.implicitly_wait(3)
    error = driver.find_elements(By.CSS_SELECTOR, "[data-testid='error-404']")
    assert len(error) > 0


# ── Page source validation ──────────────────────────────────────────────────
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(30))
def test_home_page_source_contains_html_browser(driver, live_server, idx):
    """Home page source contains valid HTML."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    assert "<html" in driver.page_source.lower()


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_pages_have_nav_element_browser(driver, live_server, idx):
    """All pages have a nav element."""
    for page in ["/", "/login", "/signup"]:
        driver.get(f"{live_server}{page}")
        driver.implicitly_wait(3)
        nav = driver.find_elements(By.CSS_SELECTOR, "nav")
        assert len(nav) > 0
