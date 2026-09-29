"""
Configuration for the Smart Personal Finance Management System (Flask Web Version).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "finance.db"

# Flask secret key (change in production)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production-2026")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

APP_TITLE = "Smart Personal Finance Management System"
APP_VERSION = "2.0.0 (Web)"
DEFAULT_CURRENCY = "PHP"

DEFAULT_CATEGORIES = [
    ("Food & Dining", "expense"),
    ("Transportation", "expense"),
    ("Housing / Rent", "expense"),
    ("Utilities", "expense"),
    ("Entertainment", "expense"),
    ("Healthcare", "expense"),
    ("Education", "expense"),
    ("Shopping", "expense"),
    ("Personal Care", "expense"),
    ("Miscellaneous", "expense"),
    ("Salary", "income"),
    ("Freelance / Side Income", "income"),
    ("Investment Returns", "income"),
    ("Gifts / Other Income", "income"),
]
