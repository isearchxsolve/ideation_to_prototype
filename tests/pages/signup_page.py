"""Signup / registration page object."""

from __future__ import annotations

from tests.pages.base_page import BasePage
from tests.pages.page_factory import register


@register("/signup", "signup")
class SignupPage(BasePage):
    """New account registration form."""

    PATH = "/signup"
    NAME_INPUT = ("css selector", "[data-testid='signup-name']")
    EMAIL_INPUT = ("css selector", "[data-testid='signup-email']")
    PASSWORD_INPUT = ("css selector", "[data-testid='signup-password']")
    CONFIRM_INPUT = ("css selector", "[data-testid='signup-confirm']")
    SUBMIT_BUTTON = ("css selector", "[data-testid='signup-submit']")
    SUCCESS_BANNER = ("css selector", "[data-testid='signup-success']")
    ERROR_BANNER = ("css selector", "[data-testid='signup-error']")

    def navigate(self) -> SignupPage:
        """Navigate to the signup page."""
        self.open(self.PATH)
        return self

    def register(self, name: str, email: str, password: str) -> SignupPage:
        """Fill in registration form and submit."""
        self.type(self.NAME_INPUT, name)
        self.type(self.EMAIL_INPUT, email)
        self.type(self.PASSWORD_INPUT, password)
        self.type(self.CONFIRM_INPUT, password)
        self.click(self.SUBMIT_BUTTON)
        return self

    def success_message(self) -> str:
        """Get success message text."""
        return self.get_text(self.SUCCESS_BANNER)
