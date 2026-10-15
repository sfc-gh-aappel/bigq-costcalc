# Step 10 — Project Storage Growth

## Purpose

Forecast storage volume month by month for the 36-month projection, using a separate annual growth rate for Year 1, Year 2, and Year 3.

## Why This Matters

Data volumes don't stay flat. Applying a growth rate produces a realistic projection rather than assuming static storage. Each year can have its own rate to reflect the customer's expected data growth.

## Inputs

| Input | Source | Description |
|---|---|---|
| Month 1 Storage (TB) | Step 9 | Starting storage including time travel / failsafe |
| Storage Growth (Year 1, 2, 3) | Assumption | Annual storage growth for each year (default: 12.7% each) |

## Formulas

**Convert each year's annual rate to a monthly rate:**

```
Monthly Rate = (1 + Annual Rate) ^ (1/12) - 1
```

**Grow month by month, using the rate for the year that month falls in:**

```
Month N Storage (TB) = Month N-1 Storage x (1 + Monthly Rate for that year)
```

Months 1–12 use the Year 1 rate, 13–24 the Year 2 rate, and 25–36 the Year 3 rate.

## Example

Sample Retail Co: 54 TB in month 1, growth of 12.7% / 10% / 8%:

| Month | Storage (TB) |
|---|---|
| 1 | 54.0 |
| 12 | 60.3 |
| 24 | 66.3 |
| 36 | 71.6 |

## Output

Monthly storage volume in TB for each of the 36 months — carried forward to Step 11 for cost calculation.

## Next Step

[Step 11 — Calculate Monthly Storage Cost](Step%2011%20-%20Calculate%20Monthly%20Storage%20Cost.md)
