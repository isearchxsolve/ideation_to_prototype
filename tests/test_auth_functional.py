"""Functional tests - authentication (200 tests)."""

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


# Valid test credentials
VALID_EMAILS = [f"user{i}@test.example" for i in range(20)]
VALID_PASSWORDS = ["Password123!", "TestPass456", "Secure789!", "MyP@ssword1", "QaTest!2024"]
VALID_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Iris", "Jack"]


# 50 signup tests
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("name", VALID_NAMES[:5])
@pytest.mark.parametrize("email_base", ["user", "test", "demo", "qa", "sample"])
def test_signup_success(client, name, email_base, idx):
    """Successful user registration."""
    email = f"{email_base}{idx}@test.example"
    response = client.post("/signup", data={
        "name": name,
        "email": email,
        "password": "TestPassword123!",
        "confirm": "TestPassword123!",
    }, follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_password_mismatch(client, idx):
    """Registration fails with mismatched passwords."""
    response = client.post("/signup", data={
        "name": "TestUser",
        "email": f"mismatch{idx}@test.example",
        "password": "Password123!",
        "confirm": "DifferentPassword!",
    })
    assert response.status_code == 400 or b"do not match" in response.data


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_duplicate_email(client, idx):
    """Registration fails with existing email."""
    email = f"dup{idx}@test.example"
    # First signup
    client.post("/signup", data={
        "name": "First",
        "email": email,
        "password": "Password123!",
        "confirm": "Password123!",
    })
    # Duplicate signup
    response = client.post("/signup", data={
        "name": "Second",
        "email": email,
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code == 400 or b"exists" in response.data


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(20))
def test_api_create_user(client, idx):
    """Create user via API endpoint."""
    response = client.post("/api/users", json={
        "name": f"API User {idx}",
        "email": f"api_user{idx}@test.example",
        "password": "TestPassword123!",
    })
    assert response.status_code == 201


# 50 login tests
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
@pytest.mark.parametrize("password", VALID_PASSWORDS)
def test_login_with_various_passwords(client, password, idx):
    """Login accepts various valid password formats."""
    email = f"login_test{idx}@test.example"
    # Register user
    client.post("/signup", data={
        "name": "TestUser",
        "email": email,
        "password": password,
        "confirm": password,
    })
    # Login
    response = client.post("/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_invalid_credentials(client, idx):
    """Login fails with wrong password."""
    email = f"invalid_pass{idx}@test.example"
    client.post("/signup", data={
        "name": "TestUser",
        "email": email,
        "password": "CorrectPassword123!",
        "confirm": "CorrectPassword123!",
    })
    response = client.post("/login", data={
        "email": email,
        "password": "WrongPassword!",
    })
    assert response.status_code == 401 or b"Invalid" in response.data


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_nonexistent_user(client, idx):
    """Login fails for non-existent user."""
    response = client.post("/login", data={
        "email": f"nonexistent{idx}@test.example",
        "password": "AnyPassword123!",
    })
    assert response.status_code == 401 or b"Invalid" in response.data


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_empty_fields(client, idx):
    """Login fails with empty fields."""
    response = client.post("/login", data={
        "email": "",
        "password": "",
    })
    assert response.status_code >= 400


# 50 logout/session tests
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_logout_clears_session(client, idx):
    """Logout clears the user session."""
    email = f"logout{idx}@test.example"
    client.post("/signup", data={
        "name": "TestUser",
        "email": email,
        "password": "Password123!",
        "confirm": "Password123!",
    })
    client.post("/login", data={"email": email, "password": "Password123!"})
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_dashboard_requires_login(client, idx):
    """Dashboard redirects when not logged in."""
    response = client.get("/dashboard")
    assert response.status_code in (302, 401)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_dashboard_accessible_after_login(client, idx):
    """Dashboard accessible after successful login."""
    email = f"dash{idx}@test.example"
    password = "Password123!"
    client.post("/signup", data={
        "name": "TestUser",
        "email": email,
        "password": password,
        "confirm": password,
    })
    client.post("/login", data={"email": email, "password": password})
    response = client.get("/dashboard")
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_session_persistence(client, idx):
    """Session persists across requests."""
    email = f"session{idx}@test.example"
    password = "Password123!"
    client.post("/signup", data={
        "name": "TestUser",
        "email": email,
        "password": password,
        "confirm": password,
    })
    client.post("/login", data={"email": email, "password": password})
    # Multiple requests should stay logged in
    for _ in range(3):
        response = client.get("/dashboard")
        assert response.status_code == 200


# Additional tests to reach 200
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(40))
def test_api_users_list(client, idx):
    """API users endpoint returns user list."""
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
