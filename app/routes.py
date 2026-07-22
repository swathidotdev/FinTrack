from flask import Blueprint, render_template, request, redirect, url_for, session
from app.models import (
    get_all_transactions, add_transaction, add_transactions_bulk,
    get_transactions_by_month, set_budget, get_budgets,
)
from app.auth import login_required
from project import categorize_transaction, parse_csv_import, calculate_monthly_total
from datetime import date as date_module
import os
import tempfile

bp = Blueprint("main", __name__)


@bp.route("/")
@login_required
def index():
    user_id = session.get("user_id")
    transactions = get_all_transactions(user_id)

    current_month = date_module.today().strftime("%Y-%m")
    month_transactions = get_transactions_by_month(user_id, current_month)

    month_total = calculate_monthly_total(month_transactions, current_month)

    category_totals = {}
    for t in month_transactions:
        category_totals[t["category"]] = category_totals.get(t["category"], 0) + t["amount"]
    category_totals = {cat: round(total, 2) for cat, total in category_totals.items()}

    # Compare spending against budgets to flag over-limit categories
    budgets = {b["category"]: b["monthly_limit"] for b in get_budgets(user_id)}
    budget_status = {}
    for category, limit in budgets.items():
        spent = category_totals.get(category, 0)
        budget_status[category] = {
            "limit": limit,
            "spent": spent,
            "over": spent > limit,
        }

    return render_template(
        "dashboard.html",
        transactions=transactions,
        current_month=current_month,
        month_total=month_total,
        category_totals=category_totals,
        budget_status=budget_status,
    )


@bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    user_id = session.get("user_id")
    if request.method == "POST":
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()
        amount_raw = request.form.get("amount", "").strip()

        if not date or not description or not amount_raw:
            return render_template("add_transaction.html", error="All fields are required.")

        try:
            amount = float(amount_raw)
        except ValueError:
            return render_template("add_transaction.html", error="Amount must be a number.")

        category = categorize_transaction(description)
        add_transaction(user_id, date, description, amount, category)

        return redirect(url_for("main.index"))

    return render_template("add_transaction.html", error=None)


@bp.route("/import", methods=["GET", "POST"])
@login_required
def import_csv():
    user_id = session.get("user_id")
    if request.method == "POST":
        file = request.files.get("csv_file")

        if not file or file.filename == "":
            return render_template("import_csv.html", error="Please choose a CSV file.")

        if not file.filename.lower().endswith(".csv"):
            return render_template("import_csv.html", error="File must be a .csv file.")

        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(temp_path)

        transactions = parse_csv_import(temp_path)
        os.remove(temp_path)

        if not transactions:
            return render_template("import_csv.html", error="No valid rows found in that CSV.")

        for t in transactions:
            t["category"] = categorize_transaction(t["description"])

        add_transactions_bulk(user_id, transactions)

        return redirect(url_for("main.index"))

    return render_template("import_csv.html", error=None)


@bp.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    user_id = session.get("user_id")
    if request.method == "POST":
        category = request.form.get("category", "").strip()
        limit_raw = request.form.get("monthly_limit", "").strip()

        if not category or not limit_raw:
            return render_template("budgets.html", error="Both fields are required.", budgets=get_budgets(user_id))

        try:
            limit = float(limit_raw)
        except ValueError:
            return render_template("budgets.html", error="Limit must be a number.", budgets=get_budgets(user_id))

        set_budget(user_id, category, limit)
        return redirect(url_for("main.budgets"))

    return render_template("budgets.html", error=None, budgets=get_budgets(user_id))