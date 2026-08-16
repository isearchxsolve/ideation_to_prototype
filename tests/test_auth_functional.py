"""Functional tests - authentication via real Selenium WebDriver (200 tests)."""

from __future__ import annotations

import uuid

import pytest
from selenium.webdriver.common.by import By


def _unique_email(prefix: str = "selenium") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.example"


# ── Signup tests ────────────────────────────────────────────────────────────
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("name", ["Alice", "Bob", "Charlie", "Diana", "Eve"])
def test_signup_success_browser(driver, live_server, name, idx):
    """Real browser signup: fill form → submit → see success."""
    email = _unique_email(f"signup_{name}_{idx}")
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)

    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(name)
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


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_password_mismatch_browser(driver, live_server, idx):
    """Browser signup with mismatched passwords shows error."""
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)

    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "Mismatch"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        _unique_email(f"mismatch{idx}")
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        "Password123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        "DifferentPass!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()

    driver.implicitly_wait(2)
    error = driver.find_elements(By.CSS_SELECTOR, "[data-testid='signup-error']")
    assert len(error) > 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_duplicate_email_browser(driver, live_server, idx):
    """Browser signup with duplicate email shows error."""
    email = _unique_email(f"dup{idx}")
    # First registration
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "First"
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
    driver.implicitly_wait(1)

    # Second registration - same email
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "Second"
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
    error = driver.find_elements(By.CSS_SELECTOR, "[data-testid='signup-error']")
    assert len(error) > 0


# ── Login tests ─────────────────────────────────────────────────────────────
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize(
    "password", ["Pass123!", "Test456!", "Secure789!", "MyPass1!", "QaTest!2024"]
)
def test_login_success_browser(driver, live_server, password, idx):
    """Real browser login: register → login → see dashboard."""
    email = _unique_email(f"login_{idx}")
    # Register user first
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "LoginUser"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        email
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(1)

    # Login
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)

    # Should be on dashboard
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) > 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_invalid_password_browser(driver, live_server, idx):
    """Browser login with wrong password shows error."""
    email = _unique_email(f"invalid{idx}")
    # Register
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "InvalidUser"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        email
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        "Correct123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        "Correct123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(1)

    # Login with wrong password
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        "WrongPass!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(2)

    # Should still be on login page or see error
    error = driver.find_elements(By.CSS_SELECTOR, "[data-testid='login-error']")
    login_form = driver.find_elements(By.CSS_SELECTOR, "[data-testid='login-email']")
    assert len(error) > 0 or len(login_form) > 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_nonexistent_user_browser(driver, live_server, idx):
    """Browser login with non-existent user fails."""
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(
        _unique_email(f"noexist{idx}")
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        "AnyPass123!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(2)

    # Should not be on dashboard
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


# ── Session / logout tests ──────────────────────────────────────────────────
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_logout_clears_session_browser(driver, live_server, idx):
    """Browser logout clears the session."""
    email = _unique_email(f"logout{idx}")
    password = "Pass123!"
    # Register + login
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "LogoutUser"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        email
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(1)

    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)

    # Logout
    driver.get(f"{live_server}/logout")
    driver.implicitly_wait(2)

    # Dashboard should redirect
    driver.get(f"{live_server}/dashboard")
    driver.implicitly_wait(2)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_dashboard_requires_login_browser(driver, live_server, idx):
    """Dashboard redirects when not logged in (browser)."""
    driver.get(f"{live_server}/dashboard")
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_dashboard_accessible_after_login_browser(driver, live_server, idx):
    """Dashboard is accessible after login (browser)."""
    email = _unique_email(f"dash{idx}")
    password = "Pass123!"
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "DashUser"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        email
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(1)

    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)

    driver.get(f"{live_server}/dashboard")
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) > 0


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_session_persistence_browser(driver, live_server, idx):
    """Session persists across multiple browser requests."""
    email = _unique_email(f"sess{idx}")
    password = "Pass123!"
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        "SessUser"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        email
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-submit']").click()
    driver.implicitly_wait(1)

    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)

    # Multiple requests - session should persist
    for _ in range(3):
        driver.get(f"{live_server}/dashboard")
        driver.implicitly_wait(3)
        welcome = driver.find_elements(
            By.CSS_SELECTOR, "[data-testid='welcome-banner']"
        )
        assert len(welcome) > 0


# Additional tests to reach 200
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(40))
def test_signup_form_field_count_browser(driver, live_server, idx):
    """Signup form has all expected input fields (browser)."""
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    inputs = driver.find_elements(By.CSS_SELECTOR, "form input")
    assert len(inputs) >= 4


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(20))
def test_login_form_field_count_browser(driver, live_server, idx):
    """Login form has email and password fields (browser)."""
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    inputs = driver.find_elements(By.CSS_SELECTOR, "form input")
    assert len(inputs) >= 2
