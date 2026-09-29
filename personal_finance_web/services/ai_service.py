"""
AI-assisted spending analysis service using Google's Gemini API.
Provides spending analysis, budgeting suggestions, and open-ended answers.
"""

import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from database.db_manager import DatabaseManager
from services.analysis_service import AnalysisService

# Attempt to load dotenv if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class AIService:
    """
    Integrates Google's Gemini generateContent API for:
    - Spending pattern summarization
    - Budgeting suggestions
    - Open-ended questions, using user data when relevant
    """

    SYSTEM_PROMPT = (
        "You are a helpful general-purpose AI assistant with strong personal finance expertise. "
        "Answer the user's actual question directly, whether it is about personal finance or "
        "a general topic. "
        "When transaction data is provided and relevant, use it carefully. "
        "Give clear, actionable, and realistic advice for finance questions. "
        "Be concise yet thorough. Use bullet points where helpful. "
        "Never invent transactions that are not in the data. "
        "Currency is Philippine Peso (PHP) unless stated otherwise. "
        "Do not force unrelated questions into budgeting or spending analysis."
    )

    def __init__(self, db: DatabaseManager = None, api_key: str = None):
        self.db = db or DatabaseManager()
        self.analysis = AnalysisService(self.db)
        self.api_key = (
            api_key
            or os.getenv("GOOGLE_AI_API_KEY", "")
            or os.getenv("GEMINI_API_KEY", "")
        )
        self.model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def _call_gemini(self, user_message: str, max_output_tokens: int = 8192) -> str:
        if not self.api_key:
            return (
                "AI service is not configured. Please set the GOOGLE_AI_API_KEY "
                "environment variable and restart the app."
            )

        payload = {
            "systemInstruction": {
                "parts": [{"text": self.SYSTEM_PROMPT}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_message}],
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": max_output_tokens,
            },
        }
        request = Request(
            f"{self.endpoint}?key={self.api_key}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        for attempt in range(3):
            try:
                with urlopen(request, timeout=45) as response:
                    response_data = json.loads(response.read().decode("utf-8"))
                break
            except HTTPError as exc:
                try:
                    error_data = json.loads(exc.read().decode("utf-8"))
                    error_message = error_data.get("error", {}).get("message", "request rejected")
                except (json.JSONDecodeError, UnicodeDecodeError):
                    error_message = "request rejected"
                if exc.code in {429, 500, 502, 503, 504} and attempt < 2:
                    time.sleep(2**attempt)
                    continue
                return f"Gemini request failed: {error_message}"
            except URLError:
                if attempt < 2:
                    time.sleep(2**attempt)
                    continue
                return "Gemini request failed: the service could not be reached."
            except (TimeoutError, json.JSONDecodeError):
                if attempt < 2:
                    time.sleep(2**attempt)
                    continue
                return "Gemini request failed: the response was invalid or timed out."
            except Exception:
                return "Gemini request failed unexpectedly. Please try again."

        candidates = response_data.get("candidates", [])
        if not candidates:
            return "Gemini returned no answer for this request."

        parts = candidates[0].get("content", {}).get("parts", [])
        answer = "".join(part.get("text", "") for part in parts).strip()
        return answer or "Gemini returned an empty answer."

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
        result = self._call_gemini(prompt)
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
        result = self._call_gemini(prompt)
        self._log_analysis(user_id, "suggest_budget", context[:500], result)
        return result

    def ask_question(
        self,
        user_id: int,
        question: str,
        start_date: str = None,
        end_date: str = None,
    ) -> str:
        """Answer an open-ended question, using the user's transaction context when relevant."""
        context = self.analysis.prepare_ai_context(user_id, start_date, end_date)
        prompt = (
            f"User question: {question}\n\n"
            "Answer this question directly and naturally. If it relates to the user's "
            "personal finances, use the transaction context below. If it is a general "
            "question, answer from general knowledge and do not force a budgeting answer. "
            "Do not pretend the transaction data contains facts it does not contain.\n\n"
            f"{context}"
        )
        result = self._call_gemini(prompt)
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
