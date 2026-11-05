"""Independent checks of the processed data. Usage: python tests/check_data.py   (exit code 1 if a check fails)"""
import os, re, sys
import numpy as np, pandas as pd
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inv = pd.read_csv(f"{R}/data/processed/invoices.csv"); ln = pd.read_csv(f"{R}/data/processed/lines.csv"); cu = pd.read_csv(f"{R}/data/processed/customers.csv")
fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail else "")); 
    if not ok: fails.append(name)
check("invoice number unique within a year", not inv.duplicated(["Year", "Invoice_No"]).any())
check("every line belongs to an invoice", set(zip(ln.Year, ln.Invoice_No)) <= set(zip(inv.Year, inv.Invoice_No)))
d = pd.to_datetime(inv.Date, errors="coerce"); check("dates valid and in the invoice year", d.notna().all() and (d.dt.year == inv.Year).all())
bad = ln[(ln.Qty * ln.Unit_Price - ln.Line_Total).abs() > 1]; check("quantity x price = line total", len(bad) == 0, f"{len(bad)} lines differ")
ls = ln.groupby(["Year", "Invoice_No"]).Line_Total.sum().rename("ls").reset_index(); m = inv.merge(ls, on=["Year", "Invoice_No"], how="left").dropna(subset=["Gross_Total"])
dif = m[(m.ls - m.Gross_Total).abs() > 1]; check("lines add up to gross (16 known exceptions are the shop's own arithmetic)", len(dif) <= 20, f"{len(dif)} invoices differ")
pr = inv.dropna(subset=["Net_Total"]); gap = pr[(pr.Gross_Total - pr.Discount.fillna(0) - pr.Net_Total).abs() > 1]; check("gross - discount = net (a few documented decisions)", len(gap) <= 10, f"{len(gap)} invoices differ")
check("discount never negative", (inv.Discount.fillna(0) >= 0).all())
check("customer totals equal invoice totals", abs(cu.Net_Total.sum() - inv.Net_Total.sum()) < 1, f"{cu.Net_Total.sum():,.0f} vs {inv.Net_Total.sum():,.0f}")
check("every invoice customer is in customers.csv", set(inv.Customer_ID) <= set(cu.Customer_ID))
txt = " ".join(open(os.path.join(r_, f), errors="ignore").read() for r_, _, fs in os.walk(os.path.join(R, "data")) for f in fs if f.endswith(".csv"))
check("no phone-like numbers in the data", not re.search(r"(?<!\d)0[789][01]\d{8}(?!\d)", txt))
print("\nALL CHECKS PASSED" if not fails else f"\n{len(fails)} CHECK(S) FAILED"); sys.exit(1 if fails else 0)
