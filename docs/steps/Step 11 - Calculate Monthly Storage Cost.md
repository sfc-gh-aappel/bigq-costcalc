# Step 11 — Calculate Monthly Storage Cost

## Purpose

Convert the projected monthly storage volume into dollars using the customer's price per TB.

## Why This Matters

This produces the storage cost component of the estimate. The price per TB varies by customer contract and region.

## Inputs

| Input | Source | Description |
|---|---|---|
| Month N Storage (TB) | Step 10 | Projected storage volume for each month |
| Price per TB | Customer | Price per TB per month (default: $23.00) |

## Formula

```
Monthly Storage Cost ($) = Month N Storage (TB) x Price per TB
```

## Notes on Price per TB

Use the customer's actual contracted rate when available. Otherwise use the $23.00 default and say so in the report.

## Example

Sample Retail Co at $23.00 per TB:

| Month | Storage (TB) | Monthly Storage Cost |
|---|---|---|
| 1 | 54.0 | $1,242 |
| 12 | 60.3 | $1,386 |
| 24 | 66.3 | $1,524 |
| 36 | 71.6 | $1,646 |

## Output

Monthly storage cost in dollars for each month — carried forward to Step 13 for annual summation.

## Next Step

[Step 12 — Project Compute Growth](Step%2012%20-%20Project%20Compute%20Growth.md)
