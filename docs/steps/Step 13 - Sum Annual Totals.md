# Step 13 — Sum Annual Totals

## Purpose

Add up the monthly storage and compute costs into totals for Year 1, Year 2, and Year 3.

## Why This Matters

Contract negotiations and budget planning happen at an annual level. Summing the monthly projections gives the customer (and the account team) the annual figures they need for pricing discussions.

## Inputs

| Input | Source | Description |
|---|---|---|
| Monthly Storage Cost | Step 11 | Storage cost for each month (months 1–36) |
| Monthly Compute Cost | Step 12 | Compute cost for each month (months 1–36) |

## Formulas

```
Year 1 Total = SUM of monthly storage + compute cost for months 1–12
Year 2 Total = SUM of monthly storage + compute cost for months 13–24
Year 3 Total = SUM of monthly storage + compute cost for months 25–36
```

## Example

Sample Retail Co:

| Component | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Storage | $15,753 | $17,518 | $19,077 |
| Compute | $2,235,475 | $2,371,578 | $2,537,588 |
| **Total** | **$2,251,228** | **$2,389,096** | **$2,556,665** |

## Output

Annual totals for Years 1, 2, and 3 — carried forward to Step 14 for range application.

## Next Step

[Step 14 — Apply Low / High Range](Step%2014%20-%20Apply%20Low%20High%20Range.md)
