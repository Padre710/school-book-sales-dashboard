# Methodology: from handwritten invoices to a trusted dataset

## The problem
The sales of a small publisher were recorded on handwritten, carbon-copy invoice books. Each invoice was photographed, and an AI model read each photo into a spreadsheet (one row = one book line of an invoice). That first reading contained errors: misread digits and names, lines attached to the wrong invoice, photo links pointing at the wrong invoice, the same paper counted twice.

## Principle: never trust one reading, never guess
- A value is accepted only if the spreadsheet **agrees with at least one independent reading** of the photo. Two readers agreeing with each other is not enough (their mistakes are correlated; on a hand-checked year such automatic fixes were wrong about half the time).
- Independent readers were separate AI agents that worked on neutral copies of the photos and **never saw the spreadsheet**, the year folder or the invoice number.
- Anything that needs a decision is flagged, not guessed. No line that is not on the paper stays in the data; removals are logged.

## What was built
1. Two independent reading passes over 492 photos (names, lines, totals, dates).
2. A vote that compares the spreadsheet with the readers line by line.
3. **32 written rules** that clear invoices automatically when the evidence is strong. Families:
   - *Arithmetic*: quantity x price = line total; lines add up to the total; with two trusted fields the third is calculated; one unknown line is solved from the total; with one line, a certain total and several possible prices, only the price that gives a whole number of copies is chosen.
   - *Discounts*: a clean percentage (5, 10, 15, 20, 25) or a small round-figure difference is a discount, not an error; what was paid is the number after the discount.
   - *Dates and numbering*: invoice numbers run in time order, so a date that breaks the order of its neighbours is suspect; the neighbours and the readers settle it. A year written wrongly on the paper is a human slip, the neighbourhood wins.
   - *Photo links*: swapped or rotated links between invoices are detected from the printed numbers and repaired.
   - *Titles*: short forms written on the lines are mapped to the standard title.
   - *Not a sale*: a balance brought forward or a returned-books credit is not recorded as a sale.
4. **Human review**: what no rule could settle went to the owner, one invoice at a time, with the upright photo and a table of what was read and how sure each cell is. Every answer is logged and often became a new rule, so the owner was asked less and less.
5. **A final review** of the finished data (see data_quality.md) and an audit trail: every commit, every decision, how many invoices each rule cleared.

## Result
- 606 invoices, review queue empty in every year.
- For 2019-2026 (without 2021) the owner was asked about **47 of 487 invoices (9.7%)**; when 2021 was done entirely by hand it took 71%.
- The rules cleared the rest, together with decisions made from the photo under the owner's standing rules (logged and reversible).

## What was not automated
Reading the photos is still imperfect: faded ink, overwritten numbers and cropped edges. That is why every value is cross-checked, and why the data carries documented limitations (docs/limitations.md).
