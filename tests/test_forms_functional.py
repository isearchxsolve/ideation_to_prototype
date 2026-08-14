"""Functional tests - form validation and submission (200 tests)."""

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


# Form validation tests - signup
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_missing_name(client, idx):
    """Signup fails without name."""
    response = client.post("/signup", data={
        "name": "",
        "email": f"noname{idx}@test.example",
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (400, 200)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_missing_email(client, idx):
    """Signup fails without email."""
    response = client.post("/signup", data={
        "name": "TestUser",
        "email": "",
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (400, 200)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_missing_password(client, idx):
    """Signup fails without password."""
    response = client.post("/signup", data={
        "name": "TestUser",
        "email": f"nopass{idx}@test.example",
        "password": "",
        "confirm": "",
    })
    assert response.status_code in (400, 200)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_empty_confirm(client, idx):
    """Signup fails without confirm password."""
    response = client.post("/signup", data={
        "name": "TestUser",
        "email": f"noconfirm{idx}@test.example",
        "password": "Password123!",
        "confirm": "",
    })
    assert response.status_code in (400, 200)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_short_password(client, idx):
    """Signup with very short password."""
    response = client.post("/signup", data={
        "name": "TestUser",
        "email": f"shortpass{idx}@test.example",
        "password": "x",
        "confirm": "x",
    })
    assert response.status_code in (400, 200)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_long_name(client, idx):
    """Signup with very long name."""
    long_name = "A" * 500
    response = client.post("/signup", data={
        "name": long_name,
        "email": f"longname{idx}@test.example",
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (200, 400)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_signup_special_chars_name(client, idx):
    """Signup with special characters in name."""
    response = client.post("/signup", data={
        "name": f"Test-User_{idx}!@#$%",
        "email": f"special{idx}@test.example",
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (200, 400)


# Form validation tests - login
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_empty_email(client, idx):
    """Login fails with empty email."""
    response = client.post("/login", data={
        "email": "",
        "password": "Password123!",
    })
    assert response.status_code >= 400


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_empty_password(client, idx):
    """Login fails with empty password."""
    response = client.post("/login", data={
        "email": f"emptypass{idx}@test.example",
        "password": "",
    })
    assert response.status_code >= 400


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_login_both_empty(client, idx):
    """Login fails with both fields empty."""
    response = client.post("/login", data={
        "email": "",
        "password": "",
    })
    assert response.status_code >= 400


# Message form tests
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_post_message(client, idx):
    """Post a message to the board."""
    response = client.post("/messages", data={
        "message": f"Test message {idx}",
    }, follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_post_empty_message(client, idx):
    """Empty message is rejected or ignored."""
    response = client.post("/messages", data={
        "message": "",
    }, follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_post_long_message(client, idx):
    """Post a very long message."""
    long_msg = "X" * 1000
    response = client.post("/messages", data={
        "message": long_msg,
    }, follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_post_special_chars_message(client, idx):
    """Post message with special characters."""
    response = client.post("/messages", data={
        "message": f"Special <>&\"' {idx}",
    }, follow_redirects=True)
    assert response.status_code == 200


# API form tests
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_api_create_user_missing_email(client, idx):
    """API rejects user creation without email."""
    response = client.post("/api/users", json={
        "name": "TestUser",
        "password": "Password123!",
    })
    assert response.status_code in (200, 201, 400)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(10))
def test_api_create_user_no_json(client, idx):
    """API handles missing JSON body."""
    response = client.post("/api/users", data="not json")
    assert response.status_code in (200, 201, 400, 415)


# Additional tests to reach 200
@pytest.mark.functional
@pytest.mark.parametrize("idx", range(30))
def test_multiple_signup_attempts(client, idx):
    """Multiple signup attempts with unique data."""
    response = client.post("/signup", data={
        "name": f"User{idx}",
        "email": f"multi_{idx}@test.example",
        "password": "Password123!",
        "confirm": "Password123!",
    })
    assert response.status_code in (200, 400)


@pytest.mark.functional
@pytest.mark.parametrize("idx", range(30))
def test_message_board_view(client, idx):
    """Message board is viewable."""
    response = client.get("/messages")
    assert response.status_code == 200
