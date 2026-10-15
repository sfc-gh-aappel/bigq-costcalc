# Step 8 — Determine Starting Compute Credits

## Purpose

Combine the averaged reservation and on-demand credits into a single starting monthly credit number. This is the baseline for the growth projection in Step 12.

## Why This Matters

BigQuery customers often have both reservation and on-demand projects. On Snowflake, all compute comes from the same credit pool regardless of whether the original workload was flat-rate or on-demand. Summing the two gives us the total equivalent monthly credit consumption.

## Inputs

| Input | Source | Description |
|---|---|---|
| Avg Monthly Credits (Reservation) | Step 7 | Average monthly credits for reservation projects |
| Avg Monthly Credits (On-Demand) | Step 7 | Average monthly credits for on-demand projects |

## Formula

```
Starting Monthly Credits = Avg Monthly Credits (Reservation) + Avg Monthly Credits (On-Demand)
```

## Example

| Component | Avg Monthly Credits |
|---|---|
| Reservation | 42,153 |
| On-Demand | 3,385 |
| **Starting Total** | **45,538** |

## Output

A single starting monthly credit number — this is the month-one baseline used in the compute projection (Step 12).

## Next Step

[Step 9 — Calculate Month-One Storage](Step%2009%20-%20Calculate%20Month-One%20Storage.md)
