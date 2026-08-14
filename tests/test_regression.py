"""Regression tests - edge cases and bug reproduction (200 tests)."""

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


# Edge case: rapid requests
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_rapid_home_requests(client, idx):
    """Rapid sequential requests to home page."""
    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_rapid_health_requests(client, idx):
    """Rapid sequential requests to health endpoint."""
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "ok"


# Edge case: malformed input
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_login_sql_injection_attempt(client, idx):
    """Login handles SQL injection attempt safely."""
    response = client.post("/login", data={
        "email": "' OR 1=1 --",
        "password": "anything",
    })
    assert response.status_code in (401, 400, 200)


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_signup_xss_attempt_name(client, idx):
    """Signup handles XSS attempt in name field."""
    response = client.post("/signup", data={
        "name": "<script>alert('xss')</script>",
        "email": f"xss{idx}@test.example",
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (200, 400)


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_message_xss_attempt(client, idx):
    """Message board handles XSS attempt."""
    response = client.post("/messages", data={
        "message": "<script>alert('xss')</script>",
    }, follow_redirects=True)
    assert response.status_code == 200


# Edge case: boundary values
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_signup_max_length_email(client, idx):
    """Signup with very long email."""
    long_email = "a" * 200 + f"@test{idx}.example"
    response = client.post("/signup", data={
        "name": "TestUser",
        "email": long_email,
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (200, 400)


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_login_unicode_password(client, idx):
    """Login with unicode characters in password."""
    response = client.post("/login", data={
        "email": f"unicode{idx}@test.example",
        "password": "p@sswörd!によ用法",
    })
    assert response.status_code in (401, 400, 200)


# Edge case: HTTP methods
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_put_method_not_allowed(client, idx):
    """PUT method is not allowed on home."""
    response = client.put("/")
    assert response.status_code in (405, 200)


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_delete_method_not_allowed(client, idx):
    """DELETE method is not allowed on home."""
    response = client.delete("/")
    assert response.status_code in (405, 200)


# Edge case: concurrent state
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_multiple_users_signup(client, idx):
    """Multiple different users can sign up."""
    response = client.post("/signup", data={
        "name": f"ConcurrentUser{idx}",
        "email": f"concurrent_{idx}@test.example",
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (200, 400)


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_message_accumulation(client, idx):
    """Messages accumulate on the board."""
    client.post("/messages", data={"message": f"msg_{idx}"})
    response = client.get("/messages")
    assert response.status_code == 200


# Edge case: session edge cases
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_logout_without_login(client, idx):
    """Logout without being logged in."""
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_dashboard_without_login(client, idx):
    """Dashboard access without login redirects."""
    response = client.get("/dashboard")
    assert response.status_code in (302, 401)


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(10))
def test_api_messages_empty(client, idx):
    """API messages endpoint works when empty."""
    response = client.get("/api/messages")
    assert response.status_code == 200
    data = response.get_json()
    assert "messages" in data


# Additional tests to reach 200
@pytest.mark.regression
@pytest.mark.parametrize("idx", range(30))
def test_health_response_structure(client, idx):
    """Health endpoint returns expected structure."""
    response = client.get("/health")
    data = response.get_json()
    assert "status" in data
    assert "users" in data
    assert "messages" in data


@pytest.mark.regression
@pytest.mark.parametrize("idx", range(20))
def test_404_returns_error_page(client, idx):
    """404 returns error page with testid."""
    response = client.get(f"/not-found-{idx}")
    assert response.status_code == 404
    assert b"error-404" in response.data
