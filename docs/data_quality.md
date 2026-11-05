# Data quality: the final review

The finished data was checked once more, independently of the cleaning rules.

| Check | Result |
|---|---|
| Every photo belongs to exactly one invoice, in one year (no paper counted twice) | passed after fixing one double count found by this check |
| The number printed on the paper equals the invoice number (two blind readers) | 487 photos compared; the differences are partial misreads or documented decisions |
| No two invoices with the same customer, date, total and lines | passed |
| Quantity x price = line total | passed |
| Lines add up to the gross total | passed for all but 16 invoices (difference ₦39,847 of ₦12.2 million): the shop's own arithmetic or a missing line; kept as written and listed |
| Gross - discount = net | passed, apart from documented decisions on a few invoices |
| Dates are valid, in the right year, and fit the invoice numbering | passed apart from invoices confirmed by the owner |
| Titles are the 13 standard titles | passed |
| Prices follow a sensible trend per title | each title rises over time; unusual prices are listed for a person to look at |
| All dashboard totals reconcile (yearly = monthly = customers = lines) | passed to the naira (analysis/tables/reconcile.txt) |

## What the final review found and fixed
1. A group of invoices moved from one year to another were still present in both (counted twice).
2. One invoice carried a copy of its neighbour's lines; the real paper was a different customer with a single line.
3. Two different papers shared one invoice number.

## Customers
497 spellings of customer names (abbreviations, typos, a place added) were merged into 337 customers (plus a publisher-branch group). Safe merges were automatic; the doubtful ones were decided by the owner. The customer type (school, bookshop, individual, regional coordinator) is decided from the words in the name and carries a confidence.
