"""Message board page object for the demo target app."""

from __future__ import annotations

from tests.pages.base_page import BasePage
from tests.pages.page_factory import register


@register("/messages", "messages")
class MessagesPage(BasePage):
    """Public message board with a post form and message list."""

    PATH = "/messages"
    TITLE = ("css selector", "[data-testid='messages-title']")
    MESSAGE_INPUT = ("css selector", "[data-testid='message-input']")
    MESSAGE_SUBMIT = ("css selector", "[data-testid='message-submit']")
    MESSAGES_LIST = ("css selector", "[data-testid='messages-list']")
    MESSAGE_ITEM = ("css selector", "[data-testid='message-item']")

    def navigate(self) -> MessagesPage:
        """Navigate to the message board."""
        self.open(self.PATH)
        return self

    def post_message(self, text: str) -> MessagesPage:
        """Type a message and submit the form."""
        self.type(self.MESSAGE_INPUT, text)
        self.click(self.MESSAGE_SUBMIT)
        return self

    def message_texts(self) -> list[str]:
        """Return the visible message texts, oldest first."""
        if not self.is_present(self.MESSAGE_ITEM, timeout=2):
            return []
        return [el.text.strip() for el in self.find_all(self.MESSAGE_ITEM)]

    def message_count(self) -> int:
        """Return the number of visible messages."""
        return len(self.message_texts())

    def has_message(self, text: str) -> bool:
        """Check whether a message with the given text is visible."""
        return text in self.message_texts()
