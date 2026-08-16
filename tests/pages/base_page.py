"""Base Page Object Model class for the Selenium QA framework.

Provides common, robust UI interaction primitives used by every page object:
explicit waits, safe clicks, typing, text retrieval, and screenshot capture.
All locators prefer data-testid attributes for stability.
"""

from __future__ import annotations

import logging
from pathlib import Path

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)

Locator = tuple[str, str]


class BasePage:
    """Encapsulates shared Selenium interactions with retry + explicit waits."""

    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 15) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open(self, path: str = "") -> BasePage:
        """Navigate to base_url + path and return self for chaining."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.driver.get(url)
        return self

    def get_url(self) -> str:
        return self.driver.current_url

    # ------------------------------------------------------------------ #
    # Locator helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def by_testid(testid: str) -> Locator:
        return (By.CSS_SELECTOR, f"[data-testid='{testid}']")

    @staticmethod
    def by_css(css: str) -> Locator:
        return (By.CSS_SELECTOR, css)

    @staticmethod
    def by_xpath(xpath: str) -> Locator:
        return (By.XPATH, xpath)

    # ------------------------------------------------------------------ #
    # Element resolution
    # ------------------------------------------------------------------ #
    def find(self, locator: Locator, timeout: int | None = None) -> WebElement:
        """Wait for element presence and return it."""
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator: Locator, timeout: int | None = None) -> WebElement:
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located(locator))

    def find_all(
        self, locator: Locator, timeout: int | None = None
    ) -> list[WebElement]:
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_all_elements_located(locator))

    def is_present(self, locator: Locator, timeout: int = 3) -> bool:
        try:
            self.find(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def is_visible(self, locator: Locator, timeout: int = 3) -> bool:
        try:
            self.find_visible(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------ #
    # Interactions
    # ------------------------------------------------------------------ #
    def click(self, locator: Locator, timeout: int | None = None) -> BasePage:
        """Click an element, retrying once on interception/staleness."""
        element = self.find_visible(locator, timeout=timeout)
        try:
            element.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", element)
        return self

    def type(self, locator: Locator, text: str, clear: bool = True) -> BasePage:
        """Type text into an input, optionally clearing it first."""
        element = self.find_visible(locator)
        if clear:
            element.clear()
        element.send_keys(text)
        return self

    def get_text(self, locator: Locator) -> str:
        element = self.find_visible(locator)
        return element.text.strip()

    def get_attribute(self, locator: Locator, name: str) -> str | None:
        element = self.find(locator)
        return element.get_attribute(name)

    def get_value(self, locator: Locator) -> str:
        value = self.get_attribute(locator, "value")
        return value if value is not None else ""

    def select_option(self, locator: Locator, value: str) -> BasePage:
        """Select an option in a <select> by its value attribute."""
        from selenium.webdriver.support.ui import Select

        element = self.find(locator)
        Select(element).select_by_value(value)
        return self

    def submit(self, locator: Locator) -> BasePage:
        element = self.find_visible(locator)
        element.submit()
        return self

    # ------------------------------------------------------------------ #
    # State assertions helpers
    # ------------------------------------------------------------------ #
    def wait_for_text(
        self, locator: Locator, text: str, timeout: int | None = None
    ) -> bool:
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.text_to_be_present_in_element(locator, text))
            return True
        except TimeoutException:
            return False

    def wait_for_url_contains(self, fragment: str, timeout: int | None = None) -> bool:
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.url_contains(fragment))
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------ #
    # Screenshots
    # ------------------------------------------------------------------ #
    def screenshot(self, name: str, directory: Path | None = None) -> Path:
        """Capture a screenshot to reports/screenshots/<name>.png."""
        target = directory or Path("reports/screenshots")
        target.mkdir(parents=True, exist_ok=True)
        safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
        path = target / f"{safe}.png"
        self.driver.save_screenshot(str(path))
        logger.info("Screenshot saved: %s", path)
        return path

    # ------------------------------------------------------------------ #
    # Misc
    # ------------------------------------------------------------------ #
    def scroll_into_view(self, locator: Locator) -> BasePage:
        element = self.find(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        return self

    def execute_script(self, script: str, *args) -> object:
        return self.driver.execute_script(script, *args)
