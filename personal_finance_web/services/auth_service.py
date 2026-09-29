"""
Authentication and user management service.
"""

from typing import Optional

from database.db_manager import DatabaseManager
from models.user import User


class AuthService:
    """Handles user registration, login, and profile retrieval."""

    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()

    def register(self, username: str, password: str, full_name: str, email: str = "") -> User:
        if not username or not password or not full_name:
            raise ValueError("Username, password, and full name are required.")
        if len(password) < 4:
            raise ValueError("Password must be at least 4 characters.")

        existing = self.db.fetch_one(
            "SELECT id FROM users WHERE username = ?", (username.strip(),)
        )
        if existing:
            raise ValueError(f"Username '{username}' is already taken.")

        user = User(username=username.strip(), password=password, full_name=full_name, email=email)
        user_id = self.db.insert(
            """INSERT INTO users (username, password_hash, full_name, email)
               VALUES (?, ?, ?, ?)""",
            (user.username, user.password_hash, user.full_name, user.email),
        )
        user.id = user_id
        return user

    def login(self, username: str, password: str) -> User:
        row = self.db.fetch_one(
            "SELECT * FROM users WHERE username = ? AND is_active = 1",
            (username.strip(),),
        )
        if not row:
            raise ValueError("Invalid username or password.")

        user = User(
            username=row["username"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            email=row["email"] or "",
            entity_id=row["id"],
            is_active=bool(row["is_active"]),
        )
        if not user.verify_password(password):
            raise ValueError("Invalid username or password.")
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        row = self.db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
        if not row:
            return None
        return User(
            username=row["username"],
            password_hash=row["password_hash"],
            full_name=row["full_name"],
            email=row["email"] or "",
            entity_id=row["id"],
            is_active=bool(row["is_active"]),
        )
