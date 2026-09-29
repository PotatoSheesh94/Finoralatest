"""
Spending analysis service – pure Python aggregations used as input to the AI layer
and for dashboard statistics.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from database.db_manager import DatabaseManager
from models.transaction import Transaction
from services.transaction_service import TransactionService


class AnalysisService:
    """Computes spending summaries, category breakdowns, and period comparisons."""

    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
        self.tx_service = TransactionService(self.db)

    def get_summary(
        self,
        user_id: int,
        start_date: str = None,
        end_date: str = None,
    ) -> Dict:
        """Return total income, total expense, net, and transaction count."""
        transactions = self.tx_service.get_transactions(
            user_id=user_id, start_date=start_date, end_date=end_date, limit=10000
        )
        total_income = sum(t.amount for t in transactions if t.is_income())
        total_expense = sum(t.amount for t in transactions if t.is_expense())
        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net": round(total_income - total_expense, 2),
            "transaction_count": len(transactions),
            "start_date": start_date,
            "end_date": end_date,
        }

    def get_category_breakdown(
        self,
        user_id: int,
        start_date: str = None,
        end_date: str = None,
        trans_type: str = "expense",
    ) -> List[Dict]:
        """Return list of {category, amount, percentage} sorted by amount descending."""
        transactions = self.tx_service.get_transactions(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            trans_type=trans_type,
            limit=10000,
        )
        totals: Dict[str, float] = defaultdict(float)
        for t in transactions:
            name = t.category.name if t.category else "Uncategorized"
            totals[name] += t.amount

        grand_total = sum(totals.values()) or 1.0
        breakdown = [
            {
                "category": cat,
                "amount": round(amt, 2),
                "percentage": round(amt / grand_total * 100, 1),
            }
            for cat, amt in sorted(totals.items(), key=lambda x: x[1], reverse=True)
        ]
        return breakdown

    def get_monthly_trend(
        self, user_id: int, months: int = 6
    ) -> List[Dict]:
        """Return monthly income/expense aggregates for the last N months."""
        today = datetime.now()
        result = []
        for i in range(months - 1, -1, -1):
            # Approximate month start/end
            year = today.year
            month = today.month - i
            while month <= 0:
                month += 12
                year -= 1
            start = f"{year:04d}-{month:02d}-01"
            if month == 12:
                end = f"{year:04d}-12-31"
            else:
                next_m = month + 1
                end_dt = datetime(year, next_m, 1) - timedelta(days=1)
                end = end_dt.strftime("%Y-%m-%d")

            summary = self.get_summary(user_id, start, end)
            result.append({
                "period": f"{year:04d}-{month:02d}",
                "income": summary["total_income"],
                "expense": summary["total_expense"],
                "net": summary["net"],
            })
        return result

    def prepare_ai_context(
        self,
        user_id: int,
        start_date: str = None,
        end_date: str = None,
    ) -> str:
        """
        Build a textual summary of recent transactions and statistics
        suitable for sending to the Gemini API.
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        summary = self.get_summary(user_id, start_date, end_date)
        breakdown = self.get_category_breakdown(user_id, start_date, end_date, "expense")
        income_breakdown = self.get_category_breakdown(user_id, start_date, end_date, "income")
        transactions = self.tx_service.get_transactions(
            user_id=user_id, start_date=start_date, end_date=end_date, limit=50
        )

        lines = [
            f"Period: {start_date} to {end_date}",
            f"Total Income: {summary['total_income']:.2f}",
            f"Total Expenses: {summary['total_expense']:.2f}",
            f"Net: {summary['net']:.2f}",
            f"Number of transactions: {summary['transaction_count']}",
            "",
            "Expense breakdown by category:",
        ]
        for item in breakdown[:15]:
            lines.append(f"  - {item['category']}: {item['amount']:.2f} ({item['percentage']}%)")

        lines.append("")
        lines.append("Income sources:")
        for item in income_breakdown[:10]:
            lines.append(f"  - {item['category']}: {item['amount']:.2f}")

        lines.append("")
        lines.append("Recent transactions (up to 30):")
        for t in transactions[:30]:
            sign = "-" if t.is_expense() else "+"
            cat = t.category.name if t.category else "?"
            lines.append(
                f"  {t.transaction_date} | {sign}{t.amount:.2f} | {cat} | {t.description}"
            )

        return "\n".join(lines)
