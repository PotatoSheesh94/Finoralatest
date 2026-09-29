"""Finora – Smart Personal Finance Management System with AI-Assisted Spending Analysis."""

import os
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

from config import (
    SECRET_KEY,
    APP_TITLE,
    APP_VERSION,
    DATABASE_PATH,
    PROJECT_TITLE,
    APP_DESCRIPTION,
    TAGLINE,
    LEADER,
    TEAM_MEMBERS,
    PROFESSOR,
)
from database.db_manager import DatabaseManager
from services.auth_service import AuthService
from services.transaction_service import TransactionService
from services.analysis_service import AnalysisService
from services.ai_service import AIService
from models.transaction import Transaction
from models.budget import Budget
from models.category import Category
from utils.validators import validate_amount, validate_date, validate_non_empty
from utils.helpers import today_str, first_day_of_month, last_n_days, format_currency


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Initialize database on startup
    DatabaseManager()

    # ---------- Auth decorator ----------
    def login_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated

    def get_current_user():
        if "user_id" not in session:
            return None
        auth = AuthService()
        return auth.get_user_by_id(session["user_id"])

    # ---------- Context processor (available in all templates) ----------
    @app.context_processor
    def inject_globals():
        user = get_current_user()
        summary = None
        if user:
            try:
                analysis = AnalysisService()
                summary = analysis.get_summary(user.id, first_day_of_month(), today_str())
            except Exception:
                summary = None
        return {
            "app_title": APP_TITLE,
            "app_version": APP_VERSION,
            "project_title": PROJECT_TITLE,
            "app_description": APP_DESCRIPTION,
            "tagline": TAGLINE,
            "leader": LEADER,
            "team_members": TEAM_MEMBERS,
            "professor": PROFESSOR,
            "current_user": user,
            "month_summary": summary,
            "format_currency": format_currency,
        }

    # ---------- Auth routes ----------
    @app.route("/")
    def index():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            try:
                user = AuthService().login(username, password)
                session["user_id"] = user.id
                session["username"] = user.username
                session["full_name"] = user.full_name
                flash(f"Welcome back, {user.full_name}!", "success")
                return redirect(url_for("dashboard"))
            except ValueError as e:
                flash(str(e), "danger")
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            try:
                user = AuthService().register(username, password, full_name, email)
                flash("Account created successfully. Please log in.", "success")
                return redirect(url_for("login"))
            except ValueError as e:
                flash(str(e), "danger")
        return render_template("register.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    @app.route("/credits")
    def credits():
        return render_template("credits.html")

    # ---------- Dashboard ----------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = get_current_user()
        analysis = AnalysisService()
        tx_service = TransactionService()
        summary = analysis.get_summary(user.id, first_day_of_month(), today_str())
        recent = tx_service.get_transactions(user.id, limit=8)
        breakdown = analysis.get_category_breakdown(user.id, first_day_of_month(), today_str(), "expense")
        return render_template(
            "dashboard.html",
            summary=summary,
            recent_transactions=recent,
            breakdown=breakdown[:6],
        )

    # ---------- Transactions ----------
    @app.route("/transactions")
    @login_required
    def transactions():
        user = get_current_user()
        service = TransactionService()
        start = request.args.get("start") or None
        end = request.args.get("end") or None
        ttype = request.args.get("type") or None
        search = request.args.get("search") or None
        if ttype == "all":
            ttype = None
        txs = service.get_transactions(
            user_id=user.id, start_date=start, end_date=end,
            trans_type=ttype, search=search
        )
        return render_template(
            "transactions.html",
            transactions=txs,
            filters={"start": start or "", "end": end or "", "type": ttype or "all", "search": search or ""},
        )

    @app.route("/transactions/add", methods=["GET", "POST"])
    @login_required
    def add_transaction():
        user = get_current_user()
        service = TransactionService()
        categories = service.get_categories(user.id)
        if request.method == "POST":
            try:
                amount = validate_amount(request.form.get("amount", ""))
                date = validate_date(request.form.get("transaction_date", ""))
                cat_id = int(request.form.get("category_id"))
                trans_type = request.form.get("type")
                description = request.form.get("description", "").strip()
                # Validate category belongs to type
                cats = {c.id: c for c in categories}
                if cat_id not in cats:
                    raise ValueError("Invalid category.")
                cat = cats[cat_id]
                if cat.type != trans_type:
                    # Allow but warn – or force match
                    pass
                tx = Transaction(
                    user_id=user.id,
                    category_id=cat_id,
                    amount=amount,
                    trans_type=trans_type,
                    description=description,
                    transaction_date=date,
                    category=cat,
                )
                service.add_transaction(tx)
                flash("Transaction added successfully.", "success")
                return redirect(url_for("transactions"))
            except (ValueError, TypeError) as e:
                flash(str(e), "danger")
        return render_template(
            "transaction_form.html",
            categories=categories,
            transaction=None,
            today=today_str(),
        )

    @app.route("/transactions/<int:tx_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_transaction(tx_id):
        user = get_current_user()
        service = TransactionService()
        tx = service.get_transaction_by_id(tx_id, user.id)
        if not tx:
            flash("Transaction not found.", "danger")
            return redirect(url_for("transactions"))
        categories = service.get_categories(user.id)
        if request.method == "POST":
            try:
                amount = validate_amount(request.form.get("amount", ""))
                date = validate_date(request.form.get("transaction_date", ""))
                cat_id = int(request.form.get("category_id"))
                trans_type = request.form.get("type")
                description = request.form.get("description", "").strip()
                cats = {c.id: c for c in categories}
                cat = cats.get(cat_id)
                tx.amount = amount
                tx.transaction_date = date
                tx.description = description
                tx._type = trans_type
                if cat:
                    tx.category = cat
                service.update_transaction(tx)
                flash("Transaction updated.", "success")
                return redirect(url_for("transactions"))
            except (ValueError, TypeError) as e:
                flash(str(e), "danger")
        return render_template(
            "transaction_form.html",
            categories=categories,
            transaction=tx,
            today=today_str(),
        )

    @app.route("/transactions/<int:tx_id>/delete", methods=["POST"])
    @login_required
    def delete_transaction(tx_id):
        user = get_current_user()
        service = TransactionService()
        if service.delete_transaction(tx_id, user.id):
            flash("Transaction deleted.", "success")
        else:
            flash("Could not delete transaction.", "danger")
        return redirect(url_for("transactions"))

    # ---------- Reports ----------
    @app.route("/reports")
    @login_required
    def reports():
        user = get_current_user()
        analysis = AnalysisService()
        period = request.args.get("period", "this_month")
        if period == "this_month":
            start, end = first_day_of_month(), today_str()
        elif period == "30":
            start, end = last_n_days(30)
        elif period == "90":
            start, end = last_n_days(90)
        else:
            start, end = None, None
        summary = analysis.get_summary(user.id, start, end)
        expense_bd = analysis.get_category_breakdown(user.id, start, end, "expense")
        income_bd = analysis.get_category_breakdown(user.id, start, end, "income")
        trend = analysis.get_monthly_trend(user.id, months=6)
        return render_template(
            "reports.html",
            summary=summary,
            expense_breakdown=expense_bd,
            income_breakdown=income_bd,
            trend=trend,
            period=period,
        )

    # ---------- AI Assistant ----------
    @app.route("/ai", methods=["GET", "POST"])
    @login_required
    def ai_assistant():
        user = get_current_user()
        ai = AIService()
        result = None
        action = None
        period = request.form.get("period") or request.args.get("period") or "90"
        if period == "this_month":
            start, end = first_day_of_month(), today_str()
        elif period == "30":
            start, end = last_n_days(30)
        elif period == "90":
            start, end = last_n_days(90)
        else:
            start, end = None, None

        if request.method == "POST":
            action = request.form.get("action")
            if not ai.is_available:
                flash("Google Gemini API key is not configured. Set GOOGLE_AI_API_KEY in the app secrets.", "warning")
            else:
                try:
                    if action == "summarize":
                        result = ai.summarize_spending(user.id, start, end)
                    elif action == "budget":
                        result = ai.suggest_budget(user.id, start, end)
                    elif action == "ask":
                        question = request.form.get("question", "").strip()
                        if not question:
                            flash("Please enter a question.", "warning")
                        else:
                            result = ai.ask_question(user.id, question, start, end)
                except Exception as e:
                    result = f"Error contacting AI service: {e}"

        return render_template(
            "ai_assistant.html",
            result=result,
            action=action,
            period=period,
            ai_available=ai.is_available,
        )

    # ---------- Budgets ----------
    @app.route("/budgets")
    @login_required
    def budgets():
        user = get_current_user()
        service = TransactionService()
        budget_list = service.get_budgets(user.id)
        return render_template("budgets.html", budgets=budget_list)

    @app.route("/budgets/add", methods=["GET", "POST"])
    @login_required
    def add_budget():
        user = get_current_user()
        service = TransactionService()
        categories = service.get_categories(user.id, cat_type="expense")
        if request.method == "POST":
            try:
                amount = validate_amount(request.form.get("amount", ""))
                start = validate_date(request.form.get("start_date", ""))
                period = request.form.get("period", "monthly")
                notes = request.form.get("notes", "").strip()
                cat_id_raw = request.form.get("category_id")
                cat_id = int(cat_id_raw) if cat_id_raw and cat_id_raw != "0" else None
                category = None
                if cat_id:
                    for c in categories:
                        if c.id == cat_id:
                            category = c
                            break
                budget = Budget(
                    user_id=user.id,
                    amount=amount,
                    period=period,
                    start_date=start,
                    category_id=cat_id,
                    notes=notes,
                    category=category,
                )
                service.add_budget(budget)
                flash("Budget created.", "success")
                return redirect(url_for("budgets"))
            except (ValueError, TypeError) as e:
                flash(str(e), "danger")
        return render_template(
            "budget_form.html",
            categories=categories,
            today=today_str(),
        )

    @app.route("/budgets/<int:budget_id>/delete", methods=["POST"])
    @login_required
    def delete_budget(budget_id):
        user = get_current_user()
        service = TransactionService()
        if service.delete_budget(budget_id, user.id):
            flash("Budget deleted.", "success")
        else:
            flash("Could not delete budget.", "danger")
        return redirect(url_for("budgets"))

    return app


app = create_app()

if __name__ == "__main__":
    # host=0.0.0.0 allows access from other devices on the same network (useful for mobile testing)
    app.run(
        debug=os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"},
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
