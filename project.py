import csv

from app import create_app


# Keyword -> category mapping used by categorize_transaction()
CATEGORY_KEYWORDS = {
    "Food": ["swiggy", "zomato", "restaurant", "cafe", "starbucks", "mcdonald"],
    "Transport": ["uber", "ola", "petrol", "fuel", "metro", "taxi"],
    "Groceries": ["bigbasket", "grofers", "supermarket", "grocery"],
    "Shopping": ["amazon", "flipkart", "myntra", "mall"],
    "Bills": ["electricity", "water bill", "internet", "recharge", "wifi"],
    "Rent": ["rent"],
    "Entertainment": ["netflix", "spotify", "movie", "prime video", "hotstar"],
}


def main():
    """Entry point. Starts the Flask web app."""
    app = create_app()
    app.run(debug=True)


def categorize_transaction(description):
    """Guess a spending category from a transaction description,
    using simple keyword matching. Returns 'Other' if no keyword matches.

    >>> categorize_transaction("UBER RIDE 12/07")
    'Transport'
    """
    if not description:
        return "Other"

    description_lower = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category

    return "Other"


def calculate_monthly_total(transactions, month):
    """Sum the amount of all transactions whose date falls in the given month.

    transactions: list of dicts, each with at least 'date' (YYYY-MM-DD) and 'amount' (float/str)
    month: string in 'YYYY-MM' format, e.g. '2026-07'

    Returns a float total. Returns 0.0 if no matches.
    """
    total = 0.0

    for t in transactions:
        date = t.get("date", "")
        if date.startswith(month):
            total += float(t.get("amount", 0))

    return round(total, 2)


def parse_csv_import(filepath):
    """Read a CSV file of transactions and return a list of dicts.

    Expected CSV columns: date,description,amount
    Rows with a missing date, description, or an invalid amount are skipped.

    Returns an empty list if the file doesn't exist or is empty.
    """
    transactions = []

    try:
        with open(filepath, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                date = row.get("date", "").strip()
                description = row.get("description", "").strip()
                amount_raw = row.get("amount", "").strip()

                if not date or not description or not amount_raw:
                    continue

                try:
                    amount = float(amount_raw)
                except ValueError:
                    continue

                transactions.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                })
    except FileNotFoundError:
        return []

    return transactions


if __name__ == "__main__":
    main()