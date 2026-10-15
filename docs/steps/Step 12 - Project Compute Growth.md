# Step 12 — Project Compute Growth

## Purpose

Forecast monthly compute credits and cost for the 36-month projection, using a separate annual growth rate for Year 1, Year 2, and Year 3.

## Why This Matters

Compute workloads typically grow as the customer adds users, queries, ETL jobs, and new use cases. Applying a growth rate produces a realistic trajectory rather than a flat line.

## Inputs

| Input | Source | Description |
|---|---|---|
| Starting Monthly Credits | Step 8 | Baseline monthly credit consumption |
| Compute Growth (Year 1, 2, 3) | Assumption | Annual compute growth for each year (default: 5% each) |
| Price per Credit | Customer | Price per credit (default: $4.00, Business Critical list price) |

## Formulas

**Convert each year's annual rate to a monthly rate:**

```
Monthly Rate = (1 + Annual Rate) ^ (1/12) - 1
```

Example: 5% annual = (1.05)^(1/12) - 1 = **0.41% monthly**

**Grow month by month, using the rate for the year that month falls in:**

```
Month N Credits = Month N-1 Credits x (1 + Monthly Rate for that year)
Month N Compute Cost ($) = Month N Credits x Price per Credit
```

## Example

Sample Retail Co: 45,538 starting credits, growth of 5% / 7% / 7%, $4.00 per credit:

| Month | Credits | Monthly Compute Cost |
|---|---|---|
| 1 | 45,538 | $182,152 |
| 12 | 47,621 | $190,484 |
| 24 | 50,954 | $203,817 |
| 36 | 54,521 | $218,085 |

## Output

Monthly credits and compute cost for each of the 36 months — carried forward to Step 13 for annual summation.

## Next Step

[Step 13 — Sum Annual Totals](Step%2013%20-%20Sum%20Annual%20Totals.md)
