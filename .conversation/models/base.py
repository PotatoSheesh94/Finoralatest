"""
Abstract base entity providing common identity and representation behaviour.
Demonstrates encapsulation and a foundation for inheritance.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseEntity(ABC):
    """Abstract base class for all domain entities."""

    def __init__(self, entity_id: int = None):
        self._id = entity_id

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        if value is not None and value < 0:
            raise ValueError("Entity ID cannot be negative.")
        self._id = value

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize entity to a dictionary."""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"
