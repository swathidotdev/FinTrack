from app.db import get_db


def add_transaction(user_id, date, description, amount, category):
    """Insert a single transaction. Returns the new row's id."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (user_id, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
        (user_id, date, description, amount, category),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def add_transactions_bulk(user_id, transactions):
    """Insert many transactions at once, e.g. from a CSV import.
    Each item in `transactions` must be a dict with date, description, amount, category."""
    conn = get_db()
    cursor = conn.cursor()
    for t in transactions:
        cursor.execute(
            "INSERT INTO transactions (user_id, date, description, amount, category) VALUES (?, ?, ?, ?, ?)",
            (user_id, t["date"], t["description"], t["amount"], t["category"]),
        )
    conn.commit()
    conn.close()


def get_all_transactions(user_id):
    """Return transactions for a specific user, most recent first, as a list of dicts."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_transactions_by_month(user_id, month):
    """Return transactions for a user whose date starts with the given 'YYYY-MM' string."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE user_id = ? AND date LIKE ? ORDER BY date",
        (user_id, f"{month}%"),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def set_budget(user_id, category, monthly_limit):
    """Create or update the monthly budget limit for a category."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO budgets (user_id, category, monthly_limit)
           VALUES (?, ?, ?)""",
        (user_id, category, monthly_limit),
    )
    conn.commit()
    conn.close()


def get_budgets(user_id):
    """Return all budgets for a user as a list of dicts."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM budgets WHERE user_id = ?",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]