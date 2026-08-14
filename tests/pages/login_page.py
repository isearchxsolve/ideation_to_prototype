"""Login page object for the demo target app."""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver

from tests.pages.base_page import BasePage
from tests.pages.page_factory import register


@register("/login", "login")
class LoginPage(BasePage):
    """Authentication page with email/password fields."""

    PATH = "/login"
    EMAIL_INPUT = ("css selector", "[data-testid='login-email']")
    PASSWORD_INPUT = ("css selector", "[data-testid='login-password']")
    SUBMIT_BUTTON = ("css selector", "[data-testid='login-submit']")
    ERROR_BANNER = ("css selector", "[data-testid='login-error']")
    FORGOT_LINK = ("css selector", "[data-testid='login-forgot']")

    def navigate(self) -> "LoginPage":
        """Navigate to the login page."""
        self.open(self.PATH)
        return self

    def login(self, email: str, password: str) -> "LoginPage":
        """Fill in login form and submit."""
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BUTTON)
        return self

    def error_message(self) -> str:
        """Get error message text."""
        return self.get_text(self.ERROR_BANNER)
