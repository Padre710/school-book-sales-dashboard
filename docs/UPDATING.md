# Updating the dashboard

**New invoices:** append rows with the same columns to `data/processed/invoices.csv` and `data/processed/lines.csv` (and a row to `customers.csv` for a new customer, with a new Customer_ID). Then run `python tests/check_data.py` and `python analysis/update_dashboard.py`.

**Costs:** put `book_costs.csv` (columns as in `book_costs_TEMPLATE.csv`: Book_Title, Year, Unit_Cost_NGN), or `cost_by_year.csv` (Year, Average_Unit_Cost_NGN_all_titles), or `cost_pct_of_price.csv` (Year, Cost_Pct) in `data/costs/` and run `python analysis/update_dashboard.py`. The Profit tab fills in; titles or years without a cost show revenue only. Cost files are ignored by git by default (`.gitignore`) so they stay private.

**The totals must reconcile:** the build stops if the yearly, monthly, customer and line tables disagree; fix the data first.
