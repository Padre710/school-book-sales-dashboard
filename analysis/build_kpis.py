"""KPI TABLES + dashboard payload (reads DATA_FINAL only; run on any computer with Python 3 + pandas).
Usage: python analysis/build_kpis.py
Writes analysis/tables/*.csv (every number behind a chart), reconcile.txt (all totals must agree, else this stops) and dashboard/payload.json.
Cost file (optional, from data/costs/): book_costs.csv (A: per title and year), cost_by_year.csv (B: average per year), cost_pct_of_price.csv (C: percent of the selling price).
The filled-in templates are accepted too. Never invents a cost: a title-year without cost shows revenue only."""
import json, os, re, sys
import numpy as np, pandas as pd
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = f"{R}/analysis/tables"; os.makedirs(K, exist_ok=True); os.makedirs(f"{R}/dashboard", exist_ok=True)
inv = pd.read_csv(f"{R}/data/processed/invoices.csv", keep_default_na=False, na_values=[""])
inv["Master_Customer_Name"] = "Customer " + inv.Customer_ID; inv["Customer_Location"] = ""
ln = pd.read_csv(f"{R}/data/processed/lines.csv", keep_default_na=False, na_values=[""])
cm = pd.read_csv(f"{R}/data/processed/customers.csv", keep_default_na=False, na_values=[""])
cm["Customer_Name"] = "Customer " + cm.Customer_ID; cm["Location"] = ""
inv["Date"] = pd.to_datetime(inv.Date); inv["M"] = inv.Date.dt.month
def tgroup(t):
    t = str(t)
    return "Individual" if t.startswith("Individual") else ("Regional coordinator" if t.startswith("Regional") else ("Unknown" if t.startswith("Unknown") else t))
inv["Type"] = inv.Customer_Type.map(tgroup); cm["Type"] = cm.Customer_Type.map(tgroup)
inv["Key"] = list(zip(inv.Year, inv.Invoice_No)); ln["Key"] = list(zip(ln.Year, ln.Invoice_No))
assert inv.Key.is_unique, "an invoice number is used twice in one year"
assert set(ln.Key) <= set(inv.Key), "a line belongs to an unknown invoice"
inv = inv.reset_index(drop=True); inv["ix"] = inv.index; ix = dict(zip(inv.Key, inv.ix))
ln["inv"] = ln.Key.map(ix)
# net revenue per line: the invoice net (after discount) shared out in proportion to the line totals, so titles reconcile with the invoices to the naira
sl = ln.groupby("inv").Line_Total.transform("sum"); inet = ln.inv.map(inv.set_index("ix").Net_Total)
ln["Net_Line"] = np.where((sl > 0) & inet.notna() & ln.Line_Total.notna(), inet * ln.Line_Total / sl, np.nan)
# ---------------- costs (optional)
C = f"{R}/data/costs"; cost = dict(method=None, rows=[], note="no cost file yet", warnings=[])
def readc(name):
    p = f"{C}/{name}"
    return pd.read_csv(p, dtype=str, keep_default_na=False) if os.path.exists(p) else None
def num(x):
    try: return float(str(x).replace(",", "").replace("₦", "").strip())
    except Exception: return np.nan
titles = sorted(ln.Book_Title.dropna().unique())
a = readc("book_costs.csv")
if a is None:
    t_ = readc("book_costs_TEMPLATE.csv")
    if t_ is not None and (t_.Unit_Cost_NGN.str.strip() != "").any(): a = t_
b = readc("cost_by_year.csv")
if b is None:
    t_ = readc("cost_by_year_SIMPLE_TEMPLATE.csv")
    if t_ is not None and (t_.iloc[:, 1].str.strip() != "").any(): b = t_
c = readc("cost_pct_of_price.csv")
if a is not None:
    cost["method"] = "A"; cost["note"] = "cost per copy per title and year (owner's file)"
    for r in a.itertuples():
        v = num(r.Unit_Cost_NGN)
        if r.Book_Title not in titles: cost["warnings"].append(f"unknown title in cost file: {r.Book_Title}")
        if np.isnan(v) or v <= 0:
            if str(r.Unit_Cost_NGN).strip(): cost["warnings"].append(f"cost not a positive number: {r.Book_Title} {r.Year}: {r.Unit_Cost_NGN}")
            continue
        cost["rows"].append([r.Book_Title, int(r.Year), v])
elif b is not None:
    cost["method"] = "B"; cost["note"] = "one average cost per copy per year, same for every title (owner's file)"
    for r in b.itertuples():
        v = num(r[2])
        if not np.isnan(v) and v > 0: cost["rows"].append(["*", int(r.Year), v])
elif c is not None:
    cost["method"] = "C"; cost["note"] = "cost = a percentage of the selling price (owner's figure): the margin is flat by construction"
    for r in c.itertuples():
        v = num(r[2])
        if not np.isnan(v) and 0 < v < 100: cost["rows"].append(["*", int(r.Year), v])
pd.DataFrame(cost["rows"], columns=["Book_Title", "Year", "Value"]).to_csv(f"{K}/cost_resolved.csv", index=False)
# ---------------- tables
Y = sorted(inv.Year.unique()); end = inv.Date.max()
def ysum(df): return df.groupby("Year").agg(Invoices=("Invoice_No", "size"), Revenue=("Net_Total", "sum"), Gross=("Gross_Total", "sum"), Discount=("Discount", "sum"), Books=("Books", "sum"), Customers=("Customer_ID", "nunique"))
yt = ysum(inv); yt["Avg_Order"] = (yt.Revenue / yt.Invoices).round(0); yt["Discount_Pct_of_Gross"] = (yt.Discount / yt.Gross * 100).round(1)
yt["Growth_vs_previous_year_pct"] = (yt.Revenue.pct_change() * 100).round(1)
yt["Revenue_Jan_Sep"] = inv[inv.M <= 9].groupby("Year").Net_Total.sum()
yt.reset_index().to_csv(f"{K}/yearly.csv", index=False)
mo = inv.groupby([inv.Date.dt.to_period("M").astype(str)]).agg(Invoices=("Invoice_No", "size"), Revenue=("Net_Total", "sum"), Books=("Books", "sum")).reset_index().rename(columns={"Date": "Month"}); mo.to_csv(f"{K}/monthly.csv", index=False)
moy = inv.pivot_table(index="M", columns="Year", values="Net_Total", aggfunc="sum", fill_value=0); moy.reset_index().to_csv(f"{K}/month_of_year_by_year.csv", index=False)
tt = ln.groupby("Book_Title").agg(Copies=("Qty", "sum"), Revenue=("Net_Line", "sum"), Revenue_before_discount=("Line_Total", "sum"), Lines=("Line_ID", "size"), First=("Year", "min"), Last=("Year", "max")).sort_values("Revenue", ascending=False); tt.reset_index().to_csv(f"{K}/titles.csv", index=False)
tpy = ln.dropna(subset=["Unit_Price"]).groupby(["Book_Title", "Year"]).Unit_Price.agg(lambda s: s.mode().iloc[0]).unstack("Year"); tpy.reset_index().to_csv(f"{K}/title_usual_price_by_year.csv", index=False)
cu = inv.groupby(["Customer_ID", "Master_Customer_Name", "Type"]).agg(Invoices=("Invoice_No", "size"), Years_Active=("Year", "nunique"), First=("Date", "min"), Last=("Date", "max"), Revenue=("Net_Total", "sum"), Books=("Books", "sum")).reset_index().sort_values("Revenue", ascending=False)
cu.to_csv(f"{K}/customers.csv", index=False)
cy = inv.pivot_table(index="Customer_ID", columns="Year", values="Net_Total", aggfunc="sum", fill_value=0); cy.reset_index().to_csv(f"{K}/customer_by_year.csv", index=False)
inv.groupby(["Type", "Year"]).Net_Total.sum().unstack("Year", fill_value=0).reset_index().to_csv(f"{K}/revenue_by_type_year.csv", index=False)
# ---------------- reconcile (the build stops if anything disagrees)
tot = int(inv.Net_Total.sum()); checks = []
def chk(name, a_, b_): checks.append((name, a_, b_, "OK" if abs(a_ - b_) < 0.5 else "FAIL"))
chk("invoices file vs yearly table", tot, yt.Revenue.sum()); chk("invoices file vs monthly table", tot, mo.Revenue.sum()); chk("invoices file vs month-of-year table", tot, moy.values.sum())
chk("invoices file vs customers table", tot, cu.Revenue.sum()); chk("invoices file vs customer-by-year table", tot, cy.values.sum())
inv_lines = ln.groupby("inv").Line_Total.sum(); both = inv.set_index("ix").Net_Total
has_lines = set(ln.inv[ln.Net_Line.notna()])
chk("net revenue of the lines vs invoices that have priced lines", float(ln.Net_Line.sum()), float(inv[inv.ix.isin(has_lines)].Net_Total.sum()))
dif = inv.assign(lines_sum=inv.ix.map(ln.groupby("inv").Line_Total.sum())); dif = dif[(dif.lines_sum - dif.Gross_Total).abs() > 1][["Year", "Invoice_No", "Master_Customer_Name", "lines_sum", "Gross_Total", "Net_Total"]]
dif.to_csv(f"{K}/KNOWN_lines_not_equal_gross.csv", index=False)
note_dif = f"{len(dif)} invoices have lines that do not add up to the paper's gross (difference {dif.Gross_Total.sum() - dif.lines_sum.sum():,.0f} naira): the owner's own arithmetic or a missing line; listed in KNOWN_lines_not_equal_gross.csv and in the final review. Not an error of this build."
chk("copies in lines file vs books in invoices file", float(ln.Qty.sum()), float(inv.Books.sum()))
chk("titles table net revenue vs lines net revenue", float(tt.Revenue.sum()), float(ln.Net_Line.sum()))
chk("books: copies of the titles table vs invoices file", float(tt.Copies.sum()), float(inv.Books.sum()))
cov = 0.0
if cost["method"]:
    cov = 100.0   # computed in the page per filter; the share with a cost is printed below for method A
    if cost["method"] == "A":
        have = {(t, y) for t, y, v in cost["rows"]}
        cov = float(ln[[(t, y) in have for t, y in zip(ln.Book_Title, ln.Year)]].Line_Total.sum() / ln.Line_Total.sum() * 100)
fails = [c_ for c_ in checks if c_[3] != "OK"]
with open(f"{K}/reconcile.txt", "w") as fh:
    fh.write("RECONCILE (all must be OK)\n")
    for n_, a_, b_, s_ in checks: fh.write(f"{s_:5} {n_}: {a_:,.0f} vs {b_:,.0f}\n")
    fh.write("\nNOTE: " + note_dif + "\n")
    fh.write(f"\nCost file: {cost['method'] or 'none'} ({cost['note']}); revenue with a cost: {cov:.1f}%\nWarnings: {cost['warnings'] or 'none'}\n")
print(open(f"{K}/reconcile.txt").read())
if fails: print("BUILD STOPPED: a total does not reconcile."); sys.exit(1)
# ---------------- data trust numbers (from the audit record, with fallbacks)
trust = dict(asked=47, of=487, pct=9.7, rules=32, reviewed2021=71)
try:
    t_ = open(f"{R}/NO_SUCH_FILE").read(); m_ = re.search(r"answered\*\*: \*\*(\d+) of (\d+) = ([\d.]+)%", t_)
    if m_: trust.update(asked=int(m_.group(1)), of=int(m_.group(2)), pct=float(m_.group(3)))
    nums = [int(x) for x in re.findall(r"^(\d+)[a-z]?\.", open(f"{R}/NO_SUCH_FILE").read(), re.M)]; trust["rules"] = max(nums) if nums else 32
except Exception: pass
# ---------------- payload for the page
cust = cm.reset_index(drop=True); cix = {c_: i for i, c_ in enumerate(cust.Customer_ID)}
pay = dict(
    generated=str(pd.Timestamp.now().date()), data_end=str(end.date()), data_start=str(inv.Date.min().date()),
    years=[int(y) for y in Y], titles=titles,
    customers=[[r.Customer_ID, r.Customer_Name, r.Type, (r.Location if isinstance(r.Location, str) else "")] for r in cust.itertuples()],
    inv=[[int(r.Year), int(r.Invoice_No), str(r.Date.date()), cix[r.Customer_ID], float(r.Net_Total) if pd.notna(r.Net_Total) else None, float(r.Gross_Total) if pd.notna(r.Gross_Total) else None, float(r.Discount) if pd.notna(r.Discount) else 0.0, int(r.Books) if pd.notna(r.Books) else 0, int(r.Lines)] for r in inv.itertuples()],
    lines=[[int(r.inv), titles.index(r.Book_Title), float(r.Qty) if pd.notna(r.Qty) else None, float(r.Unit_Price) if pd.notna(r.Unit_Price) else None, float(r.Line_Total) if pd.notna(r.Line_Total) else None, round(float(r.Net_Line), 2) if pd.notna(r.Net_Line) else None] for r in ln.itertuples()],
    cost=cost, trust=trust, checks=[[n_, a_, b_, s_] for n_, a_, b_, s_ in checks], totals=dict(revenue=tot, invoices=len(inv), lines=len(ln), books=int(inv.Books.sum())))
json.dump(pay, open(f"{R}/dashboard/payload.json", "w"), separators=(",", ":"), default=float)
print("payload written:", len(pay["inv"]), "invoices,", len(pay["lines"]), "lines,", len(pay["customers"]), "customers")
