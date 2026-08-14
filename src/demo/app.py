"""Demo Flask application for Selenium QA testing.

Provides a realistic target app with auth, messaging, and navigation
for the 1000 Selenium test cases.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for


def create_app() -> Flask:
    """Create and configure the demo Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key-for-qa-only"
    
    # In-memory data stores
    users: Dict[str, Dict[str, Any]] = {}
    messages: List[Dict[str, Any]] = []

    # HTML Templates with data-testid attributes
    BASE_TEMPLATE = """<!DOCTYPE html>
<html><head><title>{title}</title></head><body>
<nav>
  <a href="/" data-testid="nav-home">Home</a>
  <a href="/login" data-testid="nav-login">Login</a>
  <a href="/signup" data-testid="nav-signup">Sign Up</a>
  <a href="/dashboard" data-testid="nav-dashboard">Dashboard</a>
</nav>
<main>{content}</main>
</body></html>"""

    HOME_HTML = BASE_TEMPLATE.format(
        title="Home",
        content="""
<h1 data-testid="hero-heading">Welcome to Demo App</h1>
<p data-testid="hero-subtitle">A sample application for QA testing</p>
<div data-testid="features">
  <div data-testid="feature-auth">User Authentication</div>
  <div data-testid="feature-messages">Message Board</div>
</div>"""
    )

    LOGIN_HTML = BASE_TEMPLATE.format(
        title="Login",
        content="""
<h1 data-testid="login-title">Login</h1>
<form method="POST" action="/login">
  <input type="email" name="email" placeholder="Email" data-testid="login-email" required>
  <input type="password" name="password" placeholder="Password" data-testid="login-password" required>
  <button type="submit" data-testid="login-submit">Login</button>
</form>
<p data-testid="login-error" class="error"></p>
<a href="/forgot" data-testid="login-forgot">Forgot password?</a>"""
    )

    SIGNUP_HTML = BASE_TEMPLATE.format(
        title="Sign Up",
        content="""
<h1 data-testid="signup-title">Create Account</h1>
<form method="POST" action="/signup">
  <input type="text" name="name" placeholder="Name" data-testid="signup-name" required>
  <input type="email" name="email" placeholder="Email" data-testid="signup-email" required>
  <input type="password" name="password" placeholder="Password" data-testid="signup-password" required>
  <input type="password" name="confirm" placeholder="Confirm" data-testid="signup-confirm" required>
  <button type="submit" data-testid="signup-submit">Sign Up</button>
</form>
<p data-testid="signup-success" class="success"></p>
<p data-testid="signup-error" class="error"></p>"""
    )

    DASHBOARD_HTML = BASE_TEMPLATE.format(
        title="Dashboard",
        content="""
<h1 data-testid="welcome-banner">Welcome, {username}!</h1>
<div data-testid="user-menu">
  <button data-testid="logout-button">Logout</button>
</div>
<div data-testid="dashboard-content">
  <p>You are logged in.</p>
</div>"""
    )

    MESSAGES_HTML = BASE_TEMPLATE.format(
        title="Messages",
        content="""
<h1 data-testid="messages-title">Message Board</h1>
<form method="POST" action="/messages">
  <input type="text" name="message" placeholder="Message" data-testid="message-input" required>
  <button type="submit" data-testid="message-submit">Post</button>
</form>
<ul data-testid="messages-list">
{messages}
</ul>"""
    )

    @app.route("/")
    def home():
        return HOME_HTML

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "users": len(users), "messages": len(messages)})

    @app.route("/api/status")
    def api_status():
        return jsonify({"healthy": True, "version": "1.0.0"})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            user = users.get(email)
            if user and user.get("password") == password:
                session["user_email"] = email
                return redirect("/dashboard")
            return LOGIN_HTML.replace('<p data-testid="login-error"', 
                                      '<p data-testid="login-error">Invalid credentials</p><p data-testid="login-error"'), 401
        return LOGIN_HTML

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            name = request.form.get("name", "")
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            confirm = request.form.get("confirm", "")
            
            if password != confirm:
                return SIGNUP_HTML.replace('<p data-testid="signup-error"',
                                          '<p data-testid="signup-error">Passwords do not match</p><p data-testid="signup-error"'), 400
            
            if email in users:
                return SIGNUP_HTML.replace('<p data-testid="signup-error"',
                                          '<p data-testid="signup-error">Email already exists</p><p data-testid="signup-error"'), 400
            
            users[email] = {
                "id": str(uuid.uuid4()),
                "name": name,
                "email": email,
                "password": password,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            return SIGNUP_HTML.replace('<p data-testid="signup-success"',
                                       '<p data-testid="signup-success">Account created!</p><p data-testid="signup-success"')
        return SIGNUP_HTML

    @app.route("/dashboard")
    def dashboard():
        email = session.get("user_email")
        if not email or email not in users:
            return redirect("/login")
        username = users[email].get("name", "User")
        return DASHBOARD_HTML.format(username=username)

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        session.pop("user_email", None)
        return redirect("/")

    @app.route("/messages", methods=["GET", "POST"])
    def messages_view():
        if request.method == "POST":
            msg = request.form.get("message", "").strip()
            if msg:
                messages.append({
                    "id": str(uuid.uuid4()),
                    "text": msg,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            return redirect("/messages")
        
        msgs_html = "\n".join(
            f'<li data-testid="message-item" data-id="{m["id"]}">{m["text"]}</li>'
            for m in messages[-50:]
        )
        return MESSAGES_HTML.format(messages=msgs_html)

    @app.route("/api/messages")
    def api_messages():
        return jsonify({"messages": messages[-50:]})

    @app.route("/api/users", methods=["GET", "POST"])
    def api_users():
        if request.method == "POST":
            data = request.get_json() or {}
            email = data.get("email", "")
            if email and email not in users:
                users[email] = {
                    "id": str(uuid.uuid4()),
                    "name": data.get("name", ""),
                    "email": email,
                    "password": data.get("password", ""),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            return jsonify({"created": True}), 201
        return jsonify({"users": [{"id": u["id"], "name": u["name"], "email": u["email"]} for u in users.values()]})

    @app.route("/about")
    def about():
        return BASE_TEMPLATE.format(title="About", content="<h1>About</h1><p>Demo app for QA testing.</p>")

    @app.errorhandler(404)
    def not_found(e):
        return BASE_TEMPLATE.format(title="404", content='<h1 data-testid="error-404">Page Not Found</h1>'), 404

    @app.errorhandler(500)
    def server_error(e):
        return BASE_TEMPLATE.format(title="500", content='<h1 data-testid="error-500">Server Error</h1>'), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=8000, debug=True)
