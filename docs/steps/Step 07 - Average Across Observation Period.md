# Step 7 — Average Across the Observation Period

## Purpose

Compute a single representative monthly credit figure by averaging across all months of source data. This becomes the baseline for the multi-year projection.

## Why This Matters

Monthly BigQuery consumption varies due to seasonality, one-time loads, and business cycles. Averaging across the observation window (e.g., March through September) smooths these fluctuations and produces a more defensible starting point than picking a single month.

## Inputs

| Input | Source | Description |
|---|---|---|
| Monthly Credits (Reservation) | Step 5 | Credits per month for each observed month, reservation projects |
| Monthly Credits (On-Demand) | Step 5 | Credits per month for each observed month, on-demand projects |
| Number of Months | Source data | Count of months in the observation period |

## Formulas

```
Avg Monthly Credits (Reservation) = SUM(Monthly Reservation Credits) / Number of Months

Avg Monthly Credits (On-Demand)   = SUM(Monthly On-Demand Credits) / Number of Months
```

## Example

Using 7 months of data (March through September):

| Pricing Model | Total Credits (7 months) | Avg Monthly Credits |
|---|---|---|
| Reservation | 295,069 | 42,153 |
| On-Demand | 23,698 | 3,385 |

## Output

Two average monthly credit values — carried forward to Step 8.

## Next Step

[Step 8 — Determine Starting Compute Credits](Step%2008%20-%20Determine%20Starting%20Compute%20Credits.md)
