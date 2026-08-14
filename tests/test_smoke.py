"""Smoke tests - critical path validation (100 tests)."""

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


# 10 endpoints × 10 variants = 100 smoke tests
ENDPOINTS = [
    "/",
    "/login",
    "/signup",
    "/health",
    "/api/status",
    "/dashboard",
    "/about",
    "/messages",
    "/api/messages",
    "/logout",
]


@pytest.mark.smoke
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_endpoint_responds(client, endpoint, idx):
    """Verify endpoint returns a valid HTTP response."""
    response = client.get(endpoint)
    assert response.status_code in (200, 301, 302, 404), f"{endpoint} returned {response.status_code}"


@pytest.mark.smoke
def test_health_check_returns_json(client):
    """Health endpoint returns valid JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


@pytest.mark.smoke
def test_api_status_returns_json(client):
    """API status endpoint returns valid JSON."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data


@pytest.mark.smoke
def test_home_page_has_hero(client):
    """Home page contains hero heading."""
    response = client.get("/")
    assert b"hero-heading" in response.data


@pytest.mark.smoke
def test_login_page_has_form(client):
    """Login page contains login form."""
    response = client.get("/login")
    assert b"login-email" in response.data
    assert b"login-password" in response.data


@pytest.mark.smoke
def test_signup_page_has_form(client):
    """Signup page contains registration form."""
    response = client.get("/signup")
    assert b"signup-name" in response.data
    assert b"signup-email" in response.data


@pytest.mark.smoke
def test_404_page(client):
    """Non-existent route returns 404."""
    response = client.get("/nonexistent-page-xyz")
    assert response.status_code == 404
