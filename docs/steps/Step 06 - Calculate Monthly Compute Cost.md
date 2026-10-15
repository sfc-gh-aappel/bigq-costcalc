# Step 6 — Calculate Monthly Snowflake Compute Cost

## Purpose

Convert the monthly credit consumption into dollars using the customer's contracted price per credit.

## Why This Matters

This produces the actual dollar figure for each month's compute cost on Snowflake. The price per credit varies by customer based on their contract (ACV tier, edition, region).

## Inputs

| Input | Source | Description |
|---|---|---|
| Credits per Month | Step 5 | Monthly credit consumption by pricing model |
| Price per Credit | Customer contract | Price per credit (default: $4.00, Business Critical list price) |

## Formula

```
Monthly Compute Cost ($) = Credits per Month x Price per Credit
```

## Example

| Month | Pricing Model | Credits/Month | Price/Credit | Monthly Cost |
|---|---|---|---|---|
| March | Reservation | 40,169 | $4.00 | $160,674 |
| March | On-Demand | 3,259 | $4.00 | $13,037 |
| **March** | **Total** | **43,428** | | **$173,711** |

## Output

Monthly compute cost in dollars by pricing model — carried forward to Step 7 for averaging.

## Next Step

[Step 7 — Average Across the Observation Period](Step%2007%20-%20Average%20Across%20Observation%20Period.md)
