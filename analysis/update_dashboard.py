"""One command to rebuild the dashboard: python analysis/update_dashboard.py
Rebuilds the KPI tables (with the reconcile checks) and dashboard/index.html from the data. If a cost file is in data/costs/
(book_costs.csv, cost_by_year.csv or cost_pct_of_price.csv) the Profit page turns on by itself."""
import os, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for step in ("build_kpis.py", "build_dashboard.py"):
    r = subprocess.run([sys.executable, f"{R}/analysis/{step}"], cwd=R)
    if r.returncode != 0: print("\nSTOPPED in", step, ": see the message above (a total that does not reconcile or a cost-file problem)."); sys.exit(r.returncode)
print("\nDONE. Open dashboard/index.html in your browser (double-click it).")
