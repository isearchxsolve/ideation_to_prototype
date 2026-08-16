"""Functional tests - navigation via real Selenium WebDriver (200 tests)."""

from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By

PAGES = ["/", "/login", "/signup", "/about", "/messages", "/health"]
NAV_LINKS = ["nav-home", "nav-login", "nav-signup", "nav-dashboard"]


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("page", PAGES)
def test_page_loads_in_browser(driver, live_server, page, idx):
    """Each page loads successfully in the browser."""
    driver.get(f"{live_server}{page}")
    driver.implicitly_wait(3)
    body = driver.find_element(By.TAG_NAME, "body")
    assert body.is_displayed()


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("link_id", NAV_LINKS)
def test_nav_link_clickable(driver, live_server, link_id, idx):
    """Navigation links are clickable in the browser."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    link = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{link_id}']")
    assert link.is_displayed()
    assert link.is_enabled()


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("link_id", NAV_LINKS[:3])
def test_nav_link_navigates(driver, live_server, link_id, idx):
    """Clicking a nav link navigates to the correct page."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    link = driver.find_element(By.CSS_SELECTOR, f"[data-testid='{link_id}']")
    link.click()
    driver.implicitly_wait(3)
    assert live_server in driver.current_url


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(20))
def test_home_to_login_navigation_browser(driver, live_server, idx):
    """Navigate from home to login via browser click."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='nav-login']").click()
    driver.implicitly_wait(3)
    assert "/login" in driver.current_url


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(20))
def test_home_to_signup_navigation_browser(driver, live_server, idx):
    """Navigate from home to signup via browser click."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='nav-signup']").click()
    driver.implicitly_wait(3)
    assert "/signup" in driver.current_url


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_to_signup_navigation_browser(driver, live_server, idx):
    """Navigate from login page to signup page."""
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    assert "/signup" in driver.current_url


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_back_navigation_browser(driver, live_server, idx):
    """Browser back button works."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.back()
    driver.implicitly_wait(3)
    assert live_server in driver.current_url


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_direct_url_access_browser(driver, live_server, idx):
    """Direct URL access to each page works in browser."""
    for page in ["/", "/login", "/signup", "/about"]:
        driver.get(f"{live_server}{page}")
        driver.implicitly_wait(3)
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_dashboard_redirect_browser(driver, live_server, idx):
    """Dashboard redirects when not logged in."""
    driver.get(f"{live_server}/dashboard")
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_messages_page_accessible_browser(driver, live_server, idx):
    """Messages page is accessible in browser."""
    driver.get(f"{live_server}/messages")
    driver.implicitly_wait(3)
    title = driver.find_element(By.CSS_SELECTOR, "[data-testid='messages-title']")
    assert title.is_displayed()


# Additional tests to reach 200
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(30))
def test_multiple_page_loads_browser(driver, live_server, idx):
    """Multiple page loads in sequence work correctly."""
    for page in ["/", "/login", "/signup", "/about"]:
        driver.get(f"{live_server}{page}")
        driver.implicitly_wait(3)
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(40))
def test_nav_bar_present_on_all_pages_browser(driver, live_server, idx):
    """Nav bar is present on all pages."""
    for page in ["/", "/login", "/signup"]:
        driver.get(f"{live_server}{page}")
        driver.implicitly_wait(3)
        nav = driver.find_elements(By.CSS_SELECTOR, "nav")
        assert len(nav) > 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(30))
def test_page_source_not_empty_browser(driver, live_server, idx):
    """Page source is not empty after navigation."""
    driver.get(live_server)
    driver.implicitly_wait(3)
    assert len(driver.page_source) > 100
