"""
General helper functions.
"""

from datetime import datetime, timedelta


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def first_day_of_month() -> str:
    now = datetime.now()
    return now.strftime("%Y-%m-01")


def last_n_days(n: int = 30) -> tuple:
    end = datetime.now()
    start = end - timedelta(days=n)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def format_currency(amount: float, symbol: str = "₱") -> str:
    return f"{symbol}{amount:,.2f}"
