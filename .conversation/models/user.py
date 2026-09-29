"""
User domain model with encapsulation of credentials and profile data.
"""

import hashlib
from typing import Any, Dict, Optional

from models.base import BaseEntity


class User(BaseEntity):
    """Represents an application user."""

    def __init__(
        self,
        username: str,
        password: str = None,
        full_name: str = "",
        email: str = "",
        entity_id: int = None,
        password_hash: str = None,
        is_active: bool = True,
    ):
        super().__init__(entity_id)
        self._username = username
        self._full_name = full_name
        self._email = email
        self._is_active = is_active

        if password_hash:
            self._password_hash = password_hash
        elif password:
            self._password_hash = self._hash_password(password)
        else:
            self._password_hash = None

    @staticmethod
    def _hash_password(password: str) -> str:
        """Simple SHA-256 hash (suitable for academic project; production would use bcrypt)."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self._password_hash == self._hash_password(password)

    # --- Properties (encapsulation) ---
    @property
    def username(self) -> str:
        return self._username

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        self._full_name = value.strip() if value else ""

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value.strip() if value else ""

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def password_hash(self) -> Optional[str]:
        return self._password_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "username": self._username,
            "full_name": self._full_name,
            "email": self._email,
            "is_active": self._is_active,
        }

    def __str__(self) -> str:
        return f"User({self._username} – {self._full_name})"
