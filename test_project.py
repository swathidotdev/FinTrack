from project import categorize_transaction, calculate_monthly_total, parse_csv_import


def test_categorize_transaction():
    assert categorize_transaction("UBER RIDE 12/07") == "Transport"
    assert categorize_transaction("SWIGGY ORDER #4521") == "Food"
    assert categorize_transaction("NETFLIX SUBSCRIPTION") == "Entertainment"
    assert categorize_transaction("RANDOM UNKNOWN MERCHANT") == "Other"
    assert categorize_transaction("") == "Other"


def test_calculate_monthly_total():
    transactions = [
        {"date": "2026-07-01", "amount": 100},
        {"date": "2026-07-15", "amount": 250.50},
        {"date": "2026-06-20", "amount": 500},  # different month, should be excluded
        {"date": "2026-07-31", "amount": "49.50"},  # string amount should still work
    ]

    assert calculate_monthly_total(transactions, "2026-07") == 400.0
    assert calculate_monthly_total(transactions, "2026-06") == 500.0
    assert calculate_monthly_total(transactions, "2026-01") == 0.0
    assert calculate_monthly_total([], "2026-07") == 0.0


def test_parse_csv_import(tmp_path):
    csv_file = tmp_path / "transactions.csv"
    csv_file.write_text(
        "date,description,amount\n"
        "2026-07-01,UBER RIDE,150\n"
        "2026-07-02,SWIGGY ORDER,320.50\n"
        "2026-07-03,,100\n"                # missing description -> skipped
        "2026-07-04,BAD AMOUNT,notanumber\n"  # invalid amount -> skipped
    )

    transactions = parse_csv_import(str(csv_file))

    assert len(transactions) == 2
    assert transactions[0]["description"] == "UBER RIDE"
    assert transactions[0]["amount"] == 150.0
    assert transactions[1]["amount"] == 320.50

    # non-existent file should return empty list, not raise
    assert parse_csv_import(str(tmp_path / "does_not_exist.csv")) == []