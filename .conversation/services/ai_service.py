"""
AI-Assisted Spending Analysis service using the OpenAI (ChatGPT) API.
Provides summarization of spending patterns and budgeting suggestions.
"""

import os
from typing import Optional

from database.db_manager import DatabaseManager
from services.analysis_service import AnalysisService

# Attempt to load dotenv if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIService:
    """
    Integrates OpenAI Chat Completions for:
    - Spending pattern summarization
    - Budgeting suggestions
    - General finance-related Q&A based on user data
    """

    SYSTEM_PROMPT = (
        "You are a professional personal finance advisor. "
        "Analyze the provided transaction data carefully. "
        "Give clear, actionable, and realistic advice. "
        "Be concise yet thorough. Use bullet points where helpful. "
        "Never invent transactions that are not in the data. "
        "Currency is Philippine Peso (PHP) unless stated otherwise. "
        "Focus on patterns, potential overspending areas, and practical budgeting recommendations."
    )

    def __init__(self, db: DatabaseManager = None, api_key: str = None):
        self.db = db or DatabaseManager()
        self.analysis = AnalysisService(self.db)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None

        if self.api_key and OPENAI_AVAILABLE:
            self._client = OpenAI(api_key=self.api_key)

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def _call_openai(self, user_message: str, max_tokens: int = 1200) -> str:
        if not self._client:
            return (
                "AI service is not configured. Please set the OPENAI_API_KEY environment variable "
                "or create a .env file containing OPENAI_API_KEY=sk-..."
            )
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=max_tokens,
                temperature=0.4,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return f"AI request failed: {str(exc)}"

    def summarize_spending(
        self,
        user_id: int,
        start_date: str = None,
        end_date: str = None,
    ) -> str:
        """Generate a natural-language summary of spending patterns."""
        context = self.analysis.prepare_ai_context(user_id, start_date, end_date)
        prompt = (
            "Based on the following personal finance data, provide a clear summary of "
            "the user's spending patterns. Highlight the largest expense categories, "
            "any notable trends, and overall financial health for the period.\n\n"
            f"{context}"
        )
        result = self._call_openai(prompt)
        self._log_analysis(user_id, "summarize_spending", context[:500], result)
        return result

    def suggest_budget(
        self,
        user_id: int,
        start_date: str = None,
        end_date: str = None,
    ) -> str:
        """Generate budgeting suggestions based on historical spending."""
        context = self.analysis.prepare_ai_context(user_id, start_date, end_date)
        prompt = (
            "Based on the following personal finance data, provide practical budgeting "
            "suggestions. Recommend realistic monthly limits for major expense categories, "
            "identify areas where the user can reduce spending, and suggest a simple "
            "savings target. Keep advice actionable and proportional to the actual income "
            "and expense levels shown.\n\n"
            f"{context}"
        )
        result = self._call_openai(prompt)
        self._log_analysis(user_id, "suggest_budget", context[:500], result)
        return result

    def ask_question(
        self,
        user_id: int,
        question: str,
        start_date: str = None,
        end_date: str = None,
    ) -> str:
        """Answer a free-form finance question using the user's transaction context."""
        context = self.analysis.prepare_ai_context(user_id, start_date, end_date)
        prompt = (
            f"User question: {question}\n\n"
            "Answer the question using only the data below. If the data is insufficient, "
            "say so clearly.\n\n"
            f"{context}"
        )
        result = self._call_openai(prompt)
        self._log_analysis(user_id, "ask_question", question, result)
        return result

    def _log_analysis(
        self, user_id: int, request_type: str, input_summary: str, response_text: str
    ) -> None:
        try:
            self.db.insert(
                """INSERT INTO ai_analysis_log
                   (user_id, request_type, input_summary, response_text)
                   VALUES (?, ?, ?, ?)""",
                (user_id, request_type, input_summary[:1000], response_text[:4000]),
            )
        except Exception:
            pass  # logging failure should not break the main flow
