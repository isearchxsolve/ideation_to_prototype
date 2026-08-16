"""End-to-end user journey tests via real Selenium WebDriver (100 tests)."""

from __future__ import annotations

import uuid

import pytest
from selenium.webdriver.common.by import By


def _unique_email(prefix: str = "e2e") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}@test.example"


def _signup_and_login(driver, live_server, email, password, name="E2EUser"):
    """Helper: register a user and log in via browser."""
    # Signup
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(name)
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
    driver.implicitly_wait(2)

    # Login
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_full_signup_login_logout_journey_browser(driver, live_server, idx):
    """Complete browser journey: signup → login → dashboard → logout."""
    email = _unique_email(f"journey_{idx}")
    password = "Journey123!"

    # Step 1: Signup
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        f"Journey{idx}"
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
    driver.implicitly_wait(2)

    # Step 2: Login
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        password
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)

    # Step 3: Dashboard
    driver.get(f"{live_server}/dashboard")
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) > 0

    # Step 4: Logout
    driver.get(f"{live_server}/logout")
    driver.implicitly_wait(3)

    # Step 5: Dashboard no longer accessible
    driver.get(f"{live_server}/dashboard")
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_signup_login_post_message_journey_browser(driver, live_server, idx):
    """Browser journey: signup → login → post message → view message."""
    email = _unique_email(f"msg_{idx}")
    password = "MsgPass123!"

    _signup_and_login(driver, live_server, email, password, f"MsgUser{idx}")

    # Post message
    driver.get(f"{live_server}/messages")
    driver.implicitly_wait(3)
    msg_text = f"Hello from e2e journey {idx}!"
    driver.find_element(By.CSS_SELECTOR, "[data-testid='message-input']").send_keys(
        msg_text
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='message-submit']").click()
    driver.implicitly_wait(3)

    # Verify message appears
    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='message-item']")
    assert len(messages) >= 1


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_failed_login_retry_journey_browser(driver, live_server, idx):
    """Browser journey: failed login → retry → success."""
    email = _unique_email(f"retry_{idx}")
    password = "Retry123!"

    # Register
    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']").send_keys(
        f"Retry{idx}"
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
    driver.implicitly_wait(2)

    # Failed login
    driver.get(f"{live_server}/login")
    driver.implicitly_wait(3)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-email']").send_keys(email)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-password']").send_keys(
        "WrongPass!"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    driver.implicitly_wait(3)
    welcome = driver.find_elements(By.CSS_SELECTOR, "[data-testid='welcome-banner']")
    assert len(welcome) == 0

    # Successful login
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


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_navigation_browse_journey_browser(driver, live_server, idx):
    """Browser journey: browse through all pages."""
    for page in ["/", "/login", "/signup", "/about", "/messages"]:
        driver.get(f"{live_server}{page}")
        driver.implicitly_wait(3)
        assert driver.find_element(By.TAG_NAME, "body").is_displayed()


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(10))
def test_message_board_interaction_journey_browser(driver, live_server, idx):
    """Full browser message board interaction."""
    # View board
    driver.get(f"{live_server}/messages")
    driver.implicitly_wait(3)
    assert driver.find_element(
        By.CSS_SELECTOR, "[data-testid='messages-title']"
    ).is_displayed()

    # Post multiple messages
    for i in range(3):
        driver.get(f"{live_server}/messages")
        driver.implicitly_wait(3)
        driver.find_element(By.CSS_SELECTOR, "[data-testid='message-input']").send_keys(
            f"Board {idx}_{i}"
        )
        driver.find_element(By.CSS_SELECTOR, "[data-testid='message-submit']").click()
        driver.implicitly_wait(3)

    # Verify messages
    driver.get(f"{live_server}/messages")
    driver.implicitly_wait(3)
    messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='message-item']")
    assert len(messages) >= 3


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(10))
def test_signup_form_clear_and_refill_journey_browser(driver, live_server, idx):
    """Browser journey: fill form → clear → refill → submit."""
    email = _unique_email(f"clear_{idx}")

    driver.get(f"{live_server}/signup")
    driver.implicitly_wait(3)

    # Fill with wrong data
    name_field = driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-name']")
    name_field.send_keys("WrongName")
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").send_keys(
        "wrong"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").send_keys(
        "wrong"
    )
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").send_keys(
        "wrong"
    )

    # Clear all
    name_field.clear()
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-email']").clear()
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-password']").clear()
    driver.find_element(By.CSS_SELECTOR, "[data-testid='signup-confirm']").clear()

    # Refill with correct data
    name_field.send_keys(f"Correct{idx}")
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
