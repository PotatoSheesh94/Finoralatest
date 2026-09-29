"""
Transaction domain model – core financial record.
Demonstrates composition (holds a Category reference) and validation.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from models.base import BaseEntity
from models.category import Category


class Transaction(BaseEntity):
    """Represents a single income or expense transaction."""

    VALID_TYPES = ("income", "expense")

    def __init__(
        self,
        user_id: int,
        category_id: int,
        amount: float,
        trans_type: str,
        description: str = "",
        transaction_date: str = None,
        entity_id: int = None,
        category: Optional[Category] = None,
    ):
        super().__init__(entity_id)
        if amount <= 0:
            raise ValueError("Transaction amount must be positive.")
        if trans_type not in self.VALID_TYPES:
            raise ValueError(f"Type must be one of {self.VALID_TYPES}")

        self._user_id = user_id
        self._category_id = category_id
        self._amount = float(amount)
        self._type = trans_type
        self._description = description.strip() if description else ""
        self._transaction_date = transaction_date or datetime.now().strftime("%Y-%m-%d")
        self._category = category  # composition / association

    # --- Properties ---
    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def category_id(self) -> int:
        return self._category_id

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        if value <= 0:
            raise ValueError("Amount must be positive.")
        self._amount = float(value)

    @property
    def type(self) -> str:
        return self._type

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value.strip() if value else ""

    @property
    def transaction_date(self) -> str:
        return self._transaction_date

    @transaction_date.setter
    def transaction_date(self, value: str) -> None:
        # Basic validation – expects YYYY-MM-DD
        datetime.strptime(value, "%Y-%m-%d")
        self._transaction_date = value

    @property
    def category(self) -> Optional[Category]:
        return self._category

    @category.setter
    def category(self, value: Category) -> None:
        self._category = value
        if value:
            self._category_id = value.id

    def is_expense(self) -> bool:
        return self._type == "expense"

    def is_income(self) -> bool:
        return self._type == "income"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "user_id": self._user_id,
            "category_id": self._category_id,
            "amount": self._amount,
            "type": self._type,
            "description": self._description,
            "transaction_date": self._transaction_date,
            "category_name": self._category.name if self._category else None,
        }

    def __str__(self) -> str:
        sign = "-" if self.is_expense() else "+"
        return f"{self._transaction_date} | {sign}{self._amount:.2f} | {self._description}"
