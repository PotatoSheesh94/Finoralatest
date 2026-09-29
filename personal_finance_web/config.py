"""
Configuration for the Smart Personal Finance Management System (Flask Web Version).
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "finance.db"

# Flask secret key. Replit's session secret is the safe default when no
# app-specific key has been configured.
SECRET_KEY = os.getenv("SECRET_KEY") or os.getenv("SESSION_SECRET") or "dev-secret-key-change-me-in-production-2026"

# Google Gemini
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

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
