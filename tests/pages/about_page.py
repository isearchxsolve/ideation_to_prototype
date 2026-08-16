"""About page object for the demo target app."""

from __future__ import annotations

from tests.pages.base_page import BasePage
from tests.pages.page_factory import register


@register("/about", "about")
class AboutPage(BasePage):
    """Static about page."""

    PATH = "/about"
    HEADING = ("css selector", "main h1")
    BODY_TEXT = ("css selector", "main p")

    def navigate(self) -> AboutPage:
        """Navigate to the about page."""
        self.open(self.PATH)
        return self

    def heading_text(self) -> str:
        """Get the page heading text."""
        return self.get_text(self.HEADING)

    def body_text(self) -> str:
        """Get the page body paragraph text."""
        return self.get_text(self.BODY_TEXT)
