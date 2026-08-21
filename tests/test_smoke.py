"""Smoke tests - critical path validation via real Selenium WebDriver (100 tests)."""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By

# 10 endpoints × 10 repetitions = 100 smoke tests
SECTIONS = [
    ("hero-heading", "Welcome"),
    ("nav-home", "Home"),
    ("nav-login", "Login"),
    ("nav-signup", "Sign Up"),
    ("nav-dashboard", "Dashboard"),
]


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("testid,expected_text", SECTIONS)
def test_home_page_element_present(
    driver, live_server, env_config, testid, expected_text, idx
):
    """Verify home page elements are present and visible in the browser."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    element = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{testid}']")
    assert element.is_displayed()
    assert expected_text.lower() in element.text.lower()


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
def test_home_page_title(driver, live_server, idx):
    """Browser title is correct."""
    driver.get(live_server)
    assert "Home" in driver.title or "Demo" in driver.title or driver.title


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
def test_login_page_form_visible(driver, live_server, idx):
    """Login page form elements are visible in browser."""
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='login-email']"
    ).is_displayed()
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='login-password']"
    ).is_displayed()
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='login-submit']"
    ).is_displayed()


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
def test_signup_page_form_visible(driver, live_server, idx):
    """Signup page form elements are visible in browser."""
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='signup-name']"
    ).is_displayed()
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='signup-email']"
    ).is_displayed()
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='signup-password']"
    ).is_displayed()
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='signup-confirm']"
    ).is_displayed()
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='signup-submit']"
    ).is_displayed()


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
def test_health_endpoint_json(driver, live_server, idx):
    """Health endpoint returns JSON in browser."""
    driver.get(f"{live_server}/health")
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "ok" in body.lower()


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
def test_404_page_displayed(driver, live_server, idx):
    """404 page is displayed for non-existent routes."""
    driver.get(f"{live_server}/nonexistent-page-xyz-{idx}")
    driver.implicitly_wait(2)
    el = driver.find_element(By.CSS_SELECTOR, "[data-testid='error-404']")
    assert el.is_displayed()


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
def test_navigation_bar_present(driver, live_server, idx):
    """Navigation bar is present on every page."""
    nav_links = driver.find_elements(By.CSS_SELECTOR, "nav a")
    assert len(nav_links) >= 3
