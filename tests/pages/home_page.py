"""Home page object for the demo target app."""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver

from tests.pages.base_page import BasePage
from tests.pages.page_factory import register


@register("/", "home")
class HomePage(BasePage):
    """Landing page with hero section and navigation."""

    PATH = "/"
    HERO_HEADING = ("css selector", "[data-testid='hero-heading']")
    NAV_LOGIN = ("css selector", "[data-testid='nav-login']")
    NAV_SIGNUP = ("css selector", "[data-testid='nav-signup']")
    NAV_DASHBOARD = ("css selector", "[data-testid='nav-dashboard']")

    def navigate(self) -> "HomePage":
        """Navigate to the home page."""
        self.open(self.PATH)
        return self

    def goto_login(self) -> "HomePage":
        """Click login navigation link."""
        self.click(self.NAV_LOGIN)
        return self

    def goto_signup(self) -> "HomePage":
        """Click signup navigation link."""
        self.click(self.NAV_SIGNUP)
        return self

    def goto_dashboard(self) -> "HomePage":
        """Click dashboard navigation link."""
        self.click(self.NAV_DASHBOARD)
        return self

    def hero_text(self) -> str:
        """Get hero heading text."""
        return self.get_text(self.HERO_HEADING)
