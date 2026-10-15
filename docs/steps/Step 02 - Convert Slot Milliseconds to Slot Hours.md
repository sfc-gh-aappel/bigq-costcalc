# Step 2 — Convert Slot Milliseconds to Slot Hours

## Purpose

Convert the raw BigQuery consumption metric (slot milliseconds) into slot hours so it can be used in the credit conversion calculation.

## Why This Matters

BigQuery reports consumption in slot milliseconds — a very granular unit that isn't directly comparable to anything in Snowflake. Converting to slot hours gives us a unit we can divide by calendar hours and then map to Snowflake credits.

## Inputs

| Input | Source | Description |
|---|---|---|
| Slot Milliseconds | BigQuery source data | Total slot time consumed, per month, per pricing model |

## Formula

```
Slot Hours = Slot Milliseconds / (1,000 x 60 x 60)
```

Which simplifies to:

```
Slot Hours = Slot Milliseconds / 3,600,000
```

Calculate this for each month, separately for reservation and on-demand projects.

## Example

| Month | Pricing Model | Slot Milliseconds | Slot Hours |
|---|---|---|---|
| March | Reservation | 3,876,014,481,870 | 1,076,671 |
| March | On-Demand | 1,522,093,908,329 | 422,804 |

## Output

Monthly slot hours by pricing model — carried forward to Step 3.

## Next Step

[Step 3 — Calculate Average Number of Slots](Step%2003%20-%20Calculate%20Average%20Number%20of%20Slots.md)
