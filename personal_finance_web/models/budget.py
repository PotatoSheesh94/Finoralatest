"""
Budget domain model – supports period-based spending limits.
"""

from typing import Any, Dict, Optional

from models.base import BaseEntity
from models.category import Category


class Budget(BaseEntity):
    """Represents a budget allocation for a category or overall."""

    VALID_PERIODS = ("monthly", "weekly", "yearly")

    def __init__(
        self,
        user_id: int,
        amount: float,
        period: str,
        start_date: str,
        category_id: Optional[int] = None,
        end_date: Optional[str] = None,
        notes: str = "",
        entity_id: int = None,
        category: Optional[Category] = None,
    ):
        super().__init__(entity_id)
        if amount <= 0:
            raise ValueError("Budget amount must be positive.")
        if period not in self.VALID_PERIODS:
            raise ValueError(f"Period must be one of {self.VALID_PERIODS}")

        self._user_id = user_id
        self._category_id = category_id
        self._amount = float(amount)
        self._period = period
        self._start_date = start_date
        self._end_date = end_date
        self._notes = notes.strip() if notes else ""
        self._category = category

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def category_id(self) -> Optional[int]:
        return self._category_id

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Budget amount must be positive.")
        self._amount = float(value)

    @property
    def period(self) -> str:
        return self._period

    @property
    def start_date(self) -> str:
        return self._start_date

    @property
    def end_date(self) -> Optional[str]:
        return self._end_date

    @property
    def notes(self) -> str:
        return self._notes

    @property
    def category(self) -> Optional[Category]:
        return self._category

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "user_id": self._user_id,
            "category_id": self._category_id,
            "amount": self._amount,
            "period": self._period,
            "start_date": self._start_date,
            "end_date": self._end_date,
            "notes": self._notes,
            "category_name": self._category.name if self._category else "Overall",
        }

    def __str__(self) -> str:
        cat = self._category.name if self._category else "Overall"
        return f"Budget {cat}: {self._amount:.2f} ({self._period})"
