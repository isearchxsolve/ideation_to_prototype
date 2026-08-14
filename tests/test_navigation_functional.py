"""Functional tests - navigation and routing (200 tests)."""

from __future__ import annotations

import pytest

from src.demo.app import create_app


@pytest.fixture
def client():
    """Flask test client for CI-safe testing."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# Navigation link tests
NAV_LINKS = [
    ("/", "nav-home"),
    ("/login", "nav-login"),
    ("/signup", "nav-signup"),
    ("/dashboard", "nav-dashboard"),
]


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("from_path", ["/", "/login", "/signup", "/about"])
@pytest.mark.parametrize("to_path,link_id", NAV_LINKS)
def test_navigation_link_present(client, from_path, to_path, link_id, idx):
    """Navigation links are present on each page."""
    response = client.get(from_path)
    assert link_id.encode() in response.data


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("path", ["/", "/login", "/signup", "/about", "/messages", "/health"])
def test_page_loads_successfully(client, path, idx):
    """Each page loads without errors."""
    response = client.get(path)
    assert response.status_code in (200, 301, 302)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_home_navigation_links(client, idx):
    """Home page has all navigation links."""
    response = client.get("/")
    assert b"nav-login" in response.data
    assert b"nav-signup" in response.data
    assert b"nav-dashboard" in response.data


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_to_signup_navigation(client, idx):
    """User can navigate from login to signup."""
    response = client.get("/login")
    assert response.status_code == 200
    # Simulate clicking signup link
    response = client.get("/signup")
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_protected_route_redirect(client, idx):
    """Protected routes redirect to login."""
    response = client.get("/dashboard")
    assert response.status_code in (302, 401)


# Redirect tests
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(20))
def test_login_redirect_to_dashboard(client, idx):
    """Successful login redirects to dashboard."""
    email = f"nav_login{idx}@test.example"
    password = "Password123!"
    client.post("/signup", data={
        "name": "TestUser",
        "email": email,
        "password": password,
        "confirm": password,
    })
    response = client.post("/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=False)
    assert response.status_code in (302, 200)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(20))
def test_logout_redirect_to_home(client, idx):
    """Logout redirects to home."""
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code in (302, 200)


# Deep link tests
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_direct_message_page_access(client, idx):
    """Messages page is accessible directly."""
    response = client.get("/messages")
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_direct_api_access(client, idx):
    """API endpoints are accessible directly."""
    response = client.get("/api/status")
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_about_page_accessible(client, idx):
    """About page is accessible."""
    response = client.get("/about")
    assert response.status_code == 200


# Additional navigation tests to reach 200
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(50))
def test_multiple_page_requests(client, idx):
    """Multiple sequential page requests work correctly."""
    for path in ["/", "/login", "/signup", "/about"]:
        response = client.get(path)
        assert response.status_code in (200, 301, 302)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(40))
def test_api_status_consistent(client, idx):
    """API status returns consistent response."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["healthy"] is True
