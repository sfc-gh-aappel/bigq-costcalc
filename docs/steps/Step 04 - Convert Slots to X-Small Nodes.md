# Step 4 — Convert Slots to X-Small Snowflake Nodes

## Purpose

Translate BigQuery's average slot count into an equivalent number of X-Small Snowflake nodes.

## Why This Matters

This is the core translation step between the two platforms. BigQuery measures compute in slots (units of parallel processing capacity). Snowflake runs compute on warehouses made of nodes. The comparison used here is a hardware comparison: **16 BigQuery slots = 1 X-Small Snowflake node**.

## Inputs

| Input | Source | Description |
|---|---|---|
| Average Slots | Step 3 | Average sustained slot count for the month |
| Slots per X-Small node | Fixed | **16** BigQuery slots = 1 X-Small Snowflake node |

## Formula

```
X-Small Nodes = Average Slots / 16
```

An X-Small node uses 1 credit per hour while running, which is how Step 5 turns nodes into monthly credits.

## Notes on the 16:1 Comparison

16 slots = 1 X-Small node is a hardware comparison, not an exact performance match. Actual throughput varies by workload type (ETL vs. analytics vs. ML). Discuss it with the customer or account team before presenting the estimate.

## Example

| Month | Pricing Model | Avg Slots | X-Small Nodes |
|---|---|---|---|
| March | Reservation | 1,474.89 | 92.18 |
| March | On-Demand | 579.18 | 36.20 |

## Output

Equivalent X-Small nodes per month per pricing model — carried forward to Step 5.

## Next Step

[Step 5 — Calculate Credits per Month](Step%2005%20-%20Calculate%20Credits%20per%20Month.md)
