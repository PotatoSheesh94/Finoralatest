"""Configuration for the Finora personal finance web app."""

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

APP_TITLE = "Finora"
APP_VERSION = "1.0.0"
PROJECT_TITLE = "Final Project In OOP & Discrete Structure"
APP_DESCRIPTION = "Smart Personal Finance Management System with AI-Assisted Spending Analysis"
TAGLINE = "Understand your money. Decide smarter."
LEADER = "Harvy Aguilar"
TEAM_MEMBERS = (
    "Shiemar Maravilla",
    "Formanes Chene",
    "Daniela Diamos",
    "Hanna Nicole",
)
PROFESSOR = "Mr. Villanueva"
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
