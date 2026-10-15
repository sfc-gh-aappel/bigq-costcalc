# Step 1 — Calculate Utilization Percentage

## Purpose

Determine what fraction of available compute time the customer's BigQuery projects are actually running queries. This is calculated separately for **reservation** and **on-demand** projects because each pricing model has very different utilization patterns.

## Why This Matters

BigQuery slots are allocated continuously under reservations, but queries don't run 24/7. The utilization percentage lets us right-size the Snowflake estimate so we're not converting idle capacity into Snowflake credits. Without this adjustment, the estimate would assume the customer needs compute running around the clock, which dramatically overstates cost.

## Inputs

| Input | Source | Description |
|---|---|---|
| Total Active Minutes | BigQuery source data | Sum of minutes where queries were actively executing, across all projects of this pricing type |
| Total Minutes | Calendar | Total calendar minutes in the observation period |

## Formula

```
Utilization % = Total Active Minutes / Total Minutes
```

Calculate this separately for:
- **Reservation projects** (typical result: ~60%)
- **On-demand projects** (typical result: ~13%)

## Example

| Pricing Model | Active Minutes | Total Minutes | Utilization % |
|---|---|---|---|
| Reservation | 735,800 | 1,232,640 | 59.7% |
| On-demand | 114,020 | 924,480 | 12.3% |

## Output

Two utilization percentages — one for reservation, one for on-demand — carried forward to Step 5.

## Next Step

[Step 2 — Convert Slot Milliseconds to Slot Hours](Step%2002%20-%20Convert%20Slot%20Milliseconds%20to%20Slot%20Hours.md)
