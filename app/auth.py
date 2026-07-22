from datetime import datetime
from functools import wraps

from flask import redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    if not username or not email or not password:
        return False, "All fields are required."
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        return True, "Registration successful. Please log in."
    except Exception as e:
        conn.close()
        if "UNIQUE constraint failed" in str(e):
            if "username" in str(e):
                return False, "Username already exists."
            else:
                return False, "Email already exists."
        return False, "Registration failed."


def login_user(username: str, password: str) -> tuple[bool, str, int | None]:
    """Authenticate a user. Returns (success, message, user_id)."""
    if not username or not password:
        return False, "Username and password required.", None
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return False, "Invalid username or password.", None
    
    user_id, password_hash = row[0], row[1]
    if check_password_hash(password_hash, password):
        return True, "Login successful.", user_id
    
    return False, "Invalid username or password.", None


def login_required(f):
    """Decorator to require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
