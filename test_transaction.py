from app.db import init_db
from app.models import add_transaction, get_all_transactions, set_budget, get_budgets

init_db()

add_transaction("2026-07-01", "UBER RIDE", 180.0, "Transport")
add_transaction("2026-07-02", "SWIGGY ORDER", 340.5, "Food")

print(get_all_transactions())

set_budget("Food", 5000)
print(get_budgets())