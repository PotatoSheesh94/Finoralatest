"""
Transaction and Category management service.
Implements CRUD and higher-level business operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from database.db_manager import DatabaseManager
from models.category import Category
from models.transaction import Transaction
from models.budget import Budget


class TransactionService:
    """Business logic for transactions, categories, and budgets."""

    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()

    # ---------- Categories ----------
    def get_categories(self, user_id: int, cat_type: str = None) -> List[Category]:
        if cat_type:
            rows = self.db.fetch_all(
                """SELECT * FROM categories
                   WHERE (user_id = ? OR is_default = 1) AND type = ?
                   ORDER BY name""",
                (user_id, cat_type),
            )
        else:
            rows = self.db.fetch_all(
                """SELECT * FROM categories
                   WHERE user_id = ? OR is_default = 1
                   ORDER BY type, name""",
                (user_id,),
            )
        return [
            Category(
                name=r["name"],
                cat_type=r["type"],
                user_id=r["user_id"],
                is_default=bool(r["is_default"]),
                entity_id=r["id"],
            )
            for r in rows
        ]

    def add_category(self, user_id: int, name: str, cat_type: str) -> Category:
        cat = Category(name=name, cat_type=cat_type, user_id=user_id)
        cat_id = self.db.insert(
            "INSERT INTO categories (name, type, user_id, is_default) VALUES (?, ?, ?, 0)",
            (cat.name, cat.type, user_id),
        )
        cat.id = cat_id
        return cat

    # ---------- Transactions ----------
    def add_transaction(self, transaction: Transaction) -> Transaction:
        tid = self.db.insert(
            """INSERT INTO transactions
               (user_id, category_id, amount, type, description, transaction_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                transaction.user_id,
                transaction.category_id,
                transaction.amount,
                transaction.type,
                transaction.description,
                transaction.transaction_date,
            ),
        )
        transaction.id = tid
        return transaction

    def update_transaction(self, transaction: Transaction) -> None:
        self.db.update(
            """UPDATE transactions
               SET category_id=?, amount=?, type=?, description=?, transaction_date=?
               WHERE id=? AND user_id=?""",
            (
                transaction.category_id,
                transaction.amount,
                transaction.type,
                transaction.description,
                transaction.transaction_date,
                transaction.id,
                transaction.user_id,
            ),
        )

    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        return self.db.update(
            "DELETE FROM transactions WHERE id=? AND user_id=?",
            (transaction_id, user_id),
        ) > 0

    def get_transactions(
        self,
        user_id: int,
        start_date: str = None,
        end_date: str = None,
        trans_type: str = None,
        category_id: int = None,
        search: str = None,
        limit: int = 500,
    ) -> List[Transaction]:
        query = """
            SELECT t.*, c.name AS category_name, c.type AS category_type
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
        """
        params: list = [user_id]

        if start_date:
            query += " AND t.transaction_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND t.transaction_date <= ?"
            params.append(end_date)
        if trans_type:
            query += " AND t.type = ?"
            params.append(trans_type)
        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)
        if search:
            query += " AND (t.description LIKE ? OR c.name LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY t.transaction_date DESC, t.id DESC LIMIT ?"
        params.append(limit)

        rows = self.db.fetch_all(query, tuple(params))
        result = []
        for r in rows:
            cat = Category(
                name=r["category_name"],
                cat_type=r["category_type"],
                entity_id=r["category_id"],
            )
            t = Transaction(
                user_id=r["user_id"],
                category_id=r["category_id"],
                amount=r["amount"],
                trans_type=r["type"],
                description=r["description"] or "",
                transaction_date=r["transaction_date"],
                entity_id=r["id"],
                category=cat,
            )
            result.append(t)
        return result

    def get_transaction_by_id(self, transaction_id: int, user_id: int) -> Optional[Transaction]:
        rows = self.get_transactions(user_id=user_id, limit=10000)
        for t in rows:
            if t.id == transaction_id:
                return t
        return None

    # ---------- Budgets ----------
    def add_budget(self, budget: Budget) -> Budget:
        bid = self.db.insert(
            """INSERT INTO budgets
               (user_id, category_id, amount, period, start_date, end_date, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                budget.user_id,
                budget.category_id,
                budget.amount,
                budget.period,
                budget.start_date,
                budget.end_date,
                budget.notes,
            ),
        )
        budget.id = bid
        return budget

    def get_budgets(self, user_id: int) -> List[Budget]:
        rows = self.db.fetch_all(
            """SELECT b.*, c.name AS category_name, c.type AS category_type
               FROM budgets b
               LEFT JOIN categories c ON b.category_id = c.id
               WHERE b.user_id = ?
               ORDER BY b.start_date DESC""",
            (user_id,),
        )
        result = []
        for r in rows:
            cat = None
            if r["category_id"]:
                cat = Category(
                    name=r["category_name"] or "Unknown",
                    cat_type=r["category_type"] or "expense",
                    entity_id=r["category_id"],
                )
            b = Budget(
                user_id=r["user_id"],
                amount=r["amount"],
                period=r["period"],
                start_date=r["start_date"],
                category_id=r["category_id"],
                end_date=r["end_date"],
                notes=r["notes"] or "",
                entity_id=r["id"],
                category=cat,
            )
            result.append(b)
        return result

    def delete_budget(self, budget_id: int, user_id: int) -> bool:
        return self.db.update(
            "DELETE FROM budgets WHERE id=? AND user_id=?",
            (budget_id, user_id),
        ) > 0
