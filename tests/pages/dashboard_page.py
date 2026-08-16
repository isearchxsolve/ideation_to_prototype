"""Dashboard / landing page object for authenticated users."""

from __future__ import annotations

from tests.pages.base_page import BasePage
from tests.pages.page_factory import register


@register("/dashboard", "dashboard")
class DashboardPage(BasePage):
    """Main dashboard page after successful login."""

    PATH = "/dashboard"
    USER_MENU = ("css selector", "[data-testid='user-menu']")
    LOGOUT_BUTTON = ("css selector", "[data-testid='logout-button']")
    WELCOME_BANNER = ("css selector", "[data-testid='welcome-banner']")
    NAVIGATION_LINKS = ("css selector", "[data-testid='nav-link']")

    def navigate(self) -> DashboardPage:
        """Navigate to the dashboard page."""
        self.open(self.PATH)
        return self

    def logout(self) -> DashboardPage:
        """Click user menu then logout button."""
        self.click(self.USER_MENU)
        self.click(self.LOGOUT_BUTTON)
        return self

    def welcome_message(self) -> str:
        """Get welcome banner text."""
        return self.get_text(self.WELCOME_BANNER)

    def is_logged_in(self) -> bool:
        """Check if user is still authenticated."""
        return self.is_visible(self.USER_MENU)
