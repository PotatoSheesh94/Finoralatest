"""
Category domain model – used for both income and expense classification.
"""

from typing import Any, Dict, Optional

from models.base import BaseEntity


class Category(BaseEntity):
    """Represents a transaction category (income or expense)."""

    VALID_TYPES = ("income", "expense")

    def __init__(
        self,
        name: str,
        cat_type: str,
        user_id: Optional[int] = None,
        is_default: bool = False,
        entity_id: int = None,
    ):
        super().__init__(entity_id)
        if cat_type not in self.VALID_TYPES:
            raise ValueError(f"Category type must be one of {self.VALID_TYPES}")
        self._name = name.strip()
        self._type = cat_type
        self._user_id = user_id
        self._is_default = is_default

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Category name cannot be empty.")
        self._name = value.strip()

    @property
    def type(self) -> str:
        return self._type

    @property
    def user_id(self) -> Optional[int]:
        return self._user_id

    @property
    def is_default(self) -> bool:
        return self._is_default

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "name": self._name,
            "type": self._type,
            "user_id": self._user_id,
            "is_default": self._is_default,
        }

    def __str__(self) -> str:
        return f"{self._name} ({self._type})"
