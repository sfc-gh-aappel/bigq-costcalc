# Step 5 — Calculate Credits per Month

## Purpose

Compute the total Snowflake credits consumed per month by combining the X-Small node count with the 1 credit per hour an X-Small node uses, the number of hours in a month, and the utilization percentage.

## Why This Matters

This is where utilization enters the calculation. A customer doesn't run queries every hour of the month. On Snowflake, warehouses can auto-suspend when idle, so we only need to pay for the hours they're actually used. The utilization percentage from Step 1 scales the monthly credit count to reflect real-world usage patterns rather than 24/7 operation.

## Inputs

| Input | Source | Description |
|---|---|---|
| X-Small Nodes | Step 4 | Equivalent X-Small Snowflake nodes for the month |
| Credits per X-Small node hour | Constant | 1 |
| Hours per Month | Constant | 730 |
| Utilization % | Step 1 | Fraction of time compute is active (by pricing model) |

## Formula

```
Credits per Month = X-Small Nodes x 1 credit/hr x Hours per Month x Utilization %
```

Where:
- Hours per Month = **730**
- Utilization % = the reservation or on-demand value from Step 1

## Example

| Month | Pricing Model | X-Small Nodes | Hours | Utilization % | Credits/Month |
|---|---|---|---|---|---|
| March | Reservation | 92.18 | 730 | 59.7% | 40,169 |
| March | On-Demand | 36.20 | 730 | 12.3% | 3,259 |

## Output

Monthly credit consumption by pricing model — carried forward to Step 6 and Step 7.

## Next Step

[Step 6 — Calculate Monthly Snowflake Compute Cost](Step%2006%20-%20Calculate%20Monthly%20Compute%20Cost.md)
