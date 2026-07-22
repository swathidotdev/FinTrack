# FinTech — A Personal Budget Tracker
#### Video Demo: <YOUR YOUTUBE URL HERE>
#### Description:

FinTech is a multi-user web application for tracking personal expenses,
built with Python, Flask, and SQLite. Each user creates an account, logs
in, and gets their own private space to record transactions, import
spending history in bulk from a CSV file, view monthly totals broken down
by category, and set budget limits that trigger a warning when exceeded.

I built this because most budgeting tools are either too heavyweight
(linking real bank accounts, monthly subscriptions) or too manual (a bare
spreadsheet where every transaction has to be typed and categorized by
hand). FinTech sits in between: it automates the tedious part — guessing
a transaction's category from its description — while keeping all data
local, free, and under the user's control in a single SQLite file.

## How it works

A user signs up with a username, email, and password; the password is
hashed with Werkzeug's `generate_password_hash` before it's ever written
to disk, and every route that touches personal data is protected by a
`login_required` decorator that redirects anonymous visitors to the login
page. Once logged in, all of a user's transactions and budgets are scoped
to their `user_id`, so multiple people can use the same running instance
of the app without ever seeing each other's data.

When a transaction is added — either one at a time through the "Add" form,
or in bulk through CSV import — its description is passed through
`categorize_transaction()`, which matches keywords (like "uber" or
"swiggy") against a dictionary of category keywords and assigns a category
automatically, so the user rarely has to categorize anything by hand.

The dashboard pulls the current month's transactions, calculates a running
total with `calculate_monthly_total()`, groups spending by category for
the chart and table, and compares each category's total against any budget
limit the user has set. If a category goes over its limit, a warning
banner appears listing exactly how much they've overspent.

## File structure

- **`project.py`** — Contains `main()`, which starts the Flask server, and
  the three core functions required by CS50: `categorize_transaction()`,
  `calculate_monthly_total()`, and `parse_csv_import()`. These are kept
  free of any database or Flask dependency — pure functions that take data
  in and return data out — specifically so they can be unit tested in
  complete isolation from the rest of the app.
- **`test_project.py`** — pytest tests for the three functions above,
  using hardcoded sample data and pytest's `tmp_path` fixture to test CSV
  parsing without needing a real file on disk.
- **`app/__init__.py`** — The Flask application factory (`create_app()`),
  which sets a secret key for sessions, initializes the database, and
  registers both the main blueprint and the auth blueprint.
- **`app/db.py`** — Database connection helper and `init_db()`, which
  creates the `users`, `transactions`, and `budgets` tables if they don't
  already exist.
- **`app/models.py`** — All transaction/budget database access functions
  (`add_transaction`, `get_all_transactions`, `get_transactions_by_month`,
  `set_budget`, `get_budgets`), every one of them scoped by `user_id` so
  data stays private per account.
- **`app/auth.py`** — Authentication logic: `register_user()` and
  `login_user()` (which hash/verify passwords and talk to the database
  directly), plus the `login_required` decorator used to protect routes.
- **`app/auth_routes.py`** — The `/signup`, `/login`, and `/logout` routes.
- **`app/routes.py`** — The main app routes: dashboard (`/`), add
  transaction (`/add`), CSV import (`/import`), and budget management
  (`/budgets`) — all protected by `login_required`.
- **`app/templates/`** — Jinja2 HTML templates for every page, including
  dedicated `login.html` and `signup.html` pages.
- **`app/static/style.css`** — Custom styling (no external CSS framework):
  a card-based dashboard layout with a blue gradient top bar, pill-style
  navigation, and category badges.
- **`sample_data/sample_transactions.csv`** — Example data for testing the
  import feature and recording the demo video.

## Design decisions

I chose to keep `categorize_transaction()`, `calculate_monthly_total()`,
and `parse_csv_import()` completely free of Flask or database code. This
was a deliberate constraint: CS50 requires these to live at the top level
of `project.py` and be independently testable, so the web app is built as
a thin layer on top of them rather than the other way around — the same
three functions work identically whether they're called from a route, a
script, or a pytest test.

Authentication was added after the initial single-user version, which
meant retrofitting `user_id` onto both the `transactions` and `budgets`
tables and updating every model function to filter by it. I used Flask's
built-in `session` to store the logged-in user's ID rather than a separate
sessions table, since the app doesn't need persistent "remember me" login
across browser restarts for this scope.

For CSV imports, the uploaded file is temporarily saved to disk before
parsing, since `parse_csv_import()` expects a filepath rather than an
in-memory stream. This let me reuse the exact same tested function for
both the CLI/test path and the web upload path instead of maintaining two
separate parsers.

## Known limitations / future improvements

Category keyword matching is simple substring matching rather than
ML-based classification — it works well for common merchants but can
misclassify unfamiliar ones. A natural next step would be letting a user
correct a miscategorized transaction and have the app remember that
correction for next time. There's currently no password reset flow or
email verification, which would be needed before this could be used by
real strangers rather than as a personal/demo tool.