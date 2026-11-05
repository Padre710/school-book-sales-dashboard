# Data dictionary

All amounts are in **naira (₦), nominal** (not adjusted for inflation). Dates are the dates written on the invoices, ISO format. Customers are anonymised: `Customer_ID` is a code, ranked by total revenue (C001 is the biggest).

## data/processed/invoices.csv (one row per invoice: use this for revenue, discounts and counts)
| Column | Meaning |
|---|---|
| Year | Calendar year of the invoice |
| Invoice_No | Number printed on the invoice paper (unique within a year) |
| Date | Date written on the invoice (the day can be uncertain on a few faded papers; the month is reliable) |
| Customer_ID | Anonymous customer code, one per real customer after merging spelling variants |
| Customer_Type | School, Bookshop, Individual, Individual (probably), Regional coordinator, Unknown (decided from the wording of the name; see docs) |
| Lines | Number of book lines on the invoice |
| Books | Total copies on the invoice (sum of Qty) |
| Gross_Total | Value of the lines before discount, as written on the invoice |
| Discount | Discount given (0 if none) |
| Net_Total | What was paid (gross less discount). All invoices are assumed paid in full |
| Discount_Pct | Discount as a percentage of Gross_Total |
Empty Gross_Total / Net_Total: one invoice lists quantities only (no prices).

## data/processed/lines.csv (one row per book line)
| Column | Meaning |
|---|---|
| Line_ID | Row number |
| Year, Invoice_No | Link to invoices.csv |
| Book_Title | One of 13 standard titles (short forms written on the invoices were mapped to the full title), or TRANSPORTATION (a transport charge, not a book) |
| Qty | Copies |
| Unit_Price | Price per copy as written (some invoices show prices with a discount already inside, for example 198 instead of 220) |
| Line_Total | Qty x Unit_Price as written |
Do not add Gross/Discount/Net from this file: they live in invoices.csv. 16 invoices have lines that do not add up to the gross written on the paper (the shop's own arithmetic); they are kept as written (see docs/data_quality.md).

## data/processed/customers.csv (one row per customer)
Customer_ID, Customer_Type, Type_Confidence (high / medium / low), Invoices, Years_Active, First_Date, Last_Date, Net_Total, Books.

## analysis/tables/
Every table behind a dashboard chart (yearly, monthly, month of year, titles, usual price per title and year, customers, revenue by type and year) and `reconcile.txt` (all totals must agree: the build stops otherwise). Title revenue is the invoice's net revenue shared out over its lines in proportion to the line totals, so titles add up to the invoices.
