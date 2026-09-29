"""
Input validation helpers.
"""

import re
from datetime import datetime


def validate_amount(value: str) -> float:
    try:
        amount = float(value.replace(",", "").strip())
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(amount, 2)
    except (ValueError, TypeError):
        raise ValueError("Please enter a valid positive number for the amount.")


def validate_date(value: str) -> str:
    value = value.strip()
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")


def validate_non_empty(value: str, field_name: str = "Field") -> str:
    if not value or not str(value).strip():
        raise ValueError(f"{field_name} cannot be empty.")
    return str(value).strip()


def validate_email(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(pattern, value):
        raise ValueError("Invalid email format.")
    return value
