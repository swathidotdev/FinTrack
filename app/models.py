from app.db import get_db


def add_transaction(date, description, amount, category):
    """Insert a single transaction. Returns the new row's id."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
        (date, description, amount, category),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def add_transactions_bulk(transactions):
    """Insert many transactions at once, e.g. from a CSV import.
    Each item in `transactions` must be a dict with date, description, amount, category."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO transactions (date, description, amount, category) VALUES (:date, :description, :amount, :category)",
        transactions,
    )
    conn.commit()
    conn.close()


def get_all_transactions():
    """Return every transaction, most recent first, as a list of dicts."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM transactions ORDER BY date DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_transactions_by_month(month):
    """Return transactions whose date starts with the given 'YYYY-MM' string."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE date LIKE ? ORDER BY date",
        (f"{month}%",),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def set_budget(category, monthly_limit):
    """Create or update the monthly budget limit for a category."""
    conn = get_db()
    conn.execute(
        """INSERT INTO budgets (category, monthly_limit) VALUES (?, ?)
           ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit""",
        (category, monthly_limit),
    )
    conn.commit()
    conn.close()


def get_budgets():
    """Return all budgets as a list of dicts."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM budgets").fetchall()
    conn.close()
    return [dict(row) for row in rows]