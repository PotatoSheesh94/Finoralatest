# Smart Personal Finance Management System

A mobile-friendly Flask app for tracking income, expenses, budgets, reports, and AI-assisted spending analysis.

## Run & Operate

- `python main.py` — run the personal finance web app (port 5000)
- `python -m compileall personal_finance_web` — check Python syntax
- `pnpm run typecheck` — full typecheck for the workspace libraries
- Required secret: `OPENAI_API_KEY` — enables the AI Spending Assistant

## Stack

- Python 3.11, Flask, SQLite
- OpenAI Python SDK for AI-assisted spending analysis
- Jinja templates and responsive CSS

## Where things live

- `personal_finance_web/app.py` — Flask routes and application factory
- `personal_finance_web/database/` — SQLite schema and access
- `personal_finance_web/models/` — domain models
- `personal_finance_web/services/` — authentication, transactions, reporting, and AI services
- `personal_finance_web/templates/` and `personal_finance_web/static/` — UI

## Architecture decisions

- SQLite remains the app's local persistence layer from the imported project.
- The AI assistant reads the user's finance context and never receives a raw API key from the browser.
- Replit's `SESSION_SECRET` is used as the Flask session key unless `SECRET_KEY` is explicitly set.

## Product

- Account registration and session login
- Transaction and budget management
- Monthly dashboard and reporting
- AI-powered spending summaries, budgeting suggestions, and finance Q&A

## Gotchas

- The AI tab works only after `OPENAI_API_KEY` is configured.
- The workflow is named `Personal Finance App` and runs `cd personal_finance_web && python app.py`.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
