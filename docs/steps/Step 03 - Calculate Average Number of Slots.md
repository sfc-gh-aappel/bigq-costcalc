# Step 3 — Calculate Average Number of Slots

## Purpose

Determine the average sustained slot count the customer ran during each month. This translates "total work done" into "how much parallel capacity was needed on average."

## Why This Matters

Snowflake doesn't use slots — it runs compute on warehouses made of nodes. To bridge the two models, we need to know how many slots were running on average, so we can convert that into an equivalent number of X-Small Snowflake nodes (16 slots = 1 X-Small node).

## Inputs

| Input | Source | Description |
|---|---|---|
| Slot Hours | Step 2 | Total slot hours consumed in the month |
| Hours per Month | Constant | 730 (standard assumption for hours in a month) |

## Formula

```
Average Slots = Slot Hours / Hours per Month
```

Where Hours per Month = **730**.

## Example

| Month | Pricing Model | Slot Hours | Avg Slots |
|---|---|---|---|
| March | Reservation | 1,076,671 | 1,474.89 |
| March | On-Demand | 422,804 | 579.18 |

## Output

Average slot count per month per pricing model — carried forward to Step 4.

## Next Step

[Step 4 — Convert Slots to X-Small Snowflake Nodes](Step%2004%20-%20Convert%20Slots%20to%20X-Small%20Nodes.md)
