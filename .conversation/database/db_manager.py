"""
Database Manager – handles SQLite connection, schema creation, and low-level queries.
Implements a simple connection singleton pattern for the application lifetime.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Optional, Tuple

from config import DATABASE_PATH, DEFAULT_CATEGORIES


class DatabaseManager:
    """Centralized SQLite access layer with schema initialization and helper methods."""

    _instance: Optional["DatabaseManager"] = None

    def __new__(cls, db_path: Path = DATABASE_PATH):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: Path = DATABASE_PATH):
        if self._initialized:
            return
        self.db_path = db_path
        self._initialized = True
        self._initialize_schema()

    @contextmanager
    def get_connection(self):
        """Context manager that yields a connection and ensures proper closing."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_schema(self) -> None:
        """Create tables if they do not exist and seed default categories."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    is_active INTEGER DEFAULT 1
                )
            """)

            # Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    user_id INTEGER,
                    is_default INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(name, user_id)
                )
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    description TEXT,
                    transaction_date TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)

            # Budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category_id INTEGER,
                    amount REAL NOT NULL CHECK(amount > 0),
                    period TEXT NOT NULL CHECK(period IN ('monthly', 'weekly', 'yearly')),
                    start_date TEXT NOT NULL,
                    end_date TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)

            # AI analysis history (optional audit)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    request_type TEXT NOT NULL,
                    input_summary TEXT,
                    response_text TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Seed default categories (system-wide, user_id = NULL)
            cursor.execute("SELECT COUNT(*) FROM categories WHERE is_default = 1")
            if cursor.fetchone()[0] == 0:
                for name, cat_type in DEFAULT_CATEGORIES:
                    cursor.execute(
                        "INSERT INTO categories (name, type, user_id, is_default) VALUES (?, ?, NULL, 1)",
                        (name, cat_type)
                    )

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def insert(self, query: str, params: Tuple = ()) -> int:
        """Execute INSERT and return lastrowid."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid

    def update(self, query: str, params: Tuple = ()) -> int:
        """Execute UPDATE/DELETE and return rowcount."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
