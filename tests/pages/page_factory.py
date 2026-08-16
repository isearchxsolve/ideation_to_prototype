"""PageFactory registry mapping route paths to page objects.

This module provides a central registry so tests can request a page object
by route name without importing concrete classes directly. New pages are
registered via the ``register`` decorator or ``register_page`` function.
"""

from __future__ import annotations

from typing import ClassVar

from tests.pages.base_page import BasePage


class PageFactory:
    """Registry mapping route names to page object classes."""

    _registry: ClassVar[dict[str, type[BasePage]]] = {}
    _route_aliases: ClassVar[dict[str, str]] = {}

    @classmethod
    def register(cls, route: str, *aliases: str):
        """Class decorator to register a page object for a route."""

        def decorator(page_cls: type[BasePage]) -> type[BasePage]:
            cls._registry[route] = page_cls
            for alias in aliases:
                cls._route_aliases[alias] = route
            return page_cls

        return decorator

    @classmethod
    def register_page(cls, route: str, page_cls: type[BasePage], *aliases: str) -> None:
        """Register a page object class for a route programmatically."""
        cls._registry[route] = page_cls
        for alias in aliases:
            cls._route_aliases[alias] = route

    @classmethod
    def get_page(cls, route: str) -> type[BasePage]:
        """Return the page object class registered for ``route``.

        Raises ``KeyError`` if no page is registered for the route.
        """
        resolved = cls._route_aliases.get(route, route)
        if resolved not in cls._registry:
            raise KeyError(f"No page object registered for route: {route!r}")
        return cls._registry[resolved]

    @classmethod
    def create(
        cls, route: str, driver, base_url: str = "", timeout: int = 10
    ) -> BasePage:
        """Instantiate and return a page object for ``route``.

        Parameters
        ----------
        route : str
            The route name registered with the factory.
        driver : selenium.webdriver.WebDriver
            Active WebDriver instance.
        base_url : str
            Base URL for the application under test.
        timeout : int
            Default wait timeout in seconds.
        """
        page_cls = cls.get_page(route)
        return page_cls(driver=driver, base_url=base_url, timeout=timeout)

    @classmethod
    def all_routes(cls) -> list[str]:
        """Return all registered route names."""
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered pages (useful for testing)."""
        cls._registry.clear()
        cls._route_aliases.clear()

    @classmethod
    def is_registered(cls, route: str) -> bool:
        """Return True if a page object is registered for ``route``."""
        resolved = cls._route_aliases.get(route, route)
        return resolved in cls._registry


def get_page_class(route: str) -> type[BasePage]:
    """Module-level convenience wrapper around ``PageFactory.get_page``."""
    return PageFactory.get_page(route)


def create_page(route: str, driver, base_url: str = "", timeout: int = 10) -> BasePage:
    """Module-level convenience wrapper around ``PageFactory.create``."""
    return PageFactory.create(route, driver, base_url=base_url, timeout=timeout)


def register(route: str, *aliases: str):
    """Module-level convenience decorator for registering page objects."""
    return PageFactory.register(route, *aliases)


def list_pages() -> list[str]:
    """Return all registered route names."""
    return PageFactory.all_routes()


def find_page_by_alias(alias: str) -> str | None:
    """Resolve an alias to its canonical route name, if registered."""
    return PageFactory._route_aliases.get(alias)
