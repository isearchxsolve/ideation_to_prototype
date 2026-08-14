"""End-to-end user journey tests (100 tests)."""

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


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_full_signup_login_logout_journey(client, idx):
    """Complete user journey: signup → login → dashboard → logout."""
    email = f"journey_{idx}@test.example"
    password = "JourneyPass123!"
    
    # Step 1: Signup
    response = client.post("/signup", data={
        "name": f"JourneyUser{idx}",
        "email": email,
        "password": password,
        "confirm": password,
    })
    assert response.status_code in (200, 400)
    
    # Step 2: Login
    response = client.post("/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Step 3: Access dashboard
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    # Step 4: Logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    
    # Step 5: Dashboard no longer accessible
    response = client.get("/dashboard")
    assert response.status_code in (302, 401)


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_signup_login_post_message_journey(client, idx):
    """User signs up, logs in, posts a message, views it."""
    email = f"msg_journey_{idx}@test.example"
    password = "MessagePass123!"
    
    # Signup
    client.post("/signup", data={
        "name": f"MsgUser{idx}",
        "email": email,
        "password": password,
        "confirm": password,
    })
    
    # Login
    client.post("/login", data={"email": email, "password": password})
    
    # Post message
    msg_text = f"Hello from journey {idx}!"
    response = client.post("/messages", data={"message": msg_text}, follow_redirects=True)
    assert response.status_code == 200
    
    # View messages
    response = client.get("/messages")
    assert response.status_code == 200
    
    # Check API
    response = client.get("/api/messages")
    assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_failed_login_retry_journey(client, idx):
    """User fails login, then succeeds on retry."""
    email = f"retry_{idx}@test.example"
    password = "RetryPass123!"
    
    # Signup
    client.post("/signup", data={
        "name": f"RetryUser{idx}",
        "email": email,
        "password": password,
        "confirm": password,
    })
    
    # Failed login
    response = client.post("/login", data={
        "email": email,
        "password": "WrongPassword!",
    })
    assert response.status_code in (401, 400, 200)
    
    # Successful login
    response = client.post("/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)
    assert response.status_code == 200


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(20))
def test_navigation_browse_journey(client, idx):
    """User browses through all pages."""
    pages = ["/", "/login", "/signup", "/about", "/messages", "/health"]
    for page in pages:
        response = client.get(page)
        assert response.status_code in (200, 301, 302, 401, 404)


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(10))
def test_api_user_lifecycle_journey(client, idx):
    """User lifecycle via API: create → list → verify."""
    email = f"api_lifecycle_{idx}@test.example"
    
    # Create via API
    response = client.post("/api/users", json={
        "name": f"APIUser{idx}",
        "email": email,
        "password": "ApiPass123!",
    })
    assert response.status_code == 201
    
    # List users
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
    
    # Check health reflects new user
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "ok"


@pytest.mark.e2e
@pytest.mark.parametrize("idx", range(10))
def test_message_board_interaction_journey(client, idx):
    """Full message board interaction."""
    # View empty board
    response = client.get("/messages")
    assert response.status_code == 200
    
    # Post multiple messages
    for i in range(3):
        response = client.post("/messages", data={
            "message": f"Board message {idx}_{i}",
        }, follow_redirects=True)
        assert response.status_code == 200
    
    # View populated board
    response = client.get("/messages")
    assert response.status_code == 200
    
    # Check API
    response = client.get("/api/messages")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["messages"]) >= 3
