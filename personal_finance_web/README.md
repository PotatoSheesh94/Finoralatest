# Finora (Web Edition)
## Python OOP + Flask + AI-Assisted Spending Analysis

**Title:** Final Project In OOP & Discrete Structure  
**Description:** Smart Personal Finance Management System with AI-Assisted Spending Analysis  
**Tagline:** “Understand your money. Decide smarter.”

---

### Why Web Version?

This edition replaces the original Tkinter desktop GUI with a **responsive Flask web application**.  
You can develop, run, and demonstrate the system entirely from a mobile browser (via Replit, PythonAnywhere, Termux, or any device with a browser).

All core OOP requirements, SQLite database, business logic, and the mandatory AI feature remain identical.

---

### Features

- User registration & login (session-based)
- Full transaction CRUD with filters
- Category management (default + custom)
- Budget setting
- Dashboard with live monthly summary
- Reports: totals, category breakdown, monthly trend
- **Finora AI** (Google Gemini API)
  - Summarize spending patterns
  - Budgeting suggestions
  - Free-form finance questions
- Fully responsive (works on phones)
- Project credits page with team and professor details

---

### Project Structure (OOP Layers Preserved)

```
personal_finance_web/
├── app.py                  # Flask application & routes
├── config.py
├── requirements.txt
├── README.md
├── database/
│   └── db_manager.py       # SQLite schema & access
├── models/                 # Domain entities (inheritance, encapsulation…)
│   ├── base.py
│   ├── user.py
│   ├── category.py
│   ├── transaction.py
│   └── budget.py
├── services/               # Business logic
│   ├── auth_service.py
│   ├── transaction_service.py
│   ├── analysis_service.py
│   └── ai_service.py       # Google Gemini integration
├── utils/
├── templates/              # Mobile-friendly HTML
└── static/style.css
```

### OOP Concepts Demonstrated

| Concept            | Where                                      |
|--------------------|--------------------------------------------|
| Classes & Objects  | User, Transaction, Category, Budget, Services |
| Encapsulation      | `@property` getters/setters                |
| Inheritance        | `BaseEntity` → all domain models           |
| Polymorphism       | Overridden `to_dict()`, `__str__()`        |
| Composition        | Transaction holds Category                 |
| Constructors       | Validated `__init__`                       |
| Exception Handling | Validation, DB, API errors                 |
| Modular Design     | models / services / templates separation   |

---

### Setup (Mobile-Friendly Options)

#### Option A – Replit (easiest from phone)
1. Create a new Replit (Python).
2. Upload the project files (or clone).
3. In Secrets / Environment add `GOOGLE_AI_API_KEY`.
4. Run: `pip install -r requirements.txt && python app.py`
5. Open the webview / published URL on your phone.

#### Option B – Local / Termux
```bash
cd personal_finance_web
pip install -r requirements.txt
# create .env with your GOOGLE_AI_API_KEY
python app.py
```
Then open `http://localhost:5000` (or the device IP) in your mobile browser.

#### Option C – PythonAnywhere
Upload the folder, set the WSGI file to point to `app.py`, add the API key in Environment variables.

---

### Environment Variables

Create a `.env` file (or set secrets):

```
GOOGLE_AI_API_KEY=your-google-ai-key
GEMINI_MODEL=gemini-3-flash-preview
SECRET_KEY=any-random-string
```

Without the Google AI key the rest of the system still works; only the AI tab will show a warning.

---

### Defense Demo Flow

1. Register / Login on your phone browser.
2. Add several income & expense transactions.
3. Show Dashboard summary cards.
4. Open Transactions → filter / edit / delete.
5. Open Reports → switch periods, show breakdown.
6. Open **Finora AI**:
   - Summarize Spending Patterns
   - Get Budgeting Suggestions
   - Ask a custom question
7. Explain classes, inheritance, encapsulation, and how the AI feature receives data and returns advice.

---

### Important Notes

- The system is **more than CRUD** – it includes analysis, budgeting, and AI decision support.
- All monetary values use Philippine Peso (₱) formatting by default.
- The AI feature is connected to real transaction data and is fully demonstrable when an API key is present.

### Credits

- **Leader:** Harvy Aguilar
- **Members:** Shiemar Maravilla, Formanes Chene, Daniela Diamos, Hanna Nicole
- **Professor:** Mr. Villanueva

